from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
import logging
import os
import time
import traceback
import typing
from typing import Any
from typing import Callable
from typing import List
from typing import Literal
from typing import Optional

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket
from fastapi.websockets import WebSocketDisconnect
from typing import Optional
from google.genai import types
import graphviz
from opentelemetry import trace
from opentelemetry.sdk.trace import export as export_lib
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace import TracerProvider
from pydantic import Field
from pydantic import ValidationError
from starlette.types import Lifespan
from typing_extensions import override
from watchdog.observers import Observer

from google.adk.cli import agent_graph
from google.adk.agents.live_request_queue import LiveRequest
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.agents.run_config import StreamingMode
from google.adk.artifacts.base_artifact_service import BaseArtifactService
from google.adk.auth.credential_service.base_credential_service import BaseCredentialService
from google.adk.errors.not_found_error import NotFoundError
from google.adk.evaluation.base_eval_service import InferenceConfig
from google.adk.evaluation.base_eval_service import InferenceRequest
from google.adk.evaluation.constants import MISSING_EVAL_DEPENDENCIES_MESSAGE
from google.adk.evaluation.eval_case import EvalCase
from google.adk.evaluation.eval_case import SessionInput
from google.adk.evaluation.eval_metrics import EvalMetric
from google.adk.evaluation.eval_metrics import EvalMetricResult
from google.adk.evaluation.eval_metrics import EvalMetricResultPerInvocation
from google.adk.evaluation.eval_metrics import MetricInfo
from google.adk.evaluation.eval_result import EvalSetResult
from google.adk.evaluation.eval_set_results_manager import EvalSetResultsManager
from google.adk.evaluation.eval_sets_manager import EvalSetsManager
from google.adk.events.event import Event
from google.adk.memory.base_memory_service import BaseMemoryService
from google.adk.runners import Runner
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.session import Session
from google.adk.cli.cli_eval import EVAL_SESSION_ID_PREFIX
from google.adk.cli.cli_eval import EvalStatus
from google.adk.cli.utils import cleanup
from google.adk.cli.utils import common
from google.adk.cli.utils import envs
from google.adk.cli.utils import evals
from google.adk.cli.utils.base_agent_loader import BaseAgentLoader
from google.adk.cli.utils.shared_value import SharedValue
from google.adk.cli.utils.state import create_empty_state

logger = logging.getLogger("google_adk." + __name__)

_EVAL_SET_FILE_EXTENSION = ".evalset.json"


class ApiServerSpanExporter(export_lib.SpanExporter):

  def __init__(self, trace_dict):
    self.trace_dict = trace_dict

  def export(
      self, spans: typing.Sequence[ReadableSpan]
  ) -> export_lib.SpanExportResult:
    for span in spans:
      if (
          span.name == "call_llm"
          or span.name == "send_data"
          or span.name.startswith("execute_tool")
      ):
        attributes = dict(span.attributes)
        attributes["trace_id"] = span.get_span_context().trace_id
        attributes["span_id"] = span.get_span_context().span_id
        if attributes.get("gcp.vertex.agent.event_id", None):
          self.trace_dict[attributes["gcp.vertex.agent.event_id"]] = attributes
    return export_lib.SpanExportResult.SUCCESS

  def force_flush(self, timeout_millis: int = 30000) -> bool:
    return True


class InMemoryExporter(export_lib.SpanExporter):

  def __init__(self, trace_dict):
    super().__init__()
    self._spans = []
    self.trace_dict = trace_dict

  @override
  def export(
      self, spans: typing.Sequence[ReadableSpan]
  ) -> export_lib.SpanExportResult:
    for span in spans:
      trace_id = span.context.trace_id
      if span.name == "call_llm":
        attributes = dict(span.attributes)
        session_id = attributes.get("gcp.vertex.agent.session_id", None)
        if session_id:
          if session_id not in self.trace_dict:
            self.trace_dict[session_id] = [trace_id]
          else:
            self.trace_dict[session_id] += [trace_id]
    self._spans.extend(spans)
    return export_lib.SpanExportResult.SUCCESS

  @override
  def force_flush(self, timeout_millis: int = 30000) -> bool:
    return True

  def get_finished_spans(self, session_id: str):
    trace_ids = self.trace_dict.get(session_id, None)
    if trace_ids is None or not trace_ids:
      return []
    return [x for x in self._spans if x.context.trace_id in trace_ids]

  def clear(self):
    self._spans.clear()


# Import models from the models package
from ..models import (
    AgentRunRequest,
    HealthCheckResponse,
)

# Import platform service
from ..services.platform_service import PlatformService

# Import routers
from .routers import (
    setup_platform_router,
    setup_apps_router,
    setup_core_router,
)


class AdkWebServer:
  """Helper class for setting up and running the ADK web server on FastAPI.

  You construct this class with all the Services required to run ADK agents and
  can then call the get_fast_api_app method to get a FastAPI app instance that
  can will use your provided service instances, static assets, and agent loader.
  If you pass in a web_assets_dir, the static assets will be served under
  /dev-ui in addition to the API endpoints created by default.

  You can add add additional API endpoints by modifying the FastAPI app
  instance returned by get_fast_api_app as this class exposes the agent runners
  and most other bits of state retained during the lifetime of the server.

  Attributes:
      agent_loader: An instance of BaseAgentLoader for loading agents.
      session_service: An instance of BaseSessionService for managing sessions.
      memory_service: An instance of BaseMemoryService for managing memory.
      artifact_service: An instance of BaseArtifactService for managing
        artifacts.
      credential_service: An instance of BaseCredentialService for managing
        credentials.
      eval_sets_manager: An instance of EvalSetsManager for managing evaluation
        sets.
      eval_set_results_manager: An instance of EvalSetResultsManager for
        managing evaluation set results.
      agents_dir: Root directory containing subdirs for agents with those
        containing resources (e.g. .env files, eval sets, etc.) for the agents.
      runners_to_clean: Set of runner names marked for cleanup.
      current_app_name_ref: A shared reference to the latest ran app name.
      runner_dict: A dict of instantiated runners for each app.
  """

  def __init__(
      self,
      *,
      agent_loader: BaseAgentLoader,
      session_service: BaseSessionService,
      memory_service: BaseMemoryService,
      artifact_service: BaseArtifactService,
      credential_service: BaseCredentialService,
      eval_sets_manager: EvalSetsManager,
      eval_set_results_manager: EvalSetResultsManager,
      agents_dir: str,
  ):
    self.agent_loader = agent_loader
    self.session_service = session_service
    self.memory_service = memory_service
    self.artifact_service = artifact_service
    self.credential_service = credential_service
    self.eval_sets_manager = eval_sets_manager
    self.eval_set_results_manager = eval_set_results_manager
    self.agents_dir = agents_dir
    # Internal propeties we want to allow being modified from callbacks.
    self.runners_to_clean: set[str] = set()
    self.current_app_name_ref: SharedValue[str] = SharedValue(value="")
    self.runner_dict = {}
    # Platform service for app session management
    self.platform_service = PlatformService(
        agent_loader=agent_loader,
        session_service=session_service
    )

  async def get_runner_async(self, app_name: str) -> Runner:
    """Returns the runner for the given app."""
    if app_name in self.runners_to_clean:
      self.runners_to_clean.remove(app_name)
      runner = self.runner_dict.pop(app_name, None)
      await cleanup.close_runners(list([runner]))

    envs.load_dotenv_for_agent(os.path.basename(app_name), self.agents_dir)
    if app_name in self.runner_dict:
      return self.runner_dict[app_name]
    root_agent = self.agent_loader.load_agent(app_name)
    runner = Runner(
        app_name=app_name,
        agent=root_agent,
        artifact_service=self.artifact_service,
        session_service=self.session_service,
        memory_service=self.memory_service,
        credential_service=self.credential_service,
    )
    self.runner_dict[app_name] = runner
    return runner

  def get_fast_api_app(
      self,
      lifespan: Optional[Lifespan[FastAPI]] = None,
      allow_origins: Optional[list[str]] = None,
      web_assets_dir: Optional[str] = None,
      setup_observer: Callable[
          [Observer, "AdkWebServer"], None
      ] = lambda o, s: None,
      tear_down_observer: Callable[
          [Observer, "AdkWebServer"], None
      ] = lambda o, s: None,
      register_processors: Callable[[TracerProvider], None] = lambda o: None,
  ):
    """Creates a FastAPI app for the ADK web server.

    By default it'll just return a FastAPI instance with the API server
    endpoints,
    but if you specify a web_assets_dir, it'll also serve the static web assets
    from that directory.

    Args:
      lifespan: The lifespan of the FastAPI app.
      allow_origins: The origins that are allowed to make cross-origin requests.
      web_assets_dir: The directory containing the web assets to serve.
      setup_observer: Callback for setting up the file system observer.
      tear_down_observer: Callback for cleaning up the file system observer.
      register_processors: Callback for additional Span processors to be added
        to the TracerProvider.

    Returns:
      A FastAPI app instance.
    """
    # Properties we don't need to modify from callbacks
    trace_dict = {}
    session_trace_dict = {}
    # Set up a file system watcher to detect changes in the agents directory.
    observer = Observer()
    setup_observer(observer, self)

    @asynccontextmanager
    async def internal_lifespan(app: FastAPI):
      try:
        if lifespan:
          async with lifespan(app) as lifespan_context:
            yield lifespan_context
        else:
          yield
      finally:
        tear_down_observer(observer, self)
        # Create tasks for all runner closures to run concurrently
        await cleanup.close_runners(list(self.runner_dict.values()))

    # Set up tracing in the FastAPI server.
    provider = TracerProvider()
    provider.add_span_processor(
        export_lib.SimpleSpanProcessor(ApiServerSpanExporter(trace_dict))
    )
    memory_exporter = InMemoryExporter(session_trace_dict)
    provider.add_span_processor(export_lib.SimpleSpanProcessor(memory_exporter))

    register_processors(provider)

    trace.set_tracer_provider(provider)

    # Run the FastAPI server.
    app = FastAPI(lifespan=internal_lifespan)

    if allow_origins:
      app.add_middleware(
          CORSMiddleware,
          allow_origins=allow_origins,
          allow_credentials=True,
          allow_methods=["*"],
          allow_headers=["*"],
      )

    # 设置核心路由器
    core_router = setup_core_router(self.get_runner_async)
    
    # 重写核心路由器中的方法以访问实例变量
    @core_router.get("/list-apps")
    def list_apps() -> list[str]:
      return self.agent_loader.list_agents()

    @core_router.post("/run", response_model_exclude_none=True)
    async def agent_run(req: AgentRunRequest) -> list[Event]:
      session = await self.session_service.get_session(
          app_name=req.app_name, user_id=req.user_id, session_id=req.session_id
      )
      if not session:
        raise HTTPException(status_code=404, detail="Session not found")
      runner = await self.get_runner_async(req.app_name)
      events = [
          event
          async for event in runner.run_async(
              user_id=req.user_id,
              session_id=req.session_id,
              new_message=req.new_message,
          )
      ]
      logger.info("Generated %s events in agent run", len(events))
      logger.debug("Events generated: %s", events)
      return events

    @core_router.post("/run_sse")
    async def agent_run_sse(req: AgentRunRequest) -> StreamingResponse:
      # SSE endpoint
      session = await self.session_service.get_session(
          app_name=req.app_name, user_id=req.user_id, session_id=req.session_id
      )
      if not session:
        raise HTTPException(status_code=404, detail="Session not found")

      # Convert the events to properly formatted SSE
      async def event_generator():
        try:
          stream_mode = (
              StreamingMode.SSE if req.streaming else StreamingMode.NONE
          )
          runner = await self.get_runner_async(req.app_name)
          async for event in runner.run_async(
              user_id=req.user_id,
              session_id=req.session_id,
              new_message=req.new_message,
              state_delta=req.state_delta,
              run_config=RunConfig(streaming_mode=stream_mode),
          ):
            # Format as SSE data
            sse_event = event.model_dump_json(exclude_none=True, by_alias=True)
            logger.debug(
                "Generated event in agent run streaming: %s", sse_event
            )
            yield f"data: {sse_event}\\n\\n"
        except Exception as e:
          logger.exception("Error in event_generator: %s", e)
          # You might want to yield an error event here
          yield f'data: {{"error": "{str(e)}"}}\\n\\n'

      # Returns a streaming response with the proper media type for SSE
      return StreamingResponse(
          event_generator(),
          media_type="text/event-stream",
      )

    @core_router.get("/debug/trace/{event_id}")
    def get_trace_dict(event_id: str) -> Any:
      event_dict = trace_dict.get(event_id, None)
      if event_dict is None:
        raise HTTPException(status_code=404, detail="Trace not found")
      return event_dict

    @core_router.get("/debug/trace/session/{session_id}")
    def get_session_trace(session_id: str) -> Any:
      spans = memory_exporter.get_finished_spans(session_id)
      if not spans:
        return []
      return [
          {
              "name": s.name,
              "span_id": s.context.span_id,
              "trace_id": s.context.trace_id,
              "start_time": s.start_time,
              "end_time": s.end_time,
              "attributes": dict(s.attributes),
              "parent_span_id": s.parent.span_id if s.parent else None,
          }
          for s in spans
      ]
    
    app.include_router(core_router)
    
    # 设置平台路由器
    platform_router = setup_platform_router(self.platform_service)
    app.include_router(platform_router)
    
    # 设置应用路由器
    apps_router = setup_apps_router(
        agent_loader=self.agent_loader,
        session_service=self.session_service,
        memory_service=self.memory_service,
        artifact_service=self.artifact_service,
        eval_sets_manager=self.eval_sets_manager,
        eval_set_results_manager=self.eval_set_results_manager,
        current_app_name_ref=self.current_app_name_ref,
        runner_dict=self.runner_dict,
        runners_to_clean=self.runners_to_clean,
        agents_dir=self.agents_dir,
        get_runner_async_func=self.get_runner_async,
    )
    app.include_router(apps_router)

    if web_assets_dir:
      import mimetypes

      mimetypes.add_type("application/javascript", ".js", True)
      mimetypes.add_type("text/javascript", ".js", True)

      @app.get("/")
      async def redirect_root_to_dev_ui():
        return RedirectResponse("/dev-ui/")

      @app.get("/dev-ui")
      async def redirect_dev_ui_add_slash():
        return RedirectResponse("/dev-ui/")

      app.mount(
          "/dev-ui/",
          StaticFiles(directory=web_assets_dir, html=True, follow_symlink=True),
          name="static",
      )

    return app
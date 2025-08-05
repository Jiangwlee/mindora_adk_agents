"""
应用管理路由器
处理所有 /apps/* 端点
"""
import time
import logging
from typing import Any, Optional, List, Literal
from fastapi import APIRouter, Query, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from google.genai import types
from google.adk.events.event import Event
from google.adk.sessions.session import Session
from google.adk.evaluation.eval_case import EvalCase
from google.adk.evaluation.eval_sets_manager import EvalSetsManager
from google.adk.evaluation.eval_set_results_manager import EvalSetResultsManager
from google.adk.evaluation.eval_result import EvalSetResult
from google.adk.artifacts.base_artifact_service import BaseArtifactService
from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.memory.base_memory_service import BaseMemoryService
from google.adk.agents.live_request_queue import LiveRequest
from google.adk.cli.utils.shared_value import SharedValue
from google.adk.cli.utils.base_agent_loader import BaseAgentLoader
from google.adk.cli.utils.state import create_empty_state
from google.adk.cli.cli_eval import EVAL_SESSION_ID_PREFIX
from google.adk.errors.not_found_error import NotFoundError
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from pydantic import ValidationError
import asyncio
import traceback
import graphviz

from ...models import (
    AddSessionToEvalSetRequest,
    RunEvalRequest,
    RunEvalResult,
    GetEventGraphResult,
)
from google.adk.evaluation.local_eval_service import LocalEvalService
from google.adk.evaluation.metric_evaluator_registry import DEFAULT_METRIC_EVALUATOR_REGISTRY
from google.adk.cli import agent_graph
from google.adk.evaluation.constants import MISSING_EVAL_DEPENDENCIES_MESSAGE
from google.adk.cli.utils import evals, cleanup
from google.adk.cli.cli_eval import _collect_eval_results, _collect_inferences

logger = logging.getLogger("google_adk." + __name__)

apps_router = APIRouter(prefix="/apps", tags=["apps"])


def setup_apps_router(
    agent_loader: BaseAgentLoader,
    session_service: BaseSessionService,
    memory_service: BaseMemoryService,
    artifact_service: BaseArtifactService,
    eval_sets_manager: EvalSetsManager,
    eval_set_results_manager: EvalSetResultsManager,
    current_app_name_ref: SharedValue[str],
    runner_dict: dict,
    runners_to_clean: set[str],
    agents_dir: str,
    get_runner_async_func,
):
    """设置应用路由器，注入依赖服务"""

    @apps_router.get(
        "/{app_name}/users/{user_id}/sessions/{session_id}",
        response_model_exclude_none=True,
    )
    async def get_session(
        app_name: str, user_id: str, session_id: str
    ) -> Session:
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        current_app_name_ref.value = app_name
        return session

    @apps_router.get(
        "/{app_name}/users/{user_id}/sessions",
        response_model_exclude_none=True,
    )
    async def list_sessions(app_name: str, user_id: str) -> list[Session]:
        list_sessions_response = await session_service.list_sessions(
            app_name=app_name, user_id=user_id
        )
        return [
            session
            for session in list_sessions_response.sessions
            # Remove sessions that were generated as a part of Eval.
            if not session.id.startswith(EVAL_SESSION_ID_PREFIX)
        ]

    @apps_router.post(
        "/{app_name}/users/{user_id}/sessions/{session_id}",
        response_model_exclude_none=True,
    )
    async def create_session_with_id(
        app_name: str,
        user_id: str,
        session_id: str,
        state: Optional[dict[str, Any]] = None,
    ) -> Session:
        if (
            await session_service.get_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )
            is not None
        ):
            raise HTTPException(
                status_code=400, detail=f"Session already exists: {session_id}"
            )
        session = await session_service.create_session(
            app_name=app_name, user_id=user_id, state=state, session_id=session_id
        )
        logger.info("New session created: %s", session_id)
        return session

    @apps_router.post(
        "/{app_name}/users/{user_id}/sessions",
        response_model_exclude_none=True,
    )
    async def create_session(
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        events: Optional[list[Event]] = None,
    ) -> Session:
        session = await session_service.create_session(
            app_name=app_name, user_id=user_id, state=state
        )

        if events:
            for event in events:
                await session_service.append_event(session=session, event=event)

        logger.info("New session created")
        return session

    @apps_router.delete("/{app_name}/users/{user_id}/sessions/{session_id}")
    async def delete_session(app_name: str, user_id: str, session_id: str):
        await session_service.delete_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    @apps_router.get(
        "/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}",
        response_model_exclude_none=True,
    )
    async def load_artifact(
        app_name: str,
        user_id: str,
        session_id: str,
        artifact_name: str,
        version: Optional[int] = Query(None),
    ) -> Optional[types.Part]:
        artifact = await artifact_service.load_artifact(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=artifact_name,
            version=version,
        )
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return artifact

    @apps_router.get(
        "/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions/{version_id}",
        response_model_exclude_none=True,
    )
    async def load_artifact_version(
        app_name: str,
        user_id: str,
        session_id: str,
        artifact_name: str,
        version_id: int,
    ) -> Optional[types.Part]:
        artifact = await artifact_service.load_artifact(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=artifact_name,
            version=version_id,
        )
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return artifact

    @apps_router.get(
        "/{app_name}/users/{user_id}/sessions/{session_id}/artifacts",
        response_model_exclude_none=True,
    )
    async def list_artifact_names(
        app_name: str, user_id: str, session_id: str
    ) -> list[str]:
        return await artifact_service.list_artifact_keys(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

    @apps_router.get(
        "/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}/versions",
        response_model_exclude_none=True,
    )
    async def list_artifact_versions(
        app_name: str, user_id: str, session_id: str, artifact_name: str
    ) -> list[int]:
        return await artifact_service.list_versions(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=artifact_name,
        )

    @apps_router.delete(
        "/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}",
    )
    async def delete_artifact(
        app_name: str, user_id: str, session_id: str, artifact_name: str
    ):
        await artifact_service.delete_artifact(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=artifact_name,
        )

    @apps_router.post(
        "/{app_name}/eval_sets/{eval_set_id}",
        response_model_exclude_none=True,
    )
    def create_eval_set(
        app_name: str,
        eval_set_id: str,
    ):
        """创建评估集"""
        try:
            eval_sets_manager.create_eval_set(app_name, eval_set_id)
        except ValueError as ve:
            raise HTTPException(
                status_code=400,
                detail=str(ve),
            ) from ve

    @apps_router.get(
        "/{app_name}/eval_sets",
        response_model_exclude_none=True,
    )
    def list_eval_sets(app_name: str) -> list[str]:
        """列出应用的所有评估集"""
        try:
            return eval_sets_manager.list_eval_sets(app_name)
        except NotFoundError as e:
            logger.warning(e)
            return []

    @apps_router.post(
        "/{app_name}/eval_sets/{eval_set_id}/add_session",
        response_model_exclude_none=True,
    )
    async def add_session_to_eval_set(
        app_name: str, eval_set_id: str, req: AddSessionToEvalSetRequest
    ):
        # 获取会话
        session = await session_service.get_session(
            app_name=app_name, user_id=req.user_id, session_id=req.session_id
        )
        assert session, "Session not found."

        # 转换会话数据为评估调用
        invocations = evals.convert_session_to_eval_invocations(session)

        # 使用初始会话状态填充会话
        initial_session_state = create_empty_state(
            agent_loader.load_agent(app_name)
        )

        new_eval_case = EvalCase(
            eval_id=req.eval_id,
            conversation=invocations,
            session_input=evals.SessionInput(
                app_name=app_name,
                user_id=req.user_id,
                state=initial_session_state,
            ),
            creation_timestamp=time.time(),
        )

        try:
            eval_sets_manager.add_eval_case(
                app_name, eval_set_id, new_eval_case
            )
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve)) from ve

    @apps_router.get(
        "/{app_name}/eval_sets/{eval_set_id}/evals",
        response_model_exclude_none=True,
    )
    def list_evals_in_eval_set(
        app_name: str,
        eval_set_id: str,
    ) -> list[str]:
        """列出评估集中的所有评估"""
        eval_set_data = eval_sets_manager.get_eval_set(app_name, eval_set_id)

        if not eval_set_data:
            raise HTTPException(
                status_code=400, detail=f"Eval set `{eval_set_id}` not found."
            )

        return sorted([x.eval_id for x in eval_set_data.eval_cases])

    @apps_router.get(
        "/{app_name}/eval_sets/{eval_set_id}/evals/{eval_case_id}",
        response_model_exclude_none=True,
    )
    def get_eval(
        app_name: str, eval_set_id: str, eval_case_id: str
    ) -> EvalCase:
        """获取评估集中的评估用例"""
        eval_case_to_find = eval_sets_manager.get_eval_case(
            app_name, eval_set_id, eval_case_id
        )

        if eval_case_to_find:
            return eval_case_to_find

        raise HTTPException(
            status_code=404,
            detail=(
                f"Eval set `{eval_set_id}` or Eval `{eval_case_id}` not found."
            ),
        )

    @apps_router.put(
        "/{app_name}/eval_sets/{eval_set_id}/evals/{eval_case_id}",
        response_model_exclude_none=True,
    )
    def update_eval(
        app_name: str,
        eval_set_id: str,
        eval_case_id: str,
        updated_eval_case: EvalCase,
    ):
        if (
            updated_eval_case.eval_id
            and updated_eval_case.eval_id != eval_case_id
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Eval id in EvalCase should match the eval id in the API route."
                ),
            )

        # 覆盖值，要么覆盖相同的值，要么覆盖空字段
        updated_eval_case.eval_id = eval_case_id
        try:
            eval_sets_manager.update_eval_case(
                app_name, eval_set_id, updated_eval_case
            )
        except NotFoundError as nfe:
            raise HTTPException(status_code=404, detail=str(nfe)) from nfe

    @apps_router.delete("/{app_name}/eval_sets/{eval_set_id}/evals/{eval_case_id}")
    def delete_eval(app_name: str, eval_set_id: str, eval_case_id: str):
        try:
            eval_sets_manager.delete_eval_case(
                app_name, eval_set_id, eval_case_id
            )
        except NotFoundError as nfe:
            raise HTTPException(status_code=404, detail=str(nfe)) from nfe

    @apps_router.post(
        "/{app_name}/eval_sets/{eval_set_id}/run_eval",
        response_model_exclude_none=True,
    )
    async def run_eval(
        app_name: str, eval_set_id: str, req: RunEvalRequest
    ) -> list[RunEvalResult]:
        """运行评估"""
        try:
            eval_set = eval_sets_manager.get_eval_set(app_name, eval_set_id)

            if not eval_set:
                raise HTTPException(
                    status_code=400, detail=f"Eval set `{eval_set_id}` not found."
                )

            root_agent = agent_loader.load_agent(app_name)

            eval_case_results = []

            eval_service = LocalEvalService(
                root_agent=root_agent,
                eval_sets_manager=eval_sets_manager,
                eval_set_results_manager=eval_set_results_manager,
                session_service=session_service,
                artifact_service=artifact_service,
            )
            
            from google.adk.evaluation.base_eval_service import InferenceConfig, InferenceRequest
            
            inference_request = InferenceRequest(
                app_name=app_name,
                eval_set_id=eval_set.eval_set_id,
                eval_case_ids=req.eval_ids,
                inference_config=InferenceConfig(),
            )
            inference_results = await _collect_inferences(
                inference_requests=[inference_request], eval_service=eval_service
            )

            eval_case_results = await _collect_eval_results(
                inference_results=inference_results,
                eval_service=eval_service,
                eval_metrics=req.eval_metrics,
            )
        except ModuleNotFoundError as e:
            logger.exception("%s", e)
            raise HTTPException(
                status_code=400, detail=MISSING_EVAL_DEPENDENCIES_MESSAGE
            ) from e

        run_eval_results = []
        for eval_case_result in eval_case_results:
            run_eval_results.append(
                RunEvalResult(
                    eval_set_file=eval_case_result.eval_set_file,
                    eval_set_id=eval_set_id,
                    eval_id=eval_case_result.eval_id,
                    final_eval_status=eval_case_result.final_eval_status,
                    overall_eval_metric_results=eval_case_result.overall_eval_metric_results,
                    eval_metric_result_per_invocation=eval_case_result.eval_metric_result_per_invocation,
                    user_id=eval_case_result.user_id,
                    session_id=eval_case_result.session_id,
                )
            )

        return run_eval_results

    @apps_router.get(
        "/{app_name}/eval_results/{eval_result_id}",
        response_model_exclude_none=True,
    )
    def get_eval_result(
        app_name: str,
        eval_result_id: str,
    ) -> EvalSetResult:
        """获取给定评估ID的评估结果"""
        try:
            return eval_set_results_manager.get_eval_set_result(
                app_name, eval_result_id
            )
        except ValueError as ve:
            raise HTTPException(status_code=404, detail=str(ve)) from ve
        except ValidationError as ve:
            raise HTTPException(status_code=500, detail=str(ve)) from ve

    @apps_router.get(
        "/{app_name}/eval_results",
        response_model_exclude_none=True,
    )
    def list_eval_results(app_name: str) -> list[str]:
        """列出应用的所有评估结果"""
        return eval_set_results_manager.list_eval_set_results(app_name)

    @apps_router.get(
        "/{app_name}/eval_metrics",
        response_model_exclude_none=True,
    )
    def list_eval_metrics(app_name: str) -> list:
        """列出应用的所有评估指标"""
        try:
            # 目前忽略app_name，因为评估指标不与app_name绑定，但未来可能会绑定
            return DEFAULT_METRIC_EVALUATOR_REGISTRY.get_registered_metrics()
        except ModuleNotFoundError as e:
            logger.exception("%s\n%s", MISSING_EVAL_DEPENDENCIES, e)
            raise HTTPException(
                status_code=400, detail=MISSING_EVAL_DEPENDENCIES_MESSAGE
            ) from e

    @apps_router.get(
        "/{app_name}/users/{user_id}/sessions/{session_id}/events/{event_id}/graph",
        response_model_exclude_none=True,
    )
    async def get_event_graph(
        app_name: str, user_id: str, session_id: str, event_id: str
    ):
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        session_events = session.events if session else []
        event = next((x for x in session_events if x.id == event_id), None)
        if not event:
            return {}

        function_calls = event.get_function_calls()
        function_responses = event.get_function_responses()
        root_agent = agent_loader.load_agent(app_name)
        dot_graph = None
        if function_calls:
            function_call_highlights = []
            for function_call in function_calls:
                from_name = event.author
                to_name = function_call.name
                function_call_highlights.append((from_name, to_name))
                dot_graph = await agent_graph.get_agent_graph(
                    root_agent, function_call_highlights
                )
        elif function_responses:
            function_responses_highlights = []
            for function_response in function_responses:
                from_name = function_response.name
                to_name = event.author
                function_responses_highlights.append((from_name, to_name))
                dot_graph = await agent_graph.get_agent_graph(
                    root_agent, function_responses_highlights
                )
        else:
            from_name = event.author
            to_name = ""
            dot_graph = await agent_graph.get_agent_graph(
                root_agent, [(from_name, to_name)]
            )
        if dot_graph and isinstance(dot_graph, graphviz.Digraph):
            return GetEventGraphResult(dot_src=dot_graph.source)
        else:
            return {}

    @apps_router.websocket("/run_live")
    async def agent_live_run(
        websocket: WebSocket,
        app_name: str,
        user_id: str,
        session_id: str,
        modalities: List[Literal["TEXT", "AUDIO"]] = Query(
            default=["TEXT", "AUDIO"]
        ),  # 只允许 "TEXT" 或 "AUDIO"
    ) -> None:
        await websocket.accept()

        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        if not session:
            # 先接受连接，让客户端知道连接已建立，然后关闭
            await websocket.close(code=1002, reason="Session not found")
            return

        from google.adk.agents.live_request_queue import LiveRequestQueue

        live_request_queue = LiveRequestQueue()

        async def forward_events():
            runner = await get_runner_async_func(app_name)
            async for event in runner.run_live(
                session=session, live_request_queue=live_request_queue
            ):
                await websocket.send_text(
                    event.model_dump_json(exclude_none=True, by_alias=True)
                )

        async def process_messages():
            try:
                while True:
                    data = await websocket.receive_text()
                    # 验证并发送接收到的消息到实时队列
                    live_request_queue.send(LiveRequest.model_validate_json(data))
            except ValidationError as ve:
                logger.error("process_messages 中的验证错误: %s", ve)

        # 并发运行两个任务，如果一个失败则取消所有
        tasks = [
            asyncio.create_task(forward_events()),
            asyncio.create_task(process_messages()),
        ]
        done, pending = await asyncio.wait(
            tasks, return_when=asyncio.FIRST_EXCEPTION
        )
        try:
            # 这会重新抛出已完成任务中的任何异常
            for task in done:
                task.result()
        except WebSocketDisconnect:
            logger.info("客户端在 process_messages 期间断开连接。")
        except Exception as e:
            logger.exception("实时WebSocket通信期间出错: %s", e)
            traceback.print_exc()
            WEBSOCKET_INTERNAL_ERROR_CODE = 1011
            WEBSOCKET_MAX_BYTES_FOR_REASON = 123
            await websocket.close(
                code=WEBSOCKET_INTERNAL_ERROR_CODE,
                reason=str(e)[:WEBSOCKET_MAX_BYTES_FOR_REASON],
            )
        finally:
            for task in pending:
                task.cancel()
    
    return apps_router
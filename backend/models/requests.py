"""
Request models for API endpoints.
"""
from typing import Any, Optional
from google.genai import types
from pydantic import Field

from google.adk.cli.utils import common
from google.adk.evaluation.eval_metrics import EvalMetric


class AgentRunRequest(common.BaseModel):
    """Request model for running an agent."""
    app_name: str
    user_id: str
    session_id: str
    new_message: types.Content
    streaming: bool = False
    state_delta: Optional[dict[str, Any]] = None


class AddSessionToEvalSetRequest(common.BaseModel):
    """Request model for adding a session to an evaluation set."""
    eval_id: str
    session_id: str
    user_id: str


class RunEvalRequest(common.BaseModel):
    """Request model for running an evaluation."""
    eval_ids: list[str] = Field(
        default=[],
        description="List of evaluation IDs to run. If empty, all evals in the eval set are run."
    )
    eval_metrics: list[EvalMetric] = Field(
        default=[],
        description="List of evaluation metrics to use."
    )
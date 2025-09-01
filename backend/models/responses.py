"""
Response models for API endpoints.
"""
from typing import Any, Optional
from pydantic import Field

from google.adk.cli.utils import common
from google.adk.evaluation.eval_metrics import EvalMetric, EvalMetricResult, EvalMetricResultPerInvocation
from google.adk.cli.cli_eval import EvalStatus


class RunEvalResult(common.BaseModel):
    """Response model for evaluation results."""
    eval_set_file: str
    eval_set_id: str
    eval_id: str
    final_eval_status: EvalStatus
    eval_metric_results: list[tuple[EvalMetric, EvalMetricResult]] = Field(
        deprecated=True,
        default=[],
        description="This field is deprecated, use overall_eval_metric_results instead."
    )
    overall_eval_metric_results: list[EvalMetricResult]
    eval_metric_result_per_invocation: list[EvalMetricResultPerInvocation]
    user_id: str
    session_id: str


class GetEventGraphResult(common.BaseModel):
    """Response model for event graph data."""
    dot_src: str


class AppInfo(common.BaseModel):
    """Response model for application information."""
    name: str
    description: Optional[str] = None
    version: Optional[str] = None
    config: Optional[dict[str, Any]] = None


class HealthCheckResponse(common.BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    version: Optional[str] = None
    uptime: Optional[float] = None
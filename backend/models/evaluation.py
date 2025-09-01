"""
Evaluation-related models.
"""
from typing import Any, Optional
from google.adk.cli.utils import common
from google.adk.evaluation.eval_case import EvalCase
from google.adk.evaluation.eval_result import EvalSetResult
from google.adk.evaluation.eval_metrics import MetricInfo


class EvaluationCase(common.BaseModel):
    """Extended evaluation case model with additional metadata."""
    base_case: EvalCase
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: Optional[list[str]] = None
    priority: Optional[str] = None  # 'low', 'medium', 'high'


class EvaluationSet(common.BaseModel):
    """Evaluation set model with metadata."""
    name: str
    description: Optional[str] = None
    app_name: str
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: Optional[list[str]] = None
    is_active: bool = True


class EvaluationSummary(common.BaseModel):
    """Summary of evaluation results."""
    total_evals: int
    passed_evals: int
    failed_evals: int
    success_rate: float
    average_score: Optional[float] = None
    execution_time: Optional[float] = None


class EvaluationDetail(common.BaseModel):
    """Detailed evaluation result."""
    eval_id: str
    status: str
    score: Optional[float] = None
    metrics: dict[str, Any]
    execution_time: Optional[float] = None
    error_message: Optional[str] = None
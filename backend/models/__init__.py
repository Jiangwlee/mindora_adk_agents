"""
Models package for backend data structures.
"""

# Import all models for easy access
from .requests import (
    AgentRunRequest,
    AddSessionToEvalSetRequest,
    RunEvalRequest,
)

from .responses import (
    RunEvalResult,
    GetEventGraphResult,
    AppInfo,
    HealthCheckResponse,
)

from .evaluation import (
    EvaluationCase,
    EvaluationSet,
    EvaluationSummary,
    EvaluationDetail,
)

from .session import (
    SessionInfo,
    SessionCreateRequest,
    SessionUpdateRequest,
    SessionListResponse,
    SessionExportRequest,
    SessionImportRequest,
)

from .platform import (
    AppInfo,
    AppType,
    UserMode,
    SessionStatus,
    UiConfig,
    AppSessionInfo,
    AppLaunchRequest,
    AppLaunchResponse,
    AppListResponse,
    AppSessionUpdateRequest,
    AppSessionListResponse,
)

__all__ = [
    # Request models
    "AgentRunRequest",
    "AddSessionToEvalSetRequest", 
    "RunEvalRequest",
    
    # Response models
    "RunEvalResult",
    "GetEventGraphResult",
    "AppInfo",
    "HealthCheckResponse",
    
    # Evaluation models
    "EvaluationCase",
    "EvaluationSet",
    "EvaluationSummary",
    "EvaluationDetail",
    
    # Session models
    "SessionInfo",
    "SessionCreateRequest",
    "SessionUpdateRequest",
    "SessionListResponse",
    "SessionExportRequest",
    "SessionImportRequest",
    
    # Platform models
    "AppInfo",
    "AppType",
    "UserMode",
    "SessionStatus",
    "UiConfig",
    "AppSessionInfo",
    "AppLaunchRequest",
    "AppLaunchResponse",
    "AppListResponse",
    "AppSessionUpdateRequest",
    "AppSessionListResponse",
]
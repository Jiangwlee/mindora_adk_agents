"""
Session-related models.
"""
from typing import Any, Optional, List
from google.adk.cli.utils import common
from google.adk.sessions.session import Session


class SessionInfo(common.BaseModel):
    """Extended session information model."""
    base_session: Session
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    tags: Optional[list[str]] = None
    metadata: Optional[dict[str, Any]] = None
    is_active: bool = True


class SessionCreateRequest(common.BaseModel):
    """Request model for creating a session."""
    app_name: str
    user_id: str
    session_id: Optional[str] = None
    state: Optional[dict[str, Any]] = None
    events: Optional[list[Any]] = None
    metadata: Optional[dict[str, Any]] = None
    tags: Optional[list[str]] = None


class SessionUpdateRequest(common.BaseModel):
    """Request model for updating a session."""
    state: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None
    tags: Optional[list[str]] = None


class SessionListResponse(common.BaseModel):
    """Response model for listing sessions."""
    sessions: List[SessionInfo]
    total_count: int
    page: Optional[int] = None
    page_size: Optional[int] = None


class SessionExportRequest(common.BaseModel):
    """Request model for exporting sessions."""
    session_ids: List[str]
    format: str = "json"  # 'json', 'csv', 'yaml'
    include_events: bool = True
    include_artifacts: bool = False


class SessionImportRequest(common.BaseModel):
    """Request model for importing sessions."""
    sessions_data: Any  # JSON data containing sessions
    overwrite_existing: bool = False
    validate_only: bool = False
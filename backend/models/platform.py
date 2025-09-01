"""
Platform-related models for AI Agent App Platform.
"""
from typing import Any, Optional, List, Literal
from google.adk.cli.utils import common
from google.adk.sessions.session import Session
from enum import Enum
from pydantic import Field


class AppType(str, Enum):
    """Application type enumeration."""
    CHATBOT = "chatbot"
    CUSTOM = "custom"


class UserMode(str, Enum):
    """User mode enumeration for app sessions."""
    INDIVIDUAL = "individual"
    ANONYMOUS = "anonymous"
    SHARED = "shared"


class SessionStatus(str, Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"


class UiConfig(common.BaseModel):
    """UI configuration for applications."""
    theme: Literal["modern", "classic"] = "modern"
    layout: Literal["chat", "dashboard", "custom"] = "chat"
    features: List[str] = []
    colors: Optional[dict[str, str]] = None


class AppInfo(common.BaseModel):
    """Application information model."""
    name: str = Field(..., alias="name")
    description: str = Field(..., alias="description")
    app_type: AppType = Field(..., alias="appType")
    capabilities: List[str] = Field(default=[], alias="capabilities")
    ui_config: UiConfig = Field(..., alias="uiConfig")
    created_at: str = Field(..., alias="createdAt")
    version: str = Field(default="1.0.0", alias="version")
    author: Optional[str] = Field(default=None, alias="author")
    tags: List[str] = Field(default=[], alias="tags")
    
    class Config:
        populate_by_name = True


class AppSessionInfo(common.BaseModel):
    """App session information model."""
    session_id: str
    app_name: str
    user_id: str
    user_mode: UserMode
    created_at: str
    updated_at: str
    status: SessionStatus
    expires_at: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    is_persistent: bool = False
    
    class Config:
        populate_by_name = True


class AppLaunchRequest(common.BaseModel):
    """Request model for launching an application."""
    user_id: Optional[str] = None
    user_mode: UserMode = UserMode.INDIVIDUAL
    session_config: Optional[dict[str, Any]] = None
    metadata: Optional[dict[str, Any]] = None


class AppLaunchResponse(common.BaseModel):
    """Response model for application launch."""
    session_info: AppSessionInfo = Field(..., alias="sessionInfo")
    app_info: AppInfo = Field(..., alias="appInfo")
    websocket_url: Optional[str] = Field(default=None, alias="websocketUrl")
    sse_url: Optional[str] = Field(default=None, alias="sseUrl")
    
    class Config:
        populate_by_name = True


class AppListResponse(common.BaseModel):
    """Response model for listing applications."""
    apps: List[AppInfo] = Field(..., alias="apps")
    total_count: int = Field(..., alias="totalCount")
    categories: dict[str, int] = Field(default={}, alias="categories")
    
    class Config:
        populate_by_name = True


class AppSessionUpdateRequest(common.BaseModel):
    """Request model for updating app session."""
    status: Optional[SessionStatus] = None
    metadata: Optional[dict[str, Any]] = None
    expires_at: Optional[str] = None


class AppSessionListResponse(common.BaseModel):
    """Response model for listing app sessions."""
    sessions: List[AppSessionInfo]
    total_count: int
    active_count: int
    page: Optional[int] = None
    page_size: Optional[int] = None
    
    class Config:
        populate_by_name = True
"""
Platform service for managing AI Agent App Platform functionality.
"""
import asyncio
import logging
import time
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from ..models.platform import (
    AppInfo,
    AppSessionInfo,
    AppLaunchRequest,
    AppLaunchResponse,
    SessionStatus,
    UserMode,
    AppType,
    UiConfig,
    AppSessionUpdateRequest,
    AppSessionListResponse,
)
from ..models.session import SessionCreateRequest
from google.adk.sessions.session import Session
from google.adk.cli.utils.agent_loader import BaseAgentLoader
from google.adk.sessions.base_session_service import BaseSessionService

logger = logging.getLogger(__name__)


class PlatformService:
    """Service for managing platform-level application sessions."""

    def __init__(
        self,
        agent_loader: BaseAgentLoader,
        session_service: BaseSessionService,
        default_session_timeout: int = 3600,  # 1 hour
    ):
        self.agent_loader = agent_loader
        self.session_service = session_service
        self.default_session_timeout = default_session_timeout
        self._app_sessions: Dict[str, AppSessionInfo] = {}  # session_id -> AppSessionInfo
        self._app_cache: Optional[List[AppInfo]] = None
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutes

    async def get_platform_apps(self) -> List[AppInfo]:
        """Get all available applications with platform information."""
        current_time = time.time()
        
        # Return cached data if still valid
        if (self._app_cache is not None and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._app_cache
        
        # Get agent names from agent loader
        agent_names = self.agent_loader.list_agents()
        apps = []
        
        for agent_name in agent_names:
            try:
                # Load agent to get its configuration
                agent = self.agent_loader.load_agent(agent_name)
                
                # Extract platform information from agent configuration
                # This assumes agents have been extended with platform configuration
                app_info = self._extract_app_info_from_agent(agent, agent_name)
                apps.append(app_info)
            except Exception as e:
                logger.warning(f"Failed to load agent {agent_name}: {e}")
                # Create minimal app info for compatibility
                ui_config = UiConfig(
                    theme="modern",
                    layout="chat",
                    features=[]
                )
                apps.append(AppInfo(
                    name=agent_name,
                    description=f"Agent: {agent_name}",
                    app_type=AppType.CHATBOT,
                    capabilities=[],
                    ui_config=ui_config,
                    created_at="2025-01-01T00:00:00Z",
                ))
        
        # Cache the results
        self._app_cache = apps
        self._cache_timestamp = current_time
        
        return apps

    def _extract_app_info_from_agent(self, agent, agent_name: str) -> AppInfo:
        """Extract AppInfo from agent configuration."""
        # Try to get platform configuration from agent attributes
        platform_config = getattr(agent, 'platform_config', None)
        
        if platform_config:
            ui_config_dict = platform_config.get('ui_config', {
                "theme": "modern",
                "layout": "chat", 
                "features": []
            })
            ui_config = UiConfig(**ui_config_dict)
            
            return AppInfo(
                name=agent_name,
                description=platform_config.get('description', f"Agent: {agent_name}"),
                app_type=AppType(platform_config.get('app_type', 'chatbot')),
                capabilities=platform_config.get('capabilities', []),
                ui_config=ui_config,
                created_at=platform_config.get('created_at', "2025-01-01T00:00:00Z"),
                version=platform_config.get('version', '1.0.0'),
                author=platform_config.get('author'),
                tags=platform_config.get('tags', []),
            )
        else:
            # Default configuration for agents without platform config
            ui_config = UiConfig(
                theme="modern",
                layout="chat",
                features=[]
            )
            return AppInfo(
                name=agent_name,
                description=f"Agent: {agent_name}",
                app_type=AppType.CHATBOT,
                capabilities=[],
                ui_config=ui_config,
                created_at="2025-01-01T00:00:00Z",
            )

    async def get_app_by_name(self, name: str) -> Optional[AppInfo]:
        """Get application information by name."""
        apps = await self.get_platform_apps()
        for app in apps:
            if app.name == name:
                return app
        return None

    async def launch_app_session(
        self, 
        app_name: str, 
        launch_request: AppLaunchRequest
    ) -> AppLaunchResponse:
        """Launch an application session."""
        # Verify app exists
        app_info = await self.get_app_by_name(app_name)
        if not app_info:
            raise ValueError(f"Application '{app_name}' not found")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Determine user ID based on user mode
        user_id = self._resolve_user_id(launch_request.user_mode, launch_request.user_id, app_name)
        
        # Create session timeout
        timeout = launch_request.session_config.get('timeout', self.default_session_timeout) if launch_request.session_config else self.default_session_timeout
        expires_at = datetime.now() + timedelta(seconds=timeout)
        
        # Create underlying ADK session
        adk_session = await self._create_adk_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            launch_request=launch_request
        )
        
        # Create app session info
        app_session = AppSessionInfo(
            session_id=session_id,
            app_name=app_name,
            user_id=user_id,
            user_mode=launch_request.user_mode,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            status=SessionStatus.ACTIVE,
            expires_at=expires_at.isoformat(),
            metadata=launch_request.metadata or {},
            is_persistent=launch_request.session_config.get('persistent', False) if launch_request.session_config else False
        )
        
        # Store app session
        self._app_sessions[session_id] = app_session
        
        logger.info(f"Launched app session: {session_id} for app: {app_name}, user: {user_id}")
        
        # Return launch response
        return AppLaunchResponse(
            session_info=app_session,
            app_info=app_info,
            websocket_url=f"ws://localhost:8000/run_live?app_name={app_name}&user_id={user_id}&session_id={session_id}",
            sse_url=f"http://localhost:8000/run_sse"
        )

    def _resolve_user_id(self, user_mode: UserMode, provided_user_id: Optional[str], app_name: str) -> str:
        """Resolve user ID based on user mode."""
        if user_mode == UserMode.ANONYMOUS:
            return "anonymous_user"
        elif user_mode == UserMode.SHARED:
            return f"shared_{app_name}"
        elif user_mode == UserMode.INDIVIDUAL:
            return provided_user_id or "default_user"
        else:
            return "default_user"

    async def _create_adk_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        launch_request: AppLaunchRequest
    ) -> Session:
        """Create underlying ADK session."""
        # Check if session already exists
        existing_session = await self.session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        if existing_session:
            return existing_session
        
        # Create new session
        session = await self.session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=launch_request.session_config.get('state') if launch_request.session_config else None
        )
        
        return session

    async def get_app_session(self, session_id: str) -> Optional[AppSessionInfo]:
        """Get app session information."""
        app_session = self._app_sessions.get(session_id)
        if not app_session:
            return None
        
        # Check if session is expired
        if app_session.expires_at:
            expires_at = datetime.fromisoformat(app_session.expires_at)
            if datetime.now() > expires_at:
                app_session.status = SessionStatus.EXPIRED
                self._app_sessions[session_id] = app_session
        
        return app_session

    async def update_app_session(
        self, 
        session_id: str, 
        update_request: AppSessionUpdateRequest
    ) -> Optional[AppSessionInfo]:
        """Update app session information."""
        app_session = await self.get_app_session(session_id)
        if not app_session:
            return None
        
        # Update fields
        if update_request.status:
            app_session.status = update_request.status
        if update_request.metadata:
            app_session.metadata.update(update_request.metadata)
        if update_request.expires_at:
            app_session.expires_at = update_request.expires_at
        
        app_session.updated_at = datetime.now().isoformat()
        self._app_sessions[session_id] = app_session
        
        return app_session

    async def list_app_sessions(
        self,
        app_name: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[SessionStatus] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None
    ) -> AppSessionListResponse:
        """List app sessions with filtering."""
        sessions = list(self._app_sessions.values())
        
        # Apply filters
        if app_name:
            sessions = [s for s in sessions if s.app_name == app_name]
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        # Count active sessions
        active_count = len([s for s in sessions if s.status == SessionStatus.ACTIVE])
        
        # Apply pagination
        total_count = len(sessions)
        if page is not None and page_size is not None:
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            sessions = sessions[start_idx:end_idx]
        
        return AppSessionListResponse(
            sessions=sessions,
            total_count=total_count,
            active_count=active_count,
            page=page,
            page_size=page_size
        )

    async def delete_app_session(self, session_id: str) -> bool:
        """Delete app session."""
        if session_id not in self._app_sessions:
            return False
        
        app_session = self._app_sessions[session_id]
        
        # Delete underlying ADK session
        try:
            await self.session_service.delete_session(
                app_name=app_session.app_name,
                user_id=app_session.user_id,
                session_id=session_id
            )
        except Exception as e:
            logger.warning(f"Failed to delete ADK session {session_id}: {e}")
        
        # Remove app session
        del self._app_sessions[session_id]
        
        logger.info(f"Deleted app session: {session_id}")
        return True

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, app_session in self._app_sessions.items():
            if app_session.expires_at:
                expires_at = datetime.fromisoformat(app_session.expires_at)
                if current_time > expires_at:
                    expired_sessions.append(session_id)
        
        # Delete expired sessions
        deleted_count = 0
        for session_id in expired_sessions:
            if await self.delete_app_session(session_id):
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} expired sessions")
        return deleted_count
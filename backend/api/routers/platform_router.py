"""
平台管理路由器
处理所有 /platform/* 端点
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from ...models.platform import (
    AppLaunchRequest,
    AppLaunchResponse,
    AppSessionUpdateRequest,
    AppSessionListResponse,
    AppListResponse,
    SessionStatus,
)
from ...services.platform_service import PlatformService

platform_router = APIRouter(prefix="/platform", tags=["platform"])


def setup_platform_router(platform_service: PlatformService):
    """设置平台路由器，注入依赖服务"""
    
    @platform_router.get("/apps", response_model=AppListResponse)
    async def get_platform_apps() -> AppListResponse:
        """获取所有可用的应用程序"""
        apps = await platform_service.get_platform_apps()
        
        # 按应用类型分组
        categories = {}
        for app in apps:
            app_type = app.app_type.value
            categories[app_type] = categories.get(app_type, 0) + 1
        
        return AppListResponse(
            apps=apps,
            total_count=len(apps),
            categories=categories
        )

    @platform_router.get("/apps/{name}", response_model_exclude_none=True)
    async def get_platform_app(name: str):
        """根据名称获取应用信息"""
        app = await platform_service.get_app_by_name(name)
        if not app:
            raise HTTPException(status_code=404, detail="Application not found")
        return app

    @platform_router.post("/apps/{name}/launch", response_model=AppLaunchResponse)
    async def launch_app(name: str, launch_request: AppLaunchRequest):
        """启动应用会话"""
        try:
            response = await platform_service.launch_app_session(name, launch_request)
            return response
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to launch application: {str(e)}")

    @platform_router.get("/sessions/{session_id}", response_model_exclude_none=True)
    async def get_platform_session(session_id: str):
        """获取平台会话信息"""
        session = await platform_service.get_app_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    @platform_router.put("/sessions/{session_id}", response_model_exclude_none=True)
    async def update_platform_session(session_id: str, update_request: AppSessionUpdateRequest):
        """更新平台会话信息"""
        session = await platform_service.update_app_session(session_id, update_request)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    @platform_router.get("/sessions", response_model=AppSessionListResponse)
    async def list_platform_sessions(
        app_name: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        page: Optional[int] = Query(None),
        page_size: Optional[int] = Query(None)
    ):
        """列出平台会话，支持过滤"""
        status_enum = SessionStatus(status) if status else None
        return await platform_service.list_app_sessions(
            app_name=app_name,
            user_id=user_id,
            status=status_enum,
            page=page,
            page_size=page_size
        )

    @platform_router.delete("/sessions/{session_id}")
    async def delete_platform_session(session_id: str):
        """删除平台会话"""
        success = await platform_service.delete_app_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}

    @platform_router.post("/cleanup")
    async def cleanup_platform_sessions():
        """清理过期的平台会话"""
        deleted_count = await platform_service.cleanup_expired_sessions()
        return {"message": f"Cleaned up {deleted_count} expired sessions"}
    
    return platform_router
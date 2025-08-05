"""
路由器模块
"""
from .platform_router import platform_router, setup_platform_router
from .apps_router import apps_router, setup_apps_router
from .core_router import core_router, setup_core_router

__all__ = [
    "platform_router", "setup_platform_router",
    "apps_router", "setup_apps_router", 
    "core_router", "setup_core_router"
]
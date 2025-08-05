"""
核心路由器
处理核心端点：健康检查、列表应用、运行端点等
"""
import time
import logging
from typing import Any, Optional
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from google.adk.events.event import Event
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner

from ...models import (
    AgentRunRequest,
    HealthCheckResponse,
)

logger = logging.getLogger("google_adk." + __name__)

core_router = APIRouter(tags=["core"])


def setup_core_router(get_runner_async_func):
    """设置核心路由器，注入依赖服务"""

    @core_router.get("/health", response_model_exclude_none=True)
    def health_check() -> HealthCheckResponse:
        """健康检查端点"""
        return HealthCheckResponse(
            status="healthy",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            version="1.0.0",
            uptime=time.time()
        )

    # 注意：/list-apps, /run, /run_sse, /debug/trace/* 端点在 AdkWebServer 类中实现
# 因为它们需要访问实例变量
    
    return core_router
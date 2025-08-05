# 添加新端点和数据结构的示例

## 概述

这个文档展示了如何在 Mindora ADK Agents 项目中添加新的 API 端点和相应的数据结构。

## 后端实现

### 1. 定义数据模型

在 `backend/models/` 目录下的相应文件中定义数据模型：

```python
# backend/models/responses.py
class HealthCheckResponse(common.BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    version: Optional[str] = None
    uptime: Optional[float] = None
```

### 2. 添加 API 端点

在 `backend/api/adk_web_server.py` 中添加新的端点：

```python
# 导入新的模型
from ..models import HealthCheckResponse

# 在 AdkWebServer 类中添加端点
@app.get("/health", response_model_exclude_none=True)
def health_check() -> HealthCheckResponse:
    """Health check endpoint."""
    import time
    return HealthCheckResponse(
        status="healthy",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        version="1.0.0",
        uptime=time.time()
    )
```

### 3. 更新模型导入

确保在 `backend/models/__init__.py` 中导出新的模型：

```python
from .responses import HealthCheckResponse

__all__ = [
    # ... 其他模型
    "HealthCheckResponse",
]
```

## 前端实现

### 1. 定义 TypeScript 接口

在 `frontend/src/app/core/models/` 目录下创建对应的接口：

```typescript
// frontend/src/app/core/models/ApiResponse.ts
export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  version?: string;
  uptime?: number;
}
```

### 2. 创建服务方法

在相应的服务文件中添加 API 调用方法：

```typescript
// 例如在 agent.service.ts 中添加
getHealthCheck(): Observable<HealthCheckResponse> {
  return this.http.get<HealthCheckResponse>(`${this.backendUrl}/health`);
}
```

## 数据结构位置总结

### 后端数据结构
- **位置**: `backend/models/` 目录
- **组织方式**: 
  - `requests.py` - 请求模型
  - `responses.py` - 响应模型
  - `evaluation.py` - 评估相关模型
  - `session.py` - 会话相关模型
- **基类**: 使用 `common.BaseModel`
- **优点**: 类型安全、数据验证、IDE 支持

### 前端数据结构
- **位置**: `frontend/src/app/core/models/` 目录
- **组织方式**: 按功能模块创建文件
- **类型**: TypeScript 接口
- **优点**: 类型安全、代码提示、前后端一致性

## 最佳实践

1. **保持一致性**: 确保前后端数据结构保持一致
2. **文档化**: 为所有数据模型添加清晰的文档字符串
3. **验证**: 使用 Pydantic 的验证功能确保数据完整性
4. **版本控制**: 考虑为 API 添加版本控制
5. **测试**: 为新的端点和数据模型添加相应的测试

## 示例端点测试

使用 curl 测试新的健康检查端点：

```bash
# 启动服务器
python run_server.py

# 测试健康检查端点
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "timestamp": "2025-08-05T10:30:00Z",
  "version": "1.0.0",
  "uptime": 1234567890.123
}
```
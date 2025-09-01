# 调试指南

## 代码分层调试原则

**重要**: 项目包含两类代码，调试时需要区分对待：

### 1. Google ADK 官方代码
- **位置**: `backend/api/adk_web_server.py`、`frontend/src/app/core/services/agent.service.ts` 等
- **原则**: **假设官方代码是正确的**，不要轻易怀疑或修改
- **验证方法**: 对比官方 `/adk-debug` 页面的表现，如果官方页面正常，说明官方代码无问题

### 2. 项目自定义代码
- **位置**: `frontend/src/app/components/simplified-chat/` 等自实现组件
- **原则**: **优先检查和调试自定义代码**
- **调试重点**: 消息处理逻辑、数据转换、UI 渲染等

## 具体调试步骤

### 1. 问题复现
先在官方 `/adk-debug` 页面测试相同功能，确认是否为官方代码问题

### 2. 数据流追踪
- 添加 `console.log` 追踪数据流向
- 检查 SSE 原始数据格式和内容
- 确认前端数据处理逻辑

### 3. 分层排查
- 后端 API → 前端 Service → 前端 Component → UI 渲染
- 逐层验证数据的正确性和完整性

## 常见问题排查

### SSE 流式消息重复显示
- **现象**: 智能体回答显示多次
- **原因**: 未正确处理 ADK SSE 的 `partial` 字段
- **解决**: 区分 partial（部分）和完整消息，只显示最终完整消息
- **关键代码**: `SimplifiedChatComponent.processPart()` 方法

### SSE 消息显示问题
- 检查 `backend/api/adk_web_server.py` 中的换行符转义
- 确保 SSE 事件格式正确：`data: {json}\n\n`
- 参考 `docs/troubleshooting-sse-message-display.md`

### WebSocket 连接问题
- 确认后端服务器运行在正确端口 (8000)
- 检查 CORS 设置允许前端域名 (localhost:4200)
- 验证 WebSocket 升级请求头

### 智能体执行错误
- 检查智能体配置文件格式
- 验证 Google ADK 依赖安装
- 查看服务器日志获取详细错误信息

## 调试工具

### 快速测试脚本
```bash
# 快速API测试
uv run python tests/quick_test.py

# 平台API测试
uv run python tests/test_platform_apis.py

# 服务器集成测试
uv run python tests/test_server.py
```

### 前端调试
- 使用浏览器开发者工具
- 检查 Network 标签页的 SSE 请求
- 查看 Console 中的错误日志

## 专项调试文档

- **SSE消息显示问题**: `docs/troubleshooting-sse-message-display.md`
- **前端开发指南**: `docs/web-feature-development-guide.md`
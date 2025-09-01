# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 指导原则
- 始终使用简体中文回应
- 始终由 Claude Code 来编写测试用例，由用户来执行测试
- 始终由用户来启动服务，如果需要启动服务，请求用户来帮助

## 项目概述

**Mindora ADK Agents** - 基于 Google ADK 构建的企业级智能体开发平台

### 技术栈
- **后端**: Python 3.12 + FastAPI + Google ADK 1.9.0+
- **前端**: Angular 19 + Angular Material + TypeScript 5.7+
- **通信**: WebSocket + SSE 流式响应

### 项目状态
- **平台API**: 已完成 (18% 整体进度)
- **前端路由重构**: 进行中
- **Chatbot应用**: 计划中

### 路由结构
- `/` - 平台主页 (开发中)
- `/adk-debug` - ADK调试工具 (当前可用)
- `/app/chatbot/:name` - Chatbot应用 (计划中)
- `/app/custom/:name` - Custom应用 (计划中)

## 核心开发命令

### 启动服务
```bash
just run          # 完整开发环境
just run-backend   # 仅后端 (localhost:8000)
just run-web       # 仅前端 (localhost:4200)
```

### 测试验证
```bash
just test                              # 运行所有测试
uv run python tests/quick_test.py      # 快速功能验证
uv run python tests/test_platform_apis.py  # 平台API测试
```

## 前端开发原则

### 核心原则
1. **基于 Google ADK Web**: 本项目是 [adk-web](https://github.com/google/adk-web/) 的二次开发
2. **优先复用**: **必须优先使用** `AgentService`、`SessionService` 等现有服务
3. **保持兼容**: **不得随意修改** Google ADK Web 核心文件

### 调试策略
**重要区分**: 
- **ADK官方代码** (`adk_web_server.py`, `agent.service.ts`): 假设正确，先在 `/adk-debug` 验证
- **自定义代码** (`simplified-chat` 等): 优先检查和调试

### 常见问题
- **SSE消息重复**: 检查 `partial` 字段处理
- **SSE格式错误**: 确保使用 `\n\n` 而非 `\\n\\n`
- 详见 `docs/troubleshooting-sse-message-display.md`

## 智能体配置

支持两种应用类型：
- **chatbot**: 对话式应用 (assistant, adk_demo)
- **custom**: 自定义应用 (data_analyst)

配置示例：
```json
{
  "name": "智能体名称",
  "app_type": "chatbot",
  "ui_config": {"theme": "modern", "layout": "chat"},
  "model": "gemini-2.0-flash-exp"
}
```

---

## 详细文档索引

### 开发指南
- [项目结构详解](docs/project-structure.md)
- [开发命令参考](docs/development-commands.md) 
- [前端开发指南](docs/web-feature-development-guide.md)

### API和配置
- [API端点参考](docs/api-reference.md)
- [智能体配置](docs/agent-configuration.md)

### 调试和问题解决
- [完整调试指南](docs/debugging-guide.md)
- [SSE消息显示问题](docs/troubleshooting-sse-message-display.md)

### 项目规划
- [任务清单和进度](docs/ai-agent-app-platform-tasks.md)

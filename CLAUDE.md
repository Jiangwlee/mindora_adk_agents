# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 指导原则
- 始终使用简体中文回应

## 项目概述

Mindora ADK Agents 是一个基于 Google ADK Agents 构建的智能体平台。项目使用 Angular 19 + FastAPI + Google ADK 技术栈，为用户提供多应用 web 界面来与不同的智能体应用进行交互。

## 项目结构

```
mindora_adk_agents/
├── frontend/                    # Angular 19 web 界面
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/     # UI 组件
│   │   │   │   ├── chat/       # 聊天界面
│   │   │   │   ├── event-tab/  # 事件流标签
│   │   │   │   ├── trace-tab/  # 执行追踪标签
│   │   │   │   ├── eval-tab/   # 评估测试标签
│   │   │   │   ├── session-tab/# 会话管理标签
│   │   │   │   └── state-tab/  # 状态查看标签
│   │   │   ├── core/           # 核心服务
│   │   │   │   ├── services/   # API 服务层
│   │   │   │   └── models/     # 数据模型
│   │   │   └── app.module.ts   # 应用模块
│   │   └── assets/
│   └── package.json
├── backend/
│   ├── api/
│   │   └── adk_web_server.py   # ADK web 服务器实现
│   ├── fast_api.py            # FastAPI 应用设置
│   ├── agents/                # 智能体实现
│   └── run.py                 # 服务器启动脚本
├── docs/
│   └── design.md              # 设计文档
├── .venv/                     # Python 虚拟环境
├── run_server.py              # 主服务器入口点
├── pyproject.toml             # Python 项目配置
├── .python-version            # Python 版本规范
├── justfile                   # 命令快捷方式
└── README.md                  # 项目文档
```

## 技术栈

- **前端**: Angular 19 with Material Design (完整实现)
- **后端**: FastAPI 使用 Google ADK 内置的 FastAPI 服务器
- **智能体**: Google ADK Agents (参考: https://github.com/google/adk-samples)
- **Python**: 需要 Python 3.12+
- **虚拟环境**: 使用 .venv/ 目录

## 依赖管理

- **Python**: 使用 `pyproject.toml` 配置 `google-adk>=1.9.0` 依赖
- **包管理器**: 使用 `uv` 进行依赖管理和虚拟环境
- **JavaScript**: 使用 `npm` 进行依赖管理 (Angular 19 前端)
- **命令**: 使用 `justfile` 作为快捷命令
- **环境**: 使用 `.venv/` 虚拟环境配合 Python 3.12+

## 开发命令

### 后端命令
使用 `just` 命令运行常见任务:

- `just install` - 安装依赖
- `just run` - 运行 FastAPI 服务器
- `just run-web` - 运行带 web 界面的 FastAPI 服务器
- `just test` - 测试导入
- `just deps` - 检查依赖
- `just dev` - 开发服务器（热重载）

### 前端命令
在 `frontend/` 目录下运行:

- `npm install` - 安装前端依赖
- `npm run serve -- --backend=http://localhost:8000` - 启动开发服务器
- `npm run build` - 构建生产版本
- `npm run test` - 运行测试
- `npm run watch` - 监听模式构建

## 项目设置

### 后端设置
1. 确保 `uv` 已安装: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. 安装依赖: `just install` 或 `uv sync`
3. 运行服务器: `python run_server.py` 或 `just run`
4. 测试导入: `just test`

### 前端设置
1. 进入前端目录: `cd frontend`
2. 安装依赖: `npm install`
3. 启动开发服务器: `npm run serve -- --backend=http://localhost:8000`
4. 构建生产版本: `npm run build`

## API 测试

后端服务器提供了全面的 API 端点用于智能体交互:

### 主要端点
- `GET /list-apps` - 列出可用的智能体应用
- `POST /run` - 运行智能体（同步）
- `POST /run_sse` - 运行智能体（SSE 流式）
- `GET /docs` - 交互式 API 文档

### 会话管理
- `POST /apps/{app_name}/users/{user_id}/sessions` - 创建会话
- `GET /apps/{app_name}/users/{user_id}/sessions` - 列出会话
- `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}` - 获取会话详情

### 制品服务
- `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts` - 列出制品
- `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}/artifacts/{artifact_name}` - 获取制品

### 调试和监控
- `GET /debug/trace/session/{session_id}` - 获取会话追踪数据
- `GET /debug/trace/{event_id}` - 获取特定事件追踪

### 测试示例
```bash
# 启动服务器
python run_server.py

# 测试端点
curl http://localhost:8000/list-apps
curl -X POST http://localhost:8000/apps/adk_demo/users/test_user/sessions
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d '{"appName":"adk_demo","userId":"test_user","sessionId":"SESSION_ID","newMessage":{"role":"user","parts":[{"text":"Hello"}]}}'
```

## 关键实现细节

### FastAPI 集成
后端包含了完整的 FastAPI 实现，使用 Google ADK 内置的 FastAPI 服务器:

- **`backend/fast_api.py`**: 包含 `get_fast_api_app()` 函数，创建带有 ADK 集成的 FastAPI 应用
- **`backend/api/adk_web_server.py`**: 包含 `AdkWebServer` 类，处理智能体执行、会话管理和 API 端点

### 核心功能实现
- **智能体管理**: 列出、加载和运行 agents 目录中的智能体
- **会话管理**: 创建、管理和删除用户会话
- **制品服务**: 存储和检索智能体生成的制品
- **内存服务**: 内存和 Vertex AI 内存集成
- **评估系统**: 创建和运行智能体评估集
- **WebSocket 支持**: 通过 WebSocket 进行实时智能体通信
- **SSE 流式**: 服务器发送事件用于流式智能体响应
- **A2A 支持**: 智能体间通信协议支持
- **CORS 支持**: 可配置的 CORS 中间件
- **OpenTelemetry**: 分布式追踪支持

### 智能体开发
智能体实现应参考以下示例:
- https://github.com/google/adk-samples

## 前端架构详情

### 核心功能特性
- **智能体聊天界面**: 实时对话，支持多模态输入（文本、音频、视频、文件）
- **实时通信**: WebSocket 双向流式通信，支持音频实时处理
- **SSE 流式响应**: 服务端推送事件流，实现打字机效果
- **会话管理**: 完整的会话创建、管理、导入导出功能
- **调试追踪**: 事件流可视化、执行追踪图、LLM 请求/响应查看
- **评估系统**: 智能体评估测试套件，支持测试用例管理
- **制品管理**: 智能体生成的文件和资源管理
- **OAuth 认证**: 支持第三方服务认证流程

### 技术实现
- **Angular 19**: 现代前端框架，支持最新的 TypeScript 特性
- **Material Design**: Google 设计规范，提供一致的用户体验
- **RxJS**: 响应式编程，处理复杂的异步数据流
- **WebSocket**: 实时双向通信，支持音频流处理
- **SSE**: 服务器推送事件，实现流式响应
- **Viz.js**: 图形可视化，用于执行追踪图展示

### 主要组件结构
- **ChatComponent**: 主聊天界面，处理用户交互和消息显示
- **EventTabComponent**: 事件流标签，实时显示智能体执行事件
- **TraceTabComponent**: 追踪标签，展示执行路径和调试信息
- **EvalTabComponent**: 评估标签，提供智能体测试和评估功能
- **SessionTabComponent**: 会话管理标签，处理会话生命周期
- **StateTabComponent**: 状态查看标签，显示智能体内部状态

### 服务层架构
- **AgentService**: 智能体执行服务，处理 SSE 流式响应
- **WebSocketService**: WebSocket 服务，处理实时音频和消息通信
- **SessionService**: 会话管理服务，处理会话状态和持久化
- **TraceService**: 追踪服务，管理执行追踪数据
- **EventService**: 事件服务，处理事件流和调试信息
- **ArtifactService**: 制品服务，管理智能体生成的文件
- **EvalService**: 评估服务，处理智能体评估和测试

## 开发说明

- 项目具有完整的后端实现和功能丰富的前端界面
- 前端使用 Angular 19 框架，实现了完整的智能体开发工具链
- 后端实现了完整的 ADK Web 服务器 API，包括会话管理、制品处理和评估功能
- 项目使用中文 README，但代码和文档应使用英文
- 前端支持实时音频处理、文件上传、OAuth 认证等高级功能
- 提供完整的调试、追踪和评估工具链

## 服务器状态

后端服务器完全功能且已测试:
- ✅ 所有核心端点正常工作
- ✅ 智能体执行和会话管理正常运行
- ✅ SSE 流式和调试追踪功能正常
- ✅ 可用智能体: `adk_demo`, `assistant`
- ✅ 默认服务器运行在 `http://localhost:8000`
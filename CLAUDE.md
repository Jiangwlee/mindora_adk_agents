# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 指导原则
- 始终使用简体中文回应
- 始终由 Claude Code 来编写测试用例，由用户来执行测试
- 始终由用户来启动服务，如果需要启动服务，请求用户来帮助

## 内存记录
- 如果需要启动服务，或者进行测试，请直接要求我来执行。

## 项目概述

Mindora ADK Agents 是一个基于 Google ADK (Agent Development Kit) 构建的企业级智能体开发平台。项目采用现代化的技术栈 Angular 19 + FastAPI + Google ADK 1.9.0+，为开发者提供了完整的智能体开发、测试、部署和管理解决方案。

### 核心特性
- **全栈开发环境**: 集成前端 UI + 后端 API + 智能体引擎
- **实时交互**: 支持 WebSocket + SSE 流式响应 + 音频实时处理
- **开发工具链**: 调试追踪、性能监控、评估测试、会话管理
- **企业级功能**: 多用户支持、权限管理、分布式追踪、云集成
- **扩展性**: A2A 协议、制品管理、评估系统、热重载支持

### 技术架构

#### 后端技术栈
- **Python 3.12+**: 使用 uv 包管理器
- **FastAPI**: Web 框架和 API 服务器
- **Google ADK 1.9.0+**: 智能体开发核心引擎
- **A2A SDK 0.3.0+**: Agent-to-Agent 通信协议
- **Uvicorn**: ASGI 服务器
- **WebSocket + SSE**: 实时通信支持

#### 前端技术栈
- **Angular 19**: 现代化 SPA 框架
- **Angular Material 19**: UI 组件库
- **TypeScript 5.7+**: 类型安全的 JavaScript
- **RxJS**: 响应式编程
- **SCSS**: 样式预处理器
- **专业组件**: JSON 编辑器、Markdown 渲染、图形可视化

#### 智能体系统
- **多智能体支持**: 内置助手、数据分析师、ADK 演示智能体
- **配置驱动**: JSON 配置文件管理智能体行为
- **评估系统**: 完整的智能体测试和评估框架
- **会话管理**: 持久化智能体交互历史

## 开发指南

### 项目结构
```
mindora_adk_agents/
├── backend/                 # 后端服务
│   ├── agents/             # 智能体定义
│   │   ├── assistant/      # 助手智能体
│   │   ├── data_analyst/   # 数据分析师智能体
│   │   └── adk_demo/       # ADK 演示智能体
│   ├── api/                # API 路由和服务器
│   ├── models/             # 数据模型定义
│   └── services/           # 业务服务层
├── frontend/               # Angular 前端应用
│   ├── src/app/            # Angular 应用源码
│   │   ├── components/     # UI 组件
│   │   ├── core/           # 核心服务和模型
│   │   └── directives/     # 自定义指令
│   └── src/assets/         # 静态资源
├── docs/                   # 项目文档
├── tests/                  # 测试用例
└── justfile               # 开发任务定义
```

### 开发命令

#### 环境安装
```bash
# 安装 Python 依赖
just install
# 或
uv sync

# 安装前端依赖
cd frontend && npm install
```

#### 运行服务
```bash
# 完整开发环境 (后端 + 前端)
just run

# 仅运行后端服务
just run-backend

# 仅运行前端服务
just run-web

# 开发模式 (带热重载)
just dev
```

#### 测试和调试
```bash
# 运行测试
just test
uv run python tests/quick_test.py

# 检查依赖
just deps

# 前端测试
cd frontend && npm test
```

### API 端点

#### 平台管理
- `GET /platform/health` - 健康检查
- `GET /platform/agents` - 获取智能体列表
- `POST /platform/agents/{agent_id}/run` - 运行智能体
- `GET /platform/agents/{agent_id}/stream` - SSE 流式响应

#### 会话管理
- `GET /sessions` - 获取会话列表
- `POST /sessions` - 创建新会话
- `GET /sessions/{session_id}` - 获取会话详情
- `DELETE /sessions/{session_id}` - 删除会话

#### 评估系统
- `POST /eval/run` - 运行评估
- `GET /eval/results` - 获取评估结果
- `POST /eval/sets` - 创建评估集

### 智能体配置

智能体通过 `config.json` 文件配置：
```json
{
  "name": "智能体名称",
  "model": "gemini-2.0-flash-exp",
  "instructions": "智能体系统指令",
  "functions": [],
  "eval_config": {
    "metrics": ["accuracy", "relevance"],
    "test_sets": ["test_eval_set"]
  }
}
```

### 调试经验和最佳实践

#### 代码分层调试原则
**重要**: 项目包含两类代码，调试时需要区分对待：

1. **Google ADK 官方代码**：
   - 位置：`backend/api/adk_web_server.py`、`frontend/src/app/core/services/agent.service.ts` 等
   - 原则：**假设官方代码是正确的**，不要轻易怀疑或修改
   - 验证方法：对比官方 `/adk-debug` 页面的表现，如果官方页面正常，说明官方代码无问题

2. **项目自定义代码**：
   - 位置：`frontend/src/app/components/simplified-chat/` 等自实现组件
   - 原则：**优先检查和调试自定义代码**
   - 调试重点：消息处理逻辑、数据转换、UI 渲染等

#### 具体调试步骤
1. **问题复现**：先在官方 `/adk-debug` 页面测试相同功能，确认是否为官方代码问题
2. **数据流追踪**：
   - 添加 `console.log` 追踪数据流向
   - 检查 SSE 原始数据格式和内容
   - 确认前端数据处理逻辑
3. **分层排查**：
   - 后端 API → 前端 Service → 前端 Component → UI 渲染
   - 逐层验证数据的正确性和完整性

#### 常见问题排查

##### SSE 流式消息重复显示
- **现象**：智能体回答显示多次
- **原因**：未正确处理 ADK SSE 的 `partial` 字段
- **解决**：区分 partial（部分）和完整消息，只显示最终完整消息
- **关键代码**：`SimplifiedChatComponent.processPart()` 方法

##### SSE 消息显示问题
- 检查 `backend/api/adk_web_server.py` 中的换行符转义
- 确保 SSE 事件格式正确：`data: {json}\n\n`
- 参考 `docs/troubleshooting-sse-message-display.md`

##### WebSocket 连接问题
- 确认后端服务器运行在正确端口 (8000)
- 检查 CORS 设置允许前端域名 (localhost:4200)
- 验证 WebSocket 升级请求头

##### 智能体执行错误
- 检查智能体配置文件格式
- 验证 Google ADK 依赖安装
- 查看服务器日志获取详细错误信息

### 代码规范

#### Python 代码
- 使用 Python 3.12+ 类型注解
- 遵循 PEP 8 代码风格
- 使用 `uv` 管理依赖
- 异步编程使用 `async/await`

#### TypeScript 代码
- 严格模式 TypeScript
- Angular 19 最佳实践
- RxJS 响应式编程模式
- Angular Material 设计规范

#### 测试要求
- 后端 API 测试覆盖核心功能
- 前端组件单元测试
- 智能体集成测试
- 端到端测试场景

### 部署配置

#### 开发环境
- 后端：http://localhost:8000
- 前端：http://localhost:4200
- WebSocket：ws://localhost:8000/ws
- API 文档：http://localhost:8000/docs

#### 生产环境
- 使用环境变量配置后端 URL
- 前端构建：`npm run build`
- 后端部署：`uvicorn backend.fast_api:get_fast_api_app --host 0.0.0.0 --port 8000`

### 扩展开发

#### 添加新智能体
1. 在 `backend/agents/` 创建新目录
2. 实现 `agent.py` 和 `config.json`
3. 在 API 路由中注册
4. 添加前端支持

#### 新增 API 端点
1. 在 `backend/api/routers/` 添加路由
2. 实现业务逻辑
3. 更新 API 文档
4. 添加测试用例

#### 前端组件开发
1. 使用 Angular CLI 生成组件
2. 遵循 Material Design 规范
3. 实现响应式设计
4. 添加单元测试
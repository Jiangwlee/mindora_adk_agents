# 项目结构详解

## 目录结构
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

## 核心目录说明

### backend/agents/
包含所有智能体定义，每个智能体都有独立目录：
- `agent.py` - 智能体实现代码
- `config.json` - 智能体配置文件

### backend/api/
- `adk_web_server.py` - ADK Web 服务器（官方代码）
- `routers/` - 自定义 API 路由

### frontend/src/app/
- `components/` - 自定义 UI 组件
- `core/` - 来自 Google ADK Web 的核心服务

### docs/
项目文档集合，包含开发指南、API 文档等

### tests/
- `quick_test.py` - 快速功能验证
- `test_platform_apis.py` - 平台 API 测试
- `test_server.py` - 服务器集成测试
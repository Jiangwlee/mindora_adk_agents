# Mindora ADK Agents

Mindora ADK Agents是基于Google ADK Agents搭建的智能体平台。

# 技术栈

Next.js + FastAPI + Google ADK

1. 前端：使用 Next.Js 搭建一个多APP的Web界面，用户可以选择不同的智能体应用来完成特定工作。
2. FastAPI: 
    - 使用`from google.adk.cli.fast_api import get_fast_api_app`来创建一个fast api app，该app使用ADK内置的FastAPI Server来提供接口服务
    - 或者仿照`https://github.com/google/adk-python/blob/main/src/google/adk/cli/adk_web_server.py`和`https://github.com/google/adk-python/blob/main/src/google/adk/cli/fast_api.py`自行构建
3. Agents：参考https://github.com/google/adk-samples中的一些示例进行搭建

# 目录结构

```
mindora_adk_agents
 `- frontend
 `_ backend
    `_ agents
    `- main.py
```

# 依赖管理

1. 使用uv管理python依赖
2. 使用npm管理javascript依赖
3. 使用justfile来提供快捷命令

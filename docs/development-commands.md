# 开发命令参考

## 环境安装

### Python 依赖
```bash
# 安装 Python 依赖
just install
# 或
uv sync
```

### 前端依赖
```bash
cd frontend && npm install
```

## 运行服务

### 开发环境
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

### 端口信息
- 后端：http://localhost:8000
- 前端：http://localhost:4200
- WebSocket：ws://localhost:8000/ws
- API 文档：http://localhost:8000/docs

## 测试和调试

### 后端测试
```bash
# 运行所有测试
just test

# 快速功能验证
uv run python tests/quick_test.py

# 平台API测试
uv run python tests/test_platform_apis.py

# 服务器集成测试
uv run python tests/test_server.py

# 检查依赖
just deps
```

### 前端测试
```bash
cd frontend && npm test
cd frontend && npm run build
```

## 代码质量检查

### Python
```bash
# 代码格式化
uv run ruff format .

# 代码检查
uv run ruff check .

# 类型检查
uv run mypy .
```

### TypeScript
```bash
cd frontend && npm run lint
cd frontend && npm run type-check
```

## 常用调试命令

### 查看服务状态
```bash
# 检查端口占用
lsof -i :8000
lsof -i :4200

# 查看服务进程
ps aux | grep uvicorn
ps aux | grep ng
```

### 日志查看
```bash
# 后端日志
tail -f backend.log

# 前端开发服务器日志
cd frontend && npm run serve -- --verbose
```
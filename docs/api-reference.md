# API 端点参考

## 平台管理 API

### 应用管理
- `GET /platform/apps` - 获取应用列表
- `GET /platform/apps/{name}` - 获取应用详情  
- `POST /platform/apps/{name}/launch` - 启动应用会话

### 会话管理
- `GET /platform/sessions/{session_id}` - 获取会话信息
- `PUT /platform/sessions/{session_id}` - 更新会话
- `DELETE /platform/sessions/{session_id}` - 删除会话
- `POST /platform/cleanup` - 清理过期会话

### 健康检查
- `GET /platform/health` - 平台健康状态

## 兼容性 API (传统端点)

### 智能体管理
- `GET /list-apps` - 获取智能体列表 (兼容)
- `POST /run_sse` - SSE 流式执行 (兼容)

### 会话管理 (传统)
- `GET /sessions` - 获取会话列表
- `POST /sessions` - 创建新会话
- `GET /sessions/{session_id}` - 获取会话详情
- `DELETE /sessions/{session_id}` - 删除会话

### 评估系统
- `POST /eval/run` - 运行评估
- `GET /eval/results` - 获取评估结果
- `POST /eval/sets` - 创建评估集

## API 调用示例

### 获取应用列表
```bash
curl http://localhost:8000/platform/apps
```

### 启动应用会话
```bash
curl -X POST http://localhost:8000/platform/apps/assistant/launch \
  -H "Content-Type: application/json" \
  -d '{"userId": "user123"}'
```

### 健康检查
```bash
curl http://localhost:8000/platform/health
```
# 智能体配置详解

## 配置文件格式

智能体通过 `config.json` 文件配置，支持最新的平台应用格式：

```json
{
  "name": "智能体名称",
  "model": "gemini-2.0-flash-exp",
  "instructions": "智能体系统指令",
  "functions": [],
  "app_type": "chatbot",
  "ui_config": {
    "theme": "modern", 
    "layout": "chat",
    "colors": {
      "primary": "#1976d2",
      "accent": "#ff4081"
    }
  },
  "eval_config": {
    "metrics": ["accuracy", "relevance"],
    "test_sets": ["test_eval_set"]
  }
}
```

## 字段说明

### 基础字段
- `name`: 智能体显示名称
- `model`: 使用的 AI 模型 (如 gemini-2.0-flash-exp)
- `instructions`: 系统提示词
- `functions`: 可调用的函数列表

### 应用类型 (app_type)
- `"chatbot"`: 对话式应用，使用统一的聊天界面
- `"custom"`: 自定义应用，支持特殊布局和功能

### UI 配置 (ui_config)
- `theme`: 主题样式 ("modern", "classic")
- `layout`: 布局类型 ("chat", "dashboard", "custom")
- `colors`: 自定义配色方案

### 评估配置 (eval_config)
- `metrics`: 评估指标
- `test_sets`: 测试数据集

## 现有智能体配置

### adk_demo (Chatbot 类型)
```json
{
  "name": "ADK Demo Agent",
  "app_type": "chatbot",
  "ui_config": {
    "theme": "modern",
    "layout": "chat"
  }
}
```

### assistant (Chatbot 类型)
```json
{
  "name": "Assistant",  
  "app_type": "chatbot",
  "ui_config": {
    "theme": "modern",
    "layout": "chat"
  }
}
```

### data_analyst (Custom 类型)
```json
{
  "name": "Data Analyst",
  "app_type": "custom", 
  "ui_config": {
    "theme": "modern",
    "layout": "dashboard",
    "colors": {
      "primary": "#2196f3",
      "accent": "#ff9800"
    }
  }
}
```

## 添加新智能体

1. 在 `backend/agents/` 创建新目录
2. 实现 `agent.py` 文件
3. 创建 `config.json` 配置文件
4. 重启服务器自动加载
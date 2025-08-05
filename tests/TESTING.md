# ADK 服务器测试用例说明

## 测试脚本概述

我为您创建了两个测试脚本：

1. **`test_server.py`** - 完整的测试套件
2. **`quick_test.py`** - 快速基本功能测试

## 测试脚本功能

### 1. 完整测试套件 (`test_server.py`)

**功能：**
- 全面的 API 端点测试
- 详细的错误处理和日志记录
- 完整的测试报告生成
- 支持自定义参数

**测试的端点：**
- `GET /health` - 健康检查
- `GET /list-apps` - 应用列表
- `GET /platform/apps` - 平台应用
- `POST /apps/{app}/users/{user}/sessions` - 创建会话
- `GET /apps/{app}/users/{user}/sessions` - 会话列表
- `GET /apps/{app}/users/{user}/sessions/{session}` - 获取会话详情
- `POST /run` - 智能体运行（同步）
- `POST /run_sse` - 智能体运行（SSE流式）
- `GET /debug/trace/session/{session}` - 调试追踪
- `GET /apps/{app}/users/{user}/sessions/{session}/artifacts` - 制品列表

**使用方法：**
```bash
# 使用默认参数运行
python test_server.py

# 自定义服务器URL
python test_server.py --url http://localhost:8000

# 自定义应用和用户
python test_server.py --app assistant --user my_user

# 查看帮助
python test_server.py --help
```

**输出：**
- 控制台实时测试结果
- 生成 `test_results.json` 文件包含详细结果
- 测试统计摘要

### 2. 快速测试 (`quick_test.py`)

**功能：**
- 基本功能快速验证
- 简化的输出格式
- 适合开发过程中的快速检查

**测试的端点：**
- `GET /health` - 健康检查
- `GET /list-apps` - 应用列表
- `GET /platform/apps` - 平台应用
- `POST /apps/{app}/users/{user}/sessions` - 创建会话
- `POST /run` - 智能体运行

**使用方法：**
```bash
# 运行快速测试
python quick_test.py
```

**输出：**
- 简洁的控制台输出
- 基本的通过/失败统计

## 测试前准备

### 1. 启动服务器

确保 ADK 服务器正在运行：

```bash
# 使用虚拟环境启动
source .venv/bin/activate
python run_server.py --agents-dir backend/agents --port 8000 --reload
```

### 2. 检查依赖

确保安装了必要的依赖：

```bash
source .venv/bin/activate
pip install requests
```

## 测试执行流程

### 完整测试流程

1. **启动服务器**
   ```bash
   source .venv/bin/activate
   python run_server.py --agents-dir backend/agents --port 8000 --reload
   ```

2. **在另一个终端运行测试**
   ```bash
   # 快速测试
   python quick_test.py
   
   # 或完整测试
   python test_server.py
   ```

3. **查看结果**
   - 控制台实时输出
   - `test_results.json` 文件（完整测试）

### 预期结果

**成功情况：**
- 所有测试显示 ✅ 通过
- 服务器返回正确的响应格式
- 会话创建和智能体运行正常

**常见失败情况：**
- 服务器未启动（连接失败）
- 依赖缺失（导入错误）
- 配置问题（路径错误）

## 测试结果解读

### 状态图标
- ✅ 通过：测试成功
- ❌ 失败：测试失败
- ⚠️ 警告：测试部分成功或有异常
- ⚠️ 跳过：测试因依赖问题被跳过

### 详细结果文件

完整测试会生成 `test_results.json` 文件，包含：
- 每个测试的详细信息
- HTTP 状态码
- 响应内容
- 错误信息（如果有）

## 故障排除

### 1. 连接失败
- 确保服务器正在运行
- 检查端口是否正确
- 验证防火墙设置

### 2. 依赖问题
- 激活虚拟环境：`source .venv/bin/activate`
- 安装依赖：`pip install requests`

### 3. 服务器错误
- 检查服务器日志：`cat server.log`
- 验证配置文件
- 确认智能体文件存在

## 自定义测试

### 修改测试参数

```bash
# 使用不同的服务器地址
python test_server.py --url http://192.168.1.100:8000

# 测试不同的应用
python test_server.py --app data_analyst

# 使用不同的用户ID
python test_server.py --user admin_user
```

### 添加新的测试

可以在 `test_server.py` 中添加新的测试方法：

```python
def test_custom_endpoint(self):
    """自定义测试"""
    response = self.session.get(f"{self.base_url}/custom-endpoint")
    # 处理响应
    return {
        "test": "custom_endpoint",
        "status": "✅ 通过" if response.status_code == 200 else "❌ 失败",
        # ... 其他信息
    }
```

## 性能测试

对于性能测试，可以修改测试脚本：

```python
import time

def performance_test():
    """性能测试"""
    start_time = time.time()
    
    # 运行多次测试
    for i in range(10):
        response = requests.get("http://localhost:8000/health")
    
    end_time = time.time()
    print(f"平均响应时间: {(end_time - start_time) / 10:.2f}秒")
```

## 总结

这两个测试脚本提供了完整的 ADK 服务器测试解决方案：

- **快速测试**：用于开发过程中的快速验证
- **完整测试**：用于全面的功能验证和问题诊断

您可以根据需要选择合适的测试脚本，并根据实际情况进行定制。
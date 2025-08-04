"""
Agent: 通用助手
Description: 基于Google ADK的通用AI助手，可以回答各种问题
"""

from typing import Dict, Any
from google.adk.agents import Agent

def get_general_info(query: str) -> dict:
    """获取通用信息的工具函数
    
    Args:
        query (str): 用户查询的问题
        
    Returns:
        dict: 包含回答的字典
    """
    # 这里可以集成更多的信息源，比如网络搜索、知识库等
    # 目前提供一个基本的实现
    return {
        "status": "success",
        "answer": f"关于'{query}'的问题，我正在为您查找相关信息。"
    }

def calculate_expression(expression: str) -> dict:
    """计算数学表达式
    
    Args:
        expression (str): 数学表达式
        
    Returns:
        dict: 计算结果
    """
    try:
        # 安全的数学计算
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return {
                "status": "error",
                "error_message": "表达式包含不允许的字符"
            }
        
        result = eval(expression)
        return {
            "status": "success",
            "result": f"{expression} = {result}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"计算错误: {str(e)}"
        }

# 创建基于ADK的对话机器人Agent
root_agent = Agent(
    name="assistant_agent",
    model="gemini-2.0-flash",
    description="通用AI助手，可以回答各种问题，进行对话，翻译，总结等任务",
    instruction="""你是一个智能助手，可以帮助用户完成各种任务。

你的主要能力包括：
1. 回答各种问题
2. 进行自然对话
3. 文本翻译
4. 内容总结
5. 简单的数学计算
6. 提供通用信息和建议

请始终：
- 用中文回复（除非用户明确要求其他语言）
- 保持友好和专业的语气
- 提供准确和有用的信息
- 如果不确定，请诚实告知
- 在适当的时候使用可用的工具

记住对话的上下文，提供连贯的回复。""",
    tools=[get_general_info, calculate_expression],
)

# 保持向后兼容的类定义
class AssistantAgent:
    """通用AI助手，可以回答各种问题"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "通用助手"
        self.description = "通用AI助手，可以回答各种问题"
        self.capabilities = ['文本生成', '问答', '对话', '翻译', '总结']
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """处理消息"""
        # 现在这个方法将使用ADK Agent
        return f"ADK Agent处理: {message}"
    
    async def execute_task(self, task: str, parameters: Dict[str, Any] = None) -> str:
        """执行任务"""
        # 现在这个方法将使用ADK Agent
        return f"ADK Agent执行: {task}"

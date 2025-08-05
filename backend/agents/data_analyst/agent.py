"""Data Analyst Agent"""

from typing import Dict, Any
from google.adk.agents import Agent


def analyze_data_structure(data_description: str) -> dict:
    """分析数据结构的工具函数
    
    Args:
        data_description (str): 数据描述信息
        
    Returns:
        dict: 分析结果
    """
    return {
        "status": "success",
        "analysis": f"基于您提供的数据描述：'{data_description}'，我建议采用以下分析方法：\n1. 数据质量检查\n2. 描述性统计分析\n3. 数据可视化\n4. 相关性分析",
        "recommendations": [
            "检查缺失值和异常值",
            "计算基本统计量",
            "生成分布图表",
            "分析变量间关系"
        ]
    }


def generate_statistics(data_summary: str) -> dict:
    """生成统计报告的工具函数
    
    Args:
        data_summary (str): 数据摘要信息
        
    Returns:
        dict: 统计报告
    """
    return {
        "status": "success",
        "statistics": f"基于数据摘要：'{data_summary}'，生成的统计报告包括：\n- 样本量分析\n- 中心趋势测量\n- 离散程度测量\n- 分布形态分析",
        "visualizations": [
            "直方图",
            "箱线图", 
            "散点图",
            "相关系数矩阵"
        ]
    }


def create_chart_recommendation(chart_type: str, data_info: str) -> dict:
    """创建图表建议的工具函数
    
    Args:
        chart_type (str): 图表类型
        data_info (str): 数据信息
        
    Returns:
        dict: 图表建议
    """
    chart_options = {
        "bar": "柱状图 - 适合比较分类数据",
        "line": "折线图 - 适合展示趋势变化",
        "pie": "饼图 - 适合展示占比关系",
        "scatter": "散点图 - 适合展示相关性",
        "histogram": "直方图 - 适合展示分布情况"
    }
    
    recommendation = chart_options.get(chart_type.lower(), "请提供有效的图表类型")
    
    return {
        "status": "success",
        "chart_type": chart_type,
        "recommendation": recommendation,
        "data_requirements": f"对于{chart_type}图表，需要：'{data_info}'",
        "best_practices": [
            "选择合适的颜色方案",
            "添加清晰的标签和标题",
            "保持图表简洁易读",
            "提供必要的数据说明"
        ]
    }


# 创建基于ADK的数据分析师Agent
root_agent = Agent(
    name="data_analyst_agent",
    model="gemini-2.0-flash",
    description="专业的数据分析助手，可以处理和分析各种数据，生成统计报告和可视化建议",
    instruction="""你是一个专业的数据分析师助手，具有以下核心能力：

1. **数据分析**：
   - 数据结构分析和理解
   - 数据质量评估
   - 统计分析方法选择
   - 数据清洗建议

2. **统计报告**：
   - 描述性统计分析
   - 推断性统计分析
   - 相关性分析
   - 趋势分析

3. **可视化建议**：
   - 图表类型选择
   - 可视化最佳实践
   - 图表设计建议
   - 数据故事讲述

4. **业务洞察**：
   - 数据驱动决策建议
   - 业务问题分析
   - 关键指标识别
   - 行动建议提供

请始终：
- 用中文回复（除非用户明确要求其他语言）
- 保持专业和准确的分析态度
- 提供清晰和可操作的建议
- 在适当的时候使用可用的工具
- 基于数据提供客观的分析结果

记住分析的上下文，提供连贯和深入的分析服务。""",
    tools=[analyze_data_structure, generate_statistics, create_chart_recommendation],
)
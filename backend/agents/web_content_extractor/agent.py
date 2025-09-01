"""
Agent: 智能网页信息整理
Description: 基于Google ADK的智能网页内容提取和整理系统，支持多种输入格式
"""

from typing import Dict, Any, List
from google.adk.agents import Agent
import logging

try:
    # 尝试相对导入（在平台环境中）
    from .tools.document_processor import (
        extract_urls_from_text,
        process_word_document,
        process_excel_document,
        validate_urls
    )
    from .tools.web_crawler import (
        crawl_multiple_urls
    )
    from .tools.content_formatter import (
        format_extraction_results,
        generate_statistics_report,
        create_summary_report
    )
    from .schemas import (
        URLInfo,
        ExtractionResult,
        ExtractionOutput,
        InputType,
        ProcessingStatus,
        create_extraction_result_from_dict
    )
    from .utils import (
        validate_url,
        normalize_url,
        format_error_message,
        log_processing_stats
    )
except ImportError:
    # 降级到绝对导入（用于直接测试）
    from tools.document_processor import (
        extract_urls_from_text,
        process_word_document,
        process_excel_document,
        validate_urls
    )
    from tools.web_crawler import (
        crawl_multiple_urls
    )
    from tools.content_formatter import (
        format_extraction_results,
        generate_statistics_report,
        create_summary_report
    )
    from schemas import (
        URLInfo,
        ExtractionResult,
        ExtractionOutput,
        InputType,
        ProcessingStatus,
        create_extraction_result_from_dict
    )
    from utils import (
        validate_url,
        normalize_url,
        format_error_message,
        log_processing_stats
    )

# 配置日志
logger = logging.getLogger(__name__)

def extract_urls_from_input(content: str, source: str = "user_input") -> Dict[str, Any]:
    """
    从用户输入中提取URL信息
    
    Args:
        content: 输入内容（文本、文档路径等）
        source: 输入来源标识
    
    Returns:
        Dict: URL提取结果
    """
    try:
        logger.info(f"开始处理输入内容，来源: {source}")
        
        urls = []
        input_type = InputType.TEXT
        
        # 检测输入类型并处理
        if content.lower().endswith(('.docx', '.doc')):
            logger.info("检测到Word文档输入")
            input_type = InputType.WORD_DOCUMENT
            urls = process_word_document(content)
        elif content.lower().endswith(('.xlsx', '.xls')):
            logger.info("检测到Excel文档输入") 
            input_type = InputType.EXCEL_DOCUMENT
            urls = process_excel_document(content)
        else:
            logger.info("检测到文本输入")
            input_type = InputType.TEXT
            urls = extract_urls_from_text(content)
        
        # 验证和规范化URLs
        validated_urls = validate_urls(urls)
        
        logger.info(f"URL提取完成，找到 {len(validated_urls)} 个有效链接")
        
        return {
            "status": "success",
            "input_type": input_type.value,
            "urls_found": len(validated_urls),
            "urls": validated_urls,
            "source": source,
            "message": f"成功提取 {len(validated_urls)} 个URL链接"
        }
        
    except Exception as e:
        error_msg = format_error_message(e)
        logger.error(f"输入处理失败: {error_msg}")
        
        return {
            "status": "error",
            "error_message": error_msg,
            "urls": [],
            "source": source
        }

def extract_web_content(urls_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    提取网页内容
    
    Args:
        urls_data: URL数据字典
    
    Returns:
        Dict: 网页内容提取结果
    """
    try:
        urls = urls_data.get("urls", [])
        if not urls:
            return {
                "status": "error",
                "error_message": "没有找到有效的URL进行处理",
                "results": []
            }
        
        logger.info(f"开始提取 {len(urls)} 个URL的网页内容")
        
        # 使用网页爬虫工具批量提取内容
        results = crawl_multiple_urls(urls, max_concurrent=10)
        
        # 统计结果
        successful_count = len([r for r in results if r.get("status") == "success"])
        failed_count = len([r for r in results if r.get("status") == "error"])
        
        logger.info(f"网页内容提取完成，成功: {successful_count}, 失败: {failed_count}")
        
        return {
            "status": "success",
            "total_processed": len(urls),
            "successful_extractions": successful_count,
            "failed_extractions": failed_count,
            "results": results,
            "source": urls_data.get("source", "unknown")
        }
        
    except Exception as e:
        error_msg = format_error_message(e)
        logger.error(f"网页内容提取失败: {error_msg}")
        
        return {
            "status": "error",
            "error_message": error_msg,
            "results": []
        }

def format_final_output(extraction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化最终输出结果
    
    Args:
        extraction_data: 提取数据
    
    Returns:
        Dict: 格式化的最终结果
    """
    try:
        logger.info("开始格式化最终输出结果")
        
        # 使用内容格式化工具生成最终JSON
        formatted_result = format_extraction_results(extraction_data)
        
        # 添加统计报告
        results = extraction_data.get("results", [])
        if results:
            stats = generate_statistics_report(results)
            formatted_result["statistics"] = stats
            
            # 生成用户友好的摘要报告
            summary_text = create_summary_report(formatted_result)
            formatted_result["summary_text"] = summary_text
        
        # 记录处理统计
        total_urls = formatted_result.get("processing_info", {}).get("total_urls", 0)
        successful = formatted_result.get("processing_info", {}).get("successful_count", 0)
        failed = formatted_result.get("processing_info", {}).get("failed_count", 0)
        
        if total_urls > 0:
            # 计算总处理时间
            total_time = sum(
                r.get("processing_time_ms", 0) 
                for r in results 
                if isinstance(r, dict)
            )
            log_processing_stats(total_urls, successful, failed, total_time)
        
        logger.info("最终输出格式化完成")
        return formatted_result
        
    except Exception as e:
        error_msg = format_error_message(e)
        logger.error(f"结果格式化失败: {error_msg}")
        
        return {
            "status": "error",
            "error_message": error_msg,
            "timestamp": "error",
            "results": [],
            "errors": [{
                "url": "unknown",
                "source": "formatter",
                "error_message": error_msg
            }]
        }

# 创建基于ADK的网页内容提取Agent
root_agent = Agent(
    name="web_content_extractor",
    model="gemini-2.0-flash-exp",
    description="智能网页信息整理系统，支持多种输入格式的URL提取和网页内容抓取",
    instruction="""你是一个专业的网页信息整理助手，可以帮助用户从各种输入中提取和整理网页内容。

你的主要能力包括：
1. **输入处理**: 支持自然语言文本、Word文档(.docx)、Excel文档(.xlsx)
2. **URL提取**: 智能识别和提取各种格式的网页链接
3. **内容抓取**: 并行处理多个URL，提取网页标题和正文内容
4. **格式输出**: 生成结构化JSON结果，包含统计信息和错误报告
5. **进度反馈**: 提供清晰的处理进度和状态更新

工作流程：
1. 首先使用 extract_urls_from_input 工具从用户输入中提取URL
2. 然后使用 extract_web_content 工具并行抓取网页内容  
3. 最后使用 format_final_output 工具格式化输出结果

请始终：
- 提供清晰的处理进度反馈
- 对错误进行友好的解释
- 生成完整的统计信息
- 保持结果格式的一致性
- 使用中文与用户交流

支持的输入示例：
- 直接粘贴包含URL的文本："请提取 https://example.com 和 www.test.com 的内容"
- 上传包含链接的Word或Excel文件
- 多轮对话中追加新的URL

处理特点：
- 自动识别和规范化URL格式
- 并行处理多个URL以提高效率
- 智能内容提取，过滤无关信息
- 提供详细的错误诊断和处理建议
- 支持大批量URL的稳定处理""",
    tools=[
        extract_urls_from_input, 
        extract_web_content, 
        format_final_output
    ],
)

# 保持向后兼容的类定义（如果需要）
class WebContentExtractorAgent:
    """智能网页内容提取器Agent"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = "智能网页信息整理"
        self.description = "智能网页内容提取和整理系统"
        self.capabilities = [
            'URL提取', '网页内容抓取', '文档处理', 
            '并行处理', '结构化输出', '实时进度反馈'
        ]
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """处理用户消息"""
        return f"ADK Agent处理网页提取请求: {message}"
    
    async def extract_urls(self, content: str) -> List[str]:
        """提取URLs"""
        result = extract_urls_from_input(content)
        if result.get("status") == "success":
            return [url["url"] for url in result.get("urls", [])]
        return []
    
    async def crawl_urls(self, urls: List[str]) -> Dict[str, Any]:
        """爬取URL内容"""
        url_data = {"urls": [{"url": url} for url in urls]}
        return extract_web_content(url_data)
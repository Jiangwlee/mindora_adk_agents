"""
Content formatting tools for Web Content Extractor Agent
内容格式化工具：生成结构化JSON输出和统计报告
"""

import json
import time
from typing import List, Dict, Any
from datetime import datetime
import logging

def format_extraction_results(extraction_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化提取结果为标准JSON格式
    
    Args:
        extraction_data: 原始提取数据
        
    Returns:
        Dict: 格式化的结果
    """
    try:
        results = extraction_data.get("results", [])
        
        # 分类结果
        successful_results = [r for r in results if r.get("status") == "success"]
        failed_results = [r for r in results if r.get("status") == "error"]
        
        # 构建最终输出格式
        formatted_output = {
            "timestamp": datetime.now().isoformat(),
            "source": extraction_data.get("source", "unknown"),
            "processing_info": {
                "total_urls": len(results),
                "successful_count": len(successful_results),
                "failed_count": len(failed_results),
                "success_rate": round((len(successful_results) / len(results) * 100), 2) if results else 0
            },
            "results": [],
            "errors": [],
            "metadata": {
                "agent": "web_content_extractor",
                "version": "1.0.0",
                "extraction_method": "crawl4ai_simulation"
            }
        }
        
        # 格式化成功结果
        for result in successful_results:
            formatted_result = {
                "url": result.get("url"),
                "title": result.get("title", "无标题"),
                "content": result.get("content", ""),
                "word_count": result.get("word_count", 0),
                "source": result.get("source", "unknown"),
                "processing_time_ms": result.get("processing_time_ms", 0),
                "extracted_at": datetime.fromtimestamp(result.get("timestamp", time.time())).isoformat()
            }
            formatted_output["results"].append(formatted_result)
        
        # 格式化错误信息
        for error in failed_results:
            error_info = {
                "url": error.get("url"),
                "source": error.get("source", "unknown"),
                "error_message": error.get("error_message", "未知错误"),
                "failed_at": datetime.fromtimestamp(error.get("timestamp", time.time())).isoformat()
            }
            formatted_output["errors"].append(error_info)
        
        return formatted_output
        
    except Exception as e:
        logging.error(f"结果格式化失败: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "source": "error",
            "processing_info": {
                "total_urls": 0,
                "successful_count": 0,
                "failed_count": 1,
                "success_rate": 0
            },
            "results": [],
            "errors": [{
                "url": "unknown",
                "source": "formatter",
                "error_message": f"格式化过程失败: {str(e)}",
                "failed_at": datetime.now().isoformat()
            }],
            "metadata": {
                "agent": "web_content_extractor",
                "version": "1.0.0",
                "extraction_method": "error"
            }
        }

def generate_statistics_report(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    生成统计报告
    
    Args:
        results: 处理结果列表
        
    Returns:
        Dict: 统计报告
    """
    try:
        if not results:
            return {
                "total_processed": 0,
                "success_rate": 0,
                "average_processing_time": 0,
                "total_words_extracted": 0,
                "average_words_per_page": 0
            }
        
        successful_results = [r for r in results if r.get("status") == "success"]
        
        # 计算统计指标
        total_processing_time = sum(r.get("processing_time_ms", 0) for r in results)
        total_words = sum(r.get("word_count", 0) for r in successful_results)
        
        statistics = {
            "total_processed": len(results),
            "successful_extractions": len(successful_results),
            "failed_extractions": len(results) - len(successful_results),
            "success_rate": round((len(successful_results) / len(results) * 100), 2),
            "total_processing_time_ms": total_processing_time,
            "average_processing_time_ms": round(total_processing_time / len(results), 2),
            "total_words_extracted": total_words,
            "average_words_per_page": round(total_words / len(successful_results), 2) if successful_results else 0,
            "content_distribution": _analyze_content_distribution(successful_results)
        }
        
        return statistics
        
    except Exception as e:
        logging.error(f"统计报告生成失败: {e}")
        return {
            "error": f"统计报告生成失败: {str(e)}"
        }

def _analyze_content_distribution(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    分析内容分布
    
    Args:
        results: 成功结果列表
        
    Returns:
        Dict: 内容分布分析
    """
    try:
        if not results:
            return {"categories": {}}
            
        word_counts = [r.get("word_count", 0) for r in results]
        
        # 按内容长度分类
        categories = {
            "短内容 (<100词)": len([wc for wc in word_counts if wc < 100]),
            "中等内容 (100-500词)": len([wc for wc in word_counts if 100 <= wc < 500]),
            "长内容 (500-1000词)": len([wc for wc in word_counts if 500 <= wc < 1000]),
            "超长内容 (>1000词)": len([wc for wc in word_counts if wc >= 1000])
        }
        
        # 来源分布
        sources = {}
        for result in results:
            source = result.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        return {
            "content_length_categories": categories,
            "source_distribution": sources,
            "word_count_range": {
                "min": min(word_counts) if word_counts else 0,
                "max": max(word_counts) if word_counts else 0,
                "median": sorted(word_counts)[len(word_counts)//2] if word_counts else 0
            }
        }
    except Exception as e:
        logging.error(f"内容分布分析失败: {e}")
        return {"error": str(e)}

def create_summary_report(formatted_data: Dict[str, Any]) -> str:
    """
    创建用户友好的摘要报告
    
    Args:
        formatted_data: 格式化后的数据
        
    Returns:
        str: 摘要报告文本
    """
    try:
        info = formatted_data.get("processing_info", {})
        stats = formatted_data.get("statistics", {})
        
        summary = f"""
# 网页内容提取报告

## 处理概览
- **总URL数量**: {info.get('total_urls', 0)}
- **成功提取**: {info.get('successful_count', 0)}
- **失败数量**: {info.get('failed_count', 0)}
- **成功率**: {info.get('success_rate', 0)}%

## 内容统计
- **总字数**: {stats.get('total_words_extracted', 0):,} 字
- **平均字数/页面**: {stats.get('average_words_per_page', 0)} 字
- **平均处理时间**: {stats.get('average_processing_time_ms', 0)} 毫秒

## 处理时间
- **总处理时间**: {stats.get('total_processing_time_ms', 0)} 毫秒
- **提取完成时间**: {formatted_data.get('timestamp', '未知')}
"""
        
        # 添加错误摘要
        errors = formatted_data.get("errors", [])
        if errors:
            summary += f"\n## 处理错误 ({len(errors)} 个)\n"
            for i, error in enumerate(errors[:3], 1):  # 只显示前3个错误
                summary += f"{i}. {error.get('url', 'unknown')}: {error.get('error_message', 'unknown error')}\n"
            
            if len(errors) > 3:
                summary += f"... 还有 {len(errors) - 3} 个错误\n"
        
        return summary.strip()
        
    except Exception as e:
        return f"摘要报告生成失败: {str(e)}"
"""
Document processing tools for Web Content Extractor Agent
文档处理工具：支持Word文档、Excel文档和文本中的URL提取
"""

import re
import os
from typing import List, Dict, Any
import logging

# URL 提取正则表达式
URL_PATTERN = re.compile(
    r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?',
    re.IGNORECASE
)

def extract_urls_from_text(text: str) -> List[Dict[str, Any]]:
    """
    从文本中提取URLs
    
    Args:
        text: 输入文本
        
    Returns:
        List[Dict]: URL信息列表
    """
    try:
        urls = URL_PATTERN.findall(text)
        
        result = []
        for i, url in enumerate(urls):
            result.append({
                "url": url.strip(),
                "source": "text_input", 
                "index": i + 1,
                "context": _get_url_context(text, url)
            })
            
        return result
    except Exception as e:
        logging.error(f"文本URL提取失败: {e}")
        return []

def process_word_document(file_path: str) -> List[Dict[str, Any]]:
    """
    处理Word文档并提取URLs
    
    Args:
        file_path: Word文档路径
        
    Returns:
        List[Dict]: URL信息列表
    """
    try:
        # 这里需要根据平台的文件处理方式来实现
        # 目前返回模拟数据，实际实现时需要集成pandoc或python-docx
        logging.info(f"处理Word文档: {file_path}")
        
        # 模拟实现 - 实际需要使用pandoc或python-docx
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        # TODO: 实际实现应该使用pandoc转换为文本后提取URL
        # 或者使用python-docx直接读取文档内容
        return [
            {
                "url": "https://example.com/from-word-doc",
                "source": f"word_document:{os.path.basename(file_path)}",
                "index": 1,
                "context": "从Word文档中提取的链接"
            }
        ]
    except Exception as e:
        logging.error(f"Word文档处理失败: {e}")
        return []

def process_excel_document(file_path: str) -> List[Dict[str, Any]]:
    """
    处理Excel文档并提取URLs
    
    Args:
        file_path: Excel文档路径
        
    Returns:
        List[Dict]: URL信息列表
    """
    try:
        logging.info(f"处理Excel文档: {file_path}")
        
        # 模拟实现 - 实际需要使用pandas.read_excel()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
            
        # TODO: 实际实现应该使用pandas读取Excel文件
        # 然后遍历所有sheet和单元格提取URL
        return [
            {
                "url": "https://example.com/from-excel-sheet",
                "source": f"excel_document:{os.path.basename(file_path)}",
                "index": 1,
                "context": "从Excel文档中提取的链接"
            }
        ]
    except Exception as e:
        logging.error(f"Excel文档处理失败: {e}")
        return []

def _get_url_context(text: str, url: str, context_length: int = 50) -> str:
    """
    获取URL在文本中的上下文
    
    Args:
        text: 完整文本
        url: 目标URL
        context_length: 上下文长度
        
    Returns:
        str: URL的上下文文本
    """
    try:
        index = text.find(url)
        if index == -1:
            return ""
            
        start = max(0, index - context_length)
        end = min(len(text), index + len(url) + context_length)
        
        context = text[start:end].strip()
        return context if context else "无上下文"
    except:
        return "无上下文"

def validate_urls(urls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    验证URL列表的有效性
    
    Args:
        urls: URL信息列表
        
    Returns:
        List[Dict]: 验证后的URL列表
    """
    validated = []
    
    for url_info in urls:
        url = url_info.get("url", "").strip()
        
        # 基本URL格式验证
        if not url:
            continue
            
        # 确保URL包含协议
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                url = f'https://{url}'
            elif '.' in url and ' ' not in url:
                url = f'https://{url}'
            else:
                continue
                
        # 更新URL信息
        url_info["url"] = url
        validated.append(url_info)
    
    return validated
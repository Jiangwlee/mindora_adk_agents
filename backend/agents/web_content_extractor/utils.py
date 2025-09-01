"""
Utility functions for Web Content Extractor Agent
工具函数：通用辅助功能和帮助器
"""

import re
import logging
import time
from typing import List, Dict, Any, Optional, Union
from urllib.parse import urlparse
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL验证正则表达式
URL_REGEX = re.compile(
    r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?',
    re.IGNORECASE
)

def validate_url(url: str) -> bool:
    """
    验证URL的有效性
    
    Args:
        url: 待验证的URL
        
    Returns:
        bool: URL是否有效
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    try:
        # 使用urllib.parse进行验证
        result = urlparse(url)
        
        # 检查基本要素
        if not all([result.scheme, result.netloc]):
            return False
        
        # 检查协议
        if result.scheme.lower() not in ['http', 'https']:
            return False
        
        # 使用正则表达式进一步验证
        return bool(URL_REGEX.match(url))
        
    except Exception as e:
        logger.warning(f"URL验证失败 {url}: {e}")
        return False

def normalize_url(url: str) -> str:
    """
    规范化URL格式
    
    Args:
        url: 原始URL
        
    Returns:
        str: 规范化后的URL
    """
    if not url:
        return ""
    
    url = url.strip()
    
    # 移除多余的空格
    url = re.sub(r'\s+', '', url)
    
    # 确保有协议前缀
    if not url.startswith(('http://', 'https://')):
        if url.startswith('www.'):
            url = f'https://{url}'
        elif is_valid_domain(url.split('/')[0]):
            url = f'https://{url}'
    
    # 移除末尾的多余斜杠（但保留路径中的斜杠）
    if url.endswith('/') and url.count('/') > 3:
        url = url.rstrip('/')
    
    return url

def is_valid_domain(domain: str) -> bool:
    """
    检查是否为有效域名
    
    Args:
        domain: 域名字符串
        
    Returns:
        bool: 是否为有效域名
    """
    if not domain:
        return False
    
    # 基本长度检查
    if len(domain) > 253:
        return False
    
    # 域名格式检查
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
    return bool(re.match(pattern, domain))

def extract_domain(url: str) -> str:
    """
    从URL中提取域名
    
    Args:
        url: 完整URL
        
    Returns:
        str: 域名部分
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return ""

def categorize_error(error: Exception) -> str:
    """
    对错误进行分类
    
    Args:
        error: 异常对象
        
    Returns:
        str: 错误类别
    """
    error_str = str(error).lower()
    
    # 网络相关错误
    if any(keyword in error_str for keyword in ['timeout', 'connection', 'network', 'dns']):
        return "network_error"
    
    # HTTP错误
    elif any(keyword in error_str for keyword in ['404', '403', '500', '502', '503']):
        return "http_error"
    
    # 内容解析错误
    elif any(keyword in error_str for keyword in ['parse', 'encoding', 'decode']):
        return "parsing_error"
    
    # 文件处理错误
    elif any(keyword in error_str for keyword in ['file', 'permission', 'access']):
        return "file_error"
    
    # 其他错误
    else:
        return "unknown_error"

def format_error_message(error: Exception, url: str = "") -> str:
    """
    格式化错误消息为用户友好的形式
    
    Args:
        error: 异常对象
        url: 相关URL
        
    Returns:
        str: 格式化的错误消息
    """
    error_category = categorize_error(error)
    error_str = str(error)
    
    # 根据错误类别生成友好消息
    messages = {
        "network_error": f"网络连接失败：无法访问 {url}",
        "http_error": f"网站访问被拒绝或不可用：{error_str}",
        "parsing_error": f"页面内容解析失败：{error_str}",
        "file_error": f"文件处理失败：{error_str}",
        "unknown_error": f"未知错误：{error_str}"
    }
    
    return messages.get(error_category, f"处理失败：{error_str}")

def calculate_processing_time(start_time: float) -> int:
    """
    计算处理时间（毫秒）
    
    Args:
        start_time: 开始时间戳
        
    Returns:
        int: 处理时间（毫秒）
    """
    return int((time.time() - start_time) * 1000)

def clean_text(text: str) -> str:
    """
    清理文本内容
    
    Args:
        text: 原始文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除特殊字符
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()-]', '', text)
    
    return text.strip()

def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        str: 截断后的文本
    """
    if not text or len(text) <= max_length:
        return text
    
    # 尽量在词边界截断
    truncated = text[:max_length - len(suffix)]
    
    # 寻找最近的空格或句号
    for delimiter in [' ', '。', '.', '！', '!', '？', '?']:
        last_pos = truncated.rfind(delimiter)
        if last_pos > max_length * 0.8:  # 如果找到的位置不是太靠前
            truncated = truncated[:last_pos + 1]
            break
    
    return truncated + suffix

def extract_urls_with_regex(text: str) -> List[str]:
    """
    使用正则表达式从文本中提取URL
    
    Args:
        text: 输入文本
        
    Returns:
        List[str]: 提取到的URL列表
    """
    if not text:
        return []
    
    # 使用预编译的正则表达式
    urls = URL_REGEX.findall(text)
    
    # 去重并验证
    unique_urls = []
    for url in urls:
        url = url.strip()
        if url not in unique_urls and validate_url(url):
            unique_urls.append(url)
    
    return unique_urls

def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件扩展名（小写，不包含点）
    """
    if not filename:
        return ""
    
    parts = filename.lower().split('.')
    return parts[-1] if len(parts) > 1 else ""

def is_supported_document(filename: str) -> bool:
    """
    检查是否为支持的文档类型
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否支持
    """
    supported_extensions = ['docx', 'doc', 'xlsx', 'xls', 'txt']
    return get_file_extension(filename) in supported_extensions

def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为人类可读格式
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化的文件大小
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024.0 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def create_user_agent() -> str:
    """
    创建用户代理字符串
    
    Returns:
        str: 用户代理字符串
    """
    return "WebContentExtractor/1.0 (Mindora ADK Agents Platform)"

def rate_limit_delay(request_count: int, max_requests_per_second: int = 10) -> float:
    """
    计算速率限制延迟时间
    
    Args:
        request_count: 当前请求计数
        max_requests_per_second: 每秒最大请求数
        
    Returns:
        float: 延迟时间（秒）
    """
    if request_count <= 0:
        return 0.0
    
    min_interval = 1.0 / max_requests_per_second
    
    # 简单的线性延迟策略
    if request_count <= max_requests_per_second:
        return min_interval
    else:
        # 超过限制时增加延迟
        return min_interval * (1 + (request_count - max_requests_per_second) * 0.1)

def log_processing_stats(
    total_urls: int,
    successful: int,
    failed: int,
    total_time_ms: int
) -> None:
    """
    记录处理统计信息
    
    Args:
        total_urls: 总URL数
        successful: 成功数
        failed: 失败数
        total_time_ms: 总处理时间（毫秒）
    """
    success_rate = (successful / total_urls * 100) if total_urls > 0 else 0
    avg_time = (total_time_ms / total_urls) if total_urls > 0 else 0
    
    logger.info(f"处理完成统计:")
    logger.info(f"  总URL数: {total_urls}")
    logger.info(f"  成功: {successful} ({success_rate:.1f}%)")
    logger.info(f"  失败: {failed}")
    logger.info(f"  总耗时: {total_time_ms}ms")
    logger.info(f"  平均耗时: {avg_time:.1f}ms/URL")

# 常用常量
DEFAULT_TIMEOUT = 30  # 默认超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数
MAX_CONCURRENT = 10  # 最大并发数
MAX_FILE_SIZE = 5 * 1024 * 1024  # 最大文件大小（5MB）
SUPPORTED_ENCODINGS = ['utf-8', 'gbk', 'gb2312', 'big5']  # 支持的编码格式
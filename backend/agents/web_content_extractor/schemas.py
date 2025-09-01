"""
Data schemas for Web Content Extractor Agent
数据模式定义：核心数据结构和验证逻辑
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json

class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"

class InputType(str, Enum):
    """输入类型枚举"""
    TEXT = "text"
    WORD_DOCUMENT = "word_document"
    EXCEL_DOCUMENT = "excel_document"
    URL_LIST = "url_list"

@dataclass
class URLInfo:
    """
    URL信息数据结构
    用于存储从输入中提取的URL信息
    """
    url: str
    source: str = "unknown"
    index: int = 0
    context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理：URL规范化"""
        self.url = self._normalize_url(self.url)
    
    def _normalize_url(self, url: str) -> str:
        """URL规范化处理"""
        url = url.strip()
        
        # 确保URL有协议前缀
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                url = f'https://{url}'
            elif self._is_valid_domain(url):
                url = f'https://{url}'
        
        return url
    
    def _is_valid_domain(self, url: str) -> bool:
        """简单的域名格式验证"""
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        return bool(re.match(pattern, url.split('/')[0]))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "url": self.url,
            "source": self.source,
            "index": self.index,
            "context": self.context,
            "metadata": self.metadata
        }

@dataclass
class ExtractionResult:
    """
    提取结果数据结构
    存储单个URL的处理结果
    """
    url: str
    status: ProcessingStatus = ProcessingStatus.PENDING
    title: Optional[str] = None
    content: Optional[str] = None
    word_count: Optional[int] = None
    source: str = "unknown"
    index: int = 0
    context: str = ""
    error_message: Optional[str] = None
    processing_time_ms: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化后处理：计算字数"""
        if self.content and self.word_count is None:
            # 简单字数统计（中英文混合）
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', self.content))
            english_words = len(re.findall(r'\b[a-zA-Z]+\b', self.content))
            self.word_count = chinese_chars + english_words
    
    def is_successful(self) -> bool:
        """判断是否处理成功"""
        return self.status == ProcessingStatus.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "url": self.url,
            "status": self.status.value,
            "title": self.title,
            "content": self.content,
            "word_count": self.word_count,
            "source": self.source,
            "index": self.index,
            "context": self.context,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.metadata
        }

@dataclass
class ProcessingSummary:
    """
    处理摘要数据结构
    存储整体处理统计信息
    """
    total_urls: int = 0
    successful_count: int = 0
    failed_count: int = 0
    success_rate: float = 0.0
    total_processing_time_ms: int = 0
    average_processing_time_ms: float = 0.0
    total_words_extracted: int = 0
    average_words_per_page: float = 0.0
    
    def calculate_from_results(self, results: List[ExtractionResult]):
        """从结果列表计算统计信息"""
        self.total_urls = len(results)
        successful_results = [r for r in results if r.is_successful()]
        self.successful_count = len(successful_results)
        self.failed_count = self.total_urls - self.successful_count
        
        if self.total_urls > 0:
            self.success_rate = round((self.successful_count / self.total_urls) * 100, 2)
        
        # 计算处理时间统计
        valid_times = [r.processing_time_ms for r in results if r.processing_time_ms is not None]
        if valid_times:
            self.total_processing_time_ms = sum(valid_times)
            self.average_processing_time_ms = round(sum(valid_times) / len(valid_times), 2)
        
        # 计算字数统计
        if successful_results:
            word_counts = [r.word_count for r in successful_results if r.word_count is not None]
            if word_counts:
                self.total_words_extracted = sum(word_counts)
                self.average_words_per_page = round(sum(word_counts) / len(word_counts), 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_urls": self.total_urls,
            "successful_count": self.successful_count,
            "failed_count": self.failed_count,
            "success_rate": self.success_rate,
            "total_processing_time_ms": self.total_processing_time_ms,
            "average_processing_time_ms": self.average_processing_time_ms,
            "total_words_extracted": self.total_words_extracted,
            "average_words_per_page": self.average_words_per_page
        }

@dataclass
class ExtractionOutput:
    """
    最终输出数据结构
    标准化的JSON输出格式
    """
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "unknown"
    input_type: InputType = InputType.TEXT
    summary: ProcessingSummary = field(default_factory=ProcessingSummary)
    results: List[ExtractionResult] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_result(self, result: ExtractionResult):
        """添加处理结果"""
        self.results.append(result)
        self._update_summary()
    
    def add_results(self, results: List[ExtractionResult]):
        """批量添加处理结果"""
        self.results.extend(results)
        self._update_summary()
    
    def _update_summary(self):
        """更新摘要统计信息"""
        self.summary.calculate_from_results(self.results)
        
        # 更新错误列表
        self.errors = []
        for result in self.results:
            if not result.is_successful() and result.error_message:
                self.errors.append({
                    "url": result.url,
                    "source": result.source,
                    "error_message": result.error_message,
                    "failed_at": result.timestamp.isoformat() if result.timestamp else None
                })
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于JSON输出）"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "input_type": self.input_type.value,
            "processing_info": self.summary.to_dict(),
            "results": [r.to_dict() for r in self.results if r.is_successful()],
            "errors": self.errors,
            "metadata": {
                "agent": "web_content_extractor",
                "version": "1.0.0",
                "total_results": len(self.results),
                **self.metadata
            }
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

# 工具函数
def validate_url(url: str) -> bool:
    """
    验证URL格式的有效性
    
    Args:
        url: 待验证的URL
        
    Returns:
        bool: 是否有效
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    
    # 基本格式检查
    url_pattern = re.compile(
        r'^https?://'  # 协议
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
        r'(?::\d+)?'  # 端口
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def create_url_info_from_dict(data: Dict[str, Any]) -> URLInfo:
    """
    从字典创建URLInfo对象
    
    Args:
        data: 包含URL信息的字典
        
    Returns:
        URLInfo: URL信息对象
    """
    return URLInfo(
        url=data.get("url", ""),
        source=data.get("source", "unknown"),
        index=data.get("index", 0),
        context=data.get("context", ""),
        metadata=data.get("metadata", {})
    )

def create_extraction_result_from_dict(data: Dict[str, Any]) -> ExtractionResult:
    """
    从字典创建ExtractionResult对象
    
    Args:
        data: 包含提取结果的字典
        
    Returns:
        ExtractionResult: 提取结果对象
    """
    # 处理时间戳
    timestamp = data.get("timestamp")
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            timestamp = datetime.now()
    elif not isinstance(timestamp, datetime):
        timestamp = datetime.now()
    
    return ExtractionResult(
        url=data.get("url", ""),
        status=ProcessingStatus(data.get("status", ProcessingStatus.PENDING.value)),
        title=data.get("title"),
        content=data.get("content"),
        word_count=data.get("word_count"),
        source=data.get("source", "unknown"),
        index=data.get("index", 0),
        context=data.get("context", ""),
        error_message=data.get("error_message"),
        processing_time_ms=data.get("processing_time_ms"),
        timestamp=timestamp,
        metadata=data.get("metadata", {})
    )
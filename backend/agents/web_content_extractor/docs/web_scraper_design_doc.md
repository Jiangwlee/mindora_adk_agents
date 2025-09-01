# 智能网页信息整理 Agent 项目概要设计文档

## 1. 项目概要

本项目基于 Google Agent Development Kit (ADK) 构建一个智能网页信息整理 Agent，支持用户通过自然语言对话、上传 Word 或 Excel 文件等方式提供输入，Agent 自动提取其中的 URL，访问网页内容，提取网页标题与正文信息，并以结构化 JSON 格式输出结果。

**主要特性：**
- 支持多种输入格式（自然语言、Word、Excel文档）
- 智能网页内容提取，输出 Markdown 格式正文
- 多轮对话支持，可追加 URL 或合并历史结果
- 实时进度反馈，用户体验友好
- 流式处理架构，高效处理大批量 URL

**典型应用场景：**
- 从标讯网站自动提取投标信息
- 研究人员整理文献链接内容
- 信息收集与结构化处理

## 2. 系统设计

### 2.1 Agent 架构

系统采用 ADK 的 3-Agent 流式处理架构：

**InputProcessorAgent (单一Agent)**
- 文档解析 (pandoc + 自定义工具)
- URL提取 (正则表达式)
- 流式输出 URLInfo

**WebCrawlerAgent (ParallelAgent)**
- 并发处理多个URL
- crawl4ai集成 (智能内容提取)
- 实时进度事件
- 流式输出 PageResult

**OutputFormatterAgent (单一Agent)**
- JSON格式化
- 错误汇总报告
- 多轮对话状态管理
- 结果合并功能

**架构优势：**
- **流式处理**：边解析边处理，无需等待全部URL提取完成
- **并发优化**：WebCrawlerAgent 使用 ParallelAgent 并行处理URL
- **事件驱动**：利用 ADK 事件系统提供实时进度反馈
- **状态管理**：支持多轮对话的URL追加和结果合并

### 2.2 数据流设计

**URLInfo数据结构：**
- url: 网页链接
- source: 来源文件名或"自然语言输入"
- metadata: 附加元数据

**PageResult数据结构：**
- url_info: URLInfo对象
- title: 网页标题
- content: Markdown格式正文
- status: 处理状态 ("success" | "error")
- error_msg: 错误信息（如有）
- word_count: 内容字数统计
- timestamp: 处理时间戳

### 2.3 工具设计

| Agent | 工具名称 | 类型 | 功能说明 | 选择理由 |
|-------|---------|------|----------|----------|
| **InputProcessorAgent** | `PandocConverter` | Function tool | Word文档→Markdown转换 | pandoc对Word支持完善，功能强大 |
| | `ExcelProcessor` | Function tool | Excel→Markdown，保持表格结构 | 使用pandas.read_excel()读取，DataFrame.to_markdown()转换，成熟稳定 |
| | `URLExtractor` | Function tool | 正则表达式提取URL | 简单文本处理，无需复杂工具 |
| **WebCrawlerAgent** | `Crawl4AIWrapper` | Function tool | 网页内容→Markdown提取 | 智能内容提取，底层集成Playwright |
| | `ProgressReporter` | Function tool | 实时进度事件发送 | 与ADK事件系统集成 |
| **OutputFormatterAgent** | `JSONFormatter` | Function tool | 结果结构化为JSON | 简单数据转换 |
| | `ErrorReporter` | Function tool | 失败URL汇总报告 | 用户友好的错误提示 |
| | `ResultMerger` | Function tool | 多轮对话结果合并 | 支持历史结果整合 |

### 2.4 crawl4ai 集成方案

**选择理由：**
- **智能内容提取**：自动识别网页主要内容区域
- **Markdown输出**：结构化文本格式，便于后续LLM处理  
- **Playwright集成**：底层支持动态网页渲染
- **简化开发**：无需手动DOM解析和内容清理

crawl4ai 将作为 Function tool 集成到 WebCrawlerAgent 中，负责将网页内容转换为 Markdown 格式。

### 2.5 实时进度与事件处理

利用 ADK 的事件驱动架构实现实时进度反馈。相关文档：[Events - Agent Development Kit](https://google.github.io/adk-docs/events/)

**进度事件类型：**
- **开始处理**：`正在处理第 3/10 个URL: example.com`
- **处理成功**：`✅ 已完成: example.com (1200字)`
- **处理失败**：`❌ 失败: badurl.com (连接超时)`

WebCrawlerAgent 使用 ADK 的 ParallelAgent，每个 URL 处理过程中发送 partial 和 final 事件，前端可以实时接收进度更新。

### 2.6 多轮对话支持

**对话场景：**
1. **URL追加**：用户在后续轮次中提供额外URL
2. **结果合并**：将历史处理结果整合为统一JSON列表

**状态管理：**
利用 ADK 内置的会话状态管理，相关文档：[Sessions - Agent Development Kit](https://google.github.io/adk-docs/sessions/)
- 每轮对话结果存储在会话状态中
- 支持跨轮次的数据引用和合并
- 状态数据包括已处理URL列表、历史结果和会话轮次记录

## 3. 输入输出格式

### 3.1 支持的输入格式

**自然语言输入：**
- 用户直接在对话框中粘贴URL
- 支持包含多个URL的文本段落

**Word文档 (.docx)：**
- 支持正文、表格、脚注中的URL
- 使用 pandoc 转换为 Markdown 后提取

**Excel文档 (.xlsx)：**
- 支持多工作表处理
- 使用 pandas.read_excel() 读取所有sheet
- 通过 DataFrame.to_markdown() 保持表格结构转换
- 在转换后的Markdown文本中提取URL

### 3.2 输出JSON格式

最终输出采用结构化 JSON 格式，包含处理统计、成功结果和错误报告：

**主要字段：**
- timestamp: 处理时间戳
- source: 输入来源（文件名或"自然语言输入"）
- total_urls: 总URL数量
- successful/failed: 成功/失败计数
- results: 成功处理的页面结果数组
- errors: 失败URL的错误信息数组  
- statistics: 处理统计信息（耗时、平均长度、成功率等）

每个结果项包含 url、title、content（Markdown格式）、处理状态和时间戳等信息。

## 4. 错误处理策略

### 4.1 错误分类与处理

| 错误类型 | 处理策略 | 用户反馈 |
|---------|---------|---------|
| 网络连接失败 | 跳过该URL，记录错误 | `❌ 连接失败: timeout` |
| HTTP 4xx/5xx | 跳过该URL，记录状态码 | `❌ 访问失败: 404 Not Found` |
| 文档解析失败 | 提示用户，停止处理 | `文档格式不支持或已损坏` |
| 内容提取为空 | 标记为成功但内容为空 | `⚠️ 页面内容为空` |
| JavaScript渲染失败 | 降级为静态抓取 | 自动处理，对用户透明 |

### 4.2 容错机制

- **单点失败隔离**：一个URL失败不影响其他URL处理
- **优雅降级**：动态页面渲染失败时尝试静态抓取
- **用户友好提示**：错误信息简洁明了，避免技术术语
- **批量报告**：处理完成后统一汇报所有失败URL

## 5. 性能与扩展性

### 5.1 并发控制

**ParallelAgent配置：**
- 默认并发数：10个URL同时处理
- 自动速率限制：避免对同一域名过度请求
- 资源管理：合理控制crawl4ai的浏览器实例数量

ADK ParallelAgent 相关文档：[Parallel Agent - Agent Development Kit](https://google.github.io/adk-docs/agents/parallel/)

### 5.2 优化建议

**当前阶段（MVP）：**
- 聚焦核心功能实现
- 简单错误处理
- 基础进度反馈

**未来扩展：**
- **智能摘要**：集成LLM对长文本进行摘要
- **内容分类**：自动识别页面类型（新闻、论文、商品等）
- **结构化提取**：针对特定网站类型的专门提取规则
- **缓存机制**：避免重复抓取相同URL
- **定时任务**：支持周期性内容更新检测

## 6. 项目结构与开发参考

### 6.1 ADK项目结构

项目目录结构参考：[Academic Research Agent 示例](https://github.com/google/adk-samples/tree/main/python/agents/academic-research)

**核心文件：**
- `agent.py`: 主Agent定义，包含SequentialAgent组装
- `tools.py`: 自定义Function tools定义
- `requirements.txt`: Python依赖声明
- `README.md`: 项目说明文档

**遵循ADK规范：**
- Agent命名约定和类型定义
- Tool函数签名和文档格式
- 错误处理和日志记录标准

## 7. ADK 参考文档与资料

### 7.1 核心概念文档
- **ADK 概述**: https://google.github.io/adk-docs/
- **Agents 概念**: https://google.github.io/adk-docs/agents/
- **工具定义**: https://google.github.io/adk-docs/tools/
- **会话管理**: https://google.github.io/adk-docs/sessions/
- **事件机制**: https://google.github.io/adk-docs/events/
- **Sequential Agent**: https://google.github.io/adk-docs/agents/sequential/
- **Parallel Agent**: https://google.github.io/adk-docs/agents/parallel/

### 7.2 开发参考
- **ADK Python SDK**: https://github.com/google/adk-python
- **ADK Samples**: https://github.com/google/adk-samples
- **Academic Research Agent**: https://github.com/google/adk-samples/tree/main/python/agents/academic-research
- **Python 快速开始**: https://google.github.io/adk-docs/get-started/quickstart/
- **Streaming 流式处理**: https://google.github.io/adk-docs/streaming/

### 7.3 技术集成文档  
- **crawl4ai 项目**: https://github.com/unclecode/crawl4ai
- **pandoc 手册**: https://pandoc.org/MANUAL.html
- **Gemini API 文档**: https://ai.google.dev/docs
# AI Agent App Platform 设计方案

## 概述

本文档描述了将现有的Mindora ADK Agents调试工具改造为AI Agent App Platform的完整设计方案。目标是提供一个开箱即用的AI应用平台，支持不同类型的智能体应用。

## 需求分析

### 业务目标
- 提供一组开箱即用的AI应用
- 目标用户群体是企业用户
- 初期不用考虑复杂的用户管理
- 支持两种类型的应用：Chatbot和Custom

### 功能需求
- **平台主页**: 展示所有可用AI应用的卡片式界面
- **Chatbot类型**: 统一的聊天界面，类似ChatGPT的交互体验
- **Custom类型**: 可定制的应用页面，支持不同的业务需求
- **向后兼容**: 保持现有ADK调试工具的完整性

### 技术约束
- 仅支持Web端，无需移动端适配
- 与现有Google ADK agent系统集成
- 保持现有技术栈：Angular 19 + FastAPI + Google ADK

## 系统架构设计

### 路由架构

```
/                      # 平台主页
/app/chatbot/{name}    # Chatbot类型应用
/app/custom/{name}     # Custom类型应用
/adk-debug            # 现有调试工具
```

### 组件架构

```
Frontend Components
├── Platform Components
│   ├── HomePageComponent          # 平台主页
│   ├── AppCardComponent           # App卡片
│   ├── AppGridComponent           # App网格布局
│   └── SearchFilterComponent      # 搜索筛选
├── Chatbot Components
│   ├── ChatbotPageComponent       # Chatbot页面容器
│   ├── ModernChatComponent        # Next.js风格聊天组件
│   └── ChatSidebarComponent       # 聊天侧边栏
├── Custom Components
│   ├── CustomAppContainerComponent # Custom应用容器
│   └── DynamicLayoutComponent     # 动态布局组件
└── Legacy Components
    └── AppComponent               # 现有调试工具
```

## API设计

### 现有端点（保持不变）

```typescript
GET /list-apps
// 返回: string[] (agent名称列表)
// 保持向后兼容性
```

### 新增平台端点

```typescript
GET /platform/apps
// 返回: AppInfo[] (完整的应用信息)

GET /platform/apps/{name}
// 返回: AppInfo (单个应用详细信息)

POST /platform/apps/{name}/launch
// 启动应用会话
// 返回: SessionInfo
```

### 数据模型

```typescript
interface AppInfo {
  name: string;
  description: string;
  app_type: 'chatbot' | 'custom';
  capabilities: string[];
  ui_config: UiConfig;
  created_at: string;
}

interface UiConfig {
  theme: 'modern' | 'classic';
  layout: 'chat' | 'dashboard' | 'custom';
  features: string[];
  colors?: {
    primary: string;
    secondary: string;
  };
}

interface SessionInfo {
  session_id: string;
  app_name: string;
  user_id: string;
  created_at: string;
  status: 'active' | 'inactive';
}
```

## 后端设计

### Agent配置扩展

现有的agent配置文件需要扩展，添加`app_type`字段：

```json
{
  "name": "ADK Demo",
  "description": "ADK Demo，可以回答关于纽约的天气问题",
  "app_type": "chatbot",
  "capabilities": ["天气查询", "问答", "对话"],
  "ui_config": {
    "theme": "modern",
    "layout": "chat",
    "features": ["voice", "file_upload"]
  },
  "created_at": "2025-08-04T10:27:43.184368"
}
```

### 后端端点实现

1. **保持现有端点**: `list_apps()` 方法保持不变
2. **新增平台端点**: 
   - `get_platform_apps()` - 返回完整的App信息
   - `get_app_by_name(name)` - 返回单个App详细信息
   - `launch_app_session(name)` - 启动应用会话

## 前端设计

### 路由配置

```typescript
const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'app/chatbot/:name', component: ChatbotPageComponent },
  { path: 'app/custom/:name', component: CustomPageComponent },
  { path: 'adk-debug', component: AppComponent },
];
```

### 平台主页设计

- **卡片网格布局**: 响应式网格展示所有可用应用
- **应用分类**: 按类型分组显示（Chatbot/Custom）
- **搜索筛选**: 支持按名称、描述、功能筛选
- **应用卡片**: 显示应用名称、描述、类型、功能特性

### Chatbot应用页面

- **统一界面**: Next.js风格的现代化聊天界面
- **功能复用**: 复用现有的chat组件功能
- **多模态支持**: 支持文本、音频、视频、文件交互
- **会话管理**: 独立的会话历史和状态管理

### Custom应用页面

- **容器组件**: 提供通用的应用容器框架
- **动态布局**: 根据配置动态渲染页面结构
- **扩展接口**: 预留未来的定制化功能接口

## 数据流设计

### 应用加载流程

1. 用户访问平台主页 `/`
2. 前端调用 `/platform/apps` 获取应用列表
3. 根据应用类型渲染不同的卡片样式
4. 用户点击应用卡片，跳转到对应的应用页面
5. 应用页面根据应用类型加载对应的组件和配置

### 会话管理流程

1. 用户进入应用页面
2. 调用 `/platform/apps/{name}/launch` 启动会话
3. 建立WebSocket连接或SSE流
4. 开始与ADK agent的交互
5. 管理会话状态和历史记录

## 实施计划

### 第一阶段：基础架构（2周）

**后端任务**
1. 扩展agent配置模型，添加`app_type`字段
2. 实现新的平台API端点
3. 更新现有agent的配置文件
4. 测试向后兼容性

**前端任务**
1. 创建新的路由结构
2. 将现有主页移至 `/adk-debug`
3. 创建基础的平台主页组件
4. 实现App卡片和网格布局

### 第二阶段：平台功能（1周）

**前端任务**
1. 完善平台主页的搜索筛选功能
2. 实现应用分类和分组显示
3. 添加响应式设计
4. 集成新的平台API

**后端任务**
1. 优化平台API的性能
2. 添加错误处理和日志
3. 实现应用会话管理

### 第三阶段：Chatbot应用（2周）

**前端任务**
1. 创建Next.js风格的聊天组件
2. 实现统一的Chatbot页面
3. 复用现有的chat功能
4. 优化用户体验和界面设计

**后端任务**
1. 集成Chatbot应用的会话管理
2. 优化WebSocket/SSE通信
3. 添加性能监控

### 第四阶段：Custom应用架构（1周）

**前端任务**
1. 创建Custom应用容器组件
2. 实现动态布局系统
3. 设计配置化UI框架
4. 预留扩展接口

**后端任务**
1. 设计Custom应用的支持架构
2. 实现配置驱动的页面渲染
3. 准备未来扩展点

## 风险评估

### 技术风险

1. **向后兼容性风险**
   - 风险：现有功能被破坏
   - 缓解：渐进式改造，保持现有端点不变

2. **性能风险**
   - 风险：新功能影响现有性能
   - 缓解：性能测试和优化，代码分割

3. **架构风险**
   - 风险：Custom应用架构过度设计
   - 缓解：YAGNI原则，按需实现

### 业务风险

1. **用户体验风险**
   - 风险：新界面学习成本
   - 缓解：保持交互一致性，提供引导

2. **维护风险**
   - 风险：代码复杂度增加
   - 缓解：良好的代码组织和文档

## 技术选型

### 前端技术栈
- **框架**: Angular 19（现有）
- **UI组件**: Angular Material（现有）
- **样式**: SCSS（现有）
- **状态管理**: RxJS（现有）
- **图表**: Viz.js（现有）

### 后端技术栈
- **框架**: FastAPI（现有）
- **ADK集成**: Google ADK（现有）
- **数据序列化**: Pydantic（现有）
- **异步处理**: asyncio（现有）

### 开发工具
- **构建工具**: Angular CLI（现有）
- **包管理**: npm + uv（现有）
- **测试框架**: Karma/Jasmine（现有）
- **API文档**: FastAPI自动生成（现有）

## 监控和运维

### 性能监控
- 前端性能指标监控
- API响应时间监控
- WebSocket连接状态监控
- 内存使用监控

### 错误监控
- 前端错误收集
- 后端异常处理
- API错误日志
- 用户行为追踪

### 部署策略
- 渐进式部署
- 蓝绿部署
- 回滚机制
- 负载均衡

## 总结

本设计方案提供了一个完整的AI Agent App Platform架构，通过渐进式改造现有系统，实现以下目标：

1. **功能完整**: 提供开箱即用的AI应用平台
2. **技术先进**: 使用现代化的前端设计和架构
3. **向后兼容**: 保持现有功能的完整性
4. **可扩展性**: 支持未来的功能扩展和定制化需求
5. **用户体验**: 提供统一且友好的用户界面

该方案通过分阶段实施，可以有效控制风险，确保项目成功交付。
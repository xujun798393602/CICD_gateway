# 代码质量门禁系统架构设计文档

## 1. 业务流程描述

### 1.1 门禁扫描主流程

#### 1.1.1 Push触发流程

```
开发者Push代码 → GitLab触发CI Pipeline → CI Job调用门禁系统API → 门禁系统创建扫描任务 → 并行执行各门禁脚本 → 汇总结果 → 生成报告 → 返回CI Pipeline结果
```

**详细流程：**
1. 开发者将代码推送到指定分支（main、develop、release/*）
2. GitLab CI检测到Push事件，触发Pipeline执行
3. CI Job调用门禁系统触发接口 `POST /api/v1/scans/trigger`
4. 门禁系统验证请求参数，创建扫描任务记录（状态：pending）
5. 门禁调度器根据配置加载启用的门禁脚本
6. 并行执行各门禁脚本（代码漏洞扫描、敏感词扫描、硬编码扫描、代码规范检查）
7. 各脚本执行完成后，将结果上报到门禁系统
8. 门禁系统汇总所有脚本结果，判定门禁是否通过
9. 生成HTML报告并部署到Web服务器
10. 返回扫描结果给CI Pipeline，决定是否允许后续流程

#### 1.1.2 MR触发流程

```
创建/更新MR → GitLab触发CI Pipeline → CI Job调用门禁系统API → 门禁系统创建扫描任务 → 并行执行各门禁脚本 → 汇总结果 → 生成报告 → 发送通知 → 更新MR状态
```

**详细流程：**
1. 开发者创建或更新Merge Request
2. GitLab CI检测到MR事件，触发Pipeline执行
3. CI Job调用门禁系统触发接口，指定trigger_type为merge_request
4. 门禁系统创建扫描任务，记录MR相关信息
5. 执行门禁扫描流程（同Push流程）
6. 扫描完成后，通过GitLab API在MR上添加评论
7. 如果门禁失败，阻止MR合并
8. 发送邮件通知相关责任人

#### 1.1.3 定时触发流程

```
Cron调度器触发 → 门禁系统创建扫描任务 → 执行全量扫描 → 生成报告 → 发送通知
```

**详细流程：**
1. 门禁系统的定时调度器根据Cron表达式触发扫描
2. 扫描指定分支的最新代码
3. 执行全量门禁扫描
4. 生成扫描报告
5. 发送扫描结果通知

### 1.2 门禁脚本执行流程

```
接收扫描任务 → 加载项目配置 → 合并全局配置 → 执行脚本 → 收集输出 → 解析结果 → 上报状态
```

**详细流程：**
1. 门禁脚本通过环境变量接收扫描上下文（项目ID、扫描ID、代码路径等）
2. 加载项目级配置文件 `.quality-gate/config.yml`
3. 与全局配置合并，项目级配置优先级更高
4. 执行具体的扫描逻辑（调用第三方工具或自定义扫描逻辑）
5. 收集脚本标准输出和错误输出
6. 解析输出为标准JSON格式
7. 通过API上报扫描结果
8. 退出码表示执行状态（0成功通过、1发现问题、2执行错误、3超时）

### 1.3 报告生成流程

```
接收生成请求 → 查询扫描数据 → 汇总统计 → 生成HTML → 部署到Web服务器 → 返回访问URL
```

**详细流程：**
1. 所有门禁脚本执行完成后，触发报告生成
2. 查询扫描任务和扫描结果数据
3. 查询问题详情数据
4. 汇总统计数据（按严重级别、门禁类型、文件路径等维度）
5. 使用模板引擎生成HTML报告
6. 将HTML文件部署到Web服务器（Nginx）
7. 更新扫描任务记录中的report_url字段
8. 返回报告访问URL

### 1.4 通知发送流程

```
扫描完成 → 判断通知条件 → 加载通知配置 → 生成通知内容 → 发送通知 → 记录发送结果
```

**详细流程：**
1. 扫描任务完成后，检查是否需要发送通知
2. 根据配置判断通知条件（失败时通知、成功时通知等）
3. 加载项目通知配置（邮件接收人、GitLab评论格式等）
4. 生成通知内容（邮件模板、MR评论格式）
5. 发送邮件通知（通过SMTP服务）
6. 发送GitLab MR评论（通过GitLab API）
7. 记录通知发送日志（成功/失败、重试次数等）

## 2. 系统架构图

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              代码质量门禁系统整体架构                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              CI/CD 流水线层                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ GitLab CI   │  │ Push 触发   │  │  MR 触发    │  │ 定时触发    │        │
│  │ Pipeline    │  │             │  │             │  │             │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API 网关层                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Nginx 反向代理                               │   │
│  │                    (负载均衡、SSL终结、路由)                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              应用服务层                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 扫描管理    │  │ 报告服务    │  │ 通知服务    │  │ 配置服务    │        │
│  │ Service     │  │ Service     │  │ Service     │  │ Service     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              核心业务层                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 扫描执行    │  │ 报告生成    │  │ 通知发送    │  │ 配置管理    │        │
│  │ 模块        │  │ 模块        │  │ 模块        │  │ 模块        │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              门禁脚本层                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 代码漏洞    │  │ 敏感词      │  │ 硬编码      │  │ 代码规范    │        │
│  │ 扫描脚本    │  │ 扫描脚本    │  │ 扫描脚本    │  │ 检查脚本    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据存储层                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ MySQL       │  │ Redis       │  │ 文件存储    │  │ GitLab      │        │
│  │ 数据库      │  │ 缓存        │  │ (Nginx)     │  │ API         │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块依赖关系

```
┌─────────────────┐
│  CI/CD集成模块   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│  扫描执行模块   │─────▶│  配置管理模块   │
└────────┬────────┘      └─────────────────┘
         │
         ├──────────────────┬──────────────────┐
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  报告生成模块   │ │  通知服务模块   │ │  门禁脚本层     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                  │
         ▼                  ▼
┌─────────────────┐ ┌─────────────────┐
│  文件存储       │ │  外部服务       │
│  (Nginx)        │ │  (SMTP/GitLab)  │
└─────────────────┘ └─────────────────┘
```

## 3. 模块划分与职责边界

### 3.1 扫描执行模块（Scan Execution Module）

**职责：**
- 接收扫描触发请求，创建扫描任务
- 调度和管理门禁脚本执行
- 收集和汇总扫描结果
- 管理扫描任务生命周期

**边界：**
- 与CI/CD系统交互，接收触发请求
- 与门禁脚本交互，执行扫描任务
- 与数据库交互，存储扫描任务和结果

### 3.2 报告生成模块（Report Generation Module）

**职责：**
- 查询扫描结果数据
- 生成HTML格式的扫描报告
- 部署报告到Web服务器
- 提供报告访问和查询接口

**边界：**
- 与数据库交互，查询扫描数据
- 与文件存储交互，部署报告文件
- 提供HTTP接口供外部访问报告

### 3.3 配置管理模块（Configuration Management Module）

**职责：**
- 管理全局和项目级门禁配置
- 提供配置查询和更新接口
- 合并多级配置（项目级 > 全局级 > 默认值）
- 管理门禁脚本注册和元数据

**边界：**
- 与数据库交互，存储配置数据
- 与扫描执行模块交互，提供配置信息
- 提供API接口供外部管理配置

### 3.4 通知服务模块（Notification Service Module）

**职责：**
- 根据扫描结果判断是否需要发送通知
- 生成通知内容（邮件、MR评论）
- 发送通知到指定渠道（SMTP、GitLab API）
- 记录通知发送历史

**边界：**
- 与扫描执行模块交互，获取扫描结果
- 与外部服务交互（SMTP服务器、GitLab API）
- 与数据库交互，存储通知记录

### 3.5 CI/CD集成模块（CI/CD Integration Module）

**职责：**
- 提供GitLab CI/CD集成接口
- 处理CI Pipeline的触发和结果返回
- 管理CI/CD相关的配置和凭证
- 提供CI/CD集成示例和文档

**边界：**
- 与GitLab CI/CD系统交互
- 与扫描执行模块交互，触发扫描任务
- 提供标准化的CI/CD集成接口

## 4. 组件技术选型

### 4.1 后端技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| 编程语言 | Python 3.10+ | 生态丰富、开发效率高、团队熟悉 |
| Web框架 | FastAPI | 高性能、自动API文档、类型提示支持 |
| ORM | SQLAlchemy 2.0 | 成熟稳定、支持异步、迁移工具完善 |
| 任务调度 | APScheduler | 轻量级、支持Cron表达式、易于集成 |
| HTTP客户端 | httpx | 异步支持、性能优秀 |

### 4.2 门禁脚本技术选型

| 技术 | 选型 | 理由 |
|------|------|------|
| 门禁脚本 | Shell脚本（主选） | 兼容性好、执行效率高、CI/CD友好、维护简单 |
| 复杂分析 | Python脚本（备选） | 功能强大、跨平台、易于扩展 |

### 4.3 报告生成技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| 模板引擎 | Jinja2 | Python生态标准、语法简洁、功能强大 |
| 前端组件 | Bootstrap + DataTables | 响应式布局、排序筛选分页 |
| 报告部署 | Nginx静态文件服务 | 性能优秀、配置简单、安全可靠 |

### 4.4 通知服务技术选型

| 渠道 | 选型 | 理由 |
|------|------|------|
| 邮件 | Python smtplib | 标准库支持、功能完善 |
| GitLab | GitLab API (httpx) | 原生集成、支持Markdown |
| 未来扩展 | 企业微信/钉钉 | 插件化架构支持 |

### 4.5 存储方案

| 组件 | 选型 | 理由 |
|------|------|------|
| 关系型数据库 | MySQL 8.0 | 成熟稳定、性能优秀、运维简单 |
| 缓存 | Redis (aioredis) | 高性能、异步支持、数据结构丰富 |
| 文件存储 | 本地文件系统 + Nginx | 简单高效、访问方便、成本低廉 |

## 5. 接口契约

### 5.1 数据模型定义

```python
"""数据模型定义 - 使用 Pydantic 进行数据验证"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TriggerType(str, Enum):
    PUSH = "push"
    MERGE_REQUEST = "merge_request"
    SCHEDULE = "schedule"
    MANUAL = "manual"


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class GateResult(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanTriggerRequest(BaseModel):
    """扫描触发请求"""
    project_id: str
    repository_url: str
    branch: str
    commit_sha: str
    trigger_type: TriggerType
    merge_request_id: Optional[int] = None
    scanners: Optional[List[str]] = None
    callback_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ScanTask(BaseModel):
    """扫描任务"""
    scan_id: str
    project_id: str
    project_name: str
    status: ScanStatus
    gate_result: Optional[GateResult] = None
    total_gates: int = 0
    passed_gates: int = 0
    failed_gates: int = 0
    skipped_gates: int = 0
    total_issues: int = 0
    critical_issues: int = 0
    high_issues: int = 0
    medium_issues: int = 0
    low_issues: int = 0
    report_url: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None


class ScanResultRequest(BaseModel):
    """扫描结果上报请求"""
    scanner_id: str
    scanner_version: str
    status: str  # success/failed/timeout/skipped
    started_at: datetime
    completed_at: datetime
    duration_ms: int
    summary: Dict[str, int]
    issues: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None


class ScanStatusResponse(BaseModel):
    """扫描状态响应"""
    scan_id: str
    project_id: str
    branch: str
    commit_sha: str
    status: ScanStatus
    gate_result: Optional[GateResult] = None
    gate_passed: Optional[bool] = None
    scanners_status: List[Dict[str, Any]] = []
    summary: Dict[str, Any] = {}
    report_url: Optional[str] = None


class Report(BaseModel):
    """报告信息"""
    report_id: str
    scan_id: str
    project_id: str
    report_type: str
    format: str
    status: str
    view_url: Optional[str] = None
    download_url: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class GateConfig(BaseModel):
    """门禁配置"""
    project_id: str
    version: str = "1.0"
    gates: Dict[str, Any] = {}
    notifications: Dict[str, Any] = {}
    settings: Dict[str, Any] = {}


class Scanner(BaseModel):
    """扫描器信息"""
    scanner_id: str
    name: str
    description: str
    version: str
    category: str
    entry_point: str
    timeout: int = 600
    status: str = "active"
    supported_languages: List[str] = []
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None


class NotificationRequest(BaseModel):
    """通知请求"""
    scan_id: str
    channels: Optional[List[str]] = None
    recipients: Optional[Dict[str, List[str]]] = None
    template: str = "default"
    custom_message: Optional[str] = None
    force: bool = False


class NotificationResult(BaseModel):
    """通知结果"""
    notification_id: str
    scan_id: str
    channels: List[Dict[str, Any]] = []


class HealthStatus(BaseModel):
    """健康状态"""
    status: str  # healthy/degraded/unhealthy
    version: str
    components: Dict[str, str] = {}
```

### 5.2 扫描执行模块接口

```python
"""扫描执行模块接口"""
from abc import ABC, abstractmethod
from typing import Optional


class ScanExecutionService(ABC):
    """扫描执行服务接口"""

    @abstractmethod
    async def trigger_scan(self, request: ScanTriggerRequest) -> ScanTask:
        """触发门禁扫描"""
        ...

    @abstractmethod
    async def get_scan_status(
        self, scan_id: str, include_details: bool = False
    ) -> ScanStatusResponse:
        """查询扫描状态"""
        ...

    @abstractmethod
    async def report_scan_result(
        self, scan_id: str, result: ScanResultRequest
    ) -> Dict[str, Any]:
        """上报扫描结果"""
        ...

    @abstractmethod
    async def cancel_scan(self, scan_id: str) -> Dict[str, Any]:
        """取消扫描任务"""
        ...

    @abstractmethod
    async def retry_scan(self, scan_id: str) -> ScanTask:
        """重试扫描任务"""
        ...
```

### 5.3 报告生成模块接口

```python
"""报告生成模块接口"""
from abc import ABC, abstractmethod
from typing import List, Optional


class ReportGenerationService(ABC):
    """报告生成服务接口"""

    @abstractmethod
    async def generate_report(
        self, scan_id: str, report_type: str = "full", format: str = "html"
    ) -> Report:
        """生成扫描报告"""
        ...

    @abstractmethod
    async def get_report(
        self, report_id: str, include_content: bool = False
    ) -> Report:
        """查询报告信息"""
        ...

    @abstractmethod
    async def list_reports(
        self, project_id: str, page: int = 1, page_size: int = 20, **filters
    ) -> Dict[str, Any]:
        """查询报告列表"""
        ...

    @abstractmethod
    async def delete_report(self, report_id: str) -> Dict[str, Any]:
        """删除报告"""
        ...
```

### 5.4 配置管理模块接口

```python
"""配置管理模块接口"""
from abc import ABC, abstractmethod
from typing import List, Optional


class ConfigurationService(ABC):
    """配置管理服务接口"""

    @abstractmethod
    async def get_config(
        self, project_id: str, merged: bool = True
    ) -> GateConfig:
        """查询项目配置"""
        ...

    @abstractmethod
    async def update_config(
        self, project_id: str, config: GateConfig, comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """更新项目配置"""
        ...

    @abstractmethod
    async def register_scanner(self, scanner: Scanner) -> Scanner:
        """注册门禁脚本"""
        ...

    @abstractmethod
    async def list_scanners(
        self, category: Optional[str] = None, status: Optional[str] = None
    ) -> List[Scanner]:
        """查询扫描器列表"""
        ...
```

### 5.5 通知服务模块接口

```python
"""通知服务模块接口"""
from abc import ABC, abstractmethod
from typing import Dict, Optional


class NotificationService(ABC):
    """通知服务接口"""

    @abstractmethod
    async def send_notification(
        self, request: NotificationRequest
    ) -> NotificationResult:
        """发送通知"""
        ...

    @abstractmethod
    async def get_notification_config(
        self, project_id: str
    ) -> Dict[str, Any]:
        """查询通知配置"""
        ...

    @abstractmethod
    async def update_notification_config(
        self, project_id: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新通知配置"""
        ...
```

### 5.6 CI/CD集成模块接口

```python
"""CI/CD集成模块接口"""
from abc import ABC, abstractmethod
from typing import Optional


class CICDIntegrationService(ABC):
    """CI/CD集成服务接口"""

    @abstractmethod
    async def trigger_scan(
        self, request: ScanTriggerRequest, api_token: str
    ) -> ScanTask:
        """触发门禁扫描（带认证）"""
        ...

    @abstractmethod
    async def get_scan_status(
        self,
        scan_id: str,
        api_token: str,
        wait: bool = False,
        timeout: int = 600,
    ) -> ScanStatusResponse:
        """查询扫描状态（支持等待）"""
        ...

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """健康检查"""
        ...

    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        ...
```

## 6. DFX分析

### 6.1 安全性
- API Token认证机制
- GitLab OAuth2集成
- 敏感信息脱敏显示
- 凭证加密存储
- CI Runner容器隔离

### 6.2 可靠性
- 网络请求自动重试3次
- 报告生成失败JSON降级
- 定时扫描失败自动重试
- 单个门禁失败不影响其他门禁

### 6.3 可测试性
- 模块化设计，便于单元测试
- 接口契约清晰，便于集成测试
- 依赖注入，便于Mock测试

### 6.4 可调试性
- 结构化日志（JSON格式）
- 唯一扫描ID追踪
- 详细错误信息

### 6.5 可运维性
- 健康检查接口
- Prometheus指标接口
- 配置热更新

### 6.6 可扩展性
- 插件化门禁脚本架构
- 配置驱动的行为
- 模块化设计

### 6.7 可复用性
- 共享配置管理模块
- 通用通知服务模块
- 标准化报告生成模块

# API 接口依赖关系文档

## 1. 跨 API 调用顺序依赖

### 1.1 扫描主流程调用链

```
POST /api/v1/scans/trigger          (1) 触发扫描
    │
    ├──▶ POST /api/v1/scans/{scan_id}/results   (2) 各扫描器上报结果（并行）
    │
    ├──▶ POST /api/v1/reports/generate           (3) 生成报告
    │       │
    │       └──▶ GET /api/v1/reports/{report_id} (4) 查询报告状态
    │
    └──▶ POST /api/v1/notifications/send         (5) 发送通知
```

### 1.2 配置查询依赖

```
POST /api/v1/scans/trigger
    │
    └──▶ GET /api/v1/configs/{project_id}        (隐式依赖：系统内部调用)
            │
            └──▶ GET /api/v1/configs/_global      (隐式依赖：合并全局配置)
```

### 1.3 MR评论通知依赖

```
POST /api/v1/notifications/send
    │
    └──▶ GitLab API: POST /api/v4/projects/:id/merge_requests/:mr_id/notes
```

### 1.4 定时扫描依赖

```
Cron Scheduler (内部)
    │
    └──▶ POST /api/v1/scans/trigger              (trigger_type = "schedule")
            │
            └──▶ [同扫描主流程]
```

## 2. API 参数到数据模型字段映射

### 2.1 扫描触发接口 → scan_tasks 表

| API 参数 | 数据模型字段 | 说明 |
|----------|-------------|------|
| project_id | scan_tasks.project_id | 项目ID |
| repository_url | scan_tasks.project_url | 仓库地址 |
| branch | scan_tasks.trigger_ref | 触发引用 |
| commit_sha | scan_tasks.commit_sha | 提交SHA |
| trigger_type | scan_tasks.trigger_type | 触发类型 |
| merge_request_id | - | 仅用于GitLab API调用 |
| metadata.gitlab_user | scan_tasks.trigger_user | 触发用户 |
| - | scan_tasks.scan_id | 系统自动生成 |
| - | scan_tasks.scan_status | 初始值：pending |

### 2.2 扫描结果上报接口 → scan_results 表 + issue_details 表

| API 参数 | 数据模型字段 | 说明 |
|----------|-------------|------|
| scanner_id | scan_results.gate_type | 门禁类型 |
| scanner_version | scan_results.gate_version | 脚本版本 |
| status | scan_results.execution_status | 执行状态 |
| started_at | scan_results.started_at | 开始时间 |
| completed_at | scan_results.completed_at | 完成时间 |
| duration_ms | scan_results.duration_seconds | 毫秒转秒 |
| summary.total_issues | scan_results.total_issues | 问题总数 |
| summary.critical | scan_results.critical_issues | 严重问题数 |
| summary.high | scan_results.high_issues | 高危问题数 |
| summary.medium | scan_results.medium_issues | 中危问题数 |
| summary.low | scan_results.low_issues | 低危问题数 |
| summary.files_scanned | scan_results.scanned_files | 扫描文件数 |
| summary.lines_scanned | scan_results.total_lines | 扫描行数 |
| issues[].id | issue_details.fingerprint | 问题指纹 |
| issues[].severity | issue_details.severity | 严重级别 |
| issues[].category | issue_details.issue_type | 问题类型 |
| issues[].title | issue_details.message | 问题描述 |
| issues[].file_path | issue_details.file_path | 文件路径 |
| issues[].line_number | issue_details.line_number | 行号 |
| issues[].rule_id | issue_details.rule_id | 规则ID |

### 2.3 报告生成接口 → 报告文件

| API 参数 | 数据来源 | 说明 |
|----------|----------|------|
| scan_id | scan_tasks.scan_id | 查询扫描任务 |
| - | scan_results.* | 查询扫描结果 |
| - | issue_details.* | 查询问题详情 |
| report_type | - | 控制报告内容范围 |
| format | - | 控制输出格式 |

### 2.4 通知发送接口 → notification_logs 表

| API 参数 | 数据模型字段 | 说明 |
|----------|-------------|------|
| scan_id | notification_logs.scan_id | 关联扫描任务 |
| channels | notification_logs.notification_type | 通知类型 |
| recipients | notification_logs.recipient | 接收人 |
| - | notification_logs.notification_id | 系统自动生成 |
| - | notification_logs.send_status | 初始值：pending |

### 2.5 配置更新接口 → gate_configs 表

| API 参数 | 数据模型字段 | 说明 |
|----------|-------------|------|
| project_id | gate_configs.project_id | 项目ID |
| config.* | gate_configs.config_data | 配置数据（JSON） |
| comment | - | 记录到审计日志 |
| - | gate_configs.config_id | 系统自动生成 |
| - | gate_configs.updated_by | 当前用户 |

### 2.6 扫描器注册接口 → gate_configs 表

| API 参数 | 数据模型字段 | 说明 |
|----------|-------------|------|
| scanner_id | gate_configs.gate_type | 门禁类型 |
| name | gate_configs.gate_name | 门禁名称 |
| version | gate_configs.script_version | 脚本版本 |
| entry_point | gate_configs.script_path | 脚本路径 |
| timeout | gate_configs.timeout_seconds | 超时时间 |
| default_config | gate_configs.config_data | 默认配置 |

## 3. 接口间数据流转

### 3.1 扫描触发 → 结果上报

```
POST /scans/trigger
    │
    │ 返回 scan_id
    │
    ▼
POST /scans/{scan_id}/results
    │
    │ 使用 scan_id 关联
    │
    ▼
scan_tasks.scan_id = scan_results.scan_id
```

### 3.2 结果上报 → 报告生成

```
POST /scans/{scan_id}/results
    │
    │ 写入 scan_results + issue_details
    │
    ▼
POST /reports/generate
    │
    │ 读取 scan_results + issue_details
    │
    ▼
生成 HTML/JSON 报告文件
```

### 3.3 报告生成 → 通知发送

```
POST /reports/generate
    │
    │ 写入 report_url 到 scan_tasks
    │
    ▼
POST /notifications/send
    │
    │ 读取 scan_tasks 获取 report_url
    │
    ▼
通知内容包含报告链接
```

## 4. 依赖矩阵

| 接口 | 依赖的内部接口 | 依赖的外部服务 |
|------|---------------|---------------|
| POST /scans/trigger | GET /configs/{project_id} | 无 |
| POST /scans/{id}/results | 无 | 无 |
| GET /scans/{id}/status | 无 | 无 |
| POST /reports/generate | 无 | 无 |
| GET /reports/{id} | 无 | 无 |
| GET /reports | 无 | 无 |
| POST /notifications/send | 无 | SMTP, GitLab API |
| GET /configs/{project_id} | 无 | 无 |
| PUT /configs/{project_id} | 无 | 无 |
| POST /scanners/register | 无 | 无 |
| GET /scanners | 无 | 无 |
| GET /health | 无 | DB, Redis, GitLab API |
| GET /metrics | 无 | 无 |

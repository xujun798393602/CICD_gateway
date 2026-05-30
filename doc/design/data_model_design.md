# 数据模型设计：代码质量门禁系统

## 1. 概述

本文档定义代码质量门禁系统的数据模型，包括数据库表结构、全局数据结构和配置文件结构。数据模型支持门禁脚本管理、CI/CD 流程集成、扫描报告生成和通知发送等核心功能。

## 2. ER 图（文本描述）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              代码质量门禁系统 ER 图                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  scan_tasks  │ 1   N │ scan_results │ 1   N │ issue_details│
│   扫描任务    │───────│   扫描结果    │───────│   问题详情    │
└──────────────┘       └──────────────┘       └──────────────┘
       │                      │
       │                      │
       │ N                  N │
       │                      │
       ▼                      ▼
┌──────────────┐       ┌──────────────┐
│notification_ │       │ gate_configs │
│    logs      │       │   门禁配置    │
│   通知记录    │       │              │
└──────────────┘       └──────────────┘

关系说明：
- scan_tasks 1:N scan_results（一个扫描任务包含多个门禁扫描结果）
- scan_results 1:N issue_details（一个扫描结果包含多个问题详情）
- scan_tasks 1:N notification_logs（一个扫描任务可触发多条通知）
- gate_configs 独立管理，通过 gate_type 关联 scan_results
```

## 3. 数据库表设计

### 3.1 扫描任务表（scan_tasks）

记录每次扫描任务的基本信息和执行状态。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 主键ID |
| scan_id | VARCHAR(64) | UNIQUE, NOT NULL | - | 扫描唯一标识（UUID格式） |
| project_id | VARCHAR(128) | NOT NULL | - | GitLab 项目ID |
| project_name | VARCHAR(256) | NOT NULL | - | 项目名称 |
| project_url | VARCHAR(512) | - | - | 项目仓库地址 |
| trigger_type | VARCHAR(32) | NOT NULL | - | 触发类型：push/merge_request/schedule/manual |
| trigger_ref | VARCHAR(256) | - | - | 触发引用（分支名/MR ID） |
| trigger_user | VARCHAR(128) | - | - | 触发用户 |
| commit_sha | VARCHAR(64) | - | - | 提交SHA |
| commit_message | TEXT | - | - | 提交信息 |
| scan_status | VARCHAR(32) | NOT NULL | 'pending' | 扫描状态：pending/running/completed/failed/timeout/cancelled |
| gate_status | VARCHAR(32) | - | - | 门禁结果：passed/failed/warning |
| total_gates | INT | NOT NULL | 0 | 门禁总数 |
| passed_gates | INT | NOT NULL | 0 | 通过门禁数 |
| failed_gates | INT | NOT NULL | 0 | 失败门禁数 |
| skipped_gates | INT | NOT NULL | 0 | 跳过门禁数 |
| total_issues | INT | NOT NULL | 0 | 问题总数 |
| critical_issues | INT | NOT NULL | 0 | 严重问题数 |
| high_issues | INT | NOT NULL | 0 | 高危问题数 |
| medium_issues | INT | NOT NULL | 0 | 中危问题数 |
| low_issues | INT | NOT NULL | 0 | 低危问题数 |
| report_url | VARCHAR(512) | - | - | HTML报告地址 |
| report_json | TEXT | - | - | JSON报告内容（降级方案） |
| error_message | TEXT | - | - | 错误信息 |
| started_at | DATETIME | - | - | 扫描开始时间 |
| completed_at | DATETIME | - | - | 扫描完成时间 |
| duration_seconds | INT | - | - | 扫描耗时（秒） |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引定义：**
```sql
CREATE UNIQUE INDEX uk_scan_id ON scan_tasks(scan_id);
CREATE INDEX idx_project_id ON scan_tasks(project_id);
CREATE INDEX idx_trigger_type ON scan_tasks(trigger_type);
CREATE INDEX idx_scan_status ON scan_tasks(scan_status);
CREATE INDEX idx_gate_status ON scan_tasks(gate_status);
CREATE INDEX idx_created_at ON scan_tasks(created_at);
CREATE INDEX idx_project_created ON scan_tasks(project_id, created_at DESC);
CREATE INDEX idx_project_status ON scan_tasks(project_id, scan_status);
```

### 3.2 扫描结果表（scan_results）

记录每个门禁的扫描结果。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 主键ID |
| scan_id | VARCHAR(64) | NOT NULL | - | 关联扫描任务ID |
| gate_type | VARCHAR(64) | NOT NULL | - | 门禁类型：vulnerability/sensitive_word/hardcode/code_standard |
| gate_name | VARCHAR(128) | NOT NULL | - | 门禁名称 |
| gate_version | VARCHAR(32) | - | - | 门禁脚本版本 |
| execution_status | VARCHAR(32) | NOT NULL | 'pending' | 执行状态：pending/running/completed/failed/timeout/skipped |
| gate_result | VARCHAR(32) | - | - | 门禁结果：passed/failed/warning |
| total_issues | INT | NOT NULL | 0 | 发现问题数 |
| critical_issues | INT | NOT NULL | 0 | 严重问题数 |
| high_issues | INT | NOT NULL | 0 | 高危问题数 |
| medium_issues | INT | NOT NULL | 0 | 中危问题数 |
| low_issues | INT | NOT NULL | 0 | 低危问题数 |
| scanned_files | INT | NOT NULL | 0 | 扫描文件数 |
| total_lines | BIGINT | NOT NULL | 0 | 扫描代码行数 |
| output_log | TEXT | - | - | 脚本输出日志 |
| error_log | TEXT | - | - | 错误日志 |
| exit_code | INT | - | - | 脚本退出码 |
| error_message | VARCHAR(1024) | - | - | 错误信息 |
| started_at | DATETIME | - | - | 开始时间 |
| completed_at | DATETIME | - | - | 完成时间 |
| duration_seconds | INT | - | - | 执行耗时（秒） |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引定义：**
```sql
CREATE INDEX idx_scan_id ON scan_results(scan_id);
CREATE INDEX idx_gate_type ON scan_results(gate_type);
CREATE INDEX idx_execution_status ON scan_results(execution_status);
CREATE INDEX idx_gate_result ON scan_results(gate_result);
CREATE INDEX idx_scan_gate ON scan_results(scan_id, gate_type);
```

### 3.3 问题详情表（issue_details）

记录每个发现的问题。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 主键ID |
| scan_id | VARCHAR(64) | NOT NULL | - | 关联扫描任务ID |
| result_id | BIGINT | NOT NULL | - | 关联扫描结果ID |
| gate_type | VARCHAR(64) | NOT NULL | - | 门禁类型 |
| issue_type | VARCHAR(128) | NOT NULL | - | 问题类型 |
| severity | VARCHAR(32) | NOT NULL | - | 严重级别：critical/high/medium/low/info |
| file_path | VARCHAR(1024) | NOT NULL | - | 文件路径 |
| line_number | INT | - | - | 行号 |
| column_number | INT | - | - | 列号 |
| end_line_number | INT | - | - | 结束行号 |
| end_column_number | INT | - | - | 结束列号 |
| code_snippet | TEXT | - | - | 代码片段 |
| message | TEXT | NOT NULL | - | 问题描述 |
| rule_id | VARCHAR(128) | - | - | 规则ID |
| rule_name | VARCHAR(256) | - | - | 规则名称 |
| rule_url | VARCHAR(512) | - | - | 规则文档URL |
| cwe_id | VARCHAR(32) | - | - | CWE编号 |
| owasp_category | VARCHAR(64) | - | - | OWASP分类 |
| confidence | VARCHAR(32) | - | - | 置信度：high/medium/low |
| is_whitelisted | BOOLEAN | NOT NULL | false | 是否在白名单中 |
| whitelisted_reason | VARCHAR(256) | - | - | 白名单原因 |
| fingerprint | VARCHAR(128) | - | - | 问题指纹（用于去重） |
| metadata | JSON | - | - | 扩展元数据 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |

**索引定义：**
```sql
CREATE INDEX idx_scan_id ON issue_details(scan_id);
CREATE INDEX idx_result_id ON issue_details(result_id);
CREATE INDEX idx_gate_type ON issue_details(gate_type);
CREATE INDEX idx_severity ON issue_details(severity);
CREATE INDEX idx_file_path ON issue_details(file_path(255));
CREATE INDEX idx_rule_id ON issue_details(rule_id);
CREATE INDEX idx_fingerprint ON issue_details(fingerprint);
CREATE INDEX idx_is_whitelisted ON issue_details(is_whitelisted);
CREATE INDEX idx_scan_severity ON issue_details(scan_id, severity);
CREATE INDEX idx_scan_gate ON issue_details(scan_id, gate_type);
CREATE INDEX idx_result_severity ON issue_details(result_id, severity);
```

### 3.4 门禁配置表（gate_configs）

记录门禁规则配置。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 主键ID |
| config_id | VARCHAR(64) | UNIQUE, NOT NULL | - | 配置唯一标识 |
| project_id | VARCHAR(128) | - | - | 项目ID（NULL表示全局配置） |
| gate_type | VARCHAR(64) | NOT NULL | - | 门禁类型 |
| gate_name | VARCHAR(128) | NOT NULL | - | 门禁名称 |
| description | TEXT | - | - | 配置描述 |
| enabled | BOOLEAN | NOT NULL | true | 是否启用 |
| severity_threshold | VARCHAR(32) | NOT NULL | 'high' | 阻断阈值：critical/high/medium/low |
| timeout_seconds | INT | NOT NULL | 600 | 超时时间（秒） |
| retry_count | INT | NOT NULL | 0 | 重试次数 |
| config_data | JSON | NOT NULL | - | 门禁配置数据 |
| script_path | VARCHAR(512) | - | - | 脚本路径 |
| script_version | VARCHAR(32) | - | - | 脚本版本 |
| execution_order | INT | NOT NULL | 100 | 执行顺序 |
| created_by | VARCHAR(128) | - | - | 创建人 |
| updated_by | VARCHAR(128) | - | - | 更新人 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引定义：**
```sql
CREATE UNIQUE INDEX uk_config_id ON gate_configs(config_id);
CREATE INDEX idx_project_id ON gate_configs(project_id);
CREATE INDEX idx_gate_type ON gate_configs(gate_type);
CREATE INDEX idx_enabled ON gate_configs(enabled);
CREATE INDEX idx_project_gate ON gate_configs(project_id, gate_type);
CREATE UNIQUE INDEX uk_project_gate_type ON gate_configs(project_id, gate_type);
```

### 3.5 通知记录表（notification_logs）

记录通知发送历史。

| 字段名 | 类型 | 约束 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | - | 主键ID |
| notification_id | VARCHAR(64) | UNIQUE, NOT NULL | - | 通知唯一标识 |
| scan_id | VARCHAR(64) | NOT NULL | - | 关联扫描任务ID |
| notification_type | VARCHAR(32) | NOT NULL | - | 通知类型：email/gitlab_comment/webhook |
| recipient | VARCHAR(512) | NOT NULL | - | 接收人（邮箱/用户ID/webhook URL） |
| subject | VARCHAR(512) | - | - | 通知主题 |
| content | TEXT | NOT NULL | - | 通知内容 |
| content_type | VARCHAR(32) | NOT NULL | 'text' | 内容类型：text/html/json |
| send_status | VARCHAR(32) | NOT NULL | 'pending' | 发送状态：pending/sending/sent/failed/retry |
| retry_count | INT | NOT NULL | 0 | 已重试次数 |
| max_retries | INT | NOT NULL | 3 | 最大重试次数 |
| error_message | TEXT | - | - | 错误信息 |
| response_code | INT | - | - | 响应状态码 |
| response_body | TEXT | - | - | 响应内容 |
| sent_at | DATETIME | - | - | 发送时间 |
| next_retry_at | DATETIME | - | - | 下次重试时间 |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

**索引定义：**
```sql
CREATE UNIQUE INDEX uk_notification_id ON notification_logs(notification_id);
CREATE INDEX idx_scan_id ON notification_logs(scan_id);
CREATE INDEX idx_notification_type ON notification_logs(notification_type);
CREATE INDEX idx_send_status ON notification_logs(send_status);
CREATE INDEX idx_next_retry_at ON notification_logs(next_retry_at);
CREATE INDEX idx_created_at ON notification_logs(created_at);
CREATE INDEX idx_scan_type ON notification_logs(scan_id, notification_type);
CREATE INDEX idx_status_retry ON notification_logs(send_status, next_retry_at);
```

## 4. 全局数据结构定义

### 4.1 门禁脚本接口规范

#### 4.1.1 输入格式（Input）

门禁脚本通过环境变量接收以下信息：

| 变量名 | 说明 |
|--------|------|
| QUALITY_GATE_SCAN_ID | 扫描ID |
| QUALITY_GATE_PROJECT_ID | 项目ID |
| QUALITY_GATE_PROJECT_PATH | 项目路径 |
| QUALITY_GATE_TRIGGER_TYPE | 触发类型 |
| QUALITY_GATE_COMMIT_SHA | 提交SHA |
| QUALITY_GATE_CONFIG_PATH | 配置文件路径 |
| QUALITY_GATE_OUTPUT_DIR | 输出目录 |

#### 4.1.2 输出格式（Output）

门禁脚本通过标准输出返回 JSON 格式的扫描结果：

```json
{
  "gate_type": "string",
  "gate_name": "string",
  "gate_version": "string",
  "execution_status": "completed",
  "gate_result": "passed",
  "summary": {
    "total_issues": 0,
    "critical_issues": 0,
    "high_issues": 0,
    "medium_issues": 0,
    "low_issues": 0,
    "scanned_files": 0,
    "total_lines": 0
  },
  "issues": [
    {
      "issue_type": "string",
      "severity": "high",
      "file_path": "string",
      "line_number": 1,
      "column_number": 1,
      "code_snippet": "string",
      "message": "string",
      "rule_id": "string",
      "rule_name": "string",
      "cwe_id": "string",
      "confidence": "high"
    }
  ],
  "metadata": {
    "tool_version": "string",
    "rules_version": "string",
    "scan_duration_ms": 0
  }
}
```

**退出码规范：**
| 退出码 | 说明 |
|--------|------|
| 0 | 成功，门禁通过 |
| 1 | 成功，门禁失败（发现问题） |
| 2 | 执行错误 |
| 3 | 超时 |
| 4 | 配置错误 |
| 5 | 依赖缺失 |

## 5. 配置文件定义

### 5.1 全局配置文件（quality-gate.yml）

```yaml
# 全局配置文件：quality-gate.yml
version: "1.0"

settings:
  parallel_execution: true
  max_parallel_gates: 4
  fail_fast: false
  scan_timeout: 600
  report_timeout: 60
  report_path: "reports"
  log_level: "info"
  structured_logging: true

gates:
  vulnerability:
    enabled: true
    severity_threshold: "high"
    timeout_seconds: 300
    script_path: "scripts/vulnerability-scan.sh"
    config_data:
      rules_source: "owasp"
      languages: ["java", "python", "javascript", "typescript"]
      exclude_paths: ["**/test/**", "**/vendor/**", "**/node_modules/**"]

  sensitive_word:
    enabled: true
    severity_threshold: "high"
    timeout_seconds: 120
    script_path: "scripts/sensitive-word-scan.sh"
    config_data:
      wordlist_path: "config/sensitive-words.txt"
      regex_path: "config/sensitive-regex.yml"
      mask_enabled: true
      exclude_env_vars: true
      exclude_test_files: true

  hardcode:
    enabled: true
    severity_threshold: "medium"
    timeout_seconds: 120
    script_path: "scripts/hardcode-scan.sh"
    config_data:
      detection_types: ["ip_address", "port", "file_path", "url", "email"]
      whitelist:
        ip_addresses: ["127.0.0.1", "localhost"]
        ports: ["80", "443"]

  code_standard:
    enabled: true
    severity_threshold: "error"
    timeout_seconds: 300
    script_path: "scripts/code-standard-check.sh"
    config_data:
      tools:
        eslint: { enabled: true, config_path: ".eslintrc.js" }
        pylint: { enabled: true, config_path: ".pylintrc" }
        checkstyle: { enabled: true, config_path: "checkstyle.xml" }

notifications:
  enabled: true
  conditions:
    on_failure: true
    on_success: false
  channels:
    email:
      enabled: true
      smtp_host: "${SMTP_HOST}"
      smtp_port: 587
    gitlab_comment:
      enabled: true
      format: "markdown"
```

### 5.2 项目级配置文件（.quality-gate/config.yml）

```yaml
# 项目级配置文件：.quality-gate/config.yml
extends: "global"

project:
  id: "project-123"
  name: "My Project"

gates:
  hardcode:
    enabled: false
  vulnerability:
    severity_threshold: "critical"

notifications:
  channels:
    email:
      recipients:
        - type: "custom"
          addresses: ["project-team@example.com"]

whitelist:
  sensitive_words:
    - pattern: "test_password"
      reason: "测试环境密码"
      paths: ["**/test/**"]

triggers:
  push:
    enabled: true
    branches: ["main", "develop", "release/*"]
  merge_request:
    enabled: true
    target_branches: ["main", "develop"]
  schedule:
    enabled: true
    cron: "0 2 * * *"
    branch: "main"
```

## 6. 设计说明

### 6.1 设计原则

1. **规范化设计**：遵循第三范式，减少数据冗余
2. **扩展性**：使用 JSON 字段存储可变配置，支持未来扩展
3. **性能优化**：合理设计索引，支持高频查询场景
4. **审计追踪**：所有表包含 created_at/updated_at 字段

### 6.2 关键设计决策

| 决策项 | 决策内容 | 理由 |
|--------|----------|------|
| 主键类型 | BIGINT | 支持海量数据，性能优于 UUID |
| 扫描ID | VARCHAR(64) UUID | 全局唯一，便于跨系统关联 |
| JSON 字段 | config_data/metadata | 灵活存储可变配置，避免频繁变更表结构 |
| 索引策略 | 覆盖主要查询场景 | 平衡查询性能和写入开销 |
| 字符集 | utf8mb4 | 支持中文和特殊字符 |

### 6.3 数据生命周期

| 数据类型 | 保留策略 | 归档策略 |
|----------|----------|----------|
| scan_tasks | 90天 | 超过90天归档到冷存储 |
| scan_results | 90天 | 随 scan_tasks 一起归档 |
| issue_details | 90天 | 随 scan_results 一起归档 |
| gate_configs | 永久 | 配置变更记录保留1年 |
| notification_logs | 30天 | 超过30天清理 |

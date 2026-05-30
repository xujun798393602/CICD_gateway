# API 接口设计：代码质量门禁系统

## 1. 概述

### 1.1 基础信息

| 项目 | 说明 |
|------|------|
| API基础路径 | `/api/v1` |
| 协议 | HTTPS |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |
| 时间格式 | ISO 8601 |

### 1.2 鉴权方式

**方式一：API Token（推荐用于CI/CD集成）**
```
Authorization: Bearer <api_token>
```

**方式二：GitLab OAuth2（用于Web界面访问）**
```
Authorization: Bearer <gitlab_oauth_token>
```

### 1.3 统一响应格式

**成功响应**：
```json
{
  "code": 0,
  "message": "success",
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

**错误响应**：
```json
{
  "code": 40001,
  "message": "参数验证失败",
  "errors": [
    { "field": "project_id", "message": "项目ID不能为空" }
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_abc123def456"
}
```

### 1.4 全局错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| 0 | 200 | 成功 |
| 40001 | 400 | 参数验证失败 |
| 40101 | 401 | 未认证或Token无效 |
| 40102 | 401 | Token已过期 |
| 40301 | 403 | 无权限访问 |
| 40401 | 404 | 资源不存在 |
| 40901 | 409 | 资源冲突 |
| 42901 | 429 | 请求频率超限 |
| 50001 | 500 | 服务器内部错误 |
| 50002 | 500 | 依赖服务不可用 |

---

## 2. GitLab CI/CD 集成接口

### 2.1 门禁扫描触发接口

```
POST /api/v1/scans/trigger
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | 是 | 项目ID |
| repository_url | string | 是 | Git仓库地址 |
| branch | string | 是 | 分支名称 |
| commit_sha | string | 是 | 提交SHA |
| trigger_type | string | 是 | 触发类型：push/merge_request/schedule/manual |
| merge_request_id | integer | 否 | MR编号 |
| scanners | string[] | 否 | 指定扫描器列表 |
| callback_url | string | 否 | 回调地址 |
| metadata | object | 否 | GitLab元数据 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "scan_id": "scan_20240115_abc123",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z",
    "estimated_duration": 300
  }
}
```

**错误码**：40001, 40401, 40901, 50001

---

### 2.2 扫描结果上报接口

```
POST /api/v1/scans/{scan_id}/results
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scanner_id | string | 是 | 扫描器ID |
| scanner_version | string | 是 | 扫描器版本 |
| status | string | 是 | 状态：success/failed/timeout/skipped |
| started_at | string | 是 | 开始时间 |
| completed_at | string | 是 | 完成时间 |
| duration_ms | integer | 是 | 耗时（毫秒） |
| summary | object | 是 | 扫描摘要 |
| issues | array | 否 | 问题列表 |
| error_message | string | 否 | 错误信息 |

**Issues参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 问题ID |
| severity | string | 是 | 严重级别 |
| category | string | 是 | 问题类别 |
| title | string | 是 | 问题标题 |
| description | string | 是 | 问题描述 |
| file_path | string | 是 | 文件路径 |
| line_number | integer | 是 | 行号 |
| rule_id | string | 是 | 规则ID |
| recommendation | string | 否 | 修复建议 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "result_id": "result_20240115_xyz789",
    "scan_id": "scan_20240115_abc123",
    "gate_passed": false,
    "blocking_issues_count": 3
  }
}
```

**错误码**：40001, 40401, 40901, 50001

---

### 2.3 门禁状态查询接口

```
GET /api/v1/scans/{scan_id}/status
```

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| include_details | boolean | 否 | 是否包含详细问题列表 |
| wait | boolean | 否 | 是否等待扫描完成 |
| timeout | integer | 否 | 等待超时时间（秒） |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "scan_id": "scan_20240115_abc123",
    "status": "completed",
    "gate_result": "failed",
    "gate_passed": false,
    "scanners_status": [
      {
        "scanner_id": "vulnerability_scanner",
        "status": "success",
        "gate_passed": false,
        "critical_count": 1,
        "high_count": 2
      }
    ],
    "summary": {
      "total_scanners": 4,
      "completed_scanners": 3,
      "failed_scanners": 1,
      "total_issues": 15,
      "blocking_issues": 6
    },
    "report_url": "https://quality-gate.example.com/reports/rpt_20240115_abc123"
  }
}
```

**错误码**：40401, 50001

---

## 3. 报告服务接口

### 3.1 报告生成接口

```
POST /api/v1/reports/generate
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scan_id | string | 是 | 扫描任务ID |
| report_type | string | 否 | full/summary，默认full |
| format | string | 否 | html/json/pdf，默认html |
| options | object | 否 | 报告选项 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "report_id": "rpt_20240115_abc123",
    "status": "generating",
    "format": "html",
    "estimated_completion": "2024-01-15T10:37:00Z"
  }
}
```

**错误码**：40001, 40401, 40901, 50001

---

### 3.2 报告查询接口

```
GET /api/v1/reports/{report_id}
```

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| include_content | boolean | 否 | 是否包含报告内容 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "report_id": "rpt_20240115_abc123",
    "scan_id": "scan_20240115_abc123",
    "status": "completed",
    "format": "html",
    "download_url": "https://quality-gate.example.com/reports/download/rpt_20240115_abc123",
    "view_url": "https://quality-gate.example.com/reports/view/rpt_20240115_abc123",
    "summary": {
      "total_issues": 15,
      "critical": 1,
      "high": 5,
      "gate_passed": false
    }
  }
}
```

**错误码**：40401, 40901, 50001

---

### 3.3 报告列表接口

```
GET /api/v1/reports
```

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | string | 是 | 项目ID |
| branch | string | 否 | 分支过滤 |
| status | string | 否 | 状态过滤 |
| gate_result | string | 否 | 门禁结果过滤 |
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "report_id": "rpt_20240115_abc123",
        "status": "completed",
        "gate_passed": false,
        "total_issues": 15,
        "view_url": "https://quality-gate.example.com/reports/view/rpt_20240115_abc123"
      }
    ]
  }
}
```

**错误码**：40001, 40401, 50001

---

## 4. 配置管理接口

### 4.1 配置查询接口

```
GET /api/v1/configs/{project_id}
```

**路径参数**：project_id（`_global`表示全局配置）

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| merged | boolean | 否 | 是否返回合并后的配置 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "project_id": "proj_001",
    "config_version": "1.2.0",
    "config": {
      "scanners": {
        "vulnerability_scanner": { "enabled": true, "timeout": 300 },
        "sensitive_word_scanner": { "enabled": true, "timeout": 120 }
      },
      "notifications": {
        "enabled": true,
        "channels": { "email": { "enabled": true } }
      }
    }
  }
}
```

**错误码**：40401, 50001

---

### 4.2 配置更新接口

```
PUT /api/v1/configs/{project_id}
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| config | object | 是 | 配置内容 |
| comment | string | 否 | 变更说明 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "project_id": "proj_001",
    "config_version": "1.3.0",
    "changes": [
      { "field": "scanners.vulnerability_scanner.timeout", "old_value": 300, "new_value": 600 }
    ]
  }
}
```

**错误码**：40001, 40401, 40901, 50001

---

### 4.3 门禁脚本注册接口

```
POST /api/v1/scanners/register
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scanner_id | string | 是 | 扫描器ID |
| name | string | 是 | 显示名称 |
| description | string | 是 | 描述 |
| version | string | 是 | 版本号 |
| category | string | 是 | 类别 |
| entry_point | string | 是 | 入口脚本路径 |
| timeout | integer | 否 | 超时时间 |
| config_schema | object | 否 | 配置Schema |
| default_config | object | 否 | 默认配置 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "scanner_id": "custom_security_scanner",
    "version": "1.0.0",
    "status": "registered"
  }
}
```

**错误码**：40001, 40901, 50001

---

### 4.4 扫描器列表接口

```
GET /api/v1/scanners
```

**查询参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 按类别过滤 |
| status | string | 否 | 按状态过滤 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "total": 5,
    "scanners": [
      {
        "scanner_id": "vulnerability_scanner",
        "name": "代码漏洞扫描器",
        "version": "1.2.0",
        "category": "vulnerability",
        "status": "active"
      }
    ]
  }
}
```

**错误码**：50001

---

## 5. 通知服务接口

### 5.1 通知发送接口

```
POST /api/v1/notifications/send
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| scan_id | string | 是 | 扫描任务ID |
| channels | string[] | 否 | 通知渠道 |
| recipients | object | 否 | 自定义接收人 |
| template | string | 否 | 通知模板 |
| custom_message | string | 否 | 自定义消息 |
| force | boolean | 否 | 是否强制发送 |

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "notification_id": "notif_20240115_abc123",
    "channels": [
      { "channel": "email", "status": "sent", "recipients_count": 3 },
      { "channel": "gitlab_mr_comment", "status": "sent", "comment_id": 12345 }
    ]
  }
}
```

**错误码**：40001, 40401, 50001, 50002

---

### 5.2 通知配置接口

```
GET /api/v1/notifications/config/{project_id}
PUT /api/v1/notifications/config/{project_id}
```

**请求参数（PUT）**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| config.enabled | boolean | 否 | 是否启用 |
| config.channels.*.enabled | boolean | 否 | 渠道启用 |
| config.channels.*.recipients | string[] | 否 | 接收人 |
| config.channels.*.notify_on | string[] | 否 | 触发条件 |
| config.schedule.quiet_hours_enabled | boolean | 否 | 静默时段 |

**错误码**：40001, 40401, 50001

---

## 6. 辅助接口

### 6.1 健康检查接口

```
GET /api/v1/health
```

**成功响应**：
```json
{
  "code": 0,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "components": {
      "database": "healthy",
      "cache": "healthy",
      "storage": "healthy"
    }
  }
}
```

### 6.2 指标接口

```
GET /api/v1/metrics
```

返回 Prometheus 格式的指标数据。

---

## 7. GitLab CI/CD 集成示例

```yaml
stages:
  - quality-gate

quality_gate_scan:
  stage: quality-gate
  image: alpine:latest
  before_script:
    - apk add --no-cache curl jq
  script:
    # 1. 触发门禁扫描
    - |
      SCAN_RESPONSE=$(curl -s -X POST "${QUALITY_GATE_API}/api/v1/scans/trigger" \
        -H "Authorization: Bearer ${QUALITY_GATE_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
          "project_id": "'${CI_PROJECT_ID}'",
          "repository_url": "'${CI_REPOSITORY_URL}'",
          "branch": "'${CI_COMMIT_BRANCH}'",
          "commit_sha": "'${CI_COMMIT_SHA}'",
          "trigger_type": "'${CI_PIPELINE_SOURCE}'",
          "merge_request_id": '${CI_MERGE_REQUEST_ID:-null}'
        }')
      SCAN_ID=$(echo "${SCAN_RESPONSE}" | jq -r '.data.scan_id')

    # 2. 等待扫描完成
    - |
      MAX_WAIT=600
      WAIT_INTERVAL=10
      ELAPSED=0
      while [ ${ELAPSED} -lt ${MAX_WAIT} ]; do
        STATUS_RESPONSE=$(curl -s -X GET "${QUALITY_GATE_API}/api/v1/scans/${SCAN_ID}/status" \
          -H "Authorization: Bearer ${QUALITY_GATE_TOKEN}")
        STATUS=$(echo "${STATUS_RESPONSE}" | jq -r '.data.status')
        GATE_PASSED=$(echo "${STATUS_RESPONSE}" | jq -r '.data.gate_passed')

        if [ "${STATUS}" = "completed" ]; then
          if [ "${GATE_PASSED}" = "true" ]; then
            echo "Quality gate PASSED"
            exit 0
          else
            echo "Quality gate FAILED"
            REPORT_URL=$(echo "${STATUS_RESPONSE}" | jq -r '.data.report_url')
            echo "View report: ${REPORT_URL}"
            exit 1
          fi
        fi
        sleep ${WAIT_INTERVAL}
        ELAPSED=$((ELAPSED + WAIT_INTERVAL))
      done
      echo "Scan timeout"
      exit 1
  rules:
    - if: '$CI_PIPELINE_SOURCE == "push"'
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
  timeout: 15m
```

---

## 8. 附录

### 8.1 状态码说明

**扫描状态**：pending, running, completed, failed, timeout, cancelled
**报告状态**：generating, completed, failed
**门禁结果**：passed, failed, skipped, error

### 8.2 严重级别说明

| 级别 | 门禁策略 |
|------|----------|
| critical | 阻止合并 |
| high | 阻止合并 |
| medium | 警告，不阻止 |
| low | 警告，不阻止 |
| info | 仅记录 |

### 8.3 问题类别说明

| 类别 | 对应扫描器 |
|------|-----------|
| vulnerability | vulnerability_scanner |
| sensitive_word | sensitive_word_scanner |
| hardcode | hardcode_scanner |
| code_style | code_style_scanner |
| custom | custom_scanner |

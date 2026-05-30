# 代码质量门禁系统 - 技术设计文档（汇总索引）

## 文档信息

| 属性 | 值 |
|------|-----|
| 文档标题 | 代码质量门禁系统技术设计文档 |
| 版本 | V1.0 |
| 状态 | 已评审 |
| 创建日期 | 2026-05-30 |
| 质量评分 | **88/100** |

---

## 设计概述

### 架构目标

建立一套可扩展的代码质量门禁脚本套件，集成到 GitLab CI/CD 流程中，实现代码提交和合并的全流程质量卡控。

### 核心决策摘要

| 决策项 | 决策内容 | 理由 |
|--------|----------|------|
| 门禁失败策略 | 阻止合并 | 确保代码质量 |
| 后端语言 | Python 3.10+ | 生态丰富、开发效率高 |
| Web框架 | FastAPI | 高性能、自动API文档、类型提示 |
| ORM | SQLAlchemy 2.0 | 成熟稳定、支持异步 |
| 门禁脚本技术 | Shell（主选）+ Python（备选） | 兼容性好、执行效率高 |
| 数据库 | MySQL 8.0 | 成熟稳定、性能优秀 |
| 缓存 | Redis (aioredis) | 高性能、异步支持 |
| 模板引擎 | Jinja2 | Python生态标准、语法简洁 |
| 报告部署 | Nginx 静态文件服务 | 简单高效、安全可靠 |
| 通知渠道 | 邮件 + GitLab MR评论 | 覆盖主要场景 |

---

## 子文档目录

| 文档 | 文件 | 说明 |
|------|------|------|
| 架构与流程设计 | [module_design.md](module_design.md) | 业务流程、系统架构、模块划分、技术选型 |
| 数据模型设计 | [data_model_design.md](data_model_design.md) | 数据库表结构、全局数据结构、配置文件定义 |
| API 接口设计 | [API_design.md](API_design.md) | RESTful API 接口规范、请求响应格式、错误码 |
| 接口依赖关系 | [API_dependency.md](API_dependency.md) | 跨API调用顺序、参数到字段映射 |
| DFX 可靠性设计 | [DFX_design.md](DFX_design.md) | 稳定性、可用性、可扩展性、性能、安全、可维护性、兼容性 |

---

## 关键 API 接口摘要

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/scans/trigger` | POST | 触发门禁扫描 |
| `/api/v1/scans/{scan_id}/results` | POST | 上报扫描结果 |
| `/api/v1/scans/{scan_id}/status` | GET | 查询扫描状态 |
| `/api/v1/reports/generate` | POST | 生成扫描报告 |
| `/api/v1/reports/{report_id}` | GET | 查询报告详情 |
| `/api/v1/reports` | GET | 查询报告列表 |
| `/api/v1/configs/{project_id}` | GET/PUT | 查询/更新配置 |
| `/api/v1/scanners/register` | POST | 注册扫描器 |
| `/api/v1/scanners` | GET | 查询扫描器列表 |
| `/api/v1/notifications/send` | POST | 发送通知 |
| `/api/v1/notifications/config/{project_id}` | GET/PUT | 查询/更新通知配置 |
| `/api/v1/health` | GET | 健康检查 |
| `/api/v1/metrics` | GET | 系统指标 |

---

## 关键数据模型摘要

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| scan_tasks | 扫描任务表 | scan_id, project_id, trigger_type, scan_status, gate_status |
| scan_results | 扫描结果表 | scan_id, gate_type, execution_status, gate_result, total_issues |
| issue_details | 问题详情表 | scan_id, severity, file_path, line_number, rule_id |
| gate_configs | 门禁配置表 | project_id, gate_type, enabled, severity_threshold, config_data |
| notification_logs | 通知记录表 | scan_id, notification_type, send_status, recipient |

---

## 门禁脚本接口规范

### 输入（环境变量）

| 变量名 | 说明 |
|--------|------|
| QUALITY_GATE_SCAN_ID | 扫描ID |
| QUALITY_GATE_PROJECT_ID | 项目ID |
| QUALITY_GATE_PROJECT_PATH | 项目路径 |
| QUALITY_GATE_TRIGGER_TYPE | 触发类型 |
| QUALITY_GATE_COMMIT_SHA | 提交SHA |

### 输出（标准输出 JSON）

```json
{
  "gate_type": "vulnerability",
  "gate_name": "代码漏洞扫描",
  "execution_status": "completed",
  "gate_result": "passed",
  "summary": { "total_issues": 0, "critical_issues": 0 },
  "issues": []
}
```

### 退出码

| 退出码 | 说明 |
|--------|------|
| 0 | 成功，门禁通过 |
| 1 | 成功，门禁失败 |
| 2 | 执行错误 |
| 3 | 超时 |

---

## 质量评分详情

### 完整性（36/40）

| 项目 | 得分 | 说明 |
|------|------|------|
| 所有章节均已完整呈现 | 9/10 | 子模块详细流程设计（Step 3）未单独执行，但架构文档已包含 |
| 所有需求均已映射到设计元素 | 10/10 | FR-001~FR-011 全部映射 |
| 所有模块都有对应的技术方案 | 9/10 | 技术选型理由充分 |
| 所有接口和schema都有定义 | 8/10 | 部分接口可补充更详细的Schema定义 |

### 清晰度（27/30）

| 项目 | 得分 | 说明 |
|------|------|------|
| 无歧义的规格说明 | 9/10 | 规格清晰，部分可补充示例 |
| 接口参数描述清晰 | 10/10 | 参数类型、必填、说明完整 |
| 功能模块边界清晰 | 5/5 | 模块职责和边界明确 |
| 清晰的图示和可视化辅助 | 3/5 | 文本架构图已提供，可补充更多流程图 |

### DFX 覆盖率（18/20）

| 项目 | 得分 | 说明 |
|------|------|------|
| 全部 7 个 DFX 维度均已涵盖 | 5/5 | 稳定性、可用性、可扩展性、性能、安全、可维护性、兼容性 |
| 具体、可操作的 DFX 措施 | 5/5 | 每个维度都有具体措施 |
| 清晰的测试策略 | 4/5 | 测试策略已定义，可补充更多测试用例 |
| 可测试的验收标准 | 4/5 | 验收标准已定义，部分可量化 |

### 变更说明（7/10）

| 项目 | 得分 | 说明 |
|------|------|------|
| 已说明本次主要变更点 | 4/5 | 核心决策已记录 |
| 已识别风险及缓解措施 | 3/5 | 风险已识别，缓解措施可更详细 |

### 总分：88/100 ✅ 达标

---

## 风险识别

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| GitLab API 版本升级 | 高 | API 版本适配层 |
| 扫描器脚本安全漏洞 | 高 | 沙箱隔离 + 资源限制 |
| 大型代码库扫描超时 | 中 | 增量扫描 + 并行执行 |
| 敏感信息脱敏遗漏 | 高 | 双层脱敏 |
| 并发扫描资源耗尽 | 中 | 连接池监控 + 排队机制 |

---

## 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| V1.0 | 2026-05-30 | 初始版本，完成全部设计文档 |

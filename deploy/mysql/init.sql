-- 代码质量门禁系统 - 数据库初始化脚本

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS quality_gate
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE quality_gate;

-- ==================== 扫描任务表 ====================
CREATE TABLE IF NOT EXISTS scan_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    scan_id VARCHAR(64) UNIQUE NOT NULL COMMENT '扫描唯一标识',
    project_id VARCHAR(128) NOT NULL COMMENT 'GitLab项目ID',
    project_name VARCHAR(256) NOT NULL COMMENT '项目名称',
    project_url VARCHAR(512) COMMENT '项目仓库地址',
    trigger_type VARCHAR(32) NOT NULL COMMENT '触发类型：push/merge_request/schedule/manual',
    trigger_ref VARCHAR(256) COMMENT '触发引用（分支名/MR ID）',
    trigger_user VARCHAR(128) COMMENT '触发用户',
    commit_sha VARCHAR(64) COMMENT '提交SHA',
    commit_message TEXT COMMENT '提交信息',
    scan_status VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '扫描状态：pending/running/completed/failed/timeout/cancelled',
    gate_status VARCHAR(32) COMMENT '门禁结果：passed/failed/warning',
    total_gates INT NOT NULL DEFAULT 0 COMMENT '门禁总数',
    passed_gates INT NOT NULL DEFAULT 0 COMMENT '通过门禁数',
    failed_gates INT NOT NULL DEFAULT 0 COMMENT '失败门禁数',
    skipped_gates INT NOT NULL DEFAULT 0 COMMENT '跳过门禁数',
    total_issues INT NOT NULL DEFAULT 0 COMMENT '问题总数',
    critical_issues INT NOT NULL DEFAULT 0 COMMENT '严重问题数',
    high_issues INT NOT NULL DEFAULT 0 COMMENT '高危问题数',
    medium_issues INT NOT NULL DEFAULT 0 COMMENT '中危问题数',
    low_issues INT NOT NULL DEFAULT 0 COMMENT '低危问题数',
    report_url VARCHAR(512) COMMENT 'HTML报告地址',
    report_json TEXT COMMENT 'JSON报告内容（降级方案）',
    error_message TEXT COMMENT '错误信息',
    started_at DATETIME COMMENT '扫描开始时间',
    completed_at DATETIME COMMENT '扫描完成时间',
    duration_seconds INT COMMENT '扫描耗时（秒）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_project_id (project_id),
    INDEX idx_trigger_type (trigger_type),
    INDEX idx_scan_status (scan_status),
    INDEX idx_gate_status (gate_status),
    INDEX idx_created_at (created_at),
    INDEX idx_project_created (project_id, created_at DESC),
    INDEX idx_project_status (project_id, scan_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='扫描任务表';

-- ==================== 扫描结果表 ====================
CREATE TABLE IF NOT EXISTS scan_results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    scan_id VARCHAR(64) NOT NULL COMMENT '关联扫描任务ID',
    gate_type VARCHAR(64) NOT NULL COMMENT '门禁类型：vulnerability/sensitive_word/hardcode/code_standard',
    gate_name VARCHAR(128) NOT NULL COMMENT '门禁名称',
    gate_version VARCHAR(32) COMMENT '门禁脚本版本',
    execution_status VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '执行状态：pending/running/completed/failed/timeout/skipped',
    gate_result VARCHAR(32) COMMENT '门禁结果：passed/failed/warning',
    total_issues INT NOT NULL DEFAULT 0 COMMENT '发现问题数',
    critical_issues INT NOT NULL DEFAULT 0 COMMENT '严重问题数',
    high_issues INT NOT NULL DEFAULT 0 COMMENT '高危问题数',
    medium_issues INT NOT NULL DEFAULT 0 COMMENT '中危问题数',
    low_issues INT NOT NULL DEFAULT 0 COMMENT '低危问题数',
    scanned_files INT NOT NULL DEFAULT 0 COMMENT '扫描文件数',
    total_lines BIGINT NOT NULL DEFAULT 0 COMMENT '扫描代码行数',
    output_log TEXT COMMENT '脚本输出日志',
    error_log TEXT COMMENT '错误日志',
    exit_code INT COMMENT '脚本退出码',
    error_message VARCHAR(1024) COMMENT '错误信息',
    started_at DATETIME COMMENT '开始时间',
    completed_at DATETIME COMMENT '完成时间',
    duration_seconds INT COMMENT '执行耗时（秒）',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_scan_id (scan_id),
    INDEX idx_gate_type (gate_type),
    INDEX idx_execution_status (execution_status),
    INDEX idx_gate_result (gate_result),
    INDEX idx_scan_gate (scan_id, gate_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='扫描结果表';

-- ==================== 问题详情表 ====================
CREATE TABLE IF NOT EXISTS issue_details (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    scan_id VARCHAR(64) NOT NULL COMMENT '关联扫描任务ID',
    result_id BIGINT NOT NULL COMMENT '关联扫描结果ID',
    gate_type VARCHAR(64) NOT NULL COMMENT '门禁类型',
    issue_type VARCHAR(128) NOT NULL COMMENT '问题类型',
    severity VARCHAR(32) NOT NULL COMMENT '严重级别：critical/high/medium/low/info',
    file_path VARCHAR(1024) NOT NULL COMMENT '文件路径',
    line_number INT COMMENT '行号',
    column_number INT COMMENT '列号',
    end_line_number INT COMMENT '结束行号',
    end_column_number INT COMMENT '结束列号',
    code_snippet TEXT COMMENT '代码片段',
    message TEXT NOT NULL COMMENT '问题描述',
    rule_id VARCHAR(128) COMMENT '规则ID',
    rule_name VARCHAR(256) COMMENT '规则名称',
    rule_url VARCHAR(512) COMMENT '规则文档URL',
    cwe_id VARCHAR(32) COMMENT 'CWE编号',
    owasp_category VARCHAR(64) COMMENT 'OWASP分类',
    confidence VARCHAR(32) COMMENT '置信度：high/medium/low',
    is_whitelisted BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否在白名单中',
    whitelisted_reason VARCHAR(256) COMMENT '白名单原因',
    fingerprint VARCHAR(128) COMMENT '问题指纹（用于去重）',
    metadata JSON COMMENT '扩展元数据',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_issue_scan_id (scan_id),
    INDEX idx_issue_result_id (result_id),
    INDEX idx_issue_gate_type (gate_type),
    INDEX idx_issue_severity (severity),
    INDEX idx_issue_rule_id (rule_id),
    INDEX idx_issue_fingerprint (fingerprint),
    INDEX idx_issue_is_whitelisted (is_whitelisted),
    INDEX idx_issue_scan_severity (scan_id, severity),
    INDEX idx_issue_scan_gate (scan_id, gate_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问题详情表';

-- ==================== 门禁配置表 ====================
CREATE TABLE IF NOT EXISTS gate_configs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    config_id VARCHAR(64) UNIQUE NOT NULL COMMENT '配置唯一标识',
    project_id VARCHAR(128) COMMENT '项目ID（NULL表示全局配置）',
    gate_type VARCHAR(64) NOT NULL COMMENT '门禁类型',
    gate_name VARCHAR(128) NOT NULL COMMENT '门禁名称',
    description TEXT COMMENT '配置描述',
    enabled BOOLEAN NOT NULL DEFAULT TRUE COMMENT '是否启用',
    severity_threshold VARCHAR(32) NOT NULL DEFAULT 'high' COMMENT '阻断阈值：critical/high/medium/low',
    timeout_seconds INT NOT NULL DEFAULT 600 COMMENT '超时时间（秒）',
    retry_count INT NOT NULL DEFAULT 0 COMMENT '重试次数',
    config_data JSON NOT NULL COMMENT '门禁配置数据',
    script_path VARCHAR(512) COMMENT '脚本路径',
    script_version VARCHAR(32) COMMENT '脚本版本',
    execution_order INT NOT NULL DEFAULT 100 COMMENT '执行顺序',
    created_by VARCHAR(128) COMMENT '创建人',
    updated_by VARCHAR(128) COMMENT '更新人',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_config_project_id (project_id),
    INDEX idx_config_gate_type (gate_type),
    INDEX idx_config_enabled (enabled),
    INDEX idx_config_project_gate (project_id, gate_type),
    UNIQUE KEY uk_project_gate_type (project_id, gate_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='门禁配置表';

-- ==================== 通知记录表 ====================
CREATE TABLE IF NOT EXISTS notification_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    notification_id VARCHAR(64) UNIQUE NOT NULL COMMENT '通知唯一标识',
    scan_id VARCHAR(64) NOT NULL COMMENT '关联扫描任务ID',
    notification_type VARCHAR(32) NOT NULL COMMENT '通知类型：email/gitlab_comment/webhook',
    recipient VARCHAR(512) NOT NULL COMMENT '接收人（邮箱/用户ID/webhook URL）',
    subject VARCHAR(512) COMMENT '通知主题',
    content TEXT NOT NULL COMMENT '通知内容',
    content_type VARCHAR(32) NOT NULL DEFAULT 'text' COMMENT '内容类型：text/html/json',
    send_status VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT '发送状态：pending/sending/sent/failed/retry',
    retry_count INT NOT NULL DEFAULT 0 COMMENT '已重试次数',
    max_retries INT NOT NULL DEFAULT 3 COMMENT '最大重试次数',
    error_message TEXT COMMENT '错误信息',
    response_code INT COMMENT '响应状态码',
    response_body TEXT COMMENT '响应内容',
    sent_at DATETIME COMMENT '发送时间',
    next_retry_at DATETIME COMMENT '下次重试时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_notif_scan_id (scan_id),
    INDEX idx_notif_type (notification_type),
    INDEX idx_notif_send_status (send_status),
    INDEX idx_notif_next_retry (next_retry_at),
    INDEX idx_notif_scan_type (scan_id, notification_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知记录表';

-- ==================== 插入默认全局配置 ====================
INSERT IGNORE INTO gate_configs (config_id, project_id, gate_type, gate_name, description, enabled, severity_threshold, timeout_seconds, config_data, script_path, execution_order) VALUES
('cfg_global_vulnerability', NULL, 'vulnerability', '代码漏洞扫描', 'OWASP Top 10漏洞检测', TRUE, 'high', 300, '{"rules_source": "owasp", "languages": ["java", "python", "javascript", "typescript"], "exclude_paths": ["**/test/**", "**/vendor/**", "**/node_modules/**"]}', 'scripts/vulnerability-scan.sh', 100),
('cfg_global_sensitive_word', NULL, 'sensitive_word', '代码敏感词扫描', '检测硬编码密码、API密钥等敏感信息', TRUE, 'high', 120, '{"wordlist_path": "config/sensitive-words.txt", "regex_path": "config/sensitive-regex.yml", "mask_enabled": true, "exclude_env_vars": true}', 'scripts/sensitive-word-scan.sh', 200),
('cfg_global_hardcode', NULL, 'hardcode', '代码硬编码扫描', '检测硬编码IP、端口、路径等', TRUE, 'medium', 120, '{"detection_types": ["ip_address", "port", "file_path", "url", "email"], "whitelist": {"ip_addresses": ["127.0.0.1", "localhost"], "ports": ["80", "443"]}}', 'scripts/hardcode-scan.sh', 300),
('cfg_global_code_standard', NULL, 'code_standard', '代码规范检查', '集成ESLint、Pylint、Checkstyle', TRUE, 'error', 300, '{"tools": {"eslint": {"enabled": true}, "pylint": {"enabled": true}, "checkstyle": {"enabled": true}}}', 'scripts/code-standard-check.sh', 400);

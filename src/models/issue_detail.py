"""问题详情数据模型"""
from sqlalchemy import (
    Column, BigInteger, String, Integer, Boolean, Text, DateTime, JSON, func, Index
)
from src.core.database import Base


class IssueDetail(Base):
    """问题详情表"""
    __tablename__ = "issue_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(64), nullable=False, comment="关联扫描任务ID")
    result_id = Column(BigInteger, nullable=False, comment="关联扫描结果ID")
    gate_type = Column(String(64), nullable=False, comment="门禁类型")
    issue_type = Column(String(128), nullable=False, comment="问题类型")
    severity = Column(String(32), nullable=False, comment="严重级别")
    file_path = Column(String(1024), nullable=False, comment="文件路径")
    line_number = Column(Integer, comment="行号")
    column_number = Column(Integer, comment="列号")
    end_line_number = Column(Integer, comment="结束行号")
    end_column_number = Column(Integer, comment="结束列号")
    code_snippet = Column(Text, comment="代码片段")
    message = Column(Text, nullable=False, comment="问题描述")
    rule_id = Column(String(128), comment="规则ID")
    rule_name = Column(String(256), comment="规则名称")
    rule_url = Column(String(512), comment="规则文档URL")
    cwe_id = Column(String(32), comment="CWE编号")
    owasp_category = Column(String(64), comment="OWASP分类")
    confidence = Column(String(32), comment="置信度")
    is_whitelisted = Column(
        Boolean, nullable=False, default=False, comment="是否在白名单中"
    )
    whitelisted_reason = Column(String(256), comment="白名单原因")
    fingerprint = Column(String(128), comment="问题指纹")
    metadata_ = Column("metadata", JSON, comment="扩展元数据")
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )

    __table_args__ = (
        Index("idx_issue_scan_id", "scan_id"),
        Index("idx_issue_result_id", "result_id"),
        Index("idx_issue_gate_type", "gate_type"),
        Index("idx_issue_severity", "severity"),
        Index("idx_issue_rule_id", "rule_id"),
        Index("idx_issue_fingerprint", "fingerprint"),
        Index("idx_issue_is_whitelisted", "is_whitelisted"),
        Index("idx_issue_scan_severity", "scan_id", "severity"),
        Index("idx_issue_scan_gate", "scan_id", "gate_type"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

"""扫描任务数据模型"""
from sqlalchemy import (
    Column, BigInteger, String, Integer, Text, DateTime, func, Index
)
from src.core.database import Base


class ScanTask(Base):
    """扫描任务表"""
    __tablename__ = "scan_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(64), unique=True, nullable=False, comment="扫描唯一标识")
    project_id = Column(String(128), nullable=False, comment="GitLab项目ID")
    project_name = Column(String(256), nullable=False, comment="项目名称")
    project_url = Column(String(512), comment="项目仓库地址")
    trigger_type = Column(String(32), nullable=False, comment="触发类型")
    trigger_ref = Column(String(256), comment="触发引用")
    trigger_user = Column(String(128), comment="触发用户")
    commit_sha = Column(String(64), comment="提交SHA")
    commit_message = Column(Text, comment="提交信息")
    scan_status = Column(
        String(32), nullable=False, default="pending", comment="扫描状态"
    )
    gate_status = Column(String(32), comment="门禁结果")
    total_gates = Column(Integer, nullable=False, default=0, comment="门禁总数")
    passed_gates = Column(Integer, nullable=False, default=0, comment="通过门禁数")
    failed_gates = Column(Integer, nullable=False, default=0, comment="失败门禁数")
    skipped_gates = Column(Integer, nullable=False, default=0, comment="跳过门禁数")
    total_issues = Column(Integer, nullable=False, default=0, comment="问题总数")
    critical_issues = Column(Integer, nullable=False, default=0, comment="严重问题数")
    high_issues = Column(Integer, nullable=False, default=0, comment="高危问题数")
    medium_issues = Column(Integer, nullable=False, default=0, comment="中危问题数")
    low_issues = Column(Integer, nullable=False, default=0, comment="低危问题数")
    report_url = Column(String(512), comment="HTML报告地址")
    report_json = Column(Text, comment="JSON报告内容")
    error_message = Column(Text, comment="错误信息")
    started_at = Column(DateTime, comment="扫描开始时间")
    completed_at = Column(DateTime, comment="扫描完成时间")
    duration_seconds = Column(Integer, comment="扫描耗时")
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    __table_args__ = (
        Index("idx_project_id", "project_id"),
        Index("idx_trigger_type", "trigger_type"),
        Index("idx_scan_status", "scan_status"),
        Index("idx_gate_status", "gate_status"),
        Index("idx_created_at", "created_at"),
        Index("idx_project_created", "project_id", created_at.desc()),
        Index("idx_project_status", "project_id", "scan_status"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

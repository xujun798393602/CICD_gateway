"""扫描结果数据模型"""
from sqlalchemy import (
    Column, BigInteger, String, Integer, Text, DateTime, func, Index
)
from src.core.database import Base


class ScanResult(Base):
    """扫描结果表"""
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(64), nullable=False, comment="关联扫描任务ID")
    gate_type = Column(String(64), nullable=False, comment="门禁类型")
    gate_name = Column(String(128), nullable=False, comment="门禁名称")
    gate_version = Column(String(32), comment="门禁脚本版本")
    execution_status = Column(
        String(32), nullable=False, default="pending", comment="执行状态"
    )
    gate_result = Column(String(32), comment="门禁结果")
    total_issues = Column(Integer, nullable=False, default=0, comment="发现问题数")
    critical_issues = Column(Integer, nullable=False, default=0, comment="严重问题数")
    high_issues = Column(Integer, nullable=False, default=0, comment="高危问题数")
    medium_issues = Column(Integer, nullable=False, default=0, comment="中危问题数")
    low_issues = Column(Integer, nullable=False, default=0, comment="低危问题数")
    scanned_files = Column(Integer, nullable=False, default=0, comment="扫描文件数")
    total_lines = Column(BigInteger, nullable=False, default=0, comment="扫描代码行数")
    output_log = Column(Text, comment="脚本输出日志")
    error_log = Column(Text, comment="错误日志")
    exit_code = Column(Integer, comment="脚本退出码")
    error_message = Column(String(1024), comment="错误信息")
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    duration_seconds = Column(Integer, comment="执行耗时")
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
        Index("idx_scan_id", "scan_id"),
        Index("idx_gate_type", "gate_type"),
        Index("idx_execution_status", "execution_status"),
        Index("idx_gate_result", "gate_result"),
        Index("idx_scan_gate", "scan_id", "gate_type"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

"""门禁配置数据模型"""
from sqlalchemy import (
    Column, String, Integer, Boolean, Text, DateTime, JSON, func, Index,
    UniqueConstraint,
)
from src.core.database import Base


class GateConfig(Base):
    """门禁配置表"""
    __tablename__ = "gate_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(String(64), unique=True, nullable=False, comment="配置唯一标识")
    project_id = Column(String(128), comment="项目ID（NULL表示全局配置）")
    gate_type = Column(String(64), nullable=False, comment="门禁类型")
    gate_name = Column(String(128), nullable=False, comment="门禁名称")
    description = Column(Text, comment="配置描述")
    enabled = Column(Boolean, nullable=False, default=True, comment="是否启用")
    severity_threshold = Column(
        String(32), nullable=False, default="high", comment="阻断阈值"
    )
    timeout_seconds = Column(
        Integer, nullable=False, default=600, comment="超时时间"
    )
    retry_count = Column(Integer, nullable=False, default=0, comment="重试次数")
    config_data = Column(JSON, nullable=False, comment="门禁配置数据")
    script_path = Column(String(512), comment="脚本路径")
    script_version = Column(String(32), comment="脚本版本")
    execution_order = Column(
        Integer, nullable=False, default=100, comment="执行顺序"
    )
    created_by = Column(String(128), comment="创建人")
    updated_by = Column(String(128), comment="更新人")
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
        Index("idx_config_project_id", "project_id"),
        Index("idx_config_gate_type", "gate_type"),
        Index("idx_config_enabled", "enabled"),
        Index("idx_config_project_gate", "project_id", "gate_type"),
        UniqueConstraint("project_id", "gate_type", name="uk_project_gate_type"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

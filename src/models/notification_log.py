"""通知记录数据模型"""
from sqlalchemy import (
    Column, BigInteger, String, Integer, Text, DateTime, func, Index
)
from src.core.database import Base


class NotificationLog(Base):
    """通知记录表"""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_id = Column(
        String(64), unique=True, nullable=False, comment="通知唯一标识"
    )
    scan_id = Column(String(64), nullable=False, comment="关联扫描任务ID")
    notification_type = Column(String(32), nullable=False, comment="通知类型")
    recipient = Column(String(512), nullable=False, comment="接收人")
    subject = Column(String(512), comment="通知主题")
    content = Column(Text, nullable=False, comment="通知内容")
    content_type = Column(
        String(32), nullable=False, default="text", comment="内容类型"
    )
    send_status = Column(
        String(32), nullable=False, default="pending", comment="发送状态"
    )
    retry_count = Column(Integer, nullable=False, default=0, comment="已重试次数")
    max_retries = Column(Integer, nullable=False, default=3, comment="最大重试次数")
    error_message = Column(Text, comment="错误信息")
    response_code = Column(Integer, comment="响应状态码")
    response_body = Column(Text, comment="响应内容")
    sent_at = Column(DateTime, comment="发送时间")
    next_retry_at = Column(DateTime, comment="下次重试时间")
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
        Index("idx_notif_scan_id", "scan_id"),
        Index("idx_notif_type", "notification_type"),
        Index("idx_notif_send_status", "send_status"),
        Index("idx_notif_next_retry", "next_retry_at"),
        Index("idx_notif_scan_type", "scan_id", "notification_type"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

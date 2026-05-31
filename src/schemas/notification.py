"""通知相关Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class NotificationSendRequest(BaseModel):
    """通知发送请求"""
    scan_id: str = Field(..., description="扫描任务ID")
    channels: Optional[List[str]] = Field(None, description="通知渠道")
    recipients: Optional[Dict[str, List[str]]] = Field(None, description="自定义接收人")
    template: str = Field("default", description="通知模板")
    custom_message: Optional[str] = Field(None, description="自定义消息")
    force: bool = Field(False, description="是否强制发送")


class ChannelResult(BaseModel):
    """渠道发送结果"""
    channel: str
    status: str
    recipients_count: Optional[int] = None
    comment_id: Optional[int] = None


class NotificationSendResponse(BaseModel):
    """通知发送响应"""
    notification_id: str
    channels: List[ChannelResult] = []


class NotificationConfigRequest(BaseModel):
    """通知配置更新请求"""
    enabled: Optional[bool] = None
    channels: Optional[Dict[str, Any]] = None
    schedule: Optional[Dict[str, Any]] = None


class NotificationConfigResponse(BaseModel):
    """通知配置响应"""
    project_id: str
    enabled: bool = True
    channels: Dict[str, Any] = {}
    schedule: Dict[str, Any] = {}

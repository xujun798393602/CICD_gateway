"""配置相关Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ScannerConfig(BaseModel):
    """扫描器配置"""
    enabled: bool = True
    timeout: int = 300


class NotificationChannelConfig(BaseModel):
    """通知渠道配置"""
    enabled: bool = False
    recipients: Optional[List[str]] = None


class NotificationConfig(BaseModel):
    """通知配置"""
    enabled: bool = True
    channels: Dict[str, NotificationChannelConfig] = {}


class GateConfigData(BaseModel):
    """门禁配置数据"""
    scanners: Dict[str, ScannerConfig] = {}
    notifications: NotificationConfig = NotificationConfig()
    settings: Dict[str, Any] = {}


class ConfigResponse(BaseModel):
    """配置响应"""
    project_id: str
    config_version: str = "1.0.0"
    config: GateConfigData


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    config: Dict[str, Any] = Field(..., description="配置内容")
    comment: Optional[str] = Field(None, description="变更说明")


class ConfigUpdateResponse(BaseModel):
    """配置更新响应"""
    project_id: str
    config_version: str
    changes: List[Dict[str, Any]] = []


class ScannerRegisterRequest(BaseModel):
    """扫描器注册请求"""
    scanner_id: str = Field(..., description="扫描器ID")
    name: str = Field(..., description="显示名称")
    description: str = Field(..., description="描述")
    version: str = Field(..., description="版本号")
    category: str = Field(..., description="类别")
    entry_point: str = Field(..., description="入口脚本路径")
    timeout: int = Field(600, description="超时时间")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="配置Schema")
    default_config: Optional[Dict[str, Any]] = Field(None, description="默认配置")


class ScannerInfo(BaseModel):
    """扫描器信息"""
    scanner_id: str
    name: str
    version: str
    category: str
    status: str = "active"


class ScannerListResponse(BaseModel):
    """扫描器列表响应"""
    total: int
    scanners: List[ScannerInfo] = []

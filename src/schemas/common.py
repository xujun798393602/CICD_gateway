"""通用Schema定义"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    errors: Optional[List[Dict[str, str]]] = None
    timestamp: datetime
    request_id: Optional[str] = None


class SuccessResponse(BaseModel):
    """成功响应"""
    code: int = 0
    message: str = "success"
    data: Any
    timestamp: Optional[datetime] = None
    request_id: Optional[str] = None


class HealthStatus(BaseModel):
    """健康状态"""
    status: str  # healthy/degraded/unhealthy
    version: str
    components: Dict[str, str] = {}


class MetricsResponse(BaseModel):
    """指标响应"""
    scan_total: int = 0
    scan_success_rate: float = 0.0
    avg_scan_duration: float = 0.0
    active_scans: int = 0

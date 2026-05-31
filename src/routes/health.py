"""辅助接口路由"""
from fastapi import APIRouter

from src.core.config import settings
from src.schemas.common import SuccessResponse, HealthStatus, MetricsResponse

router = APIRouter()


@router.get("/health", response_model=SuccessResponse)
async def health_check():
    """健康检查"""
    health = HealthStatus(
        status="healthy",
        version=settings.APP_VERSION,
        components={
            "database": "healthy",
            "cache": "healthy",
            "storage": "healthy",
        },
    )
    return SuccessResponse(data=health.model_dump())


@router.get("/metrics", response_model=SuccessResponse)
async def get_metrics():
    """获取系统指标"""
    metrics = MetricsResponse(
        scan_total=0,
        scan_success_rate=0.0,
        avg_scan_duration=0.0,
        active_scans=0,
    )
    return SuccessResponse(data=metrics.model_dump())

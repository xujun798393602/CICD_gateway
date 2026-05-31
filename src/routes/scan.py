"""扫描管理路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.scan import (
    ScanTriggerRequest,
    ScanResultRequest,
)
from src.schemas.common import SuccessResponse
from src.services.scan_service import ScanService

router = APIRouter()


@router.post("/scans/trigger", response_model=SuccessResponse)
async def trigger_scan(
    request: ScanTriggerRequest,
    db: AsyncSession = Depends(get_db),
):
    """触发门禁扫描"""
    service = ScanService(db)
    result = await service.trigger_scan(request)
    return SuccessResponse(
        data=result,
        timestamp=result["created_at"],
    )


@router.get("/scans/{scan_id}/status", response_model=SuccessResponse)
async def get_scan_status(
    scan_id: str,
    include_details: bool = False,
    wait: bool = False,
    timeout: int = 600,
    db: AsyncSession = Depends(get_db),
):
    """查询扫描状态"""
    service = ScanService(db)
    result = await service.get_scan_status(scan_id)
    if not result:
        raise HTTPException(status_code=404, detail="扫描任务不存在")
    return SuccessResponse(data=result)


@router.post("/scans/{scan_id}/results", response_model=SuccessResponse)
async def report_scan_result(
    scan_id: str,
    request: ScanResultRequest,
    db: AsyncSession = Depends(get_db),
):
    """上报扫描结果"""
    service = ScanService(db)
    result = await service.report_scan_result(scan_id, request)
    if not result:
        raise HTTPException(status_code=404, detail="扫描任务不存在")
    return SuccessResponse(data=result)

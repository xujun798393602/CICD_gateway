"""报告服务路由"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.core.database import get_db
from src.schemas.report import (
    ReportGenerateRequest,
    ReportResponse,
    ReportListResponse,
)
from src.schemas.common import SuccessResponse
from src.services.report_service import ReportService

router = APIRouter()


@router.post("/reports/generate", response_model=SuccessResponse)
async def generate_report(
    request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """生成扫描报告"""
    service = ReportService(db)
    result = await service.generate_report(
        scan_id=request.scan_id,
        report_type=request.report_type,
        format=request.format,
        options=request.options,
    )
    if not result:
        raise HTTPException(status_code=404, detail="扫描任务不存在")
    return SuccessResponse(data=result)


@router.get("/reports/{report_id}", response_model=SuccessResponse)
async def get_report(
    report_id: str,
    include_content: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """查询报告详情"""
    service = ReportService(db)
    result = await service.get_report(report_id, include_content)
    if not result:
        raise HTTPException(status_code=404, detail="报告不存在")
    return SuccessResponse(data=result)


@router.get("/reports", response_model=SuccessResponse)
async def list_reports(
    project_id: str = Query(..., description="项目ID"),
    branch: Optional[str] = Query(None, description="分支过滤"),
    status: Optional[str] = Query(None, description="状态过滤"),
    gate_result: Optional[str] = Query(None, description="门禁结果过滤"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """查询报告列表"""
    service = ReportService(db)
    result = await service.list_reports(
        project_id=project_id,
        branch=branch,
        status=status,
        gate_result=gate_result,
        page=page,
        page_size=page_size,
    )
    return SuccessResponse(data=result)

"""配置管理路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.config import (
    ConfigUpdateRequest,
    ScannerRegisterRequest,
)
from src.schemas.common import SuccessResponse
from src.services.config_service import ConfigService

router = APIRouter()


@router.get("/configs/{project_id}", response_model=SuccessResponse)
async def get_config(
    project_id: str,
    merged: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """查询项目配置"""
    service = ConfigService(db)
    result = await service.get_config(project_id, merged)
    return SuccessResponse(data=result)


@router.put("/configs/{project_id}", response_model=SuccessResponse)
async def update_config(
    project_id: str,
    request: ConfigUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新项目配置"""
    service = ConfigService(db)
    result = await service.update_config(
        project_id=project_id,
        config=request.config,
        comment=request.comment,
    )
    return SuccessResponse(data=result)


@router.post("/scanners/register", response_model=SuccessResponse)
async def register_scanner(
    request: ScannerRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """注册门禁脚本"""
    service = ConfigService(db)
    try:
        result = await service.register_scanner(request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return SuccessResponse(data=result)


@router.get("/scanners", response_model=SuccessResponse)
async def list_scanners(
    category: str = None,
    status: str = None,
    db: AsyncSession = Depends(get_db),
):
    """查询扫描器列表"""
    service = ConfigService(db)
    result = await service.list_scanners(category, status)
    return SuccessResponse(data=result)

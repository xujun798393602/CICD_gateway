"""通知服务路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.notification import (
    NotificationSendRequest,
    NotificationConfigRequest,
)
from src.schemas.common import SuccessResponse
from src.services.notification_service import NotificationService

router = APIRouter()


@router.post("/notifications/send", response_model=SuccessResponse)
async def send_notification(
    request: NotificationSendRequest,
    db: AsyncSession = Depends(get_db),
):
    """发送通知"""
    service = NotificationService(db)
    result = await service.send_notification(
        scan_id=request.scan_id,
        channels=request.channels,
        recipients=request.recipients,
        template=request.template,
        custom_message=request.custom_message,
        force=request.force,
    )
    if not result:
        raise HTTPException(status_code=404, detail="扫描任务不存在")
    return SuccessResponse(data=result)


@router.get("/notifications/config/{project_id}", response_model=SuccessResponse)
async def get_notification_config(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """查询通知配置"""
    service = NotificationService(db)
    result = await service.get_notification_config(project_id)
    return SuccessResponse(data=result)


@router.put("/notifications/config/{project_id}", response_model=SuccessResponse)
async def update_notification_config(
    project_id: str,
    request: NotificationConfigRequest,
    db: AsyncSession = Depends(get_db),
):
    """更新通知配置"""
    service = NotificationService(db)
    config_data = request.model_dump(exclude_none=True)
    result = await service.update_notification_config(project_id, config_data)
    return SuccessResponse(data=result)

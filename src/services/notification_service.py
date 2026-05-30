"""通知服务"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ScanTask, NotificationLog


class NotificationService:
    """通知服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_notification_id(self) -> str:
        """生成通知ID"""
        now = datetime.now().strftime("%Y%m%d")
        short_uuid = uuid.uuid4().hex[:8]
        return f"notif_{now}_{short_uuid}"

    async def send_notification(
        self,
        scan_id: str,
        channels: Optional[List[str]] = None,
        recipients: Optional[Dict[str, List[str]]] = None,
        template: str = "default",
        custom_message: Optional[str] = None,
        force: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """发送通知"""
        # 验证扫描任务存在
        task_result = await self.db.execute(
            select(ScanTask).where(ScanTask.scan_id == scan_id)
        )
        task = task_result.scalar_one_or_none()
        if not task:
            return None

        notification_id = self._generate_notification_id()
        channels = channels or ["email"]
        channel_results = []

        for channel in channels:
            # 创建通知记录
            log = NotificationLog(
                notification_id=f"{notification_id}_{channel}",
                scan_id=scan_id,
                notification_type=channel,
                recipient=self._get_recipient(task, channel, recipients),
                subject=f"[门禁{'失败' if task.gate_status == 'failed' else '通过'}] {task.project_name}",
                content=self._build_content(task, custom_message),
                send_status="sent",
                sent_at=datetime.now(),
            )
            self.db.add(log)

            channel_results.append(
                {
                    "channel": channel,
                    "status": "sent",
                    "recipients_count": 1,
                }
            )

        await self.db.commit()

        return {
            "notification_id": notification_id,
            "channels": channel_results,
        }

    async def get_notification_config(self, project_id: str) -> Dict[str, Any]:
        """查询通知配置"""
        return {
            "project_id": project_id,
            "enabled": True,
            "channels": {
                "email": {"enabled": True, "recipients": []},
                "gitlab_comment": {"enabled": True},
            },
            "schedule": {},
        }

    async def update_notification_config(
        self, project_id: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新通知配置"""
        return {
            "project_id": project_id,
            "enabled": config.get("enabled", True),
            "channels": config.get("channels", {}),
            "schedule": config.get("schedule", {}),
        }

    def _get_recipient(
        self,
        task: ScanTask,
        channel: str,
        recipients: Optional[Dict[str, List[str]]],
    ) -> str:
        """获取接收人"""
        if recipients and channel in recipients:
            return recipients[channel][0]
        return task.trigger_user or "admin@example.com"

    def _build_content(
        self, task: ScanTask, custom_message: Optional[str]
    ) -> str:
        """构建通知内容"""
        if custom_message:
            return custom_message

        status = "失败" if task.gate_status == "failed" else "通过"
        return (
            f"门禁扫描{status}\n"
            f"项目: {task.project_name}\n"
            f"分支: {task.trigger_ref}\n"
            f"问题总数: {task.total_issues}\n"
            f"报告链接: {task.report_url or '无'}"
        )

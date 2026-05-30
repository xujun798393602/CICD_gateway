"""通知服务模块测试"""
import pytest
from httpx import AsyncClient


class TestNotificationSend:
    """测试通知发送接口 POST /api/v1/notifications/send"""

    @pytest.mark.asyncio
    async def test_send_notification_success(
        self, client: AsyncClient, sample_scan_task
    ):
        """TC-009-HP-01: 发送通知成功"""
        response = await client.post(
            "/api/v1/notifications/send",
            json={
                "scan_id": sample_scan_task.scan_id,
                "channels": ["email"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "notification_id" in data["data"]

    @pytest.mark.asyncio
    async def test_send_notification_scan_not_found(self, client: AsyncClient):
        """TC-发送通知时扫描任务不存在"""
        response = await client.post(
            "/api/v1/notifications/send",
            json={
                "scan_id": "nonexistent_scan_id",
                "channels": ["email"],
            },
        )
        assert response.status_code == 404


class TestNotificationConfig:
    """测试通知配置接口"""

    @pytest.mark.asyncio
    async def test_get_notification_config(self, client: AsyncClient):
        """TC-查询通知配置"""
        response = await client.get("/api/v1/notifications/config/proj_001")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["project_id"] == "proj_001"

    @pytest.mark.asyncio
    async def test_update_notification_config(self, client: AsyncClient):
        """TC-更新通知配置"""
        response = await client.put(
            "/api/v1/notifications/config/proj_001",
            json={
                "config": {
                    "enabled": True,
                    "channels": {
                        "email": {
                            "enabled": True,
                            "recipients": ["admin@example.com"],
                        }
                    },
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

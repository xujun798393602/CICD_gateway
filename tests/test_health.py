"""辅助接口测试"""
import pytest
from httpx import AsyncClient


class TestHealthCheck:
    """测试健康检查接口 GET /api/v1/health"""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """TC-健康检查"""
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] in ["healthy", "degraded", "unhealthy"]
        assert "version" in data["data"]
        assert "components" in data["data"]


class TestMetrics:
    """测试指标接口 GET /api/v1/metrics"""

    @pytest.mark.asyncio
    async def test_get_metrics(self, client: AsyncClient):
        """TC-获取系统指标"""
        response = await client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

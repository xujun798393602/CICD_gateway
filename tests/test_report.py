"""报告服务模块测试"""
import pytest
from httpx import AsyncClient


class TestReportGenerate:
    """测试报告生成接口 POST /api/v1/reports/generate"""

    @pytest.mark.asyncio
    async def test_generate_report_success(
        self, client: AsyncClient, sample_scan_task
    ):
        """TC-008-HP-01: 生成报告成功"""
        response = await client.post(
            "/api/v1/reports/generate",
            json={
                "scan_id": sample_scan_task.scan_id,
                "report_type": "full",
                "format": "html",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "report_id" in data["data"]
        assert data["data"]["format"] == "html"

    @pytest.mark.asyncio
    async def test_generate_report_scan_not_found(self, client: AsyncClient):
        """TC-生成报告时扫描任务不存在"""
        response = await client.post(
            "/api/v1/reports/generate",
            json={
                "scan_id": "nonexistent_scan_id",
                "report_type": "full",
                "format": "html",
            },
        )
        assert response.status_code == 404


class TestReportQuery:
    """测试报告查询接口"""

    @pytest.mark.asyncio
    async def test_get_report_success(self, client: AsyncClient, sample_scan_task):
        """TC-008-HP-03: 查询报告详情"""
        # 先生成报告
        gen_response = await client.post(
            "/api/v1/reports/generate",
            json={"scan_id": sample_scan_task.scan_id},
        )
        report_id = gen_response.json()["data"]["report_id"]

        # 查询报告
        response = await client.get(f"/api/v1/reports/{report_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["report_id"] == report_id

    @pytest.mark.asyncio
    async def test_get_report_not_found(self, client: AsyncClient):
        """TC-查询不存在的报告"""
        response = await client.get("/api/v1/reports/nonexistent_report_id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_reports(self, client: AsyncClient, sample_scan_task):
        """TC-查询报告列表"""
        # 先生成报告
        await client.post(
            "/api/v1/reports/generate",
            json={"scan_id": sample_scan_task.scan_id},
        )

        # 查询报告列表
        response = await client.get(
            "/api/v1/reports",
            params={"project_id": "proj_001", "page": 1, "page_size": 20},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert data["data"]["total"] >= 1

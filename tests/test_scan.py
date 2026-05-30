"""扫描管理模块测试"""
import pytest
from httpx import AsyncClient
from datetime import datetime


class TestScanTrigger:
    """测试扫描触发接口 POST /api/v1/scans/trigger"""

    @pytest.mark.asyncio
    async def test_trigger_scan_success(self, client: AsyncClient):
        """TC-005-HP-01: 正常触发扫描"""
        response = await client.post(
            "/api/v1/scans/trigger",
            json={
                "project_id": "proj_001",
                "repository_url": "https://gitlab.example.com/proj_001",
                "branch": "main",
                "commit_sha": "abc123def456",
                "trigger_type": "push",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "scan_id" in data["data"]
        assert data["data"]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_trigger_scan_mr(self, client: AsyncClient):
        """TC-006-HP-01: MR触发扫描"""
        response = await client.post(
            "/api/v1/scans/trigger",
            json={
                "project_id": "proj_001",
                "repository_url": "https://gitlab.example.com/proj_001",
                "branch": "feature/login",
                "commit_sha": "def456abc789",
                "trigger_type": "merge_request",
                "merge_request_id": 123,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "scan_id" in data["data"]

    @pytest.mark.asyncio
    async def test_trigger_scan_missing_required_field(self, client: AsyncClient):
        """TC-触发扫描缺少必填字段"""
        response = await client.post(
            "/api/v1/scans/trigger",
            json={
                "project_id": "proj_001",
                # 缺少 repository_url, branch, commit_sha, trigger_type
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_trigger_scan_invalid_trigger_type(self, client: AsyncClient):
        """TC-触发扫描无效触发类型"""
        response = await client.post(
            "/api/v1/scans/trigger",
            json={
                "project_id": "proj_001",
                "repository_url": "https://gitlab.example.com/proj_001",
                "branch": "main",
                "commit_sha": "abc123",
                "trigger_type": "invalid_type",
            },
        )
        assert response.status_code == 422


class TestScanStatus:
    """测试扫描状态查询接口 GET /api/v1/scans/{scan_id}/status"""

    @pytest.mark.asyncio
    async def test_get_scan_status_success(self, client: AsyncClient, sample_scan_task):
        """TC-查询扫描状态成功"""
        response = await client.get(
            f"/api/v1/scans/{sample_scan_task.scan_id}/status"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["scan_id"] == sample_scan_task.scan_id
        assert data["data"]["status"] in [
            "pending", "running", "completed", "failed", "timeout"
        ]

    @pytest.mark.asyncio
    async def test_get_scan_status_not_found(self, client: AsyncClient):
        """TC-查询不存在的扫描状态"""
        response = await client.get("/api/v1/scans/nonexistent_scan_id/status")
        assert response.status_code == 404


class TestScanResult:
    """测试扫描结果上报接口 POST /api/v1/scans/{scan_id}/results"""

    @pytest.mark.asyncio
    async def test_report_result_success(
        self, client: AsyncClient, sample_scan_task
    ):
        """TC-001-HP-01: 上报扫描结果成功"""
        response = await client.post(
            f"/api/v1/scans/{sample_scan_task.scan_id}/results",
            json={
                "scanner_id": "vulnerability_scanner",
                "scanner_version": "1.0.0",
                "status": "success",
                "started_at": "2026-05-31T10:00:00Z",
                "completed_at": "2026-05-31T10:05:00Z",
                "duration_ms": 300000,
                "summary": {
                    "total_issues": 2,
                    "critical_issues": 1,
                    "high_issues": 1,
                    "scanned_files": 10,
                    "total_lines": 1000,
                },
                "issues": [
                    {
                        "id": "issue_001",
                        "severity": "critical",
                        "category": "vulnerability",
                        "title": "SQL注入漏洞",
                        "description": "直接拼接用户输入构造SQL语句",
                        "file_path": "src/dao/UserDao.java",
                        "line_number": 45,
                        "rule_id": "SQL_INJECTION_001",
                    }
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "result_id" in data["data"]
        assert data["data"]["scan_id"] == sample_scan_task.scan_id

    @pytest.mark.asyncio
    async def test_report_result_scan_not_found(self, client: AsyncClient):
        """TC-上报结果到不存在的扫描任务"""
        response = await client.post(
            "/api/v1/scans/nonexistent_scan_id/results",
            json={
                "scanner_id": "vulnerability_scanner",
                "scanner_version": "1.0.0",
                "status": "success",
                "started_at": "2026-05-31T10:00:00Z",
                "completed_at": "2026-05-31T10:05:00Z",
                "duration_ms": 300000,
                "summary": {"total_issues": 0},
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_report_result_with_failed_status(
        self, client: AsyncClient, sample_scan_task
    ):
        """TC-001-EP-01: 上报失败状态的扫描结果"""
        response = await client.post(
            f"/api/v1/scans/{sample_scan_task.scan_id}/results",
            json={
                "scanner_id": "vulnerability_scanner",
                "scanner_version": "1.0.0",
                "status": "failed",
                "started_at": "2026-05-31T10:00:00Z",
                "completed_at": "2026-05-31T10:00:30Z",
                "duration_ms": 30000,
                "summary": {"total_issues": 0},
                "error_message": "扫描工具未安装",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

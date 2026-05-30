"""配置管理模块测试"""
import pytest
from httpx import AsyncClient


class TestConfigQuery:
    """测试配置查询接口 GET /api/v1/configs/{project_id}"""

    @pytest.mark.asyncio
    async def test_get_global_config(self, client: AsyncClient, sample_gate_config):
        """TC-010-HP-03: 查询全局配置"""
        response = await client.get("/api/v1/configs/_global")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["project_id"] == "_global"

    @pytest.mark.asyncio
    async def test_get_project_config(self, client: AsyncClient):
        """TC-查询项目配置（不存在时返回默认）"""
        response = await client.get("/api/v1/configs/proj_new")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestConfigUpdate:
    """测试配置更新接口 PUT /api/v1/configs/{project_id}"""

    @pytest.mark.asyncio
    async def test_update_config_success(self, client: AsyncClient):
        """TC-010-HP-01: 更新全局配置"""
        response = await client.put(
            "/api/v1/configs/_global",
            json={
                "config": {
                    "gates": {
                        "vulnerability": {"timeout_seconds": 600}
                    }
                },
                "comment": "增加漏洞扫描超时时间",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "config_version" in data["data"]

    @pytest.mark.asyncio
    async def test_update_project_config(self, client: AsyncClient):
        """TC-010-HP-02: 更新项目配置"""
        response = await client.put(
            "/api/v1/configs/proj_001",
            json={
                "config": {
                    "gates": {
                        "hardcode": {"enabled": False},
                        "vulnerability": {"severity_threshold": "critical"},
                    }
                }
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestScannerRegistration:
    """测试扫描器注册接口"""

    @pytest.mark.asyncio
    async def test_register_scanner(self, client: AsyncClient):
        """TC-011-HP-01: 注册新扫描器"""
        response = await client.post(
            "/api/v1/scanners/register",
            json={
                "scanner_id": "custom_security_scanner",
                "name": "自定义安全扫描器",
                "description": "自定义安全扫描脚本",
                "version": "1.0.0",
                "category": "custom",
                "entry_point": "scripts/custom-security-scan.sh",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["scanner_id"] == "custom_security_scanner"

    @pytest.mark.asyncio
    async def test_list_scanners(self, client: AsyncClient):
        """TC-查询扫描器列表"""
        # 先注册一个扫描器
        await client.post(
            "/api/v1/scanners/register",
            json={
                "scanner_id": "test_scanner",
                "name": "测试扫描器",
                "description": "测试用",
                "version": "1.0.0",
                "category": "test",
                "entry_point": "scripts/test.sh",
            },
        )

        # 查询列表
        response = await client.get("/api/v1/scanners")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1

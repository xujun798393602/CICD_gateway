"""配置管理服务"""
import uuid
from typing import Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import GateConfig


class ConfigService:
    """配置管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_config_id(self) -> str:
        """生成配置ID"""
        short_uuid = uuid.uuid4().hex[:8]
        return f"cfg_{short_uuid}"

    async def get_config(
        self, project_id: str, merged: bool = True
    ) -> Dict[str, Any]:
        """查询项目配置"""
        # 查询项目级配置
        result = await self.db.execute(
            select(GateConfig).where(GateConfig.project_id == project_id)
        )
        configs = result.scalars().all()

        # 如果没有项目级配置且需要合并，查询全局配置
        if not configs and merged:
            result = await self.db.execute(
                select(GateConfig).where(GateConfig.project_id.is_(None))
            )
            configs = result.scalars().all()

        # 构建配置数据
        config_data = {"scanners": {}, "notifications": {}, "settings": {}}
        for cfg in configs:
            config_data["scanners"][cfg.gate_type] = {
                "enabled": cfg.enabled,
                "timeout": cfg.timeout_seconds,
                "severity_threshold": cfg.severity_threshold,
                **(cfg.config_data or {}),
            }

        return {
            "project_id": project_id,
            "config_version": "1.0.0",
            "config": config_data,
        }

    async def update_config(
        self,
        project_id: str,
        config: Dict[str, Any],
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """更新项目配置"""
        changes = []

        # 处理门禁配置
        gates = config.get("gates", {})
        for gate_type, gate_config in gates.items():
            # 查询现有配置
            result = await self.db.execute(
                select(GateConfig).where(
                    GateConfig.project_id == project_id,
                    GateConfig.gate_type == gate_type,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                # 更新现有配置
                for key, value in gate_config.items():
                    if key == "enabled":
                        old_value = existing.enabled
                        existing.enabled = value
                        changes.append(
                            {
                                "field": f"gates.{gate_type}.enabled",
                                "old_value": old_value,
                                "new_value": value,
                            }
                        )
                    elif key == "timeout_seconds":
                        old_value = existing.timeout_seconds
                        existing.timeout_seconds = value
                        changes.append(
                            {
                                "field": f"gates.{gate_type}.timeout_seconds",
                                "old_value": old_value,
                                "new_value": value,
                            }
                        )
                    elif key == "severity_threshold":
                        old_value = existing.severity_threshold
                        existing.severity_threshold = value
                        changes.append(
                            {
                                "field": f"gates.{gate_type}.severity_threshold",
                                "old_value": old_value,
                                "new_value": value,
                            }
                        )
            else:
                # 创建新配置
                new_config = GateConfig(
                    config_id=self._generate_config_id(),
                    project_id=project_id if project_id != "_global" else None,
                    gate_type=gate_type,
                    gate_name=gate_type,
                    enabled=gate_config.get("enabled", True),
                    severity_threshold=gate_config.get("severity_threshold", "high"),
                    timeout_seconds=gate_config.get("timeout_seconds", 600),
                    config_data=gate_config,
                )
                self.db.add(new_config)
                changes.append(
                    {
                        "field": f"gates.{gate_type}",
                        "old_value": None,
                        "new_value": "created",
                    }
                )

        await self.db.commit()

        return {
            "project_id": project_id,
            "config_version": "1.1.0",
            "changes": changes,
        }

    async def register_scanner(
        self, scanner_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """注册门禁脚本"""
        # 检查是否已存在
        result = await self.db.execute(
            select(GateConfig).where(
                GateConfig.gate_type == scanner_data["scanner_id"]
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"扫描器 {scanner_data['scanner_id']} 已存在")

        config = GateConfig(
            config_id=self._generate_config_id(),
            gate_type=scanner_data["scanner_id"],
            gate_name=scanner_data["name"],
            description=scanner_data.get("description", ""),
            enabled=True,
            severity_threshold="high",
            timeout_seconds=scanner_data.get("timeout", 600),
            config_data=scanner_data.get("default_config", {}),
            script_path=scanner_data.get("entry_point", ""),
            script_version=scanner_data.get("version", "1.0.0"),
        )
        self.db.add(config)
        await self.db.commit()

        return {
            "scanner_id": scanner_data["scanner_id"],
            "version": scanner_data.get("version", "1.0.0"),
            "status": "registered",
        }

    async def list_scanners(
        self,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """查询扫描器列表"""
        query = select(GateConfig)
        if category:
            query = query.where(GateConfig.description.contains(category))

        result = await self.db.execute(query)
        configs = result.scalars().all()

        scanners = []
        for cfg in configs:
            scanners.append(
                {
                    "scanner_id": cfg.gate_type,
                    "name": cfg.gate_name,
                    "version": cfg.script_version or "1.0.0",
                    "category": "custom",
                    "status": "active" if cfg.enabled else "disabled",
                }
            )

        return {
            "total": len(scanners),
            "scanners": scanners,
        }

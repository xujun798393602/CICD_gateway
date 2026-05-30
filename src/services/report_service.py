"""报告生成服务"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ScanTask, ScanResult, IssueDetail


class ReportService:
    """报告生成服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_report_id(self) -> str:
        """生成报告ID"""
        now = datetime.now().strftime("%Y%m%d")
        short_uuid = uuid.uuid4().hex[:8]
        return f"rpt_{now}_{short_uuid}"

    async def generate_report(
        self,
        scan_id: str,
        report_type: str = "full",
        format: str = "html",
        options: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """生成扫描报告"""
        # 验证扫描任务存在
        task_result = await self.db.execute(
            select(ScanTask).where(ScanTask.scan_id == scan_id)
        )
        task = task_result.scalar_one_or_none()
        if not task:
            return None

        report_id = self._generate_report_id()

        # 查询扫描结果
        results = await self.db.execute(
            select(ScanResult).where(ScanResult.scan_id == scan_id)
        )
        scan_results = results.scalars().all()

        # 构建摘要
        gate_passed = task.gate_status == "passed" if task.gate_status else False
        summary = {
            "total_issues": task.total_issues,
            "critical": task.critical_issues,
            "high": task.high_issues,
            "medium": task.medium_issues,
            "low": task.low_issues,
            "gate_passed": gate_passed,
        }

        # 更新任务记录中的report_url
        report_url = f"https://quality-gate.example.com/reports/view/{report_id}"
        task.report_url = report_url
        await self.db.commit()

        return {
            "report_id": report_id,
            "scan_id": scan_id,
            "status": "completed",
            "format": format,
            "download_url": f"https://quality-gate.example.com/reports/download/{report_id}",
            "view_url": report_url,
            "summary": summary,
        }

    async def get_report(
        self, report_id: str, include_content: bool = False
    ) -> Optional[Dict[str, Any]]:
        """查询报告信息"""
        # 通过report_url查找关联的scan_id
        task_result = await self.db.execute(
            select(ScanTask).where(ScanTask.report_url.contains(report_id))
        )
        task = task_result.scalar_one_or_none()
        if not task:
            return None

        gate_passed = task.gate_status == "passed" if task.gate_status else False
        return {
            "report_id": report_id,
            "scan_id": task.scan_id,
            "status": "completed",
            "format": "html",
            "download_url": f"https://quality-gate.example.com/reports/download/{report_id}",
            "view_url": task.report_url,
            "summary": {
                "total_issues": task.total_issues,
                "critical": task.critical_issues,
                "high": task.high_issues,
                "gate_passed": gate_passed,
            },
        }

    async def list_reports(
        self,
        project_id: str,
        branch: Optional[str] = None,
        status: Optional[str] = None,
        gate_result: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """查询报告列表"""
        query = select(ScanTask).where(ScanTask.project_id == project_id)

        if branch:
            query = query.where(ScanTask.trigger_ref == branch)
        if status:
            query = query.where(ScanTask.scan_status == status)
        if gate_result:
            query = query.where(ScanTask.gate_status == gate_result)

        # 计算总数
        count_result = await self.db.execute(query)
        all_tasks = count_result.scalars().all()
        total = len(all_tasks)

        # 分页
        offset = (page - 1) * page_size
        paginated_tasks = all_tasks[offset : offset + page_size]

        items = []
        for task in paginated_tasks:
            if task.report_url:
                report_id = task.report_url.split("/")[-1]
                gate_passed = task.gate_status == "passed" if task.gate_status else False
                items.append(
                    {
                        "report_id": report_id,
                        "status": "completed",
                        "gate_passed": gate_passed,
                        "total_issues": task.total_issues,
                        "view_url": task.report_url,
                    }
                )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items,
        }

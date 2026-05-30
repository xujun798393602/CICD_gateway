"""扫描执行服务"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ScanTask, ScanResult, IssueDetail
from src.schemas.scan import (
    ScanTriggerRequest,
    ScanResultRequest,
    ScanStatusResponse,
    ScannerStatusItem,
)


class ScanService:
    """扫描执行服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_scan_id(self) -> str:
        """生成扫描ID"""
        now = datetime.now().strftime("%Y%m%d")
        short_uuid = uuid.uuid4().hex[:8]
        return f"scan_{now}_{short_uuid}"

    async def trigger_scan(self, request: ScanTriggerRequest) -> Dict[str, Any]:
        """触发门禁扫描"""
        scan_id = self._generate_scan_id()

        task = ScanTask(
            scan_id=scan_id,
            project_id=request.project_id,
            project_name=request.project_id,
            project_url=request.repository_url,
            trigger_type=request.trigger_type.value,
            trigger_ref=request.branch,
            trigger_user=request.metadata.get("user", "") if request.metadata else "",
            commit_sha=request.commit_sha,
            scan_status="pending",
            total_gates=4,
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        return {
            "scan_id": scan_id,
            "status": "pending",
            "created_at": task.created_at.isoformat(),
            "estimated_duration": 300,
        }

    async def get_scan_status(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """查询扫描状态"""
        result = await self.db.execute(
            select(ScanTask).where(ScanTask.scan_id == scan_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            return None

        # 查询各扫描器状态
        scanner_results = await self.db.execute(
            select(ScanResult).where(ScanResult.scan_id == scan_id)
        )
        scanners = scanner_results.scalars().all()

        scanners_status = []
        for sr in scanners:
            scanners_status.append(
                ScannerStatusItem(
                    scanner_id=sr.gate_type,
                    status=sr.execution_status,
                    gate_passed=sr.gate_result == "passed" if sr.gate_result else None,
                    critical_count=sr.critical_issues,
                    high_count=sr.high_issues,
                ).model_dump()
            )

        gate_passed = task.gate_status == "passed" if task.gate_status else None

        return ScanStatusResponse(
            scan_id=task.scan_id,
            status=task.scan_status,
            gate_result=task.gate_status,
            gate_passed=gate_passed,
            scanners_status=scanners_status,
            summary={
                "total_scanners": task.total_gates,
                "completed_scanners": task.passed_gates + task.failed_gates,
                "failed_scanners": task.failed_gates,
                "total_issues": task.total_issues,
                "blocking_issues": task.critical_issues + task.high_issues,
            },
            report_url=task.report_url,
        ).model_dump()

    async def report_scan_result(
        self, scan_id: str, request: ScanResultRequest
    ) -> Optional[Dict[str, Any]]:
        """上报扫描结果"""
        # 验证扫描任务存在
        task_result = await self.db.execute(
            select(ScanTask).where(ScanTask.scan_id == scan_id)
        )
        task = task_result.scalar_one_or_none()
        if not task:
            return None

        # 创建扫描结果记录
        summary = request.summary
        result = ScanResult(
            scan_id=scan_id,
            gate_type=request.scanner_id,
            gate_name=request.scanner_id,
            gate_version=request.scanner_version,
            execution_status=request.status,
            gate_result="failed" if summary.get("total_issues", 0) > 0 else "passed",
            total_issues=summary.get("total_issues", 0),
            critical_issues=summary.get("critical_issues", 0),
            high_issues=summary.get("high_issues", 0),
            medium_issues=summary.get("medium_issues", 0),
            low_issues=summary.get("low_issues", 0),
            scanned_files=summary.get("scanned_files", 0),
            total_lines=summary.get("total_lines", 0),
            error_message=request.error_message,
            started_at=request.started_at,
            completed_at=request.completed_at,
            duration_seconds=request.duration_ms // 1000,
        )
        self.db.add(result)
        await self.db.flush()

        # 创建问题详情记录
        if request.issues:
            for issue in request.issues:
                issue_detail = IssueDetail(
                    scan_id=scan_id,
                    result_id=result.id,
                    gate_type=request.scanner_id,
                    issue_type=issue.category,
                    severity=issue.severity,
                    file_path=issue.file_path,
                    line_number=issue.line_number,
                    message=issue.description,
                    rule_id=issue.rule_id,
                )
                self.db.add(issue_detail)

        # 更新扫描任务统计
        gate_passed = result.gate_result == "passed"
        total_issues = summary.get("total_issues", 0)
        critical_issues = summary.get("critical_issues", 0)
        high_issues = summary.get("high_issues", 0)

        update_values = {
            "scan_status": "running",
            "total_issues": ScanTask.total_issues + total_issues,
            "critical_issues": ScanTask.critical_issues + critical_issues,
            "high_issues": ScanTask.high_issues + high_issues,
        }
        if gate_passed:
            update_values["passed_gates"] = ScanTask.passed_gates + 1
        else:
            update_values["failed_gates"] = ScanTask.failed_gates + 1

        await self.db.execute(
            update(ScanTask)
            .where(ScanTask.scan_id == scan_id)
            .values(**update_values)
        )
        await self.db.commit()

        return {
            "result_id": f"result_{result.id}",
            "scan_id": scan_id,
            "gate_passed": gate_passed,
            "blocking_issues_count": critical_issues + high_issues,
        }

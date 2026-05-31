"""扫描相关Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TriggerType(str, Enum):
    """触发类型"""
    PUSH = "push"
    MERGE_REQUEST = "merge_request"
    SCHEDULE = "schedule"
    MANUAL = "manual"


class ScanStatus(str, Enum):
    """扫描状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class GateResult(str, Enum):
    """门禁结果"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class Severity(str, Enum):
    """严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ExecutionStatus(str, Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


# ========== 请求Schema ==========


class ScanTriggerRequest(BaseModel):
    """扫描触发请求"""
    project_id: str = Field(..., description="项目ID")
    repository_url: str = Field(..., description="Git仓库地址")
    branch: str = Field(..., description="分支名称")
    commit_sha: str = Field(..., description="提交SHA")
    trigger_type: TriggerType = Field(..., description="触发类型")
    merge_request_id: Optional[int] = Field(None, description="MR编号")
    scanners: Optional[List[str]] = Field(None, description="指定扫描器列表")
    callback_url: Optional[str] = Field(None, description="回调地址")
    metadata: Optional[Dict[str, Any]] = Field(None, description="GitLab元数据")


class IssueItem(BaseModel):
    """问题条目"""
    id: str = Field(..., description="问题ID")
    severity: str = Field(..., description="严重级别")
    category: str = Field(..., description="问题类别")
    title: str = Field(..., description="问题标题")
    description: str = Field(..., description="问题描述")
    file_path: str = Field(..., description="文件路径")
    line_number: int = Field(..., description="行号")
    rule_id: str = Field(..., description="规则ID")
    recommendation: Optional[str] = Field(None, description="修复建议")


class ScanResultRequest(BaseModel):
    """扫描结果上报请求"""
    scanner_id: str = Field(..., description="扫描器ID")
    scanner_version: str = Field(..., description="扫描器版本")
    status: str = Field(..., description="状态")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: datetime = Field(..., description="完成时间")
    duration_ms: int = Field(..., description="耗时（毫秒）")
    summary: Dict[str, int] = Field(..., description="扫描摘要")
    issues: Optional[List[IssueItem]] = Field(None, description="问题列表")
    error_message: Optional[str] = Field(None, description="错误信息")


# ========== 响应Schema ==========


class ScanTriggerResponse(BaseModel):
    """扫描触发响应"""
    scan_id: str
    status: str
    created_at: datetime
    estimated_duration: Optional[int] = None


class ScannerStatusItem(BaseModel):
    """扫描器状态条目"""
    scanner_id: str
    status: str
    gate_passed: Optional[bool] = None
    critical_count: int = 0
    high_count: int = 0


class ScanStatusResponse(BaseModel):
    """扫描状态响应"""
    scan_id: str
    status: str
    gate_result: Optional[str] = None
    gate_passed: Optional[bool] = None
    scanners_status: List[ScannerStatusItem] = []
    summary: Dict[str, Any] = {}
    report_url: Optional[str] = None


class ScanResultResponse(BaseModel):
    """扫描结果上报响应"""
    result_id: str
    scan_id: str
    gate_passed: bool
    blocking_issues_count: int

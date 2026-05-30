"""报告相关Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ReportGenerateRequest(BaseModel):
    """报告生成请求"""
    scan_id: str = Field(..., description="扫描任务ID")
    report_type: str = Field("full", description="报告类型：full/summary")
    format: str = Field("html", description="报告格式：html/json/pdf")
    options: Optional[Dict[str, Any]] = Field(None, description="报告选项")


class ReportSummary(BaseModel):
    """报告摘要"""
    total_issues: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    gate_passed: bool = False


class ReportResponse(BaseModel):
    """报告响应"""
    report_id: str
    scan_id: str
    status: str
    format: str
    download_url: Optional[str] = None
    view_url: Optional[str] = None
    summary: Optional[ReportSummary] = None


class ReportListItem(BaseModel):
    """报告列表条目"""
    report_id: str
    status: str
    gate_passed: bool
    total_issues: int
    view_url: Optional[str] = None


class ReportListResponse(BaseModel):
    """报告列表响应"""
    total: int
    page: int
    page_size: int
    items: List[ReportListItem] = []

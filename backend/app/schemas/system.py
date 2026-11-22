from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class NodeHealthStatus(BaseModel):
    node_id: str
    name: str
    role: str
    host: str
    status: str  # "ONLINE" hoặc "OFFLINE"
    latency_ms: Optional[float] = None
    database: Optional[str] = None
    bucket: Optional[str] = None
    error: Optional[str] = None


class SystemHealthData(BaseModel):
    overall_status: str  # "HEALTHY" hoặc "DEGRADED"
    nodes: List[NodeHealthStatus]


class AuditLogItem(BaseModel):
    id: int
    thoi_gian: datetime
    ma_nv_thuc_hien: Optional[str] = None
    ten_nv_thuc_hien: Optional[str] = None
    thao_tac: str
    tac_dong_len_nv: Optional[str] = None
    chi_tiet: Optional[str] = None


class AuditLogPagination(BaseModel):
    items: List[AuditLogItem]
    total: int
    page: int
    page_size: int

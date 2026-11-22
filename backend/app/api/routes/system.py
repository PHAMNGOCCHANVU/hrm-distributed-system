from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.schemas.base import ApiResponse
from app.schemas.auth import CurrentUser
from app.schemas.system import SystemHealthData, AuditLogPagination
from app.api.deps import get_current_user, require_roles
import app.services.system_service as system_service

router = APIRouter(prefix="/system", tags=["System & Monitoring"])


@router.get("/health", response_model=ApiResponse[SystemHealthData])
def get_health():
    """
    Kiểm tra độ trễ (latency ms) và trạng thái Online/Offline của 3 sites CSDL và MinIO.
    Xử lý Graceful Degradation khi có node gặp sự cố.
    """
    health_data = system_service.get_system_health()
    return ApiResponse(
        success=True,
        data=health_data,
        message="Kiểm tra kết nối cụm phân tán hoàn tất"
    )


@router.get("/audit-logs", response_model=ApiResponse[AuditLogPagination])
def get_audit_logs(
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: CurrentUser = Depends(require_roles(3, 4, "Giám đốc", "Tổng giám đốc", "Trưởng phòng"))
):
    """
    Tra cứu nhật ký kiểm toán hệ thống (Audit Trail).
    """
    logs_pagination = system_service.get_audit_trail(
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    return ApiResponse(
        success=True,
        data=logs_pagination,
        message="Lấy nhật ký kiểm toán thành công"
    )

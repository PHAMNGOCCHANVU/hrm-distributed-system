from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status

from app.schemas.base import ApiResponse
from app.schemas.auth import CurrentUser
from app.schemas.admin_request import (
    SystemAdminRequestCreate, SystemAdminApproveRequest, SystemAdminRequestResponse
)
from app.schemas.system import SystemHealthData
from app.api.deps import get_current_user
import app.services.admin_request_service as admin_service
import app.services.system_service as system_service

router = APIRouter(prefix="/system-admin", tags=["System Administration"])


@router.post("/requests", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[SystemAdminRequestResponse])
def create_admin_request(
    payload: SystemAdminRequestCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Cán bộ Phòng Vận hành (SYSTEM_OPERATOR) gửi yêu cầu quản trị kỹ thuật.
    """
    res = admin_service.create_admin_request(payload, current_user)
    return ApiResponse(
        success=True,
        data=res,
        message="Gửi yêu cầu quản trị kỹ thuật thành công"
    )


@router.get("/requests", response_model=ApiResponse[List[SystemAdminRequestResponse]])
def get_admin_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Danh sách các yêu cầu quản trị kỹ thuật.
    """
    items = admin_service.list_admin_requests(status_filter)
    return ApiResponse(
        success=True,
        data=items,
        message="Lấy danh sách yêu cầu quản trị kỹ thuật thành công"
    )


@router.put("/requests/{req_id}/approve", response_model=ApiResponse[SystemAdminRequestResponse])
def approve_admin_request(
    req_id: str,
    payload: SystemAdminApproveRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Lãnh đạo Phê duyệt Yêu cầu Quản trị Kỹ thuật (Tuân thủ Anti-self-approval Rule).
    """
    res = admin_service.approve_admin_request(req_id, payload, current_user)
    return ApiResponse(
        success=True,
        data=res,
        message="Xử lý phê duyệt yêu cầu kỹ thuật thành công"
    )


@router.get("/cluster-health", response_model=ApiResponse[SystemHealthData])
def get_cluster_health(current_user: CurrentUser = Depends(get_current_user)):
    """
    Giám sát sức khỏe cụm CSDL phân tán và MinIO dành cho System Operator & Lãnh đạo.
    """
    health_data = system_service.get_system_health()
    return ApiResponse(
        success=True,
        data=health_data,
        message="Kiểm tra kết nối cụm phân tán hoàn tất"
    )

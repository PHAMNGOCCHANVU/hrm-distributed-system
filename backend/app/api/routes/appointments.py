from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status

from app.schemas.base import ApiResponse
from app.schemas.auth import CurrentUser
from app.schemas.appointment import (
    AppointmentCreateRequest, AppointmentApproveRequest, AppointmentResponse
)
from app.api.deps import get_current_user
import app.services.appointment_service as appointment_service

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[AppointmentResponse])
def create_appointment(
    payload: AppointmentCreateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Đề xuất Bổ nhiệm / Điều chuyển chức vụ nhân sự (Maker).
    """
    res = appointment_service.create_appointment(payload, current_user)
    return ApiResponse(
        success=True,
        data=res,
        message="Tạo đề xuất bổ nhiệm thành công"
    )


@router.get("", response_model=ApiResponse[List[AppointmentResponse]])
def get_appointments(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Tra cứu danh sách phiếu đề xuất bổ nhiệm / điều chuyển.
    """
    items = appointment_service.list_appointments(status_filter)
    return ApiResponse(
        success=True,
        data=items,
        message="Lấy danh sách đề xuất bổ nhiệm thành công"
    )


@router.put("/{decision_id}/approve", response_model=ApiResponse[AppointmentResponse])
def approve_appointment(
    decision_id: str,
    payload: AppointmentApproveRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Lãnh đạo phê duyệt phiếu bổ nhiệm / điều chuyển (Checker).
    """
    res = appointment_service.approve_appointment(decision_id, payload, current_user)
    return ApiResponse(
        success=True,
        data=res,
        message="Xử lý phê duyệt đề xuất bổ nhiệm thành công"
    )

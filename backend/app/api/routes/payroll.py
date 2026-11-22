from typing import Optional, List
from fastapi import APIRouter, Depends, Query

from app.schemas.base import ApiResponse
from app.schemas.auth import CurrentUser
from app.schemas.payroll import (
    PayrollUpdateRequest, PayrollItem, PayrollUpdateResponseData, SalarySlipResponse
)
from app.api.deps import get_current_user
import app.services.payroll_service as payroll_service

router = APIRouter(prefix="/payroll", tags=["Payroll"])


@router.get("", response_model=ApiResponse[List[PayrollItem]])
def get_payrolls(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020),
    branch: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Tra cứu bảng lương hệ thống với thẩm quyền và PII Masking cho Phòng Tài Vụ.
    """
    items = payroll_service.get_payroll_list(
        current_user=current_user,
        month=month,
        year=year,
        branch=branch
    )
    return ApiResponse(
        success=True,
        data=items,
        message="Lấy danh sách bảng lương thành công"
    )


@router.get("/my-slip", response_model=ApiResponse[SalarySlipResponse])
def get_my_salary_slip(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2020),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Xem phiếu lương cá nhân của nhân viên đang đăng nhập.
    """
    slip = payroll_service.get_my_salary_slip(
        current_user=current_user,
        month=month,
        year=year
    )
    return ApiResponse(
        success=True,
        data=slip,
        message="Lấy phiếu lương cá nhân thành công"
    )


@router.put("/{ma_nv}", response_model=ApiResponse[PayrollUpdateResponseData])
def update_payroll(
    ma_nv: str,
    payload: PayrollUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Cập nhật và tính toán lương nhân sự.
    - Tổng giám đốc: Toàn quyền cập nhật bất kỳ nhân sự nào.
    - Giám đốc chi nhánh: Chỉ được cập nhật nhân sự trong chi nhánh mình quản lý (Khác chi nhánh -> 403 Forbidden).
    """
    updated = payroll_service.update_payroll(
        ma_nv=ma_nv,
        payload=payload,
        current_user=current_user
    )
    return ApiResponse(
        success=True,
        data=updated,
        message="Cập nhật và tính toán lương thành công"
    )

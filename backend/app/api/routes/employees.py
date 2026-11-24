import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, Form, File, UploadFile, HTTPException, status
from pydantic import ValidationError

from app.schemas.base import ApiResponse
from app.schemas.auth import CurrentUser
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeListPagination, EmployeeDetailResponse
)
from app.api.deps import get_current_user, require_roles
import app.services.employee_service as employee_service

router = APIRouter(prefix="/employees", tags=["Employees"])


def require_hr_or_executive(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Kiểm tra quyền tạo nhân viên và chặn dứt điểm System Operator."""
    if "SYSTEM_OPERATOR" in current_user.system_roles and not ("HR_SPECIALIST" in current_user.system_roles or "GROUP_EXECUTIVE" in current_user.system_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Quản trị kỹ thuật (System Operator) không có quyền can thiệp vào hồ sơ nhân sự!"}
        )
    if current_user.role_id in [1, 2, 4] or any(r in current_user.system_roles for r in ["HR_SPECIALIST", "GROUP_EXECUTIVE", "BRANCH_DIRECTOR"]):
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code": "FORBIDDEN", "message": "Bạn không có quyền thêm mới hồ sơ nhân sự!"}
    )


@router.get("", response_model=ApiResponse[EmployeeListPagination])
def get_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    branch: Optional[str] = Query(None),
    department_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    kpi_grade: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Tra cứu danh sách nhân sự với lọc, phân trang và tự động áp dụng Data Masking theo Role.
    """
    pagination = employee_service.list_employees(
        current_user=current_user,
        page=page,
        page_size=page_size,
        branch=branch,
        department_id=department_id,
        search=search,
        kpi_grade=kpi_grade
    )
    return ApiResponse(
        success=True,
        data=pagination,
        message="Lấy danh sách nhân viên thành công"
    )


@router.get("/colleagues", response_model=ApiResponse[List[Dict[str, Any]]])
def get_colleagues(current_user: CurrentUser = Depends(get_current_user)):
    """
    Xem danh bạ đồng nghiệp cùng phòng ban (Lương của đồng nghiệp bị MASK 100%).
    """
    colleagues = employee_service.get_colleagues(current_user)
    return ApiResponse(
        success=True,
        data=colleagues,
        message="Lấy danh bạ đồng nghiệp thành công"
    )


@router.get("/{ma_nv}", response_model=ApiResponse[EmployeeDetailResponse])
def get_employee_detail(
    ma_nv: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Lấy chi tiết 1 hồ sơ nhân sự (kỹ năng, KPI, dự án).
    """
    detail = employee_service.get_employee_detail(ma_nv, current_user)
    return ApiResponse(
        success=True,
        data=detail,
        message="Lấy chi tiết hồ sơ nhân sự thành công"
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[Dict[str, Any]])
def create_employee(
    current_user: CurrentUser = Depends(require_hr_or_executive),
    data: str = Form(..., description="Chuỗi JSON serialize từ object EmployeeCreate"),
    avatar: Optional[UploadFile] = File(None, description="Tệp ảnh đại diện"),
    cv_pdf: Optional[UploadFile] = File(None, description="Tệp scan CV PDF")
):
    """
    Thêm mới hồ sơ nhân sự đa mô hình (Multipart Form-Data):
    MinIO S3 + PostgreSQL Shard + JSONB + Compensating Transaction.
    """
    try:
        parsed_data = json.loads(data)
        emp_in = EmployeeCreate.model_validate(parsed_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_JSON", "message": "Trường 'data' không phải chuỗi JSON hợp lệ"}
        )
    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "VALIDATION_ERROR", "message": "Dữ liệu nhân viên không hợp lệ", "details": ve.errors()}
        )

    result = employee_service.create_employee(
        emp_in=emp_in,
        avatar_file=avatar,
        cv_file=cv_pdf,
        current_user=current_user
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Thêm mới hồ sơ nhân sự thành công"
    )


@router.put("/{ma_nv}", response_model=ApiResponse[Dict[str, Any]])
def update_employee(
    ma_nv: str,
    data: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    cv_pdf: Optional[UploadFile] = File(None),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Cập nhật thông tin hồ sơ nhân sự (Kiểm tra Manager Equality Rule).
    """
    emp_update = EmployeeUpdate()
    if data:
        try:
            parsed_data = json.loads(data)
            emp_update = EmployeeUpdate.model_validate(parsed_data)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_JSON", "message": "Trường 'data' không phải chuỗi JSON hợp lệ"}
            )
        except ValidationError as ve:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "VALIDATION_ERROR", "message": "Dữ liệu cập nhật không hợp lệ", "details": ve.errors()}
            )

    result = employee_service.update_employee(
        ma_nv=ma_nv,
        emp_update=emp_update,
        avatar_file=avatar,
        cv_file=cv_pdf,
        current_user=current_user
    )
    return ApiResponse(
        success=True,
        data=result,
        message="Cập nhật hồ sơ nhân sự thành công"
    )

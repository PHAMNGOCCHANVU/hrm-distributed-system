from typing import List
from fastapi import APIRouter, Depends, status

from app.schemas.base import ApiResponse
from app.schemas.auth import CurrentUser
from app.schemas.catalog import (
    DepartmentResponse, PositionResponse, RoleResponse, ProjectCreate, ProjectResponse
)
from app.api.deps import get_current_user, require_roles
import app.repositories.catalog_repo as catalog_repo

router = APIRouter(prefix="/catalogs", tags=["Catalogs"])


@router.get("/departments", response_model=ApiResponse[List[DepartmentResponse]])
def get_departments():
    """Lấy danh mục phòng ban toàn tập đoàn."""
    depts = catalog_repo.get_departments()
    return ApiResponse(
        success=True,
        data=[DepartmentResponse(ma_pb=d["mapb"], ten_pb=d["tenpb"], ma_cn=d["macn"]) for d in depts],
        message="Lấy danh mục phòng ban thành công"
    )


@router.get("/positions", response_model=ApiResponse[List[PositionResponse]])
def get_positions():
    """Lấy danh mục chức vụ."""
    positions = catalog_repo.get_positions()
    return ApiResponse(
        success=True,
        data=[PositionResponse(ma_cv=p["macv"], ten_cv=p["tencv"], he_so_luong=float(p["hesoluong"])) for p in positions],
        message="Lấy danh mục chức vụ thành công"
    )


@router.get("/roles", response_model=ApiResponse[List[RoleResponse]])
def get_roles():
    """Lấy danh mục vai trò người dùng."""
    roles = catalog_repo.get_roles()
    return ApiResponse(
        success=True,
        data=[RoleResponse(ma_vai_tro=r["mavaitro"], ten_vai_tro=r["tenvaitro"]) for r in roles],
        message="Lấy danh mục vai trò thành công"
    )


@router.get("/projects", response_model=ApiResponse[List[ProjectResponse]])
def get_projects():
    """Lấy danh sách các dự án."""
    projects = catalog_repo.get_projects()
    return ApiResponse(
        success=True,
        data=[ProjectResponse(
            ma_du_an=p["maduan"],
            ten_du_an=p["tenduan"],
            ngay_bat_dau=p.get("ngaybatdau"),
            ngay_ket_thuc=p.get("ngayketthuc")
        ) for p in projects],
        message="Lấy danh sách dự án thành công"
    )


@router.post("/projects", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[ProjectResponse])
def create_project(
    payload: ProjectCreate,
    current_user: CurrentUser = Depends(require_roles(4, "Tổng giám đốc", "Trưởng phòng"))
):
    """
    Tạo mới dự án - Ghi đồng bộ (Replicated Write) lên cả 3 sites PostgreSQL.
    """
    res = catalog_repo.create_project(
        ma_du_an=payload.ma_du_an,
        ten_du_an=payload.ten_du_an,
        ngay_bat_dau=payload.ngay_bat_dau,
        ngay_ket_thuc=payload.ngay_ket_thuc
    )
    return ApiResponse(
        success=True,
        data=ProjectResponse(
            ma_du_an=res["ma_du_an"],
            ten_du_an=res["ten_du_an"],
            ngay_bat_dau=res["ngay_bat_dau"],
            ngay_ket_thuc=res["ngay_ket_thuc"]
        ),
        message="Tạo mới dự án và đồng bộ 3 sites thành công"
    )

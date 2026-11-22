from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class DepartmentResponse(BaseModel):
    ma_pb: str
    ten_pb: str
    ma_cn: str


class PositionResponse(BaseModel):
    ma_cv: str
    ten_cv: str
    he_so_luong: float


class RoleResponse(BaseModel):
    ma_vai_tro: int
    ten_vai_tro: str


class ProjectCreate(BaseModel):
    ma_du_an: int = Field(..., description="Mã dự án (số nguyên duy nhất)")
    ten_du_an: str = Field(..., description="Tên dự án")
    ngay_bat_dau: Optional[date] = Field(None, description="Ngày bắt đầu YYYY-MM-DD")
    ngay_ket_thuc: Optional[date] = Field(None, description="Ngày kết thúc YYYY-MM-DD")


class ProjectResponse(BaseModel):
    ma_du_an: int
    ten_du_an: str
    ngay_bat_dau: Optional[date] = None
    ngay_ket_thuc: Optional[date] = None

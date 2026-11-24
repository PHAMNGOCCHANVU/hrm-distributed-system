from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AppointmentCreateRequest(BaseModel):
    ma_nv: str = Field(..., description="Mã nhân viên được đề xuất")
    chuc_vu_moi: str = Field(..., description="Chức vụ mới (CEO, GD_CN, TP, NV)")
    ma_pb_moi: str = Field(..., description="Phòng ban mới")
    ma_cn_moi: str = Field(..., description="Chi nhánh mới (HN, DN, HCM)")
    ly_do: str = Field(..., description="Lý do bổ nhiệm / điều chuyển")
    ngay_hieu_luc: Optional[date] = Field(None, description="Ngày có hiệu lực YYYY-MM-DD")


class AppointmentApproveRequest(BaseModel):
    decision: str = Field(..., description="Quyết định: APPROVED hoặc REJECTED")
    comment: Optional[str] = Field(None, description="Ý kiến phê duyệt")


class AppointmentResponse(BaseModel):
    ma_quyet_dinh: str
    loai_quyet_dinh: str = "BO_NHIEM"
    ma_nv: str
    ma_pb_cu: Optional[str] = None
    ma_pb_moi: Optional[str] = None
    ma_cv_cu: Optional[str] = None
    ma_cv_moi: Optional[str] = None
    ma_cn_cu: Optional[str] = None
    ma_cn_moi: Optional[str] = None
    nguoi_de_xuat: Optional[str] = None
    nguoi_phe_duyet: Optional[str] = None
    trang_thai: str = "PENDING"
    ly_do: Optional[str] = None
    ngay_de_xuat: Optional[datetime] = None
    ngay_hieu_luc: Optional[date] = None
    ngay_phe_duyet: Optional[datetime] = None

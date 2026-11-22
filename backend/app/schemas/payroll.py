from typing import Optional, List
from pydantic import BaseModel, Field


class PayrollUpdateRequest(BaseModel):
    thang: int = Field(..., ge=1, le=12, description="Tháng tính lương (1-12)")
    nam: int = Field(..., ge=2020, description="Năm tính lương")
    luong_co_ban: float = Field(..., ge=0, description="Lương cơ bản (>= 0)")
    phu_cap: float = Field(0.0, ge=0, description="Phụ cấp (>= 0)")
    thuong: float = Field(0.0, ge=0, description="Tiền thưởng (>= 0)")
    khau_tru: float = Field(0.0, ge=0, description="Khấu trừ bảo hiểm/thuế (>= 0)")


class PayrollItem(BaseModel):
    ma_luong: Optional[str] = None
    ma_nv: str
    ho_ten: Optional[str] = None
    so_dien_thoai: Optional[str] = None
    email: Optional[str] = None
    ma_so_thue: Optional[str] = None
    ten_phong_ban: Optional[str] = None
    chi_nhanh: Optional[str] = None
    thang: int
    nam: int
    luong_co_ban: Optional[float] = None
    phu_cap: Optional[float] = None
    thuong: Optional[float] = None
    khau_tru: Optional[float] = None
    luong_thuc_linh: Optional[float] = None
    is_pii_masked: bool = False
    is_salary_masked: bool = False


class PayrollUpdateResponseData(BaseModel):
    ma_luong: str
    ma_nv: str
    thang: int
    nam: int
    luong_co_ban: float
    phu_cap: float
    thuong: float
    khau_tru: float
    luong_thuc_linh: float


class SalarySlipResponse(BaseModel):
    ma_nv: str
    ho_ten: str
    ten_phong_ban: str
    chuc_vu: str
    thang: int
    nam: int
    luong_co_ban: float
    phu_cap: float
    thuong: float
    khau_tru: float
    luong_thuc_linh: float

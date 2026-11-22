from datetime import date
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class JsonSkill(BaseModel):
    name: str = Field(..., description="Tên kỹ năng")
    level: str = Field(..., description="Mức độ thành thạo: Beginner, Intermediate, Advanced, Expert")


class JsonKPIReview(BaseModel):
    period: str = Field(..., description="Kỳ đánh giá (VD: 2026-Q1)")
    final_grade: str = Field(..., description="Xếp loại KPI: A, B, C, D")
    feedback: Optional[str] = Field(None, description="Nhận xét đánh giá")


class EmployeeCreate(BaseModel):
    ma_nv: str = Field(..., description="Mã nhân viên (VD: NV_DN_02)")
    ho_ten: str = Field(..., description="Họ và tên")
    phai: Optional[str] = Field("Nam", description="Giới tính (Nam/Nữ)")
    ngay_sinh: Optional[date] = Field(None, description="Ngày sinh YYYY-MM-DD")
    so_dien_thoai: Optional[str] = Field(None, description="Số điện thoại")
    email: str = Field(..., description="Địa chỉ email công ty")
    ma_so_thue: Optional[str] = Field(None, description="Mã số thuế")
    ma_pb: str = Field(..., description="Mã phòng ban")
    ma_cv: str = Field(..., description="Mã chức vụ")
    ma_vai_tro: int = Field(1, description="Mã vai trò (1: Nhân viên, 2: Trưởng phòng, 3: Giám đốc, 4: Tổng giám đốc)")
    ma_cn: str = Field(..., description="Mã chi nhánh (HN, DN, HCM)")
    username: str = Field(..., description="Tên đăng nhập")
    password: str = Field(..., min_length=6, description="Mật khẩu đăng nhập")
    skills: Optional[List[JsonSkill]] = Field(default_factory=list, description="Danh sách kỹ năng bán cấu trúc JSON")
    performance_reviews: Optional[List[JsonKPIReview]] = Field(default_factory=list, description="Lịch sử đánh giá KPI JSON")


class EmployeeUpdate(BaseModel):
    ho_ten: Optional[str] = None
    phai: Optional[str] = None
    ngay_sinh: Optional[date] = None
    so_dien_thoai: Optional[str] = None
    email: Optional[str] = None
    ma_so_thue: Optional[str] = None
    ma_pb: Optional[str] = None
    ma_cv: Optional[str] = None
    ma_vai_tro: Optional[int] = None
    trang_thai: Optional[str] = None
    password: Optional[str] = None
    skills: Optional[List[JsonSkill]] = None
    performance_reviews: Optional[List[JsonKPIReview]] = None


class EmployeeItem(BaseModel):
    ma_nv: str
    ho_ten: Optional[str] = None
    phai: Optional[str] = None
    ngay_sinh: Optional[date] = None
    so_dien_thoai: Optional[str] = None
    email: Optional[str] = None
    ma_so_thue: Optional[str] = None
    ten_phong_ban: Optional[str] = None
    chuc_vu: Optional[str] = None
    ten_vai_tro: Optional[str] = None
    chi_nhanh: str
    trang_thai: Optional[str] = "DangLamViec"
    ma_pb: Optional[str] = None
    ma_cv: Optional[str] = None
    ma_vai_tro: Optional[int] = None
    kpi_q1: Optional[str] = None
    danh_gia_nhan_xet: Optional[str] = None
    skills: Optional[List[Any]] = None
    url_avatar: Optional[str] = None
    url_cv: Optional[str] = None
    luong_thuc_linh: Optional[float] = None
    is_salary_masked: bool = False
    is_pii_masked: bool = False


class EmployeeDetailResponse(EmployeeItem):
    performance_reviews: Optional[List[Any]] = None
    projects: Optional[List[Any]] = None


class EmployeeListPagination(BaseModel):
    items: List[EmployeeItem]
    total: int
    page: int
    page_size: int


class EmployeeListResponse(BaseModel):
    success: bool = True
    data: EmployeeListPagination
    message: str = "Lấy danh sách nhân viên thành công"

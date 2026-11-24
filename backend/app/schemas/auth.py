from typing import Optional, List
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Tên đăng nhập")
    password: str = Field(..., min_length=6, description="Mật khẩu tối thiểu 6 ký tự")


class UserPayload(BaseModel):
    ma_nv: str
    username: str
    full_name: str
    role_id: int
    role_name: str
    department_id: str
    department_name: str
    branch: str
    scope: str  # "GLOBAL", "BRANCH", "DEPARTMENT", "PERSONAL"
    # Các khái niệm mở rộng mô hình Tập đoàn
    position: Optional[str] = "NV"           # CEO, GD_CN, TP, NV
    cap_bac: Optional[int] = 4              # 1: CEO, 2: GD_CN, 3: TP, 4: NV
    system_roles: List[str] = []            # GROUP_EXECUTIVE, BRANCH_DIRECTOR, DEPT_MANAGER, HR_SPECIALIST, FINANCE_SPECIALIST, SYSTEM_OPERATOR, EMPLOYEE
    org_type: Optional[str] = "CHI_NHANH"    # "TAP_DOAN" hoặc "CHI_NHANH"


class LoginData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPayload


class LoginResponse(BaseModel):
    success: bool = True
    data: LoginData
    message: str = "Đăng nhập thành công"


class CurrentUser(UserPayload):
    pass

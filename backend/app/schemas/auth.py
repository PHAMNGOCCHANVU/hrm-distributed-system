from typing import Optional
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
    scope: str  # "GLOBAL" hoặc "BRANCH"


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

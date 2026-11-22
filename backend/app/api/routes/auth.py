from fastapi import APIRouter, Depends
from app.schemas.auth import LoginRequest, LoginResponse, CurrentUser, UserPayload
from app.schemas.base import ApiResponse
from app.services.auth_service import authenticate_user
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(login_req: LoginRequest):
    """
    Xác thực tài khoản và cấp phát JWT mang thông tin { role, department, branch, scope }.
    """
    return authenticate_user(login_req)


@router.get("/me", response_model=ApiResponse[UserPayload])
def get_current_user_info(current_user: CurrentUser = Depends(get_current_user)):
    """
    Lấy thông tin người dùng đang trong phiên làm việc hiện tại.
    """
    return ApiResponse(
        success=True,
        data=UserPayload(
            ma_nv=current_user.ma_nv,
            username=current_user.username,
            full_name=current_user.full_name,
            role_id=current_user.role_id,
            role_name=current_user.role_name,
            department_id=current_user.department_id,
            department_name=current_user.department_name,
            branch=current_user.branch,
            scope=current_user.scope
        ),
        message="Lấy thông tin phiên hiện tại thành công"
    )

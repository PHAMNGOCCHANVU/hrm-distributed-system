from typing import Optional, List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token
from app.schemas.auth import CurrentUser

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)
) -> CurrentUser:
    """
    Trích xuất và xác thực JWT Bearer Token từ HTTP Authorization Header.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "MISSING_TOKEN",
                "message": "Vui lòng đăng nhập để tiếp tục"
            }
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"
            }
        )

    try:
        user = CurrentUser(
            ma_nv=payload["ma_nv"],
            username=payload["sub"],
            full_name=payload.get("ho_ten", ""),
            role_id=int(payload["role_id"]),
            role_name=payload.get("role_name", ""),
            department_id=payload.get("department_id", ""),
            department_name=payload.get("department_name", ""),
            branch=payload.get("branch", "HN"),
            scope=payload.get("scope", "BRANCH")
        )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "MALFORMED_TOKEN",
                "message": f"Dữ liệu token không đúng định dạng: {e}"
            }
        )


def require_roles(*allowed_roles) -> Callable:
    """
    Dependency kiểm tra quyền người dùng theo Role ID hoặc Role Name.
    """
    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role_id in allowed_roles or current_user.role_name in allowed_roles:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Bạn không có quyền thực hiện thao tác này!"
            }
        )
    return role_checker


def require_departments(*allowed_depts) -> Callable:
    """
    Dependency kiểm tra quyền người dùng theo Tên Phòng Ban.
    """
    def dept_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.department_name in allowed_depts or current_user.role_name == "Tổng giám đốc":
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Thao tác này chỉ dành riêng cho phòng ban được chỉ định!"
            }
        )
    return dept_checker

from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from psycopg2.extras import RealDictCursor

from app.core.db_router import get_db_connection, SITE_HN, SITE_DN, SITE_HCM
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, LoginResponse, LoginData, UserPayload


def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Tìm người dùng trên cả 3 sites CSDL phân tán (HN, DN, HCM).
    Đảm bảo tính trong suốt đăng nhập xuyên chi nhánh.
    """
    user_query = """
        SELECT 
            nd.TenDangNhap, 
            nd.MatKhauHash, 
            nd.MaNV, 
            nv.HoTen, 
            nv.MaPB, 
            pb.TenPB, 
            nv.MaVaiTro, 
            vt.TenVaiTro, 
            nv.MaCN,
            nv.MaCV
        FROM NguoiDungDangNhap nd
        JOIN NhanVien nv ON nd.MaNV = nv.MaNV
        JOIN VaiTro vt ON nv.MaVaiTro = vt.MaVaiTro
        JOIN PhongBan pb ON nv.MaPB = pb.MaPB
        WHERE nd.TenDangNhap = %s
    """
    for site_key in [SITE_HN, SITE_DN, SITE_HCM]:
        try:
            with get_db_connection(site_key) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(user_query, (username,))
                    user = cur.fetchone()
                    if user:
                        return dict(user)
        except Exception:
            continue
    return None


def authenticate_user(login_req: LoginRequest) -> LoginResponse:
    """
    Xác thực thông tin đăng nhập, xác định scope (GLOBAL/BRANCH) và cấp phát JWT.
    """
    user_db = find_user_by_username(login_req.username)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Tên đăng nhập hoặc mật khẩu không chính xác"
            }
        )

    if not verify_password(login_req.password, user_db["matkhauhash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Tên đăng nhập hoặc mật khẩu không chính xác"
            }
        )

    role_id = user_db["mavaitro"]
    role_name = user_db["tenvaitro"]
    dept_name = user_db["tenpb"]
    branch = user_db["macn"]

    # Xác định Scope truy cập:
    # - Tổng giám đốc (Role 4): GLOBAL
    # - Phòng Nhân Sự, Phòng Tài Vụ: GLOBAL
    # - Giám đốc chi nhánh (Role 3): BRANCH
    # - Nhân viên/Trưởng phòng chuyên môn: BRANCH
    if role_id == 4 or role_name == "Tổng giám đốc" or dept_name in ["Phòng Nhân Sự", "Phòng Tài Vụ"]:
        user_scope = "GLOBAL"
    else:
        user_scope = "BRANCH"

    user_payload = UserPayload(
        ma_nv=user_db["manv"],
        username=user_db["tendangnhap"],
        full_name=user_db["hoten"],
        role_id=role_id,
        role_name=role_name,
        department_id=user_db["mapb"],
        department_name=dept_name,
        branch=branch,
        scope=user_scope
    )

    token_data = {
        "sub": user_payload.username,
        "ma_nv": user_payload.ma_nv,
        "ho_ten": user_payload.full_name,
        "role_id": user_payload.role_id,
        "role_name": user_payload.role_name,
        "department_id": user_payload.department_id,
        "department_name": user_payload.department_name,
        "branch": user_payload.branch,
        "scope": user_payload.scope
    }

    access_token = create_access_token(token_data)

    return LoginResponse(
        success=True,
        data=LoginData(
            access_token=access_token,
            token_type="bearer",
            user=user_payload
        ),
        message="Đăng nhập thành công"
    )

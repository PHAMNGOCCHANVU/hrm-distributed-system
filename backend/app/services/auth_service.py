from typing import Optional, Dict, Any, List
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
            COALESCE(pb.LoaiDonVi, 'CHI_NHANH') as LoaiDonVi,
            nv.MaVaiTro, 
            vt.TenVaiTro, 
            nv.MaCN,
            nv.MaCV,
            COALESCE(cv.CapBac, 4) as CapBac
        FROM NguoiDungDangNhap nd
        JOIN NhanVien nv ON nd.MaNV = nv.MaNV
        JOIN VaiTro vt ON nv.MaVaiTro = vt.MaVaiTro
        JOIN PhongBan pb ON nv.MaPB = pb.MaPB
        LEFT JOIN ChucVu cv ON nv.MaCV = cv.MaCV
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


def get_user_system_roles(ma_nv: str) -> List[str]:
    """Lấy danh sách các vai trò hệ thống đã cấp cho nhân viên."""
    roles = []
    query = "SELECT MaVaiTro FROM NhanVien_VaiTro WHERE MaNV = %s;"
    for site_key in [SITE_HN, SITE_DN, SITE_HCM]:
        try:
            with get_db_connection(site_key) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (ma_nv,))
                    rows = cur.fetchall()
                    for r in rows:
                        roles.append(r[0])
        except Exception:
            continue
    return list(set(roles))


def authenticate_user(login_req: LoginRequest) -> LoginResponse:
    """
    Xác thực thông tin đăng nhập, xác định 4 Khái niệm (Position, System Roles, Scope, Business Authority).
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
    dept_code = user_db["mapb"]
    branch = user_db["macn"]
    position = user_db.get("macv") or "NV"
    cap_bac = user_db.get("capbac") or 4
    org_type = user_db.get("loaidonvi") or "CHI_NHANH"

    # Lấy danh sách System Roles từ CSDL
    system_roles = get_user_system_roles(user_db["manv"])

    # Tự động gán System Roles dựa trên chức vụ và phòng ban thực tế
    if position in ["CEO", "TGD"] or role_id == 4 or role_name == "Tổng giám đốc":
        if "GROUP_EXECUTIVE" not in system_roles:
            system_roles.append("GROUP_EXECUTIVE")
    if position in ["GD_CN", "GD"] or role_id == 3 or role_name in ["Giám đốc", "Giám đốc chi nhánh"]:
        if "BRANCH_DIRECTOR" not in system_roles:
            system_roles.append("BRANCH_DIRECTOR")
    if position == "TP" or role_id == 2 or role_name == "Trưởng phòng":
        if "DEPT_MANAGER" not in system_roles:
            system_roles.append("DEPT_MANAGER")
    if "Nhân Sự" in dept_name or "PB_HQ_HR" in dept_code or "PB_HN_HR" in dept_code:
        if "HR_SPECIALIST" not in system_roles:
            system_roles.append("HR_SPECIALIST")
    if "Tài Vụ" in dept_name or "Tài chính" in dept_name or "PB_HQ_FIN" in dept_code:
        if "FINANCE_SPECIALIST" not in system_roles:
            system_roles.append("FINANCE_SPECIALIST")
    if "Vận hành" in dept_name or "OPS" in dept_code or "ops" in login_req.username.lower():
        if "SYSTEM_OPERATOR" not in system_roles:
            system_roles.append("SYSTEM_OPERATOR")
    if "EMPLOYEE" not in system_roles:
        system_roles.append("EMPLOYEE")

    # Xác định Scope truy cập:
    # - CEO hoặc HR/Finance cấp Tập đoàn: GLOBAL
    # - System Operator cấp Tập đoàn: GLOBAL
    # - Giám đốc chi nhánh hoặc nhân sự chi nhánh: BRANCH
    if "GROUP_EXECUTIVE" in system_roles or role_id == 4:
        user_scope = "GLOBAL"
    elif "HR_SPECIALIST" in system_roles and org_type == "TAP_DOAN":
        user_scope = "GLOBAL"
    elif "FINANCE_SPECIALIST" in system_roles:
        user_scope = "GLOBAL"
    elif "SYSTEM_OPERATOR" in system_roles and org_type == "TAP_DOAN":
        user_scope = "GLOBAL"
    else:
        user_scope = "BRANCH"

    user_payload = UserPayload(
        ma_nv=user_db["manv"],
        username=user_db["tendangnhap"],
        full_name=user_db["hoten"],
        role_id=role_id,
        role_name=role_name,
        department_id=dept_code,
        department_name=dept_name,
        branch=branch,
        scope=user_scope,
        position=position,
        cap_bac=cap_bac,
        system_roles=system_roles,
        org_type=org_type
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
        "scope": user_payload.scope,
        "position": user_payload.position,
        "cap_bac": user_payload.cap_bac,
        "system_roles": user_payload.system_roles,
        "org_type": user_payload.org_type
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

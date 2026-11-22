from typing import Optional, List, Dict, Any
from psycopg2.extras import RealDictCursor

from app.core.db_router import get_db_connection, SITE_HN


def get_payrolls(
    month: Optional[int] = None,
    year: Optional[int] = None,
    branch: Optional[str] = None,
    site_key: str = SITE_HN
) -> List[Dict[str, Any]]:
    """
    Tra cứu danh sách bảng lương qua Global Views (v_Luong, v_NhanVien, v_PhongBan).
    """
    conditions = ["1=1"]
    params: List[Any] = []

    if month is not None:
        conditions.append("l.Thang = %s")
        params.append(month)

    if year is not None:
        conditions.append("l.Nam = %s")
        params.append(year)

    if branch:
        conditions.append("nv.MaCN = %s")
        params.append(branch.upper().strip())

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT 
            l.MaLuong, l.MaNV, nv.HoTen, nv.SoDienThoai, nv.Email, nv.MaSoThue,
            nv.MaCN AS ChiNhanh, pb.TenPB AS TenPhongBan, nv.MaPB,
            l.Thang, l.Nam, l.LuongCoBan, l.PhuCap, l.Thuong, l.KhauTru, l.LuongThucLinh
        FROM v_Luong l
        JOIN v_NhanVien nv ON l.MaNV = nv.MaNV
        JOIN v_PhongBan pb ON nv.MaPB = pb.MaPB
        WHERE {where_clause}
        ORDER BY l.Nam DESC, l.Thang DESC, nv.MaNV ASC
    """

    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            return [dict(r) for r in rows]


def get_payroll_by_nv(
    ma_nv: str,
    month: int,
    year: int,
    site_key: str = SITE_HN
) -> Optional[Dict[str, Any]]:
    """
    Lấy thông tin bản ghi lương của 1 nhân viên trong 1 tháng/năm cụ thể.
    """
    query = """
        SELECT 
            l.MaLuong, l.MaNV, nv.HoTen, nv.SoDienThoai, nv.Email, nv.MaSoThue,
            nv.MaCN AS ChiNhanh, pb.TenPB AS TenPhongBan, nv.MaPB,
            l.Thang, l.Nam, l.LuongCoBan, l.PhuCap, l.Thuong, l.KhauTru, l.LuongThucLinh
        FROM v_Luong l
        JOIN v_NhanVien nv ON l.MaNV = nv.MaNV
        JOIN v_PhongBan pb ON nv.MaPB = pb.MaPB
        WHERE l.MaNV = %s AND l.Thang = %s AND l.Nam = %s
    """
    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (ma_nv, month, year))
            row = cur.fetchone()
            return dict(row) if row else None


def upsert_payroll(
    ma_nv: str,
    branch_code: str,
    month: int,
    year: int,
    luong_co_ban: float,
    phu_cap: float,
    thuong: float,
    khau_tru: float,
    site_key: str
) -> Dict[str, Any]:
    """
    Tạo mới hoặc cập nhật lương cho nhân viên trên Shard tương ứng.
    Khóa chính MaLuong định dạng: L_{branch}_{MaNV}_{month:02d}{year%100:02d}
    """
    clean_nv = ma_nv.replace("NV_", "")
    ma_luong = f"L_{branch_code}_{clean_nv}_{month:02d}{year % 100:02d}"

    upsert_sql = """
        INSERT INTO Luong (
            MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (MaLuong) DO UPDATE SET
            LuongCoBan = EXCLUDED.LuongCoBan,
            PhuCap = EXCLUDED.PhuCap,
            Thuong = EXCLUDED.Thuong,
            KhauTru = EXCLUDED.KhauTru
        RETURNING MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru, LuongThucLinh;
    """

    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(upsert_sql, (
                ma_luong, ma_nv, month, year, luong_co_ban, phu_cap, thuong, khau_tru
            ))
            row = cur.fetchone()
        conn.commit()
        return dict(row) if row else {}


def get_salary_slip(
    ma_nv: str,
    month: Optional[int] = None,
    year: Optional[int] = None,
    site_key: str = SITE_HN
) -> Optional[Dict[str, Any]]:
    """
    Lấy phiếu lương cá nhân của nhân viên.
    Nếu không truyền month/year thì lấy bản ghi mới nhất.
    """
    conditions = ["l.MaNV = %s"]
    params: List[Any] = [ma_nv]

    if month is not None:
        conditions.append("l.Thang = %s")
        params.append(month)

    if year is not None:
        conditions.append("l.Nam = %s")
        params.append(year)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT 
            l.MaNV, nv.HoTen, pb.TenPB AS TenPhongBan, cv.TenCV AS ChucVu,
            l.Thang, l.Nam, l.LuongCoBan, l.PhuCap, l.Thuong, l.KhauTru, l.LuongThucLinh
        FROM v_Luong l
        JOIN v_NhanVien nv ON l.MaNV = nv.MaNV
        JOIN v_PhongBan pb ON nv.MaPB = pb.MaPB
        JOIN ChucVu cv ON nv.MaCV = cv.MaCV
        WHERE {where_clause}
        ORDER BY l.Nam DESC, l.Thang DESC
        LIMIT 1
    """

    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            row = cur.fetchone()
            return dict(row) if row else None

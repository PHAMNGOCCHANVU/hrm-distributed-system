from typing import List, Dict, Any, Optional
from datetime import date
from psycopg2.extras import RealDictCursor

from app.core.db_router import get_db_connection, execute_replicated_write, SITE_HN


def get_departments(site_key: str = SITE_HN) -> List[Dict[str, Any]]:
    """Lấy danh sách phòng ban toàn tập đoàn từ v_PhongBan."""
    query = "SELECT MaPB, TenPB, MaCN FROM v_PhongBan ORDER BY MaCN, MaPB;"
    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return [dict(r) for r in cur.fetchall()]


def get_positions(site_key: str = SITE_HN) -> List[Dict[str, Any]]:
    """Lấy danh mục chức vụ từ bảng nhân bản ChucVu."""
    query = "SELECT MaCV, TenCV, HeSoLuong FROM ChucVu ORDER BY HeSoLuong DESC;"
    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return [dict(r) for r in cur.fetchall()]


def get_roles(site_key: str = SITE_HN) -> List[Dict[str, Any]]:
    """Lấy danh mục vai trò hệ thống từ bảng nhân bản VaiTro."""
    query = "SELECT MaVaiTro, TenVaiTro FROM VaiTro ORDER BY MaVaiTro ASC;"
    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return [dict(r) for r in cur.fetchall()]


def get_projects(site_key: str = SITE_HN) -> List[Dict[str, Any]]:
    """Lấy danh sách dự án từ bảng nhân bản DuAn."""
    query = "SELECT MaDuAn, TenDuAn, NgayBatDau, NgayKetThuc FROM DuAn ORDER BY MaDuAn ASC;"
    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return [dict(r) for r in cur.fetchall()]


def create_project(
    ma_du_an: int,
    ten_du_an: str,
    ngay_bat_dau: Optional[date] = None,
    ngay_ket_thuc: Optional[date] = None
) -> Dict[str, Any]:
    """
    Tạo mới dự án - thực thi Replicated Write đồng bộ lên cả 3 sites (site_hn, site_dn, site_hcm).
    """
    insert_sql = """
        INSERT INTO DuAn (MaDuAn, TenDuAn, NgayBatDau, NgayKetThuc)
        VALUES (%s, %s, %s, %s)
    """
    execute_replicated_write(insert_sql, (ma_du_an, ten_du_an, ngay_bat_dau, ngay_ket_thuc))
    return {
        "ma_du_an": ma_du_an,
        "ten_du_an": ten_du_an,
        "ngay_bat_dau": ngay_bat_dau,
        "ngay_ket_thuc": ngay_ket_thuc
    }

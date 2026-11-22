import time
from typing import Optional, List, Dict, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.config import settings
from app.core.minio_client import minio_client
from app.core.db_router import get_db_connection, SITE_HN, SITE_DN, SITE_HCM


def check_node_latency(site_key: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Đo thời gian phản hồi (latency ms) của 1 node PostgreSQL bằng câu lệnh SELECT 1;
    Trả về: (is_online, latency_ms, error_message).
    """
    start_time = time.perf_counter()
    try:
        params = settings.get_db_params(site_key)
        conn = psycopg2.connect(**params)
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        conn.close()
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return True, elapsed_ms, None
    except Exception as e:
        return False, None, str(e)


def check_minio_health() -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Đo thời gian phản hồi (latency ms) của MinIO Object Storage bằng list_buckets().
    Trả về: (is_online, latency_ms, error_message).
    """
    start_time = time.perf_counter()
    try:
        minio_client.list_buckets()
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return True, elapsed_ms, None
    except Exception as e:
        return False, None, str(e)


def insert_audit_log(
    manv_thuc_hien: Optional[str],
    tennv_thuc_hien: Optional[str],
    thao_tac: str,
    tac_dong_len_nv: Optional[str] = None,
    chi_tiet: Optional[str] = None,
    site_key: str = SITE_HN
):
    """
    Ghi nhật ký kiểm toán vào bảng LichSuHoatDong.
    """
    insert_sql = """
        INSERT INTO LichSuHoatDong (
            ThoiGian, MaNVThucHien, TenNVThucHien, ThaoTac, TacDongLenNV, ChiTiet
        ) VALUES (
            NOW(), %s, %s, %s, %s, %s
        )
    """
    try:
        with get_db_connection(site_key) as conn:
            with conn.cursor() as cur:
                cur.execute(insert_sql, (
                    manv_thuc_hien, tennv_thuc_hien, thao_tac, tacdong_len_nv, chi_tiet
                ))
            conn.commit()
    except Exception as e:
        # Ghi log không được làm sập luồng chính
        pass


def get_audit_logs(
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    site_key: str = SITE_HN
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Tra cứu nhật ký kiểm toán với phân trang và tìm kiếm theo từ khóa.
    """
    offset = (page - 1) * page_size
    conditions = ["1=1"]
    params: List[Any] = []

    if keyword:
        kw = f"%{keyword.strip()}%"
        conditions.append("""(
            TenNVThucHien ILIKE %s OR 
            MaNVThucHien ILIKE %s OR 
            ThaoTac ILIKE %s OR 
            TacDongLenNV ILIKE %s OR 
            ChiTiet ILIKE %s
        )""")
        params.extend([kw, kw, kw, kw, kw])

    where_clause = " AND ".join(conditions)

    count_query = f"SELECT COUNT(1) AS total FROM LichSuHoatDong WHERE {where_clause}"
    select_query = f"""
        SELECT ID, ThoiGian, MaNVThucHien, TenNVThucHien, ThaoTac, TacDongLenNV, ChiTiet
        FROM LichSuHoatDong
        WHERE {where_clause}
        ORDER BY ThoiGian DESC
        LIMIT %s OFFSET %s
    """

    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(count_query, tuple(params))
            total_row = cur.fetchone()
            total = total_row["total"] if total_row else 0

            cur.execute(select_query, tuple(params + [page_size, offset]))
            items = cur.fetchall()

    return [dict(i) for i in items], total

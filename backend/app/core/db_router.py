import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.pool import ThreadedConnectionPool

from app.core.config import settings

logger = logging.getLogger("db_router")

# Site key constants
SITE_HN = "site_hn"
SITE_DN = "site_dn"
SITE_HCM = "site_hcm"

BRANCH_SITE_MAP = {
    "HN": SITE_HN,
    "DN": SITE_DN,
    "HCM": SITE_HCM,
}

# 3 ThreadedConnectionPools
POOLS: Dict[str, Optional[ThreadedConnectionPool]] = {
    SITE_HN: None,
    SITE_DN: None,
    SITE_HCM: None,
}


def init_connection_pools():
    """Khởi tạo 3 ThreadedConnectionPool cho 3 sites CSDL phân tán."""
    for site_key in [SITE_HN, SITE_DN, SITE_HCM]:
        try:
            params = settings.get_db_params(site_key)
            pool = ThreadedConnectionPool(minconn=1, maxconn=20, **params)
            POOLS[site_key] = pool
            logger.info(f"Initialized connection pool for {site_key} successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize pool for {site_key}: {e}")
            POOLS[site_key] = None


# Auto initialize pools upon module import
init_connection_pools()


def get_pool(site_key: str) -> ThreadedConnectionPool:
    """Lấy connection pool theo site key, tự động tái khởi tạo nếu bị ngắt."""
    site_key = site_key.lower()
    pool = POOLS.get(site_key)
    if pool is None:
        params = settings.get_db_params(site_key)
        pool = ThreadedConnectionPool(minconn=1, maxconn=20, **params)
        POOLS[site_key] = pool
    return pool


@contextmanager
def get_db_connection(site_key: str):
    """Context Manager mượn và trả kết nối an toàn từ Connection Pool."""
    pool = get_pool(site_key)
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def get_read_pool(user: Optional[Any] = None) -> str:
    """
    Quyết định pool đọc:
    - Nếu xem toàn tập đoàn (scope GLOBAL, TGD, hoặc Tài Vụ/Nhân Sự toàn quyền): Trỏ vào site_hn (Coordinator FDW View).
    - Nếu là Giám đốc chi nhánh hoặc Nhân viên cục bộ xem nội bộ chi nhánh: Trỏ trực tiếp shard cục bộ site_dn/site_hcm/site_hn.
    """
    if user is None:
        return SITE_HN

    scope = getattr(user, "scope", "GLOBAL")
    role_name = getattr(user, "role_name", "")
    department_name = getattr(user, "department_name", "")
    branch = getattr(user, "branch", "HN")

    if scope == "GLOBAL" or role_name == "Tổng giám đốc" or department_name in ["Phòng Tài Vụ", "Phòng Nhân Sự"]:
        return SITE_HN

    # Nếu người dùng thuộc chi nhánh cụ thể và có phân quyền cục bộ
    return BRANCH_SITE_MAP.get(branch.upper(), SITE_HN)


def get_write_pool(branch_code: str) -> str:
    """
    Quyết định pool ghi theo MaCN của bản ghi:
    - HN -> site_hn
    - DN -> site_dn
    - HCM -> site_hcm
    """
    if not branch_code:
        return SITE_HN
    return BRANCH_SITE_MAP.get(branch_code.upper().strip(), SITE_HN)


def execute_replicated_write(query: str, params: Optional[tuple] = None) -> Dict[str, bool]:
    """
    Thực thi câu lệnh ghi đồng bộ (Replicated Write) lên toàn bộ 3 sites (HN, DN, HCM).
    Thường dùng cho các bảng danh mục chung: DuAn, ChucVu, VaiTro.
    """
    results = {}
    for site_key in [SITE_HN, SITE_DN, SITE_HCM]:
        try:
            with get_db_connection(site_key) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params or ())
                conn.commit()
                results[site_key] = True
        except Exception as e:
            logger.error(f"Replicated write failed on {site_key}: {e}")
            results[site_key] = False
            raise RuntimeError(f"Ghi đồng bộ thất bại trên {site_key}: {e}")
    return results


def close_all_pools():
    """Đóng toàn bộ connection pools khi ứng dụng tắt."""
    for site_key, pool in POOLS.items():
        if pool is not None:
            try:
                pool.closeall()
                logger.info(f"Closed connection pool for {site_key}.")
            except Exception as e:
                logger.error(f"Error closing pool {site_key}: {e}")
            POOLS[site_key] = None

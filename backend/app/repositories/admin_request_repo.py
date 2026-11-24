import uuid
from typing import Dict, Any, List, Optional
from psycopg2.extras import RealDictCursor, Json
from app.core.db_router import get_db_connection, SITE_HN, SITE_DN, SITE_HCM


def create_admin_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Tạo mới yêu cầu quản trị kỹ thuật."""
    req_id = f"YCQ_{uuid.uuid4().hex[:8].upper()}"
    insert_sql = """
        INSERT INTO YeuCauQuanTri (
            MaYeuCau, LoaiYeuCau, MaNVYeuCau, PhamViYeuCau, NoiDungYeuCau, TrangThai
        ) VALUES (
            %s, %s, %s, %s, %s, 'PENDING'
        )
        RETURNING MaYeuCau, LoaiYeuCau, MaNVYeuCau, PhamViYeuCau, NoiDungYeuCau, TrangThai, NgayTao;
    """

    params = (
        req_id,
        data["loai_yeu_cau"],
        data.get("ma_nv_yeu_cau"),
        data["pham_vi"],
        Json(data.get("thong_so_ky_thuat") or {})
    )

    with get_db_connection(SITE_HN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(insert_sql, params)
            row = cur.fetchone()
        conn.commit()

    return dict(row) if row else {}


def get_admin_request_by_id(req_id: str) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết yêu cầu quản trị kỹ thuật."""
    query = """
        SELECT MaYeuCau, LoaiYeuCau, MaNVYeuCau, MaNVPheDuyet, PhamViYeuCau, NoiDungYeuCau, TrangThai, LyDoTuChoi, NgayTao, NgayPheDuyet
        FROM YeuCauQuanTri
        WHERE MaYeuCau = %s;
    """
    with get_db_connection(SITE_HN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (req_id,))
            row = cur.fetchone()
            return dict(row) if row else None


def get_admin_requests(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Danh sách các yêu cầu quản trị kỹ thuật."""
    query = """
        SELECT MaYeuCau, LoaiYeuCau, MaNVYeuCau, MaNVPheDuyet, PhamViYeuCau, NoiDungYeuCau, TrangThai, LyDoTuChoi, NgayTao, NgayPheDuyet
        FROM YeuCauQuanTri
    """
    params = []
    if status:
        query += " WHERE TrangThai = %s"
        params.append(status)
    query += " ORDER BY NgayTao DESC;"

    with get_db_connection(SITE_HN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            return [dict(r) for r in cur.fetchall()]


def update_admin_request_status(
    req_id: str,
    new_status: str,
    approver_id: str,
    reject_reason: Optional[str] = None
):
    """Cập nhật trạng thái yêu cầu quản trị kỹ thuật."""
    update_sql = """
        UPDATE YeuCauQuanTri
        SET TrangThai = %s, MaNVPheDuyet = %s, LyDoTuChoi = %s, NgayPheDuyet = NOW()
        WHERE MaYeuCau = %s;
    """
    with get_db_connection(SITE_HN) as conn:
        with conn.cursor() as cur:
            cur.execute(update_sql, (new_status, approver_id, reject_reason, req_id))
        conn.commit()

import uuid
from typing import Dict, Any, List, Optional
from psycopg2.extras import RealDictCursor
from app.core.db_router import get_db_connection, get_write_pool, SITE_HN


def create_appointment(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo mới phiếu đề xuất Bổ nhiệm / Điều chuyển với trạng thái PENDING.
    Lưu trên Shard mục tiêu và Coordinator.
    """
    decision_id = f"QD_BN_{uuid.uuid4().hex[:8].upper()}"
    insert_sql = """
        INSERT INTO DieuChuyenBoNhiem (
            MaQuyetDinh, LoaiQuyetDinh, MaNV, MaPBCu, MaPBMoi, 
            MaCVCu, MaCVMoi, MaCNCu, MaCNMoi, NguoiDeXuat, TrangThai, LyDo, NgayHieuLuc
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', %s, %s
        )
        RETURNING MaQuyetDinh, LoaiQuyetDinh, MaNV, MaPBMoi, MaCVMoi, MaCNMoi, TrangThai, LyDo, NgayDeXuat, NgayHieuLuc;
    """

    target_branch = data.get("ma_cn_moi", "HN")
    target_site = get_write_pool(target_branch)

    params = (
        decision_id,
        data.get("loai_quyet_dinh", "BO_NHIEM"),
        data["ma_nv"],
        data.get("ma_pb_cu"),
        data.get("ma_pb_moi"),
        data.get("ma_cv_cu"),
        data.get("chuc_vu_moi"),
        data.get("ma_cn_cu"),
        data.get("ma_cn_moi"),
        data.get("nguoi_de_xuat"),
        data.get("ly_do"),
        data.get("ngay_hieu_luc")
    )

    with get_db_connection(target_site) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(insert_sql, params)
            row = cur.fetchone()
        conn.commit()

    # Nếu target_site khác SITE_HN, đồng bộ lưu trên SITE_HN để FDW/Global tra cứu
    if target_site != SITE_HN:
        try:
            with get_db_connection(SITE_HN) as conn_hn:
                with conn_hn.cursor() as cur_hn:
                    cur_hn.execute("""
                        INSERT INTO DieuChuyenBoNhiem (
                            MaQuyetDinh, LoaiQuyetDinh, MaNV, MaPBCu, MaPBMoi, 
                            MaCVCu, MaCVMoi, MaCNCu, MaCNMoi, NguoiDeXuat, TrangThai, LyDo, NgayHieuLuc
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', %s, %s)
                        ON CONFLICT (MaQuyetDinh) DO NOTHING;
                    """, params)
                conn_hn.commit()
        except Exception:
            pass

    return dict(row) if row else {}


def get_appointment_by_id(decision_id: str) -> Optional[Dict[str, Any]]:
    """Tra cứu phiếu đề xuất bổ nhiệm."""
    from app.core.db_router import SITE_DN, SITE_HCM
    query = """
        SELECT MaQuyetDinh, LoaiQuyetDinh, MaNV, MaPBCu, MaPBMoi, 
               MaCVCu, MaCVMoi, MaCNCu, MaCNMoi, NguoiDeXuat, NguoiPheDuyet, 
               TrangThai, LyDo, NgayDeXuat, NgayHieuLuc, NgayPheDuyet
        FROM DieuChuyenBoNhiem
        WHERE MaQuyetDinh = %s;
    """
    for site in [SITE_HN, SITE_DN, SITE_HCM]:
        try:
            with get_db_connection(site) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (decision_id,))
                    row = cur.fetchone()
                    if row:
                        return dict(row)
        except Exception:
            continue
    return None


def get_appointments(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lấy danh sách đề xuất bổ nhiệm / điều chuyển."""
    query = """
        SELECT MaQuyetDinh, LoaiQuyetDinh, MaNV, MaPBCu, MaPBMoi, 
               MaCVCu, MaCVMoi, MaCNCu, MaCNMoi, NguoiDeXuat, NguoiPheDuyet, 
               TrangThai, LyDo, NgayDeXuat, NgayHieuLuc, NgayPheDuyet
        FROM DieuChuyenBoNhiem
    """
    params = []
    if status:
        query += " WHERE TrangThai = %s"
        params.append(status)
    query += " ORDER BY NgayDeXuat DESC;"

    with get_db_connection(SITE_HN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            return [dict(r) for r in cur.fetchall()]


def update_appointment_status(
    decision_id: str,
    new_status: str,
    approver_id: str,
    comment: Optional[str] = None
):
    """Cập nhật trạng thái phiếu bổ nhiệm."""
    from app.core.db_router import SITE_DN, SITE_HCM
    update_sql = """
        UPDATE DieuChuyenBoNhiem
        SET TrangThai = %s, NguoiPheDuyet = %s, NgayPheDuyet = NOW()
        WHERE MaQuyetDinh = %s;
    """
    for site in [SITE_HN, SITE_DN, SITE_HCM]:
        try:
            with get_db_connection(site) as conn:
                with conn.cursor() as cur:
                    cur.execute(update_sql, (new_status, approver_id, decision_id))
                conn.commit()
        except Exception:
            pass


def apply_appointment_to_employee(ma_nv: str, chuc_vu_moi: str, ma_pb_moi: str, ma_cn_moi: str):
    """Thực thi bổ nhiệm vào hồ sơ nhân viên trên CSDL Shard."""
    target_site = get_write_pool(ma_cn_moi)
    update_nv = """
        UPDATE NhanVien
        SET MaCV = %s, MaPB = %s, MaCN = %s
        WHERE MaNV = %s;
    """
    with get_db_connection(target_site) as conn:
        with conn.cursor() as cur:
            cur.execute(update_nv, (chuc_vu_moi, ma_pb_moi, ma_cn_moi, ma_nv))
        conn.commit()

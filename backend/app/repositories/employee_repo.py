import json
from typing import Optional, List, Dict, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

from app.core.db_router import get_db_connection, SITE_HN


def get_employees(
    branch: Optional[str] = None,
    department_id: Optional[str] = None,
    search: Optional[str] = None,
    kpi_grade: Optional[str] = None,
    exclude_department_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    site_key: str = SITE_HN
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Truy vấn danh sách nhân viên từ v_HoSoNhanSu_ToanDien với phân trang và bộ lọc.
    Lưu ý: v_HoSoNhanSu_ToanDien là Coordinator View chỉ tồn tại trên site_hn.
    """
    # Đảm bảo luôn truy vấn Coordinator site_hn vì v_HoSoNhanSu_ToanDien chỉ có tại site_hn
    query_site = SITE_HN

    offset = (page - 1) * page_size
    conditions = ["1=1"]
    params: List[Any] = []

    if branch:
        conditions.append("ChiNhanh = %s")
        params.append(branch.upper().strip())

    if department_id:
        conditions.append("MaPB = %s")
        params.append(department_id.strip())

    if search:
        search_term = f"%{search.strip()}%"
        conditions.append("(HoTen ILIKE %s OR MaNV ILIKE %s OR Email ILIKE %s)")
        params.extend([search_term, search_term, search_term])

    if kpi_grade:
        conditions.append("XepLoai_KPI_Q1 = %s")
        params.append(kpi_grade.upper().strip())

    if exclude_department_name:
        conditions.append("TenPhongBan <> %s")
        params.append(exclude_department_name)

    where_clause = " AND ".join(conditions)

    count_query = f"SELECT COUNT(1) as total FROM v_HoSoNhanSu_ToanDien WHERE {where_clause}"
    select_query = f"""
        SELECT 
            MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue,
            TenPhongBan, ChucVuHienTai, TenVaiTro, ChiNhanh, TrangThai,
            MaPB, MaCV, MaVaiTro,
            Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru, LuongThucLinh,
            XepLoai_KPI_Q1, DanhGia_NhanXet, DanhSachKyNang,
            URL_AnhDaiDien, URL_BanScan_CV
        FROM v_HoSoNhanSu_ToanDien
        WHERE {where_clause}
        ORDER BY MaNV ASC
        LIMIT %s OFFSET %s
    """

    with get_db_connection(query_site) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(count_query, tuple(params))
            total_row = cur.fetchone()
            total = total_row["total"] if total_row else 0

            cur.execute(select_query, tuple(params + [page_size, offset]))
            items = cur.fetchall()

    return [dict(row) for row in items], total


def get_employee_by_id(ma_nv: str, site_key: str = SITE_HN) -> Optional[Dict[str, Any]]:
    """
    Lấy chi tiết 1 nhân viên theo mã MaNV bao gồm JSON mở rộng và danh sách dự án.
    v_NhanVien, v_PhongBan, v_HoSoMoRong tồn tại trên site_hn Coordinator.
    """
    query_site = SITE_HN
    query = """
        SELECT 
            nv.MaNV, nv.HoTen, nv.Phai, nv.NgaySinh, nv.SoDienThoai, nv.Email, nv.MaSoThue,
            pb.TenPB AS TenPhongBan, cv.TenCV AS ChucVuHienTai, vt.TenVaiTro,
            nv.MaCN AS ChiNhanh, nv.TrangThai, nv.MaPB, nv.MaCV, nv.MaVaiTro,
            l.Thang, l.Nam, l.LuongCoBan, l.PhuCap, l.Thuong, l.KhauTru, l.LuongThucLinh,
            hs.DuLieuJSON,
            CONCAT('http://localhost:9000/nhansu-bucket/', hs.DuLieuJSON ->> 'avatar_key') AS URL_AnhDaiDien,
            CONCAT('http://localhost:9000/nhansu-bucket/', hs.DuLieuJSON ->> 'cv_pdf_key') AS URL_BanScan_CV
        FROM v_NhanVien nv
        JOIN v_PhongBan pb ON nv.MaPB = pb.MaPB
        JOIN ChucVu cv ON nv.MaCV = cv.MaCV
        JOIN VaiTro vt ON nv.MaVaiTro = vt.MaVaiTro
        LEFT JOIN v_Luong l ON nv.MaNV = l.MaNV AND l.Thang = 3 AND l.Nam = 2026
        LEFT JOIN v_HoSoMoRong hs ON nv.MaNV = hs.MaNV
        WHERE nv.MaNV = %s
    """
    projects_query = """
        SELECT d.MaDuAn, d.TenDuAn, nd.NgayThamGia, d.NgayBatDau, d.NgayKetThuc
        FROM NhanVien_DuAn nd
        JOIN DuAn d ON nd.MaDuAn = d.MaDuAn
        WHERE nd.MaNV = %s
    """

    with get_db_connection(query_site) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (ma_nv,))
            row = cur.fetchone()
            if not row:
                return None
            emp = dict(row)

            cur.execute(projects_query, (ma_nv,))
            projects = cur.fetchall()
            emp["projects"] = [dict(p) for p in projects]

    return emp


def check_department_manager_exists(ma_pb: str, site_key: str, exclude_ma_nv: Optional[str] = None) -> bool:
    """
    Kiểm tra xem phòng ban đã có Trưởng phòng (MaVaiTro = 2 hoặc MaCV = 'TP') chưa.
    Tuân thủ Single Manager Rule (2.1).
    """
    query = """
        SELECT COUNT(1) AS cnt 
        FROM NhanVien 
        WHERE MaPB = %s AND (MaVaiTro = 2 OR MaCV = 'TP')
    """
    params: List[Any] = [ma_pb]
    if exclude_ma_nv:
        query += " AND MaNV <> %s"
        params.append(exclude_ma_nv)

    with get_db_connection(site_key) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, tuple(params))
            res = cur.fetchone()
            return bool(res and res["cnt"] > 0)


def check_employee_exists(ma_nv: str, email: str, username: str, site_key: str = SITE_HN) -> Optional[str]:
    """
    Kiểm tra trùng mã NV, email hoặc username.
    v_NhanVien nằm trên Coordinator site_hn.
    """
    with get_db_connection(SITE_HN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT 1 FROM v_NhanVien WHERE MaNV = %s", (ma_nv,))
            if cur.fetchone():
                return f"Mã nhân viên {ma_nv} đã tồn tại!"

            cur.execute("SELECT 1 FROM v_NhanVien WHERE Email = %s", (email,))
            if cur.fetchone():
                return f"Email {email} đã được sử dụng!"

    # Kiểm tra username trên site_hn (hoặc các shards nếu cần)
    from app.core.db_router import SITE_DN, SITE_HCM
    for sk in [SITE_HN, SITE_DN, SITE_HCM]:
        try:
            with get_db_connection(sk) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT 1 FROM NguoiDungDangNhap WHERE TenDangNhap = %s", (username,))
                    if cur.fetchone():
                        return f"Tên đăng nhập {username} đã tồn tại!"
        except Exception:
            pass

    return None


def insert_employee(data: Dict[str, Any], site_key: str):
    """
    Ghi dữ liệu nhân sự mới vào Shard tương ứng trong 1 Transaction SQL:
    - NhanVien
    - NguoiDungDangNhap
    - HoSoMoRong
    """
    insert_nv = """
        INSERT INTO NhanVien (
            MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue,
            MaPB, MaCV, MaVaiTro, MaCN, TrangThai
        ) VALUES (
            %(ma_nv)s, %(ho_ten)s, %(phai)s, %(ngay_sinh)s, %(so_dien_thoai)s, %(email)s, %(ma_so_thue)s,
            %(ma_pb)s, %(ma_cv)s, %(ma_vai_tro)s, %(ma_cn)s, %(trang_thai)s
        )
    """

    insert_user = """
        INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV)
        VALUES (%(username)s, %(password_hash)s, %(ma_nv)s)
    """

    insert_json = """
        INSERT INTO HoSoMoRong (MaNV, DuLieuJSON)
        VALUES (%(ma_nv)s, %(json_data)s)
    """

    with get_db_connection(site_key) as conn:
        with conn.cursor() as cur:
            cur.execute(insert_nv, data)
            cur.execute(insert_user, data)
            cur.execute(insert_json, {
                "ma_nv": data["ma_nv"],
                "json_data": json.dumps(data["dulieu_json"])
            })
        conn.commit()


def update_employee(ma_nv: str, data: Dict[str, Any], site_key: str):
    """
    Cập nhật thông tin nhân viên trên Shard cục bộ.
    """
    update_nv_fields = []
    params: Dict[str, Any] = {"ma_nv": ma_nv}

    for field in ["ho_ten", "phai", "ngay_sinh", "so_dien_thoai", "email", "ma_so_thue", "ma_pb", "ma_cv", "ma_vai_tro", "trang_thai"]:
        if field in data and data[field] is not None:
            col_map = {
                "ho_ten": "HoTen", "phai": "Phai", "ngay_sinh": "NgaySinh",
                "so_dien_thoai": "SoDienThoai", "email": "Email", "ma_so_thue": "MaSoThue",
                "ma_pb": "MaPB", "ma_cv": "MaCV", "ma_vai_tro": "MaVaiTro", "trang_thai": "TrangThai"
            }
            sql_col = col_map[field]
            update_nv_fields.append(f"{sql_col} = %({field})s")
            params[field] = data[field]

    with get_db_connection(site_key) as conn:
        with conn.cursor() as cur:
            if update_nv_fields:
                sql_update_nv = f"UPDATE NhanVien SET {', '.join(update_nv_fields)} WHERE MaNV = %(ma_nv)s"
                cur.execute(sql_update_nv, params)

            if "password_hash" in data and data["password_hash"]:
                cur.execute(
                    "UPDATE NguoiDungDangNhap SET MatKhauHash = %s WHERE MaNV = %s",
                    (data["password_hash"], ma_nv)
                )

            if "dulieu_json" in data and data["dulieu_json"]:
                cur.execute(
                    "UPDATE HoSoMoRong SET DuLieuJSON = %s, NgayCapNhat = NOW() WHERE MaNV = %s",
                    (json.dumps(data["dulieu_json"]), ma_nv)
                )
        conn.commit()


def get_colleagues(ma_pb: str, branch: str, site_key: str = SITE_HN) -> List[Dict[str, Any]]:
    """
    Xem danh bạ đồng nghiệp cùng phòng ban và chi nhánh. Lương bị che giấu hoàn toàn.
    v_HoSoNhanSu_ToanDien nằm trên Coordinator site_hn.
    """
    query = """
        SELECT 
            MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email,
            TenPhongBan, ChucVuHienTai, TenVaiTro, ChiNhanh, TrangThai,
            URL_AnhDaiDien
        FROM v_HoSoNhanSu_ToanDien
        WHERE MaPB = %s AND ChiNhanh = %s
        ORDER BY MaNV ASC
    """
    with get_db_connection(SITE_HN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (ma_pb, branch))
            rows = cur.fetchall()
            return [dict(r) for r in rows]

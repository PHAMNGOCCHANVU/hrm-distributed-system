import pytest
import hashlib

def ensure_test_users(db_conn_hn, db_conn_dn):
    """
    Tạo hoặc chuẩn bị các tài khoản thử nghiệm cho các vai trò nếu chưa có:
    - General Director: giap_gd (HN, Role 4)
    - Branch Director: cuong_gd_dn (DN, Role 3, Ban Giám Đốc hoặc PB_DN_01)
    - HR Staff: hr_staff (HN, Role 1, Phòng Nhân Sự)
    - Finance Staff: finance_staff (HN, Role 1, Phòng Tài Vụ)
    - Normal Employee: cuong_dn (DN, Role 1, PB_DN_01)
    """
    pwd_hash = hashlib.sha256(b"Password123").hexdigest()
    
    # 1. Tạo phòng ban Tài Vụ và Nhân Sự tại HN nếu chưa có
    with db_conn_hn.cursor() as cur:
        cur.execute("SELECT MaPB FROM PhongBan WHERE MaPB = 'PB_HN_TV';")
        if not cur.fetchone():
            cur.execute("INSERT INTO PhongBan (MaPB, TenPB, MaCN) VALUES ('PB_HN_TV', 'Phòng Tài Vụ', 'HN');")
            
        cur.execute("SELECT MaPB FROM PhongBan WHERE MaPB = 'PB_HN_NS';")
        if not cur.fetchone():
            cur.execute("INSERT INTO PhongBan (MaPB, TenPB, MaCN) VALUES ('PB_HN_NS', 'Phòng Nhân Sự', 'HN');")

        # Tạo nhân viên Finance
        cur.execute("SELECT MaNV FROM NhanVien WHERE MaNV = 'NV_HN_TV_01';")
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN)
                VALUES ('NV_HN_TV_01', 'Lê Tài Vụ', 'Nam', '1992-02-02', '0912333444', 'finance@x.corp', 'MST_TV_01', 'PB_HN_TV', 'NV', 1, 'HN');
            """)
            cur.execute("INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV) VALUES ('finance_user', %s, 'NV_HN_TV_01');", (pwd_hash,))
            cur.execute("""
                INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
                VALUES ('L_HN_TV_01_0326', 'NV_HN_TV_01', 3, 2026, 20000000, 2000000, 1000000, 0);
            """)

    # 2. Tạo Giám đốc chi nhánh DN nếu chưa có
    with db_conn_dn.cursor() as cur:
        # Đảm bảo ChucVu GD tồn tại trên site_dn
        cur.execute("""
            INSERT INTO ChucVu (MaCV, TenCV, HeSoLuong)
            VALUES ('GD', 'Giám đốc chi nhánh', 3.0)
            ON CONFLICT (MaCV) DO NOTHING;
        """)
        # Đảm bảo có vai trò 3
        cur.execute("SELECT MaNV FROM NhanVien WHERE MaNV = 'NV_DN_DIR_01';")
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN)
                VALUES ('NV_DN_DIR_01', 'Phạm Giám Đốc DN', 'Nam', '1985-05-05', '0905111222', 'director_dn@x.corp', 'MST_DN_DIR', 'PB_DN_01', 'GD', 3, 'DN');
            """)
            cur.execute("INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV) VALUES ('cuong_gd_dn', %s, 'NV_DN_DIR_01');", (pwd_hash,))
            cur.execute("""
                INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
                VALUES ('L_DN_DIR_0326', 'NV_DN_DIR_01', 3, 2026, 35000000, 5000000, 3000000, 0);
            """)

def get_auth_token(client, username, password="Password123"):
    """Lấy JWT token cho người dùng."""
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    if res.status_code == 200:
        return res.json()["data"]["access_token"]
    # Fallback thử với password 123456
    res2 = client.post("/api/auth/login", json={"username": username, "password": "123456"})
    if res2.status_code == 200:
        return res2.json()["data"]["access_token"]
    raise ValueError(f"Không thể đăng nhập cho tài khoản {username}: {res.text}")

def test_employee_salary_masking_for_colleagues(client, db_conn_hn, db_conn_dn):
    """
    Quy tắc che giấu lương (Salary Masking):
    Nhân viên chuyên trách (Role 1) gọi /api/employees:
    - Lương của đồng nghiệp khác BẮT BUỘC bị che (None hoặc is_salary_masked = True).
    - Lương của chính mình không bị che.
    """
    ensure_test_users(db_conn_hn, db_conn_dn)
    token = get_auth_token(client, "cuong_dn")
    
    response = client.get("/api/employees", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    raw_data = response.json()["data"]
    items = raw_data if isinstance(raw_data, list) else raw_data.get("items", [])
    assert len(items) > 0
    
    for emp in items:
        if emp.get("ma_nv") == "NV_DN_01":
            # Lương của chính mình -> không che
            assert emp.get("is_salary_masked") is False or emp.get("luong_thuc_linh") is not None
        else:
            # Lương của đồng nghiệp khác -> phải bị che
            assert emp.get("is_salary_masked") is True or emp.get("luong_thuc_linh") is None, \
                f"Lương của nhân viên {emp.get('ma_nv')} không được phép hiển thị cho đồng nghiệp!"

def test_finance_role_pii_masking_on_payroll(client, db_conn_hn, db_conn_dn):
    """
    Quy tắc che giấu thông tin định danh (PII Masking cho Phòng Tài Vụ):
    Nhân viên Phòng Tài Vụ gọi /api/payroll:
    - Xem được đầy đủ các chỉ số lương (không bị che lương).
    - Nhưng thông tin cá nhân (Họ tên, SĐT, Email) của nhân viên phòng khác bị che (*** Bảo mật *** hoặc None).
    """
    ensure_test_users(db_conn_hn, db_conn_dn)
    token = get_auth_token(client, "finance_user")
    
    response = client.get("/api/payroll?month=3&year=2026", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    raw_data = response.json()["data"]
    items = raw_data if isinstance(raw_data, list) else raw_data.get("items", [])
    assert len(items) > 0
    
    for record in items:
        # Cột lương luôn phải có giá trị cho phòng tài vụ
        assert record.get("luong_thuc_linh") is not None, "Tài vụ phải thấy số tiền lương để đối soát!"
        
        # Nếu nhân viên không thuộc phòng tài vụ (PB_HN_TV) -> PII phải bị mask
        if record.get("ten_phong_ban") != "Phòng Tài Vụ" and record.get("ma_pb") != "PB_HN_TV":
            ho_ten = record.get("ho_ten") or ""
            assert "***" in ho_ten or ho_ten == "" or record.get("is_pii_masked") is True, \
                f"PII họ tên của nhân viên {record.get('ma_nv')} ngoài phòng Tài vụ chưa được che giấu: {ho_ten}"

def test_branch_director_modify_other_branch_salary_forbidden(client, db_conn_hn, db_conn_dn):
    """
    Kiểm tra phân quyền cập nhật lương:
    Giám đốc chi nhánh Đà Nẵng (cuong_gd_dn) cố gắng cập nhật lương cho nhân viên thuộc chi nhánh Hà Nội (NV_HN_02):
    - BẮT BUỘC trả về HTTP 403 Forbidden.
    """
    ensure_test_users(db_conn_hn, db_conn_dn)
    token = get_auth_token(client, "cuong_gd_dn")
    
    response = client.put("/api/payroll/NV_HN_02", json={
        "thang": 3,
        "nam": 2026,
        "luong_co_ban": 50000000,
        "phu_cap": 0,
        "thuong": 0,
        "khau_tru": 0
    }, headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403, f"Expected 403 Forbidden when Branch Director updates other branch salary, got {response.status_code}"

def test_general_director_can_view_all_and_modify_any_salary(client, db_conn_hn, db_conn_dn):
    """
    Quyền tối cao toàn cục của Tổng Giám Đốc (CEO):
    - Xem danh sách nhân viên: Xem đầy đủ toàn bộ lương của tất cả nhân sự (is_salary_masked = False).
    - Cập nhật lương: Có quyền cập nhật lương cho nhân sự bất kỳ thuộc bất kỳ chi nhánh nào -> 200 OK.
    """
    ensure_test_users(db_conn_hn, db_conn_dn)
    token = get_auth_token(client, "giap_gd")
    
    # 1. Xem danh sách nhân viên
    res_list = client.get("/api/employees", headers={"Authorization": f"Bearer {token}"})
    assert res_list.status_code == 200
    items = res_list.json()["data"]["items"]
    for emp in items:
        assert emp.get("is_salary_masked") is False, f"Tổng giám đốc bị che lương của nhân viên {emp.get('ma_nv')}!"

    # 2. Cập nhật lương nhân viên tại Đà Nẵng (NV_DN_01)
    res_update_dn = client.put("/api/payroll/NV_DN_01", json={
        "thang": 3,
        "nam": 2026,
        "luong_co_ban": 22000000,
        "phu_cap": 2000000,
        "thuong": 1000000,
        "khau_tru": 500000
    }, headers={"Authorization": f"Bearer {token}"})
    assert res_update_dn.status_code == 200, f"Tổng giám đốc cập nhật lương thất bại: {res_update_dn.text}"
    assert res_update_dn.json()["data"]["luong_thuc_linh"] == 24500000.0

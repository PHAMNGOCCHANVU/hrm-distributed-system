import os
import psycopg2
import hashlib

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

SITES = [
    {"name": "site_hn", "port": 5431, "dbname": "qlns_hn", "user": "postgres", "password": "PasswordHN_123", "branch": "HN"},
    {"name": "site_dn", "port": 5434, "dbname": "qlns_dn", "user": "postgres", "password": "PasswordDN_123", "branch": "DN"},
    {"name": "site_hcm", "port": 5433, "dbname": "qlns_hcm", "user": "postgres", "password": "PasswordHCM_123", "branch": "HCM"},
]

def run_migration():
    print("=== BẮT ĐẦU NÂNG CẤP SCHEMA (06_enterprise_baseline_migration.sql) ===")
    with open("database/scripts/06_enterprise_baseline_migration.sql", "r", encoding="utf-8") as f:
        migration_sql = f.read()

    for site in SITES:
        print(f"[*] Chạy migration trên {site['name']} (Port {site['port']})...")
        conn = psycopg2.connect(
            host="localhost",
            port=site["port"],
            dbname=site["dbname"],
            user=site["user"],
            password=site["password"]
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(migration_sql)
        cur.close()
        conn.close()
        print(f"[+] Thành công trên {site['name']}!")

    print("\n=== NẠP DỮ LIỆU CƠ CẤU TỔ CHỨC 2 BỘ MÁY TẠI HN VÀ CÁC CHI NHÁNH ===")
    
    # 1. Seed Phòng Ban Hà Nội (Coordinator site_hn)
    conn_hn = psycopg2.connect(host="localhost", port=5431, dbname="qlns_hn", user="postgres", password="PasswordHN_123")
    conn_hn.autocommit = True
    cur_hn = conn_hn.cursor()

    # Cập nhật các phòng ban cũ
    cur_hn.execute("""
        UPDATE PhongBan SET LoaiDonVi = 'TAP_DOAN', ThuTuSapXep = 1 WHERE MaPB IN ('PB_HN_01', 'PB_HN_NS', 'PB_HN_TV');
    """)

    # Thêm các phòng ban chuẩn Tập đoàn và Chi nhánh HN
    depts_hn = [
        # Bộ máy Tập đoàn (LoaiDonVi = 'TAP_DOAN')
        ('PB_HQ_ADMIN', 'Văn phòng Quản trị Tập đoàn', 'HN', 'TAP_DOAN', None, 1),
        ('PB_HQ_HR', 'Phòng Nhân sự Tập đoàn', 'HN', 'TAP_DOAN', None, 2),
        ('PB_HQ_FIN', 'Phòng Tài chính Tập đoàn', 'HN', 'TAP_DOAN', None, 3),
        ('PB_HQ_OPS', 'Phòng Vận hành Tập đoàn', 'HN', 'TAP_DOAN', None, 4),
        # Bộ máy Chi nhánh Hà Nội (LoaiDonVi = 'CHI_NHANH')
        ('PB_HN_DIR', 'Ban Giám đốc Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 10),
        ('PB_HN_HR', 'Phòng Nhân sự Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 11),
        ('PB_HN_FIN', 'Phòng Tài vụ Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 12),
        ('PB_HN_OPS', 'Phòng Vận hành Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 13),
        ('PB_HN_KD', 'Phòng Kinh doanh Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 14),
    ]

    for pb in depts_hn:
        cur_hn.execute("""
            INSERT INTO PhongBan (MaPB, TenPB, MaCN, LoaiDonVi, MaDonViCha, ThuTuSapXep)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (MaPB) DO UPDATE 
            SET TenPB = EXCLUDED.TenPB, LoaiDonVi = EXCLUDED.LoaiDonVi, ThuTuSapXep = EXCLUDED.ThuTuSapXep;
        """, pb)

    # Thêm nhân viên mẫu bộ máy HN
    staff_hn = [
        # CEO Tập đoàn
        ('NV_HQ_CEO', 'Lưu Quang Giáp', 'Nam', '1980-01-15', '0912000111', 'giap.ceo@x.corp', 'MST_HQ_01', 'PB_HQ_ADMIN', 'CEO', 4, 'HN', 'DangLamViec'),
        # Trưởng phòng Vận hành Tập đoàn (System Operator)
        ('NV_HQ_OPS_01', 'Vũ Vận Hành', 'Nam', '1991-03-20', '0912333444', 'ops.hq@x.corp', 'MST_HQ_OPS', 'PB_HQ_OPS', 'TP', 2, 'HN', 'DangLamViec'),
        # Giám đốc Chi nhánh Hà Nội
        ('NV_HN_DIR_01', 'Trần Giám Đốc HN', 'Nam', '1983-05-10', '0912777888', 'dir.hn@x.corp', 'MST_HN_DIR', 'PB_HN_DIR', 'GD_CN', 3, 'HN', 'DangLamViec'),
        # Trưởng phòng Kinh doanh HN
        ('NV_HN_KD_01', 'Phạm Thị D', 'Nữ', '1992-09-15', '0912999000', 'kd.hn@x.corp', 'MST_HN_KD', 'PB_HN_KD', 'TP', 2, 'HN', 'DangLamViec'),
    ]

    for st in staff_hn:
        cur_hn.execute("""
            INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (MaNV) DO UPDATE 
            SET HoTen = EXCLUDED.HoTen, MaPB = EXCLUDED.MaPB, MaCV = EXCLUDED.MaCV, MaVaiTro = EXCLUDED.MaVaiTro;
        """, st)

    # NguoiDungDangNhap cho HN
    users_hn = [
        ('giap_ceo', hash_pw('123456'), 'NV_HQ_CEO'),
        ('ops_hq', hash_pw('123456'), 'NV_HQ_OPS_01'),
        ('dir_hn', hash_pw('123456'), 'NV_HN_DIR_01'),
    ]
    for u in users_hn:
        cur_hn.execute("""
            INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV)
            VALUES (%s, %s, %s)
            ON CONFLICT (TenDangNhap) DO UPDATE SET MatKhauHash = EXCLUDED.MatKhauHash, MaNV = EXCLUDED.MaNV;
        """, u)

    # Gán vai trò NhanVien_VaiTro cho HN
    roles_hn = [
        ('NV_HN_01', 'GROUP_EXECUTIVE', 'GLOBAL', None),
        ('NV_HQ_CEO', 'GROUP_EXECUTIVE', 'GLOBAL', None),
        ('NV_HQ_OPS_01', 'SYSTEM_OPERATOR', 'GLOBAL', None),
        ('NV_HN_NS_01', 'HR_SPECIALIST', 'GLOBAL', None),
        ('NV_HN_NS_01', 'DEPT_MANAGER', 'DEPARTMENT', 'PB_HQ_HR'),
        ('NV_HN_TV_02', 'FINANCE_SPECIALIST', 'GLOBAL', None),
        ('NV_HN_TV_02', 'DEPT_MANAGER', 'DEPARTMENT', 'PB_HQ_FIN'),
        ('NV_HN_DIR_01', 'BRANCH_DIRECTOR', 'BRANCH', 'HN'),
    ]
    for r in roles_hn:
        cur_hn.execute("""
            INSERT INTO NhanVien_VaiTro (MaNV, MaVaiTro, PhamViApDung, MaDonViApDung)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (MaNV, MaVaiTro, PhamViApDung) DO NOTHING;
        """, r)

    cur_hn.close()
    conn_hn.close()
    print("[+] Đã nạp dữ liệu Hà Nội!")

    # 2. Seed Đà Nẵng
    conn_dn = psycopg2.connect(host="localhost", port=5434, dbname="qlns_dn", user="postgres", password="PasswordDN_123")
    conn_dn.autocommit = True
    cur_dn = conn_dn.cursor()

    cur_dn.execute("""
        UPDATE PhongBan SET LoaiDonVi = 'CHI_NHANH', ThuTuSapXep = 20 WHERE MaPB IN ('PB_DN_01', 'PB_DN_BGD');
    """)

    depts_dn = [
        ('PB_DN_BGD', 'Ban Giám đốc Chi nhánh Đà Nẵng', 'DN', 'CHI_NHANH', None, 20),
        ('PB_DN_01', 'Phòng Kỹ thuật & R&D', 'DN', 'CHI_NHANH', None, 21),
        ('PB_DN_HR', 'Phòng Nhân sự Chi nhánh Đà Nẵng', 'DN', 'CHI_NHANH', None, 22),
        ('PB_DN_FIN', 'Phòng Tài vụ Chi nhánh Đà Nẵng', 'DN', 'CHI_NHANH', None, 23),
        ('PB_DN_OPS', 'Phòng Vận hành Chi nhánh Đà Nẵng', 'DN', 'CHI_NHANH', None, 24),
    ]
    for pb in depts_dn:
        cur_dn.execute("""
            INSERT INTO PhongBan (MaPB, TenPB, MaCN, LoaiDonVi, MaDonViCha, ThuTuSapXep)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (MaPB) DO UPDATE 
            SET TenPB = EXCLUDED.TenPB, LoaiDonVi = EXCLUDED.LoaiDonVi, ThuTuSapXep = EXCLUDED.ThuTuSapXep;
        """, pb)

    # Đảm bảo Giám đốc ĐN có tài khoản tuan_gd_dn
    cur_dn.execute("""
        INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai)
        VALUES ('NV_DN_DIR_02', 'Nguyễn Anh Tuấn', 'Nam', '1985-06-12', '0905111222', 'tuan.gd@x.corp', 'MST_DN_DIR', 'PB_DN_BGD', 'GD_CN', 3, 'DN', 'DangLamViec')
        ON CONFLICT (MaNV) DO UPDATE 
        SET HoTen = EXCLUDED.HoTen, MaPB = EXCLUDED.MaPB, MaCV = EXCLUDED.MaCV;
    """)
    cur_dn.execute("""
        INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV)
        VALUES ('tuan_gd_dn', %s, 'NV_DN_DIR_02')
        ON CONFLICT (TenDangNhap) DO UPDATE SET MatKhauHash = EXCLUDED.MatKhauHash;
    """, (hash_pw('123456'),))

    roles_dn = [
        ('NV_DN_DIR_02', 'BRANCH_DIRECTOR', 'BRANCH', 'DN'),
        ('NV_DN_02', 'DEPT_MANAGER', 'DEPARTMENT', 'PB_DN_01'),
        ('NV_DN_01', 'EMPLOYEE', 'PERSONAL', None),
    ]
    for r in roles_dn:
        cur_dn.execute("""
            INSERT INTO NhanVien_VaiTro (MaNV, MaVaiTro, PhamViApDung, MaDonViApDung)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (MaNV, MaVaiTro, PhamViApDung) DO NOTHING;
        """, r)

    cur_dn.close()
    conn_dn.close()
    print("[+] Đã nạp dữ liệu Đà Nẵng!")

    # 3. Seed TP.HCM
    conn_hcm = psycopg2.connect(host="localhost", port=5433, dbname="qlns_hcm", user="postgres", password="PasswordHCM_123")
    conn_hcm.autocommit = True
    cur_hcm = conn_hcm.cursor()

    cur_hcm.execute("""
        UPDATE PhongBan SET LoaiDonVi = 'CHI_NHANH', ThuTuSapXep = 30 WHERE MaPB IN ('PB_HCM_01', 'PB_HCM_BGD');
    """)

    depts_hcm = [
        ('PB_HCM_BGD', 'Ban Giám đốc Chi nhánh TP.HCM', 'HCM', 'CHI_NHANH', None, 30),
        ('PB_HCM_01', 'Phòng Kinh doanh TP.HCM', 'HCM', 'CHI_NHANH', None, 31),
        ('PB_HCM_HR', 'Phòng Nhân sự Chi nhánh TP.HCM', 'HCM', 'CHI_NHANH', None, 32),
        ('PB_HCM_FIN', 'Phòng Tài vụ Chi nhánh TP.HCM', 'HCM', 'CHI_NHANH', None, 33),
        ('PB_HCM_OPS', 'Phòng Vận hành Chi nhánh TP.HCM', 'HCM', 'CHI_NHANH', None, 34),
    ]
    for pb in depts_hcm:
        cur_hcm.execute("""
            INSERT INTO PhongBan (MaPB, TenPB, MaCN, LoaiDonVi, MaDonViCha, ThuTuSapXep)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (MaPB) DO UPDATE 
            SET TenPB = EXCLUDED.TenPB, LoaiDonVi = EXCLUDED.LoaiDonVi, ThuTuSapXep = EXCLUDED.ThuTuSapXep;
        """, pb)

    # Đảm bảo Giám đốc HCM có tài khoản bao_gd_hcm
    cur_hcm.execute("""
        INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai)
        VALUES ('NV_HCM_DIR_01', 'Huỳnh Quốc Bảo', 'Nam', '1982-10-24', '0908111222', 'bao.gd@x.corp', 'MST_HCM_DIR', 'PB_HCM_BGD', 'GD_CN', 3, 'HCM', 'DangLamViec')
        ON CONFLICT (MaNV) DO UPDATE 
        SET HoTen = EXCLUDED.HoTen, MaPB = EXCLUDED.MaPB, MaCV = EXCLUDED.MaCV;
    """)
    cur_hcm.execute("""
        INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV)
        VALUES ('bao_gd_hcm', %s, 'NV_HCM_DIR_01')
        ON CONFLICT (TenDangNhap) DO UPDATE SET MatKhauHash = EXCLUDED.MatKhauHash;
    """, (hash_pw('123456'),))

    roles_hcm = [
        ('NV_HCM_DIR_01', 'BRANCH_DIRECTOR', 'BRANCH', 'HCM'),
        ('NV_HCM_01', 'DEPT_MANAGER', 'DEPARTMENT', 'PB_HCM_01'),
        ('NV_HCM_02', 'EMPLOYEE', 'PERSONAL', None),
    ]
    for r in roles_hcm:
        cur_hcm.execute("""
            INSERT INTO NhanVien_VaiTro (MaNV, MaVaiTro, PhamViApDung, MaDonViApDung)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (MaNV, MaVaiTro, PhamViApDung) DO NOTHING;
        """, r)

    cur_hcm.close()
    conn_hcm.close()
    print("[+] Đã nạp dữ liệu TP.HCM!")

    # 4. Chạy FDW update trên Coordinator site_hn
    print("\n=== CẬP NHẬT FDW VÀ GLOBAL VIEWS TRÊN COORDINATOR (07_update_fdw_global_views.sql) ===")
    with open("database/scripts/07_update_fdw_global_views.sql", "r", encoding="utf-8") as f:
        fdw_sql = f.read()

    conn_hn = psycopg2.connect(host="localhost", port=5431, dbname="qlns_hn", user="postgres", password="PasswordHN_123")
    conn_hn.autocommit = True
    cur_hn = conn_hn.cursor()
    cur_hn.execute(fdw_sql)
    cur_hn.close()
    conn_hn.close()
    print("[+] Hoàn tất cập nhật FDW và Global Views!")

if __name__ == "__main__":
    run_migration()

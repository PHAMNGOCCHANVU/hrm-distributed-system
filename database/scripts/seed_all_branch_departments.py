import os
import psycopg2
import hashlib
import json

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

STANDARD_PW_HASH = hash_pw('123456')

SITES = {
    'HN': {
        'host': 'localhost',
        'port': 5431,
        'dbname': 'qlns_hn',
        'user': 'postgres',
        'password': 'PasswordHN_123'
    },
    'DN': {
        'host': 'localhost',
        'port': 5434,
        'dbname': 'qlns_dn',
        'user': 'postgres',
        'password': 'PasswordDN_123'
    },
    'HCM': {
        'host': 'localhost',
        'port': 5433,
        'dbname': 'qlns_hcm',
        'user': 'postgres',
        'password': 'PasswordHCM_123'
    }
}

# Danh sách phòng ban và nhân sự nạp thêm
DATA = {
    'HN': {
        'depts': [
            ('PB_HN_KD', 'Phòng Kinh doanh Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 14),
            ('PB_HN_HR', 'Phòng Nhân sự Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 11),
            ('PB_HN_FIN', 'Phòng Tài vụ Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 12),
            ('PB_HN_OPS', 'Phòng Vận hành Chi nhánh Hà Nội', 'HN', 'CHI_NHANH', None, 13),
        ],
        'staff': [
            # Phòng Kinh doanh HN
            ('NV_HN_KD_01', 'Phạm Thị Dung', 'Nữ', '1992-09-15', '0912999001', 'dung.kd.hn@x.corp', 'MST_HN_KD_01', 'PB_HN_KD', 'TP', 2, 'HN', 'DangLamViec', 'tp_kd_hn', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_HN_KD')]),
            ('NV_HN_KD_02', 'Lê Văn Doanh', 'Nam', '1995-11-20', '0912999002', 'doanh.kd.hn@x.corp', 'MST_HN_KD_02', 'PB_HN_KD', 'NV', 1, 'HN', 'DangLamViec', 'nv_kd_hn', 15000000, 2000000, 1000000, 800000, 17200000, [('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Nhân sự HN
            ('NV_HN_HR_01', 'Trịnh Thị Mai', 'Nữ', '1990-04-12', '0912888001', 'mai.hr.hn@x.corp', 'MST_HN_HR_01', 'PB_HN_HR', 'TP', 2, 'HN', 'DangLamViec', 'tp_hr_hn', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_HN_HR'), ('HR_SPECIALIST', 'BRANCH', 'HN')]),
            ('NV_HN_HR_02', 'Đỗ Minh Tú', 'Nam', '1996-07-25', '0912888002', 'tu.hr.hn@x.corp', 'MST_HN_HR_02', 'PB_HN_HR', 'NV', 1, 'HN', 'DangLamViec', 'nv_hr_hn', 15000000, 2000000, 1000000, 800000, 17200000, [('HR_SPECIALIST', 'BRANCH', 'HN'), ('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Tài vụ HN
            ('NV_HN_FIN_01', 'Nguyễn Văn Hưng', 'Nam', '1989-08-30', '0912777001', 'hung.fin.hn@x.corp', 'MST_HN_FIN_01', 'PB_HN_FIN', 'TP', 2, 'HN', 'DangLamViec', 'tp_fin_hn', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_HN_FIN'), ('FINANCE_SPECIALIST', 'BRANCH', 'HN')]),
            ('NV_HN_FIN_02', 'Vũ Mai Lan', 'Nữ', '1997-03-14', '0912777002', 'lan.fin.hn@x.corp', 'MST_HN_FIN_02', 'PB_HN_FIN', 'NV', 1, 'HN', 'DangLamViec', 'nv_fin_hn', 15000000, 2000000, 1000000, 800000, 17200000, [('FINANCE_SPECIALIST', 'BRANCH', 'HN'), ('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Vận hành HN
            ('NV_HN_OPS_01', 'Lê Vận Hành HN', 'Nam', '1991-12-05', '0912666001', 'ops.tp.hn@x.corp', 'MST_HN_OPS_01', 'PB_HN_OPS', 'TP', 2, 'HN', 'DangLamViec', 'tp_ops_hn', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_HN_OPS'), ('SYSTEM_OPERATOR', 'BRANCH', 'HN')]),
            ('NV_HN_OPS_02', 'Trần Văn Trực', 'Nam', '1994-06-18', '0912666002', 'truc.ops.hn@x.corp', 'MST_HN_OPS_02', 'PB_HN_OPS', 'NV', 1, 'HN', 'DangLamViec', 'nv_ops_hn', 15000000, 2000000, 1000000, 800000, 17200000, [('SYSTEM_OPERATOR', 'BRANCH', 'HN'), ('EMPLOYEE', 'PERSONAL', None)]),
        ]
    },
    'DN': {
        'depts': [
            ('PB_DN_KD', 'Phòng Kinh doanh Chi nhánh Đà Nẵng', 'DN', 'CHI_NHANH', None, 25),
            ('PB_DN_HR', 'Phòng Nhân sự Chi nhánh Đà Nẵng', 'DN', 'CHI_NHANH', None, 22),
            ('PB_DN_FIN', 'Phòng Tài vụ Chi nhánh Đà Nẵng', 'DN', 'CHI_NHANH', None, 23),
            ('PB_DN_OPS', 'Phòng Vận hành Chi nhánh Đà Nẵng', 'DN', 'CHI_NHANH', None, 24),
        ],
        'staff': [
            # Phòng Kinh doanh ĐN
            ('NV_DN_KD_01', 'Phan Văn Khải', 'Nam', '1991-05-19', '0905999001', 'khai.kd.dn@x.corp', 'MST_DN_KD_01', 'PB_DN_KD', 'TP', 2, 'DN', 'DangLamViec', 'tp_kd_dn', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_DN_KD')]),
            ('NV_DN_KD_02', 'Nguyễn Thị Tuyết', 'Nữ', '1996-08-11', '0905999002', 'tuyet.kd.dn@x.corp', 'MST_DN_KD_02', 'PB_DN_KD', 'NV', 1, 'DN', 'DangLamViec', 'nv_kd_dn', 15000000, 2000000, 1000000, 800000, 17200000, [('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Nhân sự ĐN
            ('NV_DN_HR_01', 'Hoàng Thị Thảo', 'Nữ', '1992-02-14', '0905888001', 'thao.hr.dn@x.corp', 'MST_DN_HR_01', 'PB_DN_HR', 'TP', 2, 'DN', 'DangLamViec', 'tp_hr_dn', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_DN_HR'), ('HR_SPECIALIST', 'BRANCH', 'DN')]),
            ('NV_DN_HR_02', 'Trần Quốc Việt', 'Nam', '1995-10-09', '0905888002', 'viet.hr.dn@x.corp', 'MST_DN_HR_02', 'PB_DN_HR', 'NV', 1, 'DN', 'DangLamViec', 'nv_hr_dn', 15000000, 2000000, 1000000, 800000, 17200000, [('HR_SPECIALIST', 'BRANCH', 'DN'), ('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Tài vụ ĐN
            ('NV_DN_FIN_01', 'Phan Thành Đạt', 'Nam', '1988-12-03', '0905777001', 'dat.fin.dn@x.corp', 'MST_DN_FIN_01', 'PB_DN_FIN', 'TP', 2, 'DN', 'DangLamViec', 'tp_fin_dn', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_DN_FIN'), ('FINANCE_SPECIALIST', 'BRANCH', 'DN')]),
            ('NV_DN_FIN_02', 'Đặng Quỳnh Nga', 'Nữ', '1997-04-22', '0905777002', 'nga.fin.dn@x.corp', 'MST_DN_FIN_02', 'PB_DN_FIN', 'NV', 1, 'DN', 'DangLamViec', 'nv_fin_dn', 15000000, 2000000, 1000000, 800000, 17200000, [('FINANCE_SPECIALIST', 'BRANCH', 'DN'), ('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Vận hành ĐN
            ('NV_DN_OPS_01', 'Bùi Quang Huy', 'Nam', '1993-06-15', '0905666001', 'huy.ops.dn@x.corp', 'MST_DN_OPS_01', 'PB_DN_OPS', 'TP', 2, 'DN', 'DangLamViec', 'tp_ops_dn', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_DN_OPS'), ('SYSTEM_OPERATOR', 'BRANCH', 'DN')]),
            ('NV_DN_OPS_02', 'Lê Hải Triều', 'Nam', '1996-01-30', '0905666002', 'trieu.ops.dn@x.corp', 'MST_DN_OPS_02', 'PB_DN_OPS', 'NV', 1, 'DN', 'DangLamViec', 'nv_ops_dn', 15000000, 2000000, 1000000, 800000, 17200000, [('SYSTEM_OPERATOR', 'BRANCH', 'DN'), ('EMPLOYEE', 'PERSONAL', None)]),
        ]
    },
    'HCM': {
        'depts': [
            ('PB_HCM_HR', 'Phòng Nhân sự Chi nhánh TP.HCM', 'HCM', 'CHI_NHANH', None, 32),
            ('PB_HCM_FIN', 'Phòng Tài vụ Chi nhánh TP.HCM', 'HCM', 'CHI_NHANH', None, 33),
            ('PB_HCM_OPS', 'Phòng Vận hành Chi nhánh TP.HCM', 'HCM', 'CHI_NHANH', None, 34),
            ('PB_HCM_KT', 'Phòng Kỹ thuật & Công nghệ HCM', 'HCM', 'CHI_NHANH', None, 35),
        ],
        'staff': [
            # Phòng Nhân sự HCM
            ('NV_HCM_HR_01', 'Nguyễn Ngọc Diễm', 'Nữ', '1991-03-27', '0908888001', 'diem.hr.hcm@x.corp', 'MST_HCM_HR_01', 'PB_HCM_HR', 'TP', 2, 'HCM', 'DangLamViec', 'tp_hr_hcm', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_HCM_HR'), ('HR_SPECIALIST', 'BRANCH', 'HCM')]),
            ('NV_HCM_HR_02', 'Lý Hoàng Nam', 'Nam', '1995-09-14', '0908888002', 'nam.hr.hcm@x.corp', 'MST_HCM_HR_02', 'PB_HCM_HR', 'NV', 1, 'HCM', 'DangLamViec', 'nv_hr_hcm', 15000000, 2000000, 1000000, 800000, 17200000, [('HR_SPECIALIST', 'BRANCH', 'HCM'), ('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Tài vụ HCM
            ('NV_HCM_FIN_01', 'Trần Công Thành', 'Nam', '1987-11-08', '0908777001', 'thanh.fin.hcm@x.corp', 'MST_HCM_FIN_01', 'PB_HCM_FIN', 'TP', 2, 'HCM', 'DangLamViec', 'tp_fin_hcm', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_HCM_FIN'), ('FINANCE_SPECIALIST', 'BRANCH', 'HCM')]),
            ('NV_HCM_FIN_02', 'Phạm Thị Kim Oanh', 'Nữ', '1996-05-12', '0908777002', 'oanh.fin.hcm@x.corp', 'MST_HCM_FIN_02', 'PB_HCM_FIN', 'NV', 1, 'HCM', 'DangLamViec', 'nv_fin_hcm', 15000000, 2000000, 1000000, 800000, 17200000, [('FINANCE_SPECIALIST', 'BRANCH', 'HCM'), ('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Vận hành HCM
            ('NV_HCM_OPS_01', 'Võ Quốc Khánh', 'Nam', '1990-10-02', '0908666001', 'khanh.ops.hcm@x.corp', 'MST_HCM_OPS_01', 'PB_HCM_OPS', 'TP', 2, 'HCM', 'DangLamViec', 'tp_ops_hcm', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_HCM_OPS'), ('SYSTEM_OPERATOR', 'BRANCH', 'HCM')]),
            ('NV_HCM_OPS_02', 'Huỳnh Gia Bảo', 'Nam', '1998-04-16', '0908666002', 'bao.ops.hcm@x.corp', 'MST_HCM_OPS_02', 'PB_HCM_OPS', 'NV', 1, 'HCM', 'DangLamViec', 'nv_ops_hcm', 15000000, 2000000, 1000000, 800000, 17200000, [('SYSTEM_OPERATOR', 'BRANCH', 'HCM'), ('EMPLOYEE', 'PERSONAL', None)]),
            # Phòng Kỹ thuật & Công nghệ HCM
            ('NV_HCM_KT_01', 'Phan Gia Huy', 'Nam', '1989-06-21', '0908555001', 'huy.kt.hcm@x.corp', 'MST_HCM_KT_01', 'PB_HCM_KT', 'TP', 2, 'HCM', 'DangLamViec', 'tp_kt_hcm', 25000000, 5000000, 2000000, 1500000, 30500000, [('DEPT_MANAGER', 'DEPARTMENT', 'PB_HCM_KT')]),
            ('NV_HCM_KT_02', 'Trương Tuấn Kiệt', 'Nam', '1995-08-30', '0908555002', 'kiet.kt.hcm@x.corp', 'MST_HCM_KT_02', 'PB_HCM_KT', 'NV', 1, 'HCM', 'DangLamViec', 'nv_kt_hcm', 15000000, 2000000, 1000000, 800000, 17200000, [('EMPLOYEE', 'PERSONAL', None)]),
        ]
    }
}

def seed():
    for branch_key, conf in SITES.items():
        print(f"\n=======================================================")
        print(f"[*] Đang nạp dữ liệu cho chi nhánh {branch_key} ({conf['dbname']} - Port {conf['port']})...")
        conn = psycopg2.connect(
            host=conf['host'],
            port=conf['port'],
            dbname=conf['dbname'],
            user=conf['user'],
            password=conf['password']
        )
        conn.autocommit = True
        cur = conn.cursor()

        branch_data = DATA.get(branch_key, {})
        
        # 1. Nạp phòng ban
        for pb in branch_data.get('depts', []):
            cur.execute("""
                INSERT INTO PhongBan (MaPB, TenPB, MaCN, LoaiDonVi, MaDonViCha, ThuTuSapXep)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (MaPB) DO UPDATE 
                SET TenPB = EXCLUDED.TenPB, LoaiDonVi = EXCLUDED.LoaiDonVi, ThuTuSapXep = EXCLUDED.ThuTuSapXep;
            """, pb)
            print(f"  [+] Đã cập nhật phòng ban: {pb[0]} - {pb[1]}")

        # 2. Nạp nhân sự, tài khoản, lương, vai trò
        for st in branch_data.get('staff', []):
            ma_nv, ho_ten, phai, ngay_sinh, sdt, email, mst, ma_pb, ma_cv, ma_vt, ma_cn, trang_thai, username, lc_ban, phu_cap, thuong, khau_tru, thuc_linh, roles = st

            # a. NhanVien
            cur.execute("""
                INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (MaNV) DO UPDATE 
                SET HoTen = EXCLUDED.HoTen, MaPB = EXCLUDED.MaPB, MaCV = EXCLUDED.MaCV, MaVaiTro = EXCLUDED.MaVaiTro,
                    Email = EXCLUDED.Email, SoDienThoai = EXCLUDED.SoDienThoai;
            """, (ma_nv, ho_ten, phai, ngay_sinh, sdt, email, mst, ma_pb, ma_cv, ma_vt, ma_cn, trang_thai))

            # b. NguoiDungDangNhap
            cur.execute("""
                INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV)
                VALUES (%s, %s, %s)
                ON CONFLICT (TenDangNhap) DO UPDATE SET MatKhauHash = EXCLUDED.MatKhauHash, MaNV = EXCLUDED.MaNV;
            """, (username, STANDARD_PW_HASH, ma_nv))

            # c. Luong (Tháng 11/2026) - LuongThucLinh là Generated Column
            ma_luong = f"L_{ma_nv}_202611"
            cur.execute("""
                INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
                VALUES (%s, %s, 11, 2026, %s, %s, %s, %s)
                ON CONFLICT (MaLuong) DO UPDATE 
                SET LuongCoBan = EXCLUDED.LuongCoBan, PhuCap = EXCLUDED.PhuCap, Thuong = EXCLUDED.Thuong, 
                    KhauTru = EXCLUDED.KhauTru;
            """, (ma_luong, ma_nv, lc_ban, phu_cap, thuong, khau_tru))

            # d. HoSoMoRong
            hs_json = json.dumps({
                "skills": ["Chuyên môn nghiệp vụ", "Tin học văn phòng", "Quản lý công việc"],
                "education": "Đại học chính quy",
                "performance_reviews": [
                    {"quarter": "Q1-2026", "final_grade": "A", "feedback": "Hoàn thành tốt nhiệm vụ được giao."}
                ]
            })
            cur.execute("""
                INSERT INTO HoSoMoRong (MaNV, DuLieuJSON, NgayCapNhat)
                VALUES (%s, %s::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT (MaNV) DO UPDATE SET DuLieuJSON = EXCLUDED.DuLieuJSON, NgayCapNhat = CURRENT_TIMESTAMP;
            """, (ma_nv, hs_json))

            # e. NhanVien_VaiTro
            for r in roles:
                role_code, scope, entity_id = r
                cur.execute("""
                    INSERT INTO NhanVien_VaiTro (MaNV, MaVaiTro, PhamViApDung, MaDonViApDung)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (MaNV, MaVaiTro, PhamViApDung) DO NOTHING;
                """, (ma_nv, role_code, scope, entity_id))

            print(f"  [+] Đã nạp nhân sự & tài khoản: {username:<12} ({ho_ten}) - PB: {ma_pb} - CV: {ma_cv}")

        cur.close()
        conn.close()

    # 3. Cập nhật FDW trên Coordinator site_hn (5431)
    print("\n=======================================================")
    print("[*] Cập nhật lại Foreign Data Wrapper (FDW) trên Coordinator site_hn...")
    conn_hn = psycopg2.connect(
        host=SITES['HN']['host'],
        port=SITES['HN']['port'],
        dbname=SITES['HN']['dbname'],
        user=SITES['HN']['user'],
        password=SITES['HN']['password']
    )
    conn_hn.autocommit = True
    cur_hn = conn_hn.cursor()
    with open("database/scripts/07_update_fdw_global_views.sql", "r", encoding="utf-8") as f:
        fdw_sql = f.read()
    cur_hn.execute(fdw_sql)
    cur_hn.close()
    conn_hn.close()
    print("[+] Hoàn tất nạp đầy đủ phòng ban và tài khoản 3 chi nhánh!")

if __name__ == '__main__':
    seed()

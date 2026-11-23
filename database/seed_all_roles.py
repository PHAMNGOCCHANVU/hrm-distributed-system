import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

import hashlib
import json
from app.core.db_router import get_db_connection, SITE_HN, SITE_DN, SITE_HCM

PASSWORD_HASH = hashlib.sha256("123456".encode()).hexdigest()

def seed_accounts():
    print("=== BẮT ĐẦU NẠP TÀI KHOẢN VÀO CSDL PHÂN TÁN ===")

    # 1. SITE HÀ NỘI
    with get_db_connection(SITE_HN) as conn:
        with conn.cursor() as cur:
            # Cập nhật mật khẩu finance_user thành 123456 nếu có
            cur.execute("UPDATE NguoiDungDangNhap SET MatKhauHash = %s WHERE TenDangNhap = 'finance_user'", (PASSWORD_HASH,))

            hn_employees = [
                {
                    "manv": "NV_HN_NS_01",
                    "hoten": "Lê Thu Trang",
                    "phai": "Nữ",
                    "ngaysinh": "1990-08-15",
                    "sdt": "0912345601",
                    "email": "tranglt@x.corp",
                    "mst": "MST_HN_NS_01",
                    "mapb": "PB_HN_NS",
                    "macv": "TP",
                    "mavaitro": 2,
                    "macn": "HN",
                    "username": "trang_tpns",
                    "role_desc": "Trưởng phòng Nhân sự",
                    "luong_cb": 30000000,
                    "phu_cap": 3000000,
                    "thuong": 5000000,
                    "skills": [{"name": "HR Strategy", "level": "Expert"}, {"name": "Talent Acquisition", "level": "Advanced"}]
                },
                {
                    "manv": "NV_HN_NS_02",
                    "hoten": "Phạm Hoàng Nam",
                    "phai": "Nam",
                    "ngaysinh": "1995-11-20",
                    "sdt": "0912345602",
                    "email": "namph@x.corp",
                    "mst": "MST_HN_NS_02",
                    "mapb": "PB_HN_NS",
                    "macv": "NV",
                    "mavaitro": 1,
                    "macn": "HN",
                    "username": "nam_ns",
                    "role_desc": "Nhân viên Nhân sự",
                    "luong_cb": 18000000,
                    "phu_cap": 1500000,
                    "thuong": 2000000,
                    "skills": [{"name": "Recruitment", "level": "Intermediate"}, {"name": "C&B", "level": "Intermediate"}]
                },
                {
                    "manv": "NV_HN_TV_02",
                    "hoten": "Đặng Thùy Dung",
                    "phai": "Nữ",
                    "ngaysinh": "1988-03-12",
                    "sdt": "0912345603",
                    "email": "dungdt@x.corp",
                    "mst": "MST_HN_TV_02",
                    "mapb": "PB_HN_TV",
                    "macv": "TP",
                    "mavaitro": 2,
                    "macn": "HN",
                    "username": "dung_tptv",
                    "role_desc": "Trưởng phòng Tài vụ",
                    "luong_cb": 32000000,
                    "phu_cap": 3500000,
                    "thuong": 6000000,
                    "skills": [{"name": "Financial Planning", "level": "Expert"}, {"name": "Tax Accounting", "level": "Expert"}]
                },
                {
                    "manv": "NV_HN_03",
                    "hoten": "Ngô Quang Minh",
                    "phai": "Nam",
                    "ngaysinh": "1987-06-25",
                    "sdt": "0912345604",
                    "email": "minhnq@x.corp",
                    "mst": "MST_HN_03",
                    "mapb": "PB_HN_01",
                    "macv": "TP",
                    "mavaitro": 2,
                    "macn": "HN",
                    "username": "minh_tpqt",
                    "role_desc": "Trưởng phòng Quản Trị Trung Tâm",
                    "luong_cb": 35000000,
                    "phu_cap": 4000000,
                    "thuong": 7000000,
                    "skills": [{"name": "Operations Management", "level": "Expert"}, {"name": "Process Automation", "level": "Advanced"}]
                }
            ]

            for emp in hn_employees:
                cur.execute("""
                    INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'DangLamViec')
                    ON CONFLICT (MaNV) DO UPDATE SET HoTen = EXCLUDED.HoTen, MaPB = EXCLUDED.MaPB, MaCV = EXCLUDED.MaCV, MaVaiTro = EXCLUDED.MaVaiTro;
                """, (emp["manv"], emp["hoten"], emp["phai"], emp["ngaysinh"], emp["sdt"], emp["email"], emp["mst"], emp["mapb"], emp["macv"], emp["mavaitro"], emp["macn"]))

                cur.execute("""
                    INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (TenDangNhap) DO UPDATE SET MatKhauHash = EXCLUDED.MatKhauHash, MaNV = EXCLUDED.MaNV;
                """, (emp["username"], PASSWORD_HASH, emp["manv"]))

                json_data = json.dumps({
                    "skills": emp["skills"],
                    "performance_reviews": [{"period": "2026-Q1", "final_grade": "A", "feedback": "Hoàn thành xuất sắc nhiệm vụ"}],
                    "avatar_key": f"avatars/{emp['manv']}.jpg",
                    "cv_pdf_key": f"cv_docs/{emp['manv']}_CV.pdf"
                })
                cur.execute("""
                    INSERT INTO HoSoMoRong (MaNV, DuLieuJSON)
                    VALUES (%s, %s::jsonb)
                    ON CONFLICT (MaNV) DO UPDATE SET DuLieuJSON = EXCLUDED.DuLieuJSON;
                """, (emp["manv"], json_data))

                ma_luong = f"L_HN_{emp['manv'][-2:]}_0326"
                cur.execute("""
                    INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
                    VALUES (%s, %s, 3, 2026, %s, %s, %s, 0)
                    ON CONFLICT (MaLuong) DO UPDATE SET LuongCoBan = EXCLUDED.LuongCoBan, PhuCap = EXCLUDED.PhuCap, Thuong = EXCLUDED.Thuong;
                """, (ma_luong, emp["manv"], emp["luong_cb"], emp["phu_cap"], emp["thuong"]))

            conn.commit()
            print("=> Đã nạp thành công 4 tài khoản tại site_hn (Hà Nội)")

    # 2. SITE ĐÀ NẴNG
    with get_db_connection(SITE_DN) as conn:
        with conn.cursor() as cur:
            # Thêm phòng Ban Giám Đốc Đà Nẵng
            cur.execute("""
                INSERT INTO PhongBan (MaPB, TenPB, MaCN)
                VALUES ('PB_DN_BGD', 'Ban Giám Đốc Đà Nẵng', 'DN')
                ON CONFLICT (MaPB) DO NOTHING;
            """)

            dn_employees = [
                {
                    "manv": "NV_DN_DIR_02",
                    "hoten": "Nguyễn Anh Tuấn",
                    "phai": "Nam",
                    "ngaysinh": "1982-04-18",
                    "sdt": "0905111222",
                    "email": "tuanna@x.corp",
                    "mst": "MST_DN_DIR_02",
                    "mapb": "PB_DN_BGD",
                    "macv": "GD",
                    "mavaitro": 3,
                    "macn": "DN",
                    "username": "tuan_gddn",
                    "role_desc": "Giám đốc Chi nhánh Đà Nẵng",
                    "luong_cb": 42000000,
                    "phu_cap": 5000000,
                    "thuong": 8000000,
                    "skills": [{"name": "Regional Leadership", "level": "Expert"}, {"name": "Engineering Operations", "level": "Expert"}]
                },
                {
                    "manv": "NV_DN_02",
                    "hoten": "Vũ Đình Khang",
                    "phai": "Nam",
                    "ngaysinh": "1991-09-09",
                    "sdt": "0905333444",
                    "email": "khangvd@x.corp",
                    "mst": "MST_DN_02",
                    "mapb": "PB_DN_01",
                    "macv": "TP",
                    "mavaitro": 2,
                    "macn": "DN",
                    "username": "khang_tpkt",
                    "role_desc": "Trưởng phòng Kỹ thuật Đà Nẵng",
                    "luong_cb": 28000000,
                    "phu_cap": 2500000,
                    "thuong": 4000000,
                    "skills": [{"name": "System Architecture", "level": "Expert"}, {"name": "PostgreSQL", "level": "Advanced"}]
                }
            ]

            for emp in dn_employees:
                cur.execute("""
                    INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'DangLamViec')
                    ON CONFLICT (MaNV) DO UPDATE SET HoTen = EXCLUDED.HoTen, MaPB = EXCLUDED.MaPB, MaCV = EXCLUDED.MaCV, MaVaiTro = EXCLUDED.MaVaiTro;
                """, (emp["manv"], emp["hoten"], emp["phai"], emp["ngaysinh"], emp["sdt"], emp["email"], emp["mst"], emp["mapb"], emp["macv"], emp["mavaitro"], emp["macn"]))

                cur.execute("""
                    INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (TenDangNhap) DO UPDATE SET MatKhauHash = EXCLUDED.MatKhauHash, MaNV = EXCLUDED.MaNV;
                """, (emp["username"], PASSWORD_HASH, emp["manv"]))

                json_data = json.dumps({
                    "skills": emp["skills"],
                    "performance_reviews": [{"period": "2026-Q1", "final_grade": "A", "feedback": "Quản lý kỹ thuật hiệu quả"}],
                    "avatar_key": f"avatars/{emp['manv']}.jpg",
                    "cv_pdf_key": f"cv_docs/{emp['manv']}_CV.pdf"
                })
                cur.execute("""
                    INSERT INTO HoSoMoRong (MaNV, DuLieuJSON)
                    VALUES (%s, %s::jsonb)
                    ON CONFLICT (MaNV) DO UPDATE SET DuLieuJSON = EXCLUDED.DuLieuJSON;
                """, (emp["manv"], json_data))

                ma_luong = f"L_DN_{emp['manv'][-2:]}_0326"
                cur.execute("""
                    INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
                    VALUES (%s, %s, 3, 2026, %s, %s, %s, 0)
                    ON CONFLICT (MaLuong) DO UPDATE SET LuongCoBan = EXCLUDED.LuongCoBan, PhuCap = EXCLUDED.PhuCap, Thuong = EXCLUDED.Thuong;
                """, (ma_luong, emp["manv"], emp["luong_cb"], emp["phu_cap"], emp["thuong"]))

            conn.commit()
            print("=> Đã nạp thành công 2 tài khoản tại site_dn (Đà Nẵng)")

    # 3. SITE TP.HCM
    with get_db_connection(SITE_HCM) as conn:
        with conn.cursor() as cur:
            # Đồng bộ danh mục ChucVu nếu thiếu GD
            cur.execute("""
                INSERT INTO ChucVu (MaCV, TenCV, HeSoLuong)
                VALUES ('GD', 'Giám đốc chi nhánh', 3.00)
                ON CONFLICT (MaCV) DO NOTHING;
            """)

            # Thêm phòng Ban Giám Đốc TP.HCM
            cur.execute("""
                INSERT INTO PhongBan (MaPB, TenPB, MaCN)
                VALUES ('PB_HCM_BGD', 'Ban Giám Đốc TP.HCM', 'HCM')
                ON CONFLICT (MaPB) DO NOTHING;
            """)

            hcm_employees = [
                {
                    "manv": "NV_HCM_DIR_01",
                    "hoten": "Huỳnh Quốc Bảo",
                    "phai": "Nam",
                    "ngaysinh": "1984-12-05",
                    "sdt": "0908777888",
                    "email": "baohq@x.corp",
                    "mst": "MST_HCM_DIR_01",
                    "mapb": "PB_HCM_BGD",
                    "macv": "GD",
                    "mavaitro": 3,
                    "macn": "HCM",
                    "username": "bao_gdhcm",
                    "role_desc": "Giám đốc Chi nhánh TP.HCM",
                    "luong_cb": 45000000,
                    "phu_cap": 5500000,
                    "thuong": 9000000,
                    "skills": [{"name": "Market Expansion", "level": "Expert"}, {"name": "Strategic Sales", "level": "Expert"}]
                },
                {
                    "manv": "NV_HCM_02",
                    "hoten": "Đỗ Thanh Thảo",
                    "phai": "Nữ",
                    "ngaysinh": "1997-07-22",
                    "sdt": "0908999000",
                    "email": "thaodt@x.corp",
                    "mst": "MST_HCM_02",
                    "mapb": "PB_HCM_01",
                    "macv": "NV",
                    "mavaitro": 1,
                    "macn": "HCM",
                    "username": "thao_nvkd",
                    "role_desc": "Nhân viên Kinh doanh TP.HCM",
                    "luong_cb": 16000000,
                    "phu_cap": 1200000,
                    "thuong": 3500000,
                    "skills": [{"name": "Customer Negotiation", "level": "Advanced"}, {"name": "CRM", "level": "Intermediate"}]
                }
            ]

            for emp in hcm_employees:
                cur.execute("""
                    INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'DangLamViec')
                    ON CONFLICT (MaNV) DO UPDATE SET HoTen = EXCLUDED.HoTen, MaPB = EXCLUDED.MaPB, MaCV = EXCLUDED.MaCV, MaVaiTro = EXCLUDED.MaVaiTro;
                """, (emp["manv"], emp["hoten"], emp["phai"], emp["ngaysinh"], emp["sdt"], emp["email"], emp["mst"], emp["mapb"], emp["macv"], emp["mavaitro"], emp["macn"]))

                cur.execute("""
                    INSERT INTO NguoiDungDangNhap (TenDangNhap, MatKhauHash, MaNV)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (TenDangNhap) DO UPDATE SET MatKhauHash = EXCLUDED.MatKhauHash, MaNV = EXCLUDED.MaNV;
                """, (emp["username"], PASSWORD_HASH, emp["manv"]))

                json_data = json.dumps({
                    "skills": emp["skills"],
                    "performance_reviews": [{"period": "2026-Q1", "final_grade": "A", "feedback": "Đạt KPI vượt chỉ tiêu kinh doanh"}],
                    "avatar_key": f"avatars/{emp['manv']}.jpg",
                    "cv_pdf_key": f"cv_docs/{emp['manv']}_CV.pdf"
                })
                cur.execute("""
                    INSERT INTO HoSoMoRong (MaNV, DuLieuJSON)
                    VALUES (%s, %s::jsonb)
                    ON CONFLICT (MaNV) DO UPDATE SET DuLieuJSON = EXCLUDED.DuLieuJSON;
                """, (emp["manv"], json_data))

                ma_luong = f"L_HCM_{emp['manv'][-2:]}_0326"
                cur.execute("""
                    INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
                    VALUES (%s, %s, 3, 2026, %s, %s, %s, 0)
                    ON CONFLICT (MaLuong) DO UPDATE SET LuongCoBan = EXCLUDED.LuongCoBan, PhuCap = EXCLUDED.PhuCap, Thuong = EXCLUDED.Thuong;
                """, (ma_luong, emp["manv"], emp["luong_cb"], emp["phu_cap"], emp["thuong"]))

            conn.commit()
            print("=> Đã nạp thành công 2 tài khoản tại site_hcm (TP.HCM)")

    print("=== HOÀN TẤT NẠP TẤT CẢ TÀI KHOẢN VÀO CỤM CSDL PHÂN TÁN ===")

if __name__ == "__main__":
    seed_accounts()

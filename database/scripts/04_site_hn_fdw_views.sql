-- 04_site_hn_fdw_views.sql
-- Cấu hình postgres_fdw, Global Views & v_HoSoNhanSu_ToanDien
-- -------------------------------------------------------------
-- 5. CẤU HÌNH LIÊN KẾT PHÂN TÁN (POSTGRES_FDW) TRỎ SANG ĐÀ NẴNG & TP.HCM
-- -------------------------------------------------------------

-- KẾT NỐI SITE ĐÀ NẴNG
CREATE SERVER srv_dn FOREIGN DATA WRAPPER postgres_fdw 
OPTIONS (host 'site_dn', dbname 'qlns_dn', port '5432');

CREATE USER MAPPING FOR postgres SERVER srv_dn 
OPTIONS (user 'dn_reader', password 'ReaderDN_123');

CREATE SCHEMA remote_dn;
IMPORT FOREIGN SCHEMA public 
LIMIT TO (PhongBan, NhanVien, Luong, ChamCong, NhanVien_DuAn, HoSoMoRong) 
FROM SERVER srv_dn INTO remote_dn;

-- KẾT NỐI SITE TP.HCM
CREATE SERVER srv_hcm FOREIGN DATA WRAPPER postgres_fdw 
OPTIONS (host 'site_hcm', dbname 'qlns_hcm', port '5432');

CREATE USER MAPPING FOR postgres SERVER srv_hcm 
OPTIONS (user 'hcm_reader', password 'ReaderHCM_123');

CREATE SCHEMA remote_hcm;
IMPORT FOREIGN SCHEMA public 
LIMIT TO (PhongBan, NhanVien, Luong, ChamCong, NhanVien_DuAn, HoSoMoRong) 
FROM SERVER srv_hcm INTO remote_hcm;

-- -------------------------------------------------------------
-- 6. TẠO CÁC VIEW TOÀN CỤC HỢP NHẤT (ĐẠT TÍNH TRONG SUỐT PHÂN MẢNH MỨC 1)
-- -------------------------------------------------------------

-- View Phòng ban toàn tập đoàn
CREATE OR REPLACE VIEW v_PhongBan AS
SELECT MaPB, TenPB, MaCN FROM public.PhongBan
UNION ALL
SELECT MaPB, TenPB, MaCN FROM remote_dn.PhongBan
UNION ALL
SELECT MaPB, TenPB, MaCN FROM remote_hcm.PhongBan;

-- View Nhân viên toàn tập đoàn
CREATE OR REPLACE VIEW v_NhanVien AS
SELECT MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai FROM public.NhanVien
UNION ALL
SELECT MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai FROM remote_dn.NhanVien
UNION ALL
SELECT MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai FROM remote_hcm.NhanVien;

-- View Bảng lương toàn tập đoàn
CREATE OR REPLACE VIEW v_Luong AS
SELECT MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru, LuongThucLinh FROM public.Luong
UNION ALL
SELECT MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru, LuongThucLinh FROM remote_dn.Luong
UNION ALL
SELECT MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru, LuongThucLinh FROM remote_hcm.Luong;

-- View Hồ sơ JSON toàn tập đoàn
CREATE OR REPLACE VIEW v_HoSoMoRong AS
SELECT MaNV, DuLieuJSON, NgayCapNhat FROM public.HoSoMoRong
UNION ALL
SELECT MaNV, DuLieuJSON, NgayCapNhat FROM remote_dn.HoSoMoRong
UNION ALL
SELECT MaNV, DuLieuJSON, NgayCapNhat FROM remote_hcm.HoSoMoRong;

-- -------------------------------------------------------------
-- 7. VIEW HỢP NHẤT TOÀN DIỆN ĐA MÔ HÌNH (QUAN HỆ + JSONB + MINIO OBJECT)
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW v_HoSoNhanSu_ToanDien AS
SELECT 
    nv.MaNV,
    nv.HoTen,
    nv.Phai,
    nv.Email,
    pb.TenPB AS TenPhongBan,
    cv.TenCV AS ChucVuHienTai,
    vt.TenVaiTro,
    nv.MaCN AS ChiNhanh,
    nv.TrangThai,
    -- Dữ liệu Lương (Quan hệ)
    l.Thang,
    l.Nam,
    l.LuongThucLinh,
    -- Trích xuất dữ liệu Bán cấu trúc JSON phẳng ra bảng
    hs.DuLieuJSON -> 'performance_reviews' -> 0 ->> 'final_grade' AS XepLoai_KPI_Q1,
    hs.DuLieuJSON -> 'performance_reviews' -> 0 ->> 'feedback' AS DanhGia_NhanXet,
    hs.DuLieuJSON -> 'skills' AS DanhSachKyNang,
    -- Tích hợp liên kết đối tượng Phi cấu trúc MinIO
    CONCAT('http://localhost:9000/nhansu-bucket/', hs.DuLieuJSON ->> 'avatar_key') AS URL_AnhDaiDien,
    CONCAT('http://localhost:9000/nhansu-bucket/', hs.DuLieuJSON ->> 'cv_pdf_key') AS URL_BanScan_CV
FROM v_NhanVien nv
JOIN v_PhongBan pb ON nv.MaPB = pb.MaPB
JOIN ChucVu cv ON nv.MaCV = cv.MaCV
JOIN VaiTro vt ON nv.MaVaiTro = vt.MaVaiTro
LEFT JOIN v_Luong l ON nv.MaNV = l.MaNV AND l.Thang = 3 AND l.Nam = 2026
LEFT JOIN v_HoSoMoRong hs ON nv.MaNV = hs.MaNV;
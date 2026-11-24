-- ==============================================================================
-- 07_update_fdw_global_views.sql
-- Cập nhật cấu hình FDW và Global Views trên Coordinator site_hn (5431)
-- ==============================================================================

-- 1. IMPORT CÁC BẢNG MỚI TỪ REMOTE SHARDS SANG COORDINATOR
DROP SCHEMA IF EXISTS remote_dn CASCADE;
CREATE SCHEMA remote_dn;
IMPORT FOREIGN SCHEMA public 
LIMIT TO (PhongBan, NhanVien, Luong, ChamCong, NhanVien_DuAn, HoSoMoRong, VaiTroHeThong, NhanVien_VaiTro, YeuCauQuanTri, DieuChuyenBoNhiem) 
FROM SERVER srv_dn INTO remote_dn;

DROP SCHEMA IF EXISTS remote_hcm CASCADE;
CREATE SCHEMA remote_hcm;
IMPORT FOREIGN SCHEMA public 
LIMIT TO (PhongBan, NhanVien, Luong, ChamCong, NhanVien_DuAn, HoSoMoRong, VaiTroHeThong, NhanVien_VaiTro, YeuCauQuanTri, DieuChuyenBoNhiem) 
FROM SERVER srv_hcm INTO remote_hcm;

-- 2. CẬP NHẬT VIEW v_PhongBan HỢP NHẤT TOÀN TẬP ĐOÀN CÓ PHÂN CẤP
CREATE OR REPLACE VIEW v_PhongBan AS
SELECT MaPB, TenPB, MaCN, LoaiDonVi, MaDonViCha, ThuTuSapXep FROM public.PhongBan
UNION ALL
SELECT MaPB, TenPB, MaCN, LoaiDonVi, MaDonViCha, ThuTuSapXep FROM remote_dn.PhongBan
UNION ALL
SELECT MaPB, TenPB, MaCN, LoaiDonVi, MaDonViCha, ThuTuSapXep FROM remote_hcm.PhongBan;

-- 3. CẬP NHẬT VIEW v_NhanVien HỢP NHẤT TOÀN TẬP ĐOÀN
CREATE OR REPLACE VIEW v_NhanVien AS
SELECT MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai FROM public.NhanVien
UNION ALL
SELECT MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai FROM remote_dn.NhanVien
UNION ALL
SELECT MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN, TrangThai FROM remote_hcm.NhanVien;

-- 4. VIEW v_Luong TOÀN TẬP ĐOÀN
CREATE OR REPLACE VIEW v_Luong AS
SELECT MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru, LuongThucLinh FROM public.Luong
UNION ALL
SELECT MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru, LuongThucLinh FROM remote_dn.Luong
UNION ALL
SELECT MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru, LuongThucLinh FROM remote_hcm.Luong;

-- 5. VIEW v_HoSoMoRong TOÀN TẬP ĐOÀN
CREATE OR REPLACE VIEW v_HoSoMoRong AS
SELECT MaNV, DuLieuJSON, NgayCapNhat FROM public.HoSoMoRong
UNION ALL
SELECT MaNV, DuLieuJSON, NgayCapNhat FROM remote_dn.HoSoMoRong
UNION ALL
SELECT MaNV, DuLieuJSON, NgayCapNhat FROM remote_hcm.HoSoMoRong;

-- 6. VIEW v_HoSoNhanSu_ToanDien HỢP NHẤT ĐA MÔ HÌNH
CREATE OR REPLACE VIEW v_HoSoNhanSu_ToanDien AS
SELECT 
    nv.MaNV, nv.HoTen, nv.Phai, nv.NgaySinh, nv.SoDienThoai, nv.Email, nv.MaSoThue,
    pb.TenPB AS TenPhongBan, cv.TenCV AS ChucVuHienTai, vt.TenVaiTro,
    nv.MaCN AS ChiNhanh, nv.TrangThai, nv.MaPB, nv.MaCV, nv.MaVaiTro,
    l.Thang, l.Nam, l.LuongCoBan, l.PhuCap, l.Thuong, l.KhauTru, l.LuongThucLinh,
    hs.DuLieuJSON -> 'performance_reviews' -> 0 ->> 'final_grade' AS XepLoai_KPI_Q1,
    hs.DuLieuJSON -> 'performance_reviews' -> 0 ->> 'feedback' AS DanhGia_NhanXet,
    hs.DuLieuJSON -> 'skills' AS DanhSachKyNang,
    CONCAT('http://localhost:9000/nhansu-bucket/', hs.DuLieuJSON ->> 'avatar_key') AS URL_AnhDaiDien,
    CONCAT('http://localhost:9000/nhansu-bucket/', hs.DuLieuJSON ->> 'cv_pdf_key') AS URL_BanScan_CV
FROM v_NhanVien nv
JOIN v_PhongBan pb ON nv.MaPB = pb.MaPB
JOIN ChucVu cv ON nv.MaCV = cv.MaCV
JOIN VaiTro vt ON nv.MaVaiTro = vt.MaVaiTro
LEFT JOIN v_Luong l ON nv.MaNV = l.MaNV AND l.Thang = 3 AND l.Nam = 2026
LEFT JOIN v_HoSoMoRong hs ON nv.MaNV = hs.MaNV;

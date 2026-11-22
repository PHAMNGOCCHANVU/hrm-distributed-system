-- 03_site_hn_init.sql
-- Tạo bảng cục bộ HN, Index, data mẫu
-- 1. BẬT TIỆN ÍCH FDW VÀ HÀM BĂM MẬT KHẨU
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 2. TẠO CẤU TRÚC DỮ LIỆU CỤC BỘ TẠI HÀ NỘI (MaCN = 'HN')
CREATE TABLE VaiTro (MaVaiTro INT PRIMARY KEY, TenVaiTro VARCHAR(50) NOT NULL);
CREATE TABLE ChucVu (MaCV VARCHAR(10) PRIMARY KEY, TenCV VARCHAR(50) NOT NULL, HeSoLuong NUMERIC(4,2) NOT NULL);
CREATE TABLE DuAn (MaDuAn INT PRIMARY KEY, TenDuAn VARCHAR(100) NOT NULL, NgayBatDau DATE, NgayKetThuc DATE);

CREATE TABLE PhongBan (
    MaPB VARCHAR(10) PRIMARY KEY,
    TenPB VARCHAR(100) NOT NULL,
    MaCN VARCHAR(10) NOT NULL,
    CONSTRAINT chk_pb_hn CHECK (MaCN = 'HN')
);

CREATE TABLE NhanVien (
    MaNV VARCHAR(20) PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    Phai VARCHAR(10),
    NgaySinh DATE,
    SoDienThoai VARCHAR(15),
    Email VARCHAR(100) UNIQUE NOT NULL,
    MaSoThue VARCHAR(20),
    MaPB VARCHAR(10) REFERENCES PhongBan(MaPB),
    MaCV VARCHAR(10) REFERENCES ChucVu(MaCV),
    MaVaiTro INT REFERENCES VaiTro(MaVaiTro),
    MaCN VARCHAR(10) NOT NULL,
    TrangThai VARCHAR(20) DEFAULT 'DangLamViec',
    CONSTRAINT chk_nv_hn CHECK (MaCN = 'HN')
);

CREATE TABLE Luong (
    MaLuong VARCHAR(30) PRIMARY KEY,
    MaNV VARCHAR(20) REFERENCES NhanVien(MaNV),
    Thang INT NOT NULL,
    Nam INT NOT NULL,
    LuongCoBan NUMERIC(15,2) NOT NULL,
    PhuCap NUMERIC(15,2) DEFAULT 0,
    Thuong NUMERIC(15,2) DEFAULT 0,
    KhauTru NUMERIC(15,2) DEFAULT 0,
    LuongThucLinh NUMERIC(15,2) GENERATED ALWAYS AS (LuongCoBan + PhuCap + Thuong - KhauTru) STORED
);

CREATE TABLE ChamCong (
    MaChamCong VARCHAR(30) PRIMARY KEY,
    MaNV VARCHAR(20) REFERENCES NhanVien(MaNV),
    NgayLam DATE NOT NULL,
    GioVao TIME,
    GioRa TIME,
    GhiChu VARCHAR(255)
);

CREATE TABLE NhanVien_DuAn (
    MaNV VARCHAR(20) REFERENCES NhanVien(MaNV),
    MaDuAn INT REFERENCES DuAn(MaDuAn),
    NgayThamGia DATE DEFAULT CURRENT_DATE,
    PRIMARY KEY (MaNV, MaDuAn)
);

CREATE TABLE NguoiDungDangNhap (
    TenDangNhap VARCHAR(50) PRIMARY KEY,
    MatKhauHash VARCHAR(64) NOT NULL,
    MaNV VARCHAR(20) REFERENCES NhanVien(MaNV)
);

CREATE TABLE HoSoMoRong (
    MaNV VARCHAR(20) PRIMARY KEY REFERENCES NhanVien(MaNV),
    DuLieuJSON JSONB NOT NULL,
    NgayCapNhat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. CHỈ MỤC CỤC BỘ TẠI HÀ NỘI
CREATE INDEX idx_hn_nv_pb ON NhanVien(MaPB);
CREATE INDEX idx_hn_luong_thang ON Luong(Nam, Thang);
CREATE INDEX idx_hn_json_gin ON HoSoMoRong USING GIN (DuLieuJSON);

-- 4. NẠP DỮ LIỆU CỤC BỘ TẠI HÀ NỘI
INSERT INTO VaiTro VALUES (1, 'Nhân viên'), (2, 'Trưởng phòng'), (3, 'Giám đốc');
INSERT INTO ChucVu VALUES ('NV', 'Nhân viên chuyên trách', 1.0), ('TP', 'Trưởng phòng khu vực', 1.5), ('GD', 'Giám đốc điều hành', 3.0);
INSERT INTO DuAn VALUES (100, 'Chuyển đổi số CSDL Phân tán', '2026-01-01', '2026-12-31');

INSERT INTO PhongBan VALUES ('PB_HN_01', 'Phòng Quản Trị Trung Tâm', 'HN');

INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN)
VALUES 
('NV_HN_01', 'Lưu Quang Giáp', 'Nam', '1980-01-15', '0912000111', 'giaplq@x.corp', 'MST_HN_01', 'PB_HN_01', 'GD', 3, 'HN'),
('NV_HN_02', 'Nguyễn Thị Hoa', 'Nữ', '1990-11-20', '0912000222', 'hoant@x.corp', 'MST_HN_02', 'PB_HN_01', 'NV', 1, 'HN');

INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
VALUES 
('L_HN_01_0326', 'NV_HN_01', 3, 2026, 45000000, 5000000, 5000000, 0),
('L_HN_02_0326', 'NV_HN_02', 3, 2026, 16000000, 1000000, 500000, 200000);

INSERT INTO ChamCong VALUES 
('CC_HN_01_01', 'NV_HN_01', '2026-03-25', '07:55', '17:00', 'Đúng giờ'),
('CC_HN_02_01', 'NV_HN_02', '2026-03-25', '08:02', '17:01', 'Đúng giờ');

INSERT INTO NhanVien_DuAn VALUES ('NV_HN_01', 100, '2026-01-01');
INSERT INTO NguoiDungDangNhap VALUES 
('giap_gd', encode(digest('123456', 'sha256'), 'hex'), 'NV_HN_01'),
('hoa_nv', encode(digest('123456', 'sha256'), 'hex'), 'NV_HN_02');

INSERT INTO HoSoMoRong (MaNV, DuLieuJSON) VALUES 
('NV_HN_01', '{
  "skills": [{"name": "Leadership", "level": "Expert"}, {"name": "Strategic Planning", "level": "Expert"}],
  "performance_reviews": [{"period": "2026-Q1", "final_grade": "A", "feedback": "Lãnh đạo xuất sắc"}],
  "avatar_key": "avatars/NV_HN_01.jpg",
  "cv_pdf_key": "cv_docs/NV_HN_01_CV.pdf"
}'),
('NV_HN_02', '{
  "skills": [{"name": "HR Management", "level": "Intermediate"}, {"name": "Communication", "level": "Advanced"}],
  "performance_reviews": [{"period": "2026-Q1", "final_grade": "B", "feedback": "Hoàn thành tốt nhiệm vụ"}],
  "avatar_key": "avatars/NV_HN_02.jpg",
  "cv_pdf_key": "cv_docs/NV_HN_02_CV.pdf"
}');

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
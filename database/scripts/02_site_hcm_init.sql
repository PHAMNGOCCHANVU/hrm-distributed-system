-- 02_site_hcm_init.sql
-- Tạo bảng, CHECK (MaCN='HCM'), Index, user hcm_reader, data 

CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- 1. DANH MỤC NHÂN BẢN
CREATE TABLE VaiTro (MaVaiTro INT PRIMARY KEY, TenVaiTro VARCHAR(50) NOT NULL);
CREATE TABLE ChucVu (MaCV VARCHAR(10) PRIMARY KEY, TenCV VARCHAR(50) NOT NULL, HeSoLuong NUMERIC(4,2) NOT NULL);
CREATE TABLE DuAn (MaDuAn INT PRIMARY KEY, TenDuAn VARCHAR(100) NOT NULL, NgayBatDau DATE, NgayKetThuc DATE);

-- 2. PHÂN MẢNH TP.HCM (MaCN = 'HCM')
CREATE TABLE PhongBan (
    MaPB VARCHAR(10) PRIMARY KEY,
    TenPB VARCHAR(100) NOT NULL,
    MaCN VARCHAR(10) NOT NULL,
    CONSTRAINT chk_pb_hcm CHECK (MaCN = 'HCM')
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
    CONSTRAINT chk_nv_hcm CHECK (MaCN = 'HCM')
);

-- 3. MẢNH DẪN XUẤT TẠI TP.HCM
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

-- 4. CHỈ MỤC & BẢO MẬT
CREATE INDEX idx_hcm_nv_pb ON NhanVien(MaPB);
CREATE INDEX idx_hcm_luong_thang ON Luong(Nam, Thang);
CREATE INDEX idx_hcm_json_gin ON HoSoMoRong USING GIN (DuLieuJSON);

CREATE USER hcm_reader WITH PASSWORD 'ReaderHCM_123';
GRANT CONNECT ON DATABASE qlns_hcm TO hcm_reader;
GRANT USAGE ON SCHEMA public TO hcm_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO hcm_reader;

-- 5. NẠP DỮ LIỆU MẪU TP.HCM
INSERT INTO VaiTro VALUES (1, 'Nhân viên'), (2, 'Trưởng phòng'), (3, 'Giám đốc');
INSERT INTO ChucVu VALUES ('NV', 'Nhân viên chuyên trách', 1.0), ('TP', 'Trưởng phòng khu vực', 1.5);
INSERT INTO DuAn VALUES (102, 'Phát triển App Mobile Nhân sự', '2026-02-01', '2026-09-01');

INSERT INTO PhongBan VALUES ('PB_HCM_01', 'Phòng Kinh Doanh TP.HCM', 'HCM');

INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN)
VALUES ('NV_HCM_01', 'Trần Thị Mỹ Linh', 'Nữ', '1995-08-20', '0908888999', 'linhttm@x.corp', 'MST_HCM_01', 'PB_HCM_01', 'TP', 2, 'HCM');

INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
VALUES ('L_HCM_01_0326', 'NV_HCM_01', 3, 2026, 25000000, 3000000, 2000000, 1000000);

INSERT INTO ChamCong VALUES ('CC_HCM_01_01', 'NV_HCM_01', '2026-03-25', '08:15', '17:30', 'Đúng giờ');
INSERT INTO NhanVien_DuAn VALUES ('NV_HCM_01', 102, '2026-02-15');
INSERT INTO NguoiDungDangNhap VALUES ('linh_hcm', encode(digest('123456', 'sha256'), 'hex'), 'NV_HCM_01');

INSERT INTO HoSoMoRong (MaNV, DuLieuJSON) VALUES ('NV_HCM_01', '{
  "skills": [{"name": "B2B Sales", "level": "Expert"}, {"name": "English", "level": "Professional"}],
  "performance_reviews": [{"period": "2026-Q1", "final_grade": "A", "feedback": "Đạt 130% chỉ tiêu kinh doanh"}],
  "avatar_key": "avatars/NV_HCM_01.jpg",
  "cv_pdf_key": "cv_docs/NV_HCM_01_CV.pdf"
}');

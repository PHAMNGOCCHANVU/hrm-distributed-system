-- 01_site_dn_init.sql
-- Tạo bảng, CHECK (MaCN='DN'), Index, user dn_reader, data mẫu
-- 1. BẢNG DANH MỤC NHÂN BẢN TOÀN CỤC (Full Replication)

CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE VaiTro (
    MaVaiTro INT PRIMARY KEY,
    TenVaiTro VARCHAR(50) NOT NULL
);

CREATE TABLE ChucVu (
    MaCV VARCHAR(10) PRIMARY KEY,
    TenCV VARCHAR(50) NOT NULL,
    HeSoLuong NUMERIC(4,2) NOT NULL
);

CREATE TABLE DuAn (
    MaDuAn INT PRIMARY KEY,
    TenDuAn VARCHAR(100) NOT NULL,
    NgayBatDau DATE,
    NgayKetThuc DATE
);

-- 2. PHÂN MẢNH NGANG CHÍNH: PHÒNG BAN & NHÂN VIÊN ĐÀ NẴNG (MaCN = 'DN')
CREATE TABLE PhongBan (
    MaPB VARCHAR(10) PRIMARY KEY,
    TenPB VARCHAR(100) NOT NULL,
    MaCN VARCHAR(10) NOT NULL,
    CONSTRAINT chk_pb_dn CHECK (MaCN = 'DN')
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
    CONSTRAINT chk_nv_dn CHECK (MaCN = 'DN')
);

-- 3. PHÂN MẢNH NGANG DẪN XUẤT: LƯƠNG, CHẤM CÔNG, TÀI KHOẢN, DỰ ÁN
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
    MatKhauHash VARCHAR(64) NOT NULL, -- SHA-256 Hash
    MaNV VARCHAR(20) REFERENCES NhanVien(MaNV)
);

-- 4. BẢNG BÁN CẤU TRÚC JSONB & LIÊN KẾT PHI CẤU TRÚC (MINIO URI)
CREATE TABLE HoSoMoRong (
    MaNV VARCHAR(20) PRIMARY KEY REFERENCES NhanVien(MaNV),
    DuLieuJSON JSONB NOT NULL,
    NgayCapNhat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. THIẾT LẬP CHỈ MỤC (INDEXING) CỤC BỘ
CREATE INDEX idx_dn_nv_pb ON NhanVien(MaPB);
CREATE INDEX idx_dn_luong_thang ON Luong(Nam, Thang);
CREATE INDEX idx_dn_json_gin ON HoSoMoRong USING GIN (DuLieuJSON);

-- 6. PHÂN QUYỀN TRUY CẬP TỪ XA CHO SITE HÀ NỘI (Chỉ đọc)
CREATE USER dn_reader WITH PASSWORD 'ReaderDN_123';
GRANT CONNECT ON DATABASE qlns_dn TO dn_reader;
GRANT USAGE ON SCHEMA public TO dn_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dn_reader;

-- 7. NẠP DỮ LIỆU MẪU ĐÀ NẴNG
INSERT INTO VaiTro VALUES (1, 'Nhân viên'), (2, 'Trưởng phòng'), (3, 'Giám đốc');
INSERT INTO ChucVu VALUES ('NV', 'Nhân viên chuyên trách', 1.0), ('TP', 'Trưởng phòng khu vực', 1.5);
INSERT INTO DuAn VALUES (101, 'Mở rộng chi nhánh miền Trung', '2026-01-01', '2026-12-31');

INSERT INTO PhongBan VALUES ('PB_DN_01', 'Phòng Kỹ Thuật Đà Nẵng', 'DN');

INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN)
VALUES ('NV_DN_01', 'Phạm Văn Cường', 'Nam', '1993-04-12', '0905123456', 'cuongpv@x.corp', 'MST_DN_01', 'PB_DN_01', 'NV', 1, 'DN');

INSERT INTO Luong (MaLuong, MaNV, Thang, Nam, LuongCoBan, PhuCap, Thuong, KhauTru)
VALUES ('L_DN_01_0326', 'NV_DN_01', 3, 2026, 18000000, 1500000, 1000000, 500000);

INSERT INTO ChamCong VALUES ('CC_DN_01_01', 'NV_DN_01', '2026-03-25', '08:00', '17:05', 'Đúng giờ');
INSERT INTO NhanVien_DuAn VALUES ('NV_DN_01', 101, '2026-01-10');
INSERT INTO NguoiDungDangNhap VALUES ('cuong_dn', encode(digest('123456', 'sha256'), 'hex'), 'NV_DN_01');

INSERT INTO HoSoMoRong (MaNV, DuLieuJSON) VALUES ('NV_DN_01', '{
  "skills": [{"name": "PostgreSQL", "level": "Advanced"}, {"name": "Docker", "level": "Intermediate"}],
  "performance_reviews": [{"period": "2026-Q1", "final_grade": "A", "feedback": "Vận hành hệ thống ổn định"}],
  "avatar_key": "avatars/NV_DN_01.jpg",
  "cv_pdf_key": "cv_docs/NV_DN_01_CV.pdf"
}');
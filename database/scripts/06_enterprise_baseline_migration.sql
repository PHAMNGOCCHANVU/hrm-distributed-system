-- ==============================================================================
-- 06_enterprise_baseline_migration.sql
-- Nâng cấp mô hình CSDL Tập đoàn: 2 Bộ máy tại HN, 4 Cấp Chức vụ & Quản trị Kỹ thuật
-- Áp dụng đồng bộ trên cả 3 sites: site_hn (5431), site_dn (5434), site_hcm (5433)
-- ==============================================================================

-- 1. BỔ SUNG PHÂN CẤP TỔ CHỨC VÀO PHÒNG BAN
DROP VIEW IF EXISTS v_HoSoNhanSu_ToanDien CASCADE;
DROP VIEW IF EXISTS v_PhongBan CASCADE;
DROP VIEW IF EXISTS v_NhanVien CASCADE;

ALTER TABLE PhongBan ALTER COLUMN MaPB TYPE VARCHAR(20);
ALTER TABLE NhanVien ALTER COLUMN MaPB TYPE VARCHAR(20);

ALTER TABLE PhongBan 
ADD COLUMN IF NOT EXISTS LoaiDonVi VARCHAR(20) DEFAULT 'CHI_NHANH',
ADD COLUMN IF NOT EXISTS MaDonViCha VARCHAR(20) NULL,
ADD COLUMN IF NOT EXISTS ThuTuSapXep INT DEFAULT 1;

CREATE INDEX IF NOT EXISTS idx_pb_loaidonvi ON PhongBan(LoaiDonVi, MaCN);

-- 2. BỔ SUNG CẤP BẬC VÀO DANH MỤC CHỨC VỤ
ALTER TABLE ChucVu 
ADD COLUMN IF NOT EXISTS CapBac INT DEFAULT 4;

-- Cập nhật cấp bậc cho các chức vụ hiện có và thêm chức vụ chuẩn
UPDATE ChucVu SET CapBac = 1 WHERE MaCV = 'CEO' OR MaCV = 'TGD';
UPDATE ChucVu SET CapBac = 2 WHERE MaCV = 'GD_CN' OR MaCV = 'GD';
UPDATE ChucVu SET CapBac = 3 WHERE MaCV = 'TP';
UPDATE ChucVu SET CapBac = 4 WHERE MaCV = 'NV';

INSERT INTO ChucVu (MaCV, TenCV, HeSoLuong, CapBac)
VALUES 
    ('CEO', 'Tổng Giám Đốc', 4.0, 1),
    ('GD_CN', 'Giám Đốc Chi Nhánh', 3.0, 2)
ON CONFLICT (MaCV) DO UPDATE 
SET CapBac = EXCLUDED.CapBac, HeSoLuong = EXCLUDED.HeSoLuong, TenCV = EXCLUDED.TenCV;

-- 3. TẠO BẢNG VAI TRÒ HỆ THỐNG CHUYÊN TRÁCH (SYSTEM ROLES)
CREATE TABLE IF NOT EXISTS VaiTroHeThong (
    MaVaiTro VARCHAR(30) PRIMARY KEY,
    TenVaiTro VARCHAR(100) NOT NULL,
    MoTa TEXT,
    PhamViMacDinh VARCHAR(20) NOT NULL -- 'GLOBAL', 'BRANCH', 'DEPARTMENT', 'PERSONAL'
);

INSERT INTO VaiTroHeThong (MaVaiTro, TenVaiTro, MoTa, PhamViMacDinh) VALUES
('GROUP_EXECUTIVE', 'Lãnh đạo cấp Tập đoàn', 'Toàn quyền điều hành và phê duyệt chiến lược toàn quốc', 'GLOBAL'),
('BRANCH_DIRECTOR', 'Lãnh đạo cấp Chi nhánh', 'Toàn quyền điều hành và phê duyệt nội bộ chi nhánh', 'BRANCH'),
('DEPT_MANAGER', 'Trưởng phòng Quản lý Chuyên môn', 'Quản lý nhân sự, đánh giá KPI và duyệt công trong phòng ban', 'DEPARTMENT'),
('HR_SPECIALIST', 'Chuyên viên Nghiệp vụ Nhân sự', 'Quản lý hồ sơ nhân viên, đề xuất bổ nhiệm, điều chuyển', 'GLOBAL'),
('FINANCE_SPECIALIST', 'Chuyên viên Nghiệp vụ Tài vụ', 'Quản trị bảng lương, đối soát tài chính quỹ lương', 'GLOBAL'),
('SYSTEM_OPERATOR', 'Quản trị Kỹ thuật Vận hành', 'Vận hành cụm node CSDL, gửi yêu cầu bảo trì kỹ thuật', 'GLOBAL'),
('EMPLOYEE', 'Nhân viên', 'Cổng thông tin nhân viên ESS (Hồ sơ, phiếu lương, danh bạ)', 'PERSONAL')
ON CONFLICT (MaVaiTro) DO UPDATE
SET TenVaiTro = EXCLUDED.TenVaiTro, MoTa = EXCLUDED.MoTa, PhamViMacDinh = EXCLUDED.PhamViMacDinh;

-- 4. BẢNG GÁN ĐA VAI TRÒ CHO NHÂN VIÊN
CREATE TABLE IF NOT EXISTS NhanVien_VaiTro (
    MaNV VARCHAR(20) REFERENCES NhanVien(MaNV),
    MaVaiTro VARCHAR(30) REFERENCES VaiTroHeThong(MaVaiTro),
    PhamViApDung VARCHAR(20) NOT NULL, -- 'GLOBAL', 'BRANCH', 'DEPARTMENT', 'PERSONAL'
    MaDonViApDung VARCHAR(20),
    NgayCap TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    NguoiCap VARCHAR(20),
    PRIMARY KEY (MaNV, MaVaiTro, PhamViApDung)
);

-- 5. BẢNG YÊU CẦU QUẢN TRỊ KỸ THUẬT (MAKER-CHECKER FOR SYSTEM OPERATORS)
CREATE TABLE IF NOT EXISTS YeuCauQuanTri (
    MaYeuCau VARCHAR(30) PRIMARY KEY,
    LoaiYeuCau VARCHAR(50) NOT NULL, -- 'CAP_QUYEN_OPERATOR', 'KHOI_PHUC_NODE', 'BAO_TRI_HE_THONG', 'XU_LY_SU_CO'
    MaNVYeuCau VARCHAR(20) REFERENCES NhanVien(MaNV),
    MaNVPheDuyet VARCHAR(20) REFERENCES NhanVien(MaNV),
    PhamViYeuCau VARCHAR(20) NOT NULL, -- 'GLOBAL' hoặc 'BRANCH'
    NoiDungYeuCau JSONB NOT NULL,
    TrangThai VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED', 'EXECUTED'
    LyDoTuChoi TEXT,
    NgayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    NgayPheDuyet TIMESTAMP
);

-- 6. BẢNG QUYẾT ĐỊNH BỔ NHIỆM & ĐIỀU CHUYỂN NHÂN SỰ
CREATE TABLE IF NOT EXISTS DieuChuyenBoNhiem (
    MaQuyetDinh VARCHAR(30) PRIMARY KEY,
    LoaiQuyetDinh VARCHAR(30) NOT NULL, -- 'BO_NHIEM', 'DIEU_CHUYEN_PHONG', 'DIEU_CHUYEN_CHI_NHANH'
    MaNV VARCHAR(20) REFERENCES NhanVien(MaNV),
    MaPBCu VARCHAR(10),
    MaPBMoi VARCHAR(10),
    MaCVCu VARCHAR(10),
    MaCVMoi VARCHAR(10),
    MaCNCu VARCHAR(10),
    MaCNMoi VARCHAR(10),
    NguoiDeXuat VARCHAR(20) REFERENCES NhanVien(MaNV),
    NguoiPheDuyet VARCHAR(20) REFERENCES NhanVien(MaNV),
    TrangThai VARCHAR(20) DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED'
    LyDo TEXT,
    NgayDeXuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    NgayHieuLuc DATE,
    NgayPheDuyet TIMESTAMP
);

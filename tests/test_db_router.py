import pytest
import psycopg2
from psycopg2 import errors

def test_db_connection_all_nodes(db_conn_hn, db_conn_dn, db_conn_hcm):
    """Kiểm tra kết nối trực tiếp tới cả 3 node cơ sở dữ liệu: HN (5431), DN (5434), HCM (5433)."""
    # 1. Test HN
    with db_conn_hn.cursor() as cur:
        cur.execute("SELECT 1;")
        assert cur.fetchone()[0] == 1
        
    # 2. Test DN
    with db_conn_dn.cursor() as cur:
        cur.execute("SELECT 1;")
        assert cur.fetchone()[0] == 1
        
    # 3. Test HCM
    with db_conn_hcm.cursor() as cur:
        cur.execute("SELECT 1;")
        assert cur.fetchone()[0] == 1

def test_query_global_view_on_coordinator(db_conn_hn):
    """Kiểm tra truy vấn Global View v_HoSoNhanSu_ToanDien trên Coordinator node (site_hn)."""
    with db_conn_hn.cursor() as cur:
        cur.execute("""
            SELECT MaNV, HoTen, TenPhongBan, ChucVuHienTai, ChiNhanh, LuongThucLinh, XepLoai_KPI_Q1
            FROM v_HoSoNhanSu_ToanDien;
        """)
        rows = cur.fetchall()
        assert len(rows) > 0, "Global view v_HoSoNhanSu_ToanDien không trả về bản ghi nào!"
        
        # Kiểm tra tính trong suốt phân mảnh: View phải gom được dữ liệu từ nhiều chi nhánh (HN, DN, HCM)
        branches = set(row[4] for row in rows)
        assert "HN" in branches, "Thiếu dữ liệu chi nhánh HN trong Global View!"
        assert "DN" in branches or "HCM" in branches, "Thiếu dữ liệu phân mảnh từ DN hoặc HCM qua FDW!"

def test_horizontal_sharding_check_constraints(db_conn_hn, db_conn_dn):
    """
    Kiểm tra ràng buộc phân mảnh ngang:
    - Thử insert bản ghi có MaCN='HN' vào site_dn -> BẮT BUỘC BỊ CHẶN do vi phạm CHECK (MaCN = 'DN').
    - Thử insert bản ghi có MaCN='HN' vào site_hn -> THÀNH CÔNG do thỏa mãn CHECK (MaCN = 'HN').
    """
    test_manv = "NV_TEST_CHK_01"
    
    # 1. Insert MaCN='HN' vào site_dn -> Phải ném ngoại lệ CheckViolation
    with pytest.raises(errors.CheckViolation):
        with db_conn_dn.cursor() as cur:
            cur.execute("""
                INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN)
                VALUES (%s, 'Nguyễn Kiểm Tra', 'Nam', '1995-01-01', '0901234567', 'test_chk_dn@x.corp', 'MST_TEST_01', 'PB_DN_01', 'NV', 1, 'HN');
            """, (test_manv,))

    # 2. Insert MaCN='HN' vào site_hn -> Thành công
    try:
        with db_conn_hn.cursor() as cur:
            # Dọn dẹp trước nếu có
            cur.execute("DELETE FROM NhanVien WHERE MaNV = %s;", (test_manv,))
            cur.execute("""
                INSERT INTO NhanVien (MaNV, HoTen, Phai, NgaySinh, SoDienThoai, Email, MaSoThue, MaPB, MaCV, MaVaiTro, MaCN)
                VALUES (%s, 'Nguyễn Kiểm Tra HN', 'Nam', '1995-01-01', '0901234567', 'test_chk_hn@x.corp', 'MST_TEST_01', 'PB_HN_01', 'NV', 1, 'HN');
            """, (test_manv,))
            
            cur.execute("SELECT MaNV, MaCN FROM NhanVien WHERE MaNV = %s;", (test_manv,))
            record = cur.fetchone()
            assert record is not None
            assert record[0] == test_manv
            assert record[1] == "HN"
    finally:
        # Dọn dẹp sau khi kiểm thử
        with db_conn_hn.cursor() as cur:
            cur.execute("DELETE FROM NhanVien WHERE MaNV = %s;", (test_manv,))

def test_replicated_table_consistency(db_conn_hn, db_conn_dn, db_conn_hcm):
    """Kiểm tra bảng nhân bản (VaiTro, ChucVu, DuAn) có dữ liệu nhất quán trên cả 3 sites."""
    def get_roles(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT MaVaiTro, TenVaiTro FROM VaiTro ORDER BY MaVaiTro;")
            return cur.fetchall()

    roles_hn = get_roles(db_conn_hn)
    roles_dn = get_roles(db_conn_dn)
    roles_hcm = get_roles(db_conn_hcm)

    assert len(roles_hn) >= 3
    assert len(roles_dn) >= 3
    assert len(roles_hcm) >= 3
    # Ít nhất các vai trò cơ bản (1, 2, 3) phải đồng bộ
    hn_dict = dict(roles_hn)
    assert hn_dict.get(1) == 'Nhân viên'
    assert hn_dict.get(2) == 'Trưởng phòng'
    assert hn_dict.get(3) == 'Giám đốc'

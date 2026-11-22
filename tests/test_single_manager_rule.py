import pytest
import json
from tests.test_rbac_masking import get_auth_token, ensure_test_users

def test_single_manager_rule_rejection(client, db_conn_hn, db_conn_dn, db_conn_hcm):
    """
    Quy tắc duy nhất 01 Trưởng phòng mỗi Phòng ban (Single Manager Rule):
    Phòng ban 'PB_HCM_01' đã có Trưởng phòng (NV_HCM_01, MaCV = 'TP', MaVaiTro = 2).
    Khi cố gắng thêm nhân viên mới vào 'PB_HCM_01' với MaVaiTro = 2 hoặc MaCV = 'TP':
    - Hệ thống BẮT BUỘC từ chối và trả về HTTP 400 Bad Request.
    - Mã lỗi (error code): 'DEPARTMENT_MANAGER_EXISTS'.
    """
    ensure_test_users(db_conn_hn, db_conn_dn)
    token = get_auth_token(client, "giap_gd")  # Dùng token Tổng giám đốc hoặc HR
    
    new_employee_payload = {
        "ma_nv": "NV_HCM_DUPLICATE_MGR",
        "ho_ten": "Nguyễn Văn Trưởng Phòng 2",
        "phai": "Nam",
        "ngay_sinh": "1990-01-01",
        "so_dien_thoai": "0988777666",
        "email": "mgr2_hcm@x.corp",
        "ma_so_thue": "MST_MGR_02",
        "ma_pb": "PB_HCM_01",
        "ma_cv": "TP",           # Chức vụ Trưởng phòng
        "ma_vai_tro": 2,          # Vai trò Trưởng phòng
        "ma_cn": "HCM",
        "username": "mgr2_hcm",
        "password": "Password123",
        "skills": [{"name": "Management", "level": "Advanced"}],
        "performance_reviews": []
    }
    
    # Gửi qua multipart/form-data
    response = client.post(
        "/api/employees",
        data={"data": json.dumps(new_employee_payload)},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400, f"Expected 400 DEPARTMENT_MANAGER_EXISTS, got {response.status_code}: {response.text}"
    data = response.json()
    assert data.get("success") is False
    assert data.get("error", {}).get("code") == "DEPARTMENT_MANAGER_EXISTS", \
        f"Expected code DEPARTMENT_MANAGER_EXISTS, got {data.get('error')}"

def test_adding_normal_employee_to_department_succeeds(client, db_conn_hn, db_conn_dn, db_conn_hcm):
    """
    Thêm nhân viên bình thường (MaVaiTro = 1, MaCV = 'NV') vào cùng phòng ban đã có Trưởng phòng:
    - BẮT BUỘC thành công (không bị kích hoạt quy tắc Single Manager Rule).
    """
    ensure_test_users(db_conn_hn, db_conn_dn)
    token = get_auth_token(client, "giap_gd")
    
    target_manv = "NV_HCM_STAFF_OK"
    
    # Dọn dẹp trước nếu tồn tại
    with db_conn_hcm.cursor() as cur:
        cur.execute("DELETE FROM HoSoMoRong WHERE MaNV = %s;", (target_manv,))
        cur.execute("DELETE FROM NguoiDungDangNhap WHERE MaNV = %s;", (target_manv,))
        cur.execute("DELETE FROM Luong WHERE MaNV = %s;", (target_manv,))
        cur.execute("DELETE FROM NhanVien WHERE MaNV = %s;", (target_manv,))

    normal_employee_payload = {
        "ma_nv": target_manv,
        "ho_ten": "Nhân Viên Hợp Lệ",
        "phai": "Nữ",
        "ngay_sinh": "1997-08-20",
        "so_dien_thoai": "0988111222",
        "email": "staff_ok_hcm@x.corp",
        "ma_so_thue": "MST_STAFF_OK",
        "ma_pb": "PB_HCM_01",
        "ma_cv": "NV",          # Chức vụ nhân viên
        "ma_vai_tro": 1,         # Vai trò nhân viên
        "ma_cn": "HCM",
        "username": "staff_ok_hcm",
        "password": "Password123",
        "skills": [{"name": "Sales", "level": "Basic"}],
        "performance_reviews": []
    }
    
    try:
        response = client.post(
            "/api/employees",
            data={"data": json.dumps(normal_employee_payload)},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code in [200, 201], f"Expected 201 Created, got {response.status_code}: {response.text}"
    finally:
        # Dọn dẹp sau kiểm thử
        with db_conn_hcm.cursor() as cur:
            cur.execute("DELETE FROM HoSoMoRong WHERE MaNV = %s;", (target_manv,))
            cur.execute("DELETE FROM NguoiDungDangNhap WHERE MaNV = %s;", (target_manv,))
            cur.execute("DELETE FROM Luong WHERE MaNV = %s;", (target_manv,))
            cur.execute("DELETE FROM NhanVien WHERE MaNV = %s;", (target_manv,))

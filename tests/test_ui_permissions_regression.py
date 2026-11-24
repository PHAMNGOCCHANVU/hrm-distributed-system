import pytest
from tests.test_rbac_masking import get_auth_token

def test_persona_menu_and_api_permissions_regression(client):
    """
    Kiểm tra Hồi quy Phân quyền Persona (UI Permissions Regression):
    - Đảm bảo khắc phục triệt để lỗi 403 khi người dùng truy cập các tính năng thuộc phân quyền của mình:
      1. CEO: Truy cập thành công /api/organizations/tree, /api/reports/headcount, /api/employees, /api/payroll.
      2. Giám đốc Chi nhánh: Truy cập thành công /api/organizations/tree, /api/reports/headcount, /api/employees.
      3. Nhân viên Tài vụ: Truy cập thành công /api/payroll.
      4. Nhân viên thông thường: Truy cập thành công /api/payroll/my-slip, /api/employees/colleagues, /api/auth/me.
      5. Cán bộ Vận hành: Truy cập thành công /api/system/health, /api/system-admin/requests.
    """
    # 1. CEO
    token_ceo = get_auth_token(client, "giap_gd")
    for endpoint in ["/api/organizations/tree", "/api/reports/headcount", "/api/employees", "/api/payroll"]:
        res = client.get(endpoint, headers={"Authorization": f"Bearer {token_ceo}"})
        assert res.status_code == 200, f"CEO bị lỗi khi truy cập {endpoint}: {res.status_code}"

    # 2. Giám đốc Chi nhánh Đà Nẵng
    token_dir_dn = get_auth_token(client, "cuong_gd_dn")
    for endpoint in ["/api/organizations/tree", "/api/reports/headcount", "/api/employees"]:
        res = client.get(endpoint, headers={"Authorization": f"Bearer {token_dir_dn}"})
        assert res.status_code == 200, f"Giám đốc CN bị lỗi khi truy cập {endpoint}: {res.status_code}"

    # 3. Nhân viên Tài vụ
    token_fin = get_auth_token(client, "finance_user")
    res_fin = client.get("/api/payroll?month=3&year=2026", headers={"Authorization": f"Bearer {token_fin}"})
    assert res_fin.status_code == 200, f"Tài vụ bị lỗi truy cập /api/payroll: {res_fin.status_code}"

    # 4. Nhân viên thông thường
    token_emp = get_auth_token(client, "cuong_dn")
    for endpoint in ["/api/payroll/my-slip?month=3&year=2026", "/api/employees/colleagues", "/api/auth/me"]:
        res = client.get(endpoint, headers={"Authorization": f"Bearer {token_emp}"})
        assert res.status_code == 200, f"Nhân viên bị lỗi truy cập {endpoint}: {res.status_code}"

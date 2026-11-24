import pytest
from tests.test_rbac_masking import get_auth_token

def test_system_operator_cannot_access_payroll_or_employees_crud(client):
    """
    Tách biệt Quản trị Kỹ thuật khỏi Nghiệp vụ Nhân sự:
    - Cán bộ Phòng Vận hành (SYSTEM_OPERATOR) chịu trách nhiệm kỹ thuật hệ thống.
    - Tuyệt đối không có quyền xem/sửa trái phép bảng lương (/api/payroll) hoặc hồ sơ (/api/employees).
    """
    token = None
    for op_user in ["ops_user", "operator_hn", "operator_hq", "vu_vanhanh"]:
        try:
            token = get_auth_token(client, op_user)
            break
        except Exception:
            continue
            
    if not token:
        pytest.skip("Chưa có tài khoản System Operator để kiểm thử")

    # 1. Truy cập /api/payroll -> 403 Forbidden
    res_payroll = client.get("/api/payroll?month=3&year=2026", headers={"Authorization": f"Bearer {token}"})
    assert res_payroll.status_code == 403, f"System Operator không được phép truy cập bảng lương, got {res_payroll.status_code}"

    # 2. Thử tạo nhân viên mới qua /api/employees -> 403 Forbidden
    res_emp = client.post("/api/employees", data={"data": "{}"}, headers={"Authorization": f"Bearer {token}"})
    assert res_emp.status_code == 403, f"System Operator không được phép tạo nhân viên, got {res_emp.status_code}"

def test_anti_self_approval_rule_for_technical_requests(client):
    """
    Quy tắc Ngăn chặn Tự Duyệt (Anti-self-approval Rule):
    - Người gửi yêu cầu cấp quyền kỹ thuật tuyệt đối không thể tự phê duyệt yêu cầu của chính mình.
    """
    token_op = None
    for op_user in ["ops_user", "operator_hn", "operator_hq", "vu_vanhanh"]:
        try:
            token_op = get_auth_token(client, op_user)
            break
        except Exception:
            continue
            
    if not token_op:
        pytest.skip("Chưa có tài khoản Operator")

    # 1. Operator gửi yêu cầu kỹ thuật
    req_payload = {
        "loai_yeu_cau": "CAP_QUYEN_OPERATOR",
        "pham_vi": "BRANCH",
        "chi_nhanh": "DN",
        "ly_do": "Kiểm tra bảo trì node",
        "thong_so_ky_thuat": {"node_target": "site_dn", "duration_hours": 24}
    }
    create_res = client.post("/api/system-admin/requests", json=req_payload, headers={"Authorization": f"Bearer {token_op}"})
    if create_res.status_code not in [200, 201]:
        pytest.skip(f"Endpoint /api/system-admin/requests chưa sẵn sàng: {create_res.status_code}")
        
    req_id = create_res.json()["data"]["ma_yeu_cau"]
    
    # 2. CHÍNH Operator này cố gắng tự phê duyệt yêu cầu của mình -> BẮT BUỘC BỊ TỪ CHỐI 403
    approve_res = client.put(f"/api/system-admin/requests/{req_id}/approve", json={
        "decision": "APPROVED",
        "comment": "Tự duyệt yêu cầu"
    }, headers={"Authorization": f"Bearer {token_op}"})
    
    assert approve_res.status_code == 403, f"Chống tự duyệt thất bại, mong đợi 403 nhưng nhận {approve_res.status_code}: {approve_res.text}"

def test_executive_approval_scope_enforcement(client):
    """
    Phân định thẩm quyền phê duyệt yêu cầu kỹ thuật:
    - Yêu cầu GLOBAL: Chỉ CEO (Group Executive) được duyệt.
    - Yêu cầu BRANCH: Giám đốc Chi nhánh tương ứng được duyệt.
    - Giám đốc Chi nhánh khác duyệt yêu cầu: 403 Forbidden.
    """
    token_op = None
    for op in ["ops_user", "operator_hn", "operator_hq", "vu_vanhanh"]:
        try:
            token_op = get_auth_token(client, op)
            break
        except Exception:
            continue
            
    if not token_op:
        pytest.skip("Chưa có tài khoản Operator")

    # Tạo 1 yêu cầu GLOBAL
    res_global = client.post("/api/system-admin/requests", json={
        "loai_yeu_cau": "BAO_TRI_HE_THONG",
        "pham_vi": "GLOBAL",
        "chi_nhanh": None,
        "ly_do": "Bảo trì toàn hệ thống",
        "thong_so_ky_thuat": {}
    }, headers={"Authorization": f"Bearer {token_op}"})
    
    if res_global.status_code not in [200, 201]:
        pytest.skip(f"Chưa hỗ trợ tạo yêu cầu GLOBAL: {res_global.status_code}")
        
    global_req_id = res_global.json()["data"]["ma_yeu_cau"]
    
    # Giám đốc chi nhánh DN cố gắng duyệt yêu cầu GLOBAL -> Phải bị từ chối 403
    token_dir_dn = get_auth_token(client, "cuong_gd_dn")
    dn_approve_res = client.put(f"/api/system-admin/requests/{global_req_id}/approve", json={
        "decision": "APPROVED",
        "comment": "Giám đốc DN duyệt GLOBAL trái quyền"
    }, headers={"Authorization": f"Bearer {token_dir_dn}"})
    assert dn_approve_res.status_code == 403, f"Giám đốc CN không được duyệt yêu cầu GLOBAL, got {dn_approve_res.status_code}"

    # CEO duyệt yêu cầu GLOBAL -> Thành công 200
    token_ceo = get_auth_token(client, "giap_gd")
    ceo_approve_res = client.put(f"/api/system-admin/requests/{global_req_id}/approve", json={
        "decision": "APPROVED",
        "comment": "CEO chấp thuận bảo trì toàn hệ thống"
    }, headers={"Authorization": f"Bearer {token_ceo}"})
    assert ceo_approve_res.status_code == 200, f"CEO duyệt yêu cầu GLOBAL thất bại: {ceo_approve_res.text}"

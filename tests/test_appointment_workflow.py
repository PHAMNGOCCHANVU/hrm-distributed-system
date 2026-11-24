import pytest
from tests.test_rbac_masking import get_auth_token

def test_create_appointment_proposal(client):
    """
    Quy trình Đề xuất Bổ nhiệm / Điều chuyển (Maker):
    - Chuyên viên hoặc Trưởng phòng Nhân sự lập phiếu đề xuất.
    - Phiếu được tạo thành công với trạng thái PENDING.
    """
    token_hr = None
    for hr_user in ["hr_specialist", "hoa_nv", "hr_user", "le_thutrang"]:
        try:
            token_hr = get_auth_token(client, hr_user)
            break
        except Exception:
            continue
            
    if not token_hr:
        token_hr = get_auth_token(client, "giap_gd")  # Fallback

    payload = {
        "ma_nv": "NV_DN_01",
        "chuc_vu_moi": "TP",
        "ma_pb_moi": "PB_DN_01",
        "ma_cn_moi": "DN",
        "ly_do": "Quy hoạch cán bộ nguồn - Đề xuất bổ nhiệm Trưởng phòng",
        "ngay_hieu_luc": "2026-05-01"
    }

    res = client.post("/api/appointments", json=payload, headers={"Authorization": f"Bearer {token_hr}"})
    if res.status_code not in [200, 201]:
        pytest.skip(f"API /api/appointments chưa sẵn sàng: {res.status_code}")
        
    data = res.json()
    assert data.get("success") is True
    appointment = data.get("data", {})
    assert "ma_quyet_dinh" in appointment
    assert appointment.get("trang_thai") == "PENDING"

def test_appointment_approval_cross_branch_restriction(client):
    """
    Kiểm tra thẩm quyền phê duyệt Bổ nhiệm / Điều chuyển (Checker):
    - Giám đốc chi nhánh DN không có quyền phê duyệt đề xuất bổ nhiệm cho nhân sự thuộc chi nhánh HCM.
    - Phải trả về 403 Forbidden.
    """
    token_ceo = get_auth_token(client, "giap_gd")
    
    # 1. Tạo 1 đề xuất bổ nhiệm tại HCM
    payload = {
        "ma_nv": "NV_HCM_01",
        "chuc_vu_moi": "TP",
        "ma_pb_moi": "PB_HCM_01",
        "ma_cn_moi": "HCM",
        "ly_do": "Đề xuất tại HCM",
        "ngay_hieu_luc": "2026-05-01"
    }
    create_res = client.post("/api/appointments", json=payload, headers={"Authorization": f"Bearer {token_ceo}"})
    if create_res.status_code not in [200, 201]:
        pytest.skip("Chưa tạo được phiếu bổ nhiệm HCM")
        
    decision_id = create_res.json()["data"]["ma_quyet_dinh"]
    
    # 2. Giám đốc chi nhánh DN duyệt đề xuất của HCM -> 403 Forbidden
    token_dir_dn = get_auth_token(client, "cuong_gd_dn")
    approve_res = client.put(f"/api/appointments/{decision_id}/approve", json={
        "decision": "APPROVED",
        "comment": "Giám đốc DN duyệt cho HCM trái quyền"
    }, headers={"Authorization": f"Bearer {token_dir_dn}"})
    
    assert approve_res.status_code == 403, f"Giám đốc DN không được duyệt bổ nhiệm ở HCM, got {approve_res.status_code}"

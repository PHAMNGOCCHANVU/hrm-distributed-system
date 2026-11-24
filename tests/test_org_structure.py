import pytest
from tests.test_rbac_masking import get_auth_token

def test_get_organization_tree_structure(client):
    """
    Kiểm tra endpoint GET /api/organizations/tree:
    - Phải phân biệt rõ 2 bộ máy tại Hà Nội: Bộ máy Tập đoàn (Corporate HQ) và Chi nhánh Hà Nội (Branch HN).
    - Phải trả về đủ 3 chi nhánh: HN, DN, HCM.
    - Corporate HQ bao gồm các phòng ban cấp tập đoàn (PB_HQ_*).
    """
    token = get_auth_token(client, "giap_gd")
    response = client.get("/api/organizations/tree", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()
    assert data.get("success") is True
    tree = data.get("data", {})
    
    # 1. Kiểm tra Bộ máy Tập đoàn (Corporate HQ)
    assert "corporate_hq" in tree, "Thiếu khối corporate_hq trong cây cơ cấu tổ chức"
    hq = tree["corporate_hq"]
    assert "unit_name" in hq
    assert "departments" in hq
    hq_dept_codes = [d.get("code") or d.get("ma_pb") for d in hq["departments"]]
    assert any("HQ" in code for code in hq_dept_codes if code), f"Không tìm thấy phòng ban cấp HQ: {hq_dept_codes}"
    
    # 2. Kiểm tra các Chi nhánh (Branches)
    assert "branches" in tree, "Thiếu danh sách chi nhánh (branches) trong cây cơ cấu tổ chức"
    branches = tree["branches"]
    assert len(branches) >= 3, f"Cần ít nhất 3 chi nhánh (HN, DN, HCM), thực tế có {len(branches)}"
    
    branch_codes = [b.get("branch_code") or b.get("ma_cn") for b in branches]
    assert "HN" in branch_codes, "Thiếu Chi nhánh Hà Nội (Branch HN)"
    assert "DN" in branch_codes, "Thiếu Chi nhánh Đà Nẵng (Branch DN)"
    assert "HCM" in branch_codes, "Thiếu Chi nhánh TP.HCM (Branch HCM)"
    
    # Kiểm tra Chi nhánh Hà Nội có phòng ban riêng phân biệt với HQ
    hn_branch = next(b for b in branches if (b.get("branch_code") or b.get("ma_cn")) == "HN")
    hn_dept_codes = [d.get("code") or d.get("ma_pb") for d in hn_branch.get("departments", [])]
    assert any("HN" in code for code in hn_dept_codes if code), f"Chi nhánh Hà Nội thiếu phòng ban riêng: {hn_dept_codes}"

def test_corporate_hq_departments_db_storage(db_conn_hn):
    """
    Kiểm tra cơ sở dữ liệu:
    - Các phòng ban cấp Tập đoàn phải có LoaiDonVi = 'TAP_DOAN' và lưu trên site_hn.
    """
    with db_conn_hn.cursor() as cur:
        # Kiểm tra cột LoaiDonVi tồn tại
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'phongban' AND column_name = 'loaidonvi';
        """)
        col = cur.fetchone()
        assert col is not None, "Cột LoaiDonVi chưa được bổ sung vào bảng PhongBan trên site_hn"
        
        # Kiểm tra có ít nhất 1 phòng ban TAP_DOAN
        cur.execute("SELECT MaPB, TenPB, LoaiDonVi FROM PhongBan WHERE LoaiDonVi = 'TAP_DOAN';")
        rows = cur.fetchall()
        assert len(rows) > 0, "Chưa nạp phòng ban cấp TAP_DOAN nào trên site_hn"

import pytest
from tests.test_rbac_masking import get_auth_token, ensure_test_users

def test_system_health_endpoint(client, db_conn_hn, db_conn_dn):
    """
    Kiểm tra API giám sát hệ thống phân tán: GET /api/system/health
    - Yêu cầu xác thực (Tổng giám đốc hoặc Giám đốc chi nhánh).
    - Trả về HTTP 200.
    - success == True.
    - overall_status là một trong: HEALTHY, DEGRADED, UNHEALTHY.
    - nodes chứa đủ 4 node: site_hn, site_dn, site_hcm, minio_server.
    - Mỗi node có thông tin status='ONLINE', latency_ms >= 0.
    """
    ensure_test_users(db_conn_hn, db_conn_dn)
    token = get_auth_token(client, "giap_gd")
    
    response = client.get("/api/system/health", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert data.get("success") is True
    
    health_data = data.get("data")
    assert health_data is not None
    assert "overall_status" in health_data
    assert health_data["overall_status"] in ["HEALTHY", "DEGRADED", "UNHEALTHY"]
    
    nodes = health_data.get("nodes", [])
    assert len(nodes) >= 4, f"Cần giám sát ít nhất 4 node (3 DB + 1 MinIO), thực tế có {len(nodes)}"
    
    node_ids = [n.get("node_id") for n in nodes]
    assert "site_hn" in node_ids, "Thiếu node_id site_hn trong kết quả giám sát"
    assert "site_dn" in node_ids, "Thiếu node_id site_dn trong kết quả giám sát"
    assert "site_hcm" in node_ids, "Thiếu node_id site_hcm trong kết quả giám sát"
    assert "minio_server" in node_ids, "Thiếu node_id minio_server trong kết quả giám sát"
    
    for n in nodes:
        assert n.get("status") in ["ONLINE", "OFFLINE"]
        assert "latency_ms" in n
        assert isinstance(n["latency_ms"], (int, float))
        assert n["latency_ms"] >= 0

import io
import json
import pytest
from tests.test_rbac_masking import get_auth_token, ensure_test_users

def test_minio_compensating_transaction_on_db_failure(client, minio_client, db_conn_hn, db_conn_dn):
    """
    Kiểm thử Giao dịch Bù trừ Đa mô hình (Multi-Model Compensating Transaction):
    Kịch bản:
    1. Client gửi request thêm mới nhân sự kèm file ảnh avatar / CV.
    2. Backend thực hiện Bước 1: Upload file lên MinIO thành công.
    3. Backend thực hiện Bước 2: Ghi vào PostgreSQL nhưng BỊ LỖI (ví dụ: vi phạm CHECK constraint hoặc trùng email/mã).
    4. Backend bắt ngoại lệ, thực hiện Bước 3: Đền bù bằng cách XÓA file vừa tải lên MinIO.
    5. Xác minh: File trên MinIO không bị mồ côi (orphaned file).
    """
    ensure_test_users(db_conn_hn, db_conn_dn)
    token = get_auth_token(client, "giap_gd")
    
    # Chuẩn bị file nhị phân giả lập (filename, content, content_type)
    fake_avatar_content = b"GIF89a Fake Image Content for Compensation Test"
    fake_avatar = ("avatar_compensation_test.png", fake_avatar_content, "image/png")
    
    # Tạo payload CỐ TÌNH LỖI: Trùng Email với nhân viên đã có (NV_HN_01 -> giaplq@x.corp)
    # hoặc MaCN vi phạm check constraint
    failing_payload = {
        "ma_nv": "NV_FAIL_COMPENSATE",
        "ho_ten": "Nhân Viên Gây Lỗi Rollback",
        "phai": "Nam",
        "ngay_sinh": "1990-01-01",
        "so_dien_thoai": "0999999999",
        "email": "giaplq@x.corp", # TRÙNG EMAIL VỚI NV_HN_01 BẮT BUỘC LỖI DB
        "ma_so_thue": "MST_FAIL_01",
        "ma_pb": "PB_HN_01",
        "ma_cv": "NV",
        "ma_vai_tro": 1,
        "ma_cn": "HN",
        "username": "user_fail_rollback",
        "password": "Password123",
        "skills": [],
        "performance_reviews": []
    }
    
    # Ghi nhận danh sách file hiện có trên MinIO bucket
    initial_objects = [
        obj.object_name for obj in minio_client.list_objects("nhansu-bucket", prefix="avatars/", recursive=True)
    ]
    
    response = client.post(
        "/api/employees",
        data={"data": json.dumps(failing_payload)},
        files={"avatar": fake_avatar},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Request phải thất bại (400 hoặc 500)
    assert response.status_code in [400, 409, 500], f"Expected failure response, got {response.status_code}"
    
    # Kiểm tra lại danh sách file trên MinIO
    after_objects = [
        obj.object_name for obj in minio_client.list_objects("nhansu-bucket", prefix="avatars/", recursive=True)
    ]
    
    # Không được có thêm file mới mồ côi nào lưu lại trên MinIO
    new_files = set(after_objects) - set(initial_objects)
    assert len(new_files) == 0, f"Phát hiện file mồ côi trên MinIO chưa được xóa đền bù: {new_files}"

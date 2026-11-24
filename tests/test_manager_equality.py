import pytest
from tests.test_rbac_masking import get_auth_token

def test_hr_manager_cannot_modify_other_department_manager(client):
    """
    Quy tắc Bình đẳng giữa các Trưởng phòng (Manager Equality Rule):
    - Mọi Trưởng phòng (Nhân sự, Tài vụ, Kinh doanh, Vận hành, Kỹ thuật) đều ngang hàng trong cấp bậc quản lý.
    - Trưởng phòng Nhân sự không thể tự ý sửa đổi hồ sơ hoặc lương của Trưởng phòng khác (Tài vụ/Kinh doanh).
    """
    # Đăng nhập bằng tài khoản Trưởng phòng Nhân sự
    token = None
    for hr_user in ["tp_hr", "hr_manager", "tp_ns_hq", "tp_ns_hn"]:
        try:
            token = get_auth_token(client, hr_user)
            break
        except Exception:
            continue
            
    if not token:
        # Nếu chưa có tài khoản test cụ thể, bỏ qua hoặc dùng tài khoản Role 2
        pytest.skip("Chưa có tài khoản Trưởng phòng Nhân sự để test quy tắc bình đẳng")

    # Thử gọi API cập nhật thông tin một Trưởng phòng khác (ví dụ: NV_HCM_01 - Trưởng phòng Kinh doanh HCM)
    response = client.put("/api/employees/NV_HCM_01", data={"data": '{"ho_ten": "Tên Đổi Trái Phép"}'}, headers={"Authorization": f"Bearer {token}"})
    # Bắt buộc bị từ chối 403 Forbidden
    assert response.status_code == 403, f"Trưởng phòng Nhân sự không được phép sửa Trưởng phòng khác, mong đợi 403 nhưng nhận {response.status_code}"

def test_corporate_hq_hr_cannot_bypass_branch_direct_management(client):
    """
    Trưởng phòng Nhân sự Tập đoàn không mặc nhiên là cấp trên hay có quyền điều hành trực tiếp
    nhân sự thuộc Chi nhánh nếu không thông qua quy trình Điều chuyển / Bổ nhiệm chính thức.
    """
    token = None
    for hq_hr in ["tp_ns_hq", "hr_hq_manager"]:
        try:
            token = get_auth_token(client, hq_hr)
            break
        except Exception:
            continue
            
    if not token:
        pytest.skip("Chưa có tài khoản Trưởng phòng Nhân sự HQ")

    # Thử trực tiếp thay đổi chức vụ nhân viên chi nhánh DN mà không qua quy trình bổ nhiệm
    response = client.put("/api/employees/NV_DN_01", data={"data": '{"ma_cv": "TP"}'}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in [400, 403], f"Cần chặn việc sửa chức vụ trực tiếp vượt quyền: {response.status_code}"

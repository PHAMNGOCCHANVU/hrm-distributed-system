from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status

from app.schemas.auth import CurrentUser
from app.schemas.appointment import (
    AppointmentCreateRequest, AppointmentApproveRequest, AppointmentResponse
)
import app.repositories.appointment_repo as appointment_repo
import app.repositories.employee_repo as employee_repo
import app.repositories.health_repo as health_repo
from app.core.db_router import get_write_pool


def create_appointment(
    req: AppointmentCreateRequest,
    current_user: CurrentUser
) -> AppointmentResponse:
    """
    Tạo đề xuất Bổ nhiệm / Điều chuyển (Maker):
    - Kiểm tra thông tin nhân viên mục tiêu.
    - Lưu đề xuất với trạng thái PENDING.
    """
    target_emp = employee_repo.get_employee_by_id(req.ma_nv)
    if not target_emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Không tìm thấy nhân viên {req.ma_nv}"}
        )

    payload = {
        "ma_nv": req.ma_nv,
        "loai_quyet_dinh": "BO_NHIEM",
        "ma_pb_cu": target_emp.get("mapb"),
        "ma_pb_moi": req.ma_pb_moi,
        "ma_cv_cu": target_emp.get("macv"),
        "chuc_vu_moi": req.chuc_vu_moi,
        "ma_cn_cu": target_emp.get("chinhanh"),
        "ma_cn_moi": req.ma_cn_moi,
        "nguoi_de_xuat": current_user.ma_nv,
        "ly_do": req.ly_do,
        "ngay_hieu_luc": req.ngay_hieu_luc
    }

    res = appointment_repo.create_appointment(payload)
    return AppointmentResponse(
        ma_quyet_dinh=res["maquyetdinh"],
        loai_quyet_dinh=res.get("loaiquyetdinh", "BO_NHIEM"),
        ma_nv=res["manv"],
        ma_pb_cu=target_emp.get("mapb"),
        ma_pb_moi=res.get("mapbmoi"),
        ma_cv_cu=target_emp.get("macv"),
        ma_cv_moi=res.get("macvmoi"),
        ma_cn_cu=target_emp.get("chinhanh"),
        ma_cn_moi=res.get("macnmoi"),
        nguoi_de_xuat=current_user.ma_nv,
        trang_thai="PENDING",
        ly_do=res.get("lydo"),
        ngay_de_xuat=res.get("ngaydexuat"),
        ngay_hieu_luc=res.get("ngayhieuluc")
    )


def approve_appointment(
    decision_id: str,
    req: AppointmentApproveRequest,
    current_user: CurrentUser
) -> AppointmentResponse:
    """
    Phê duyệt đề xuất Bổ nhiệm / Điều chuyển (Checker):
    - CEO (Group Executive): Duyệt mọi đề xuất toàn quốc, đề xuất cấp HQ và bổ nhiệm Giám đốc CN.
    - Giám đốc Chi nhánh (Branch Director): Chỉ được duyệt đề xuất nội bộ chi nhánh của mình.
    - Giám đốc chi nhánh khác cố tình duyệt -> 403 Forbidden.
    - Single Manager Rule được kiểm tra khi duyệt quyết định bổ nhiệm Trưởng phòng.
    """
    record = appointment_repo.get_appointment_by_id(decision_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Không tìm thấy phiếu quyết định {decision_id}"}
        )

    target_branch = record.get("macnmoi") or record.get("macncu")
    is_ceo = (current_user.role_id == 4 or current_user.role_name == "Tổng giám đốc" or "GROUP_EXECUTIVE" in current_user.system_roles)
    is_branch_dir = (current_user.role_id == 3 or current_user.role_name in ["Giám đốc", "Giám đốc chi nhánh"] or "BRANCH_DIRECTOR" in current_user.system_roles)

    if is_ceo:
        pass  # CEO toàn quyền duyệt
    elif is_branch_dir:
        # Giám đốc chi nhánh chỉ được duyệt nhân sự thuộc chi nhánh mình
        if target_branch != current_user.branch:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Giám đốc chi nhánh không có quyền phê duyệt đề xuất bổ nhiệm cho nhân sự thuộc chi nhánh khác!"}
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Bạn không có thẩm quyền phê duyệt quyết định bổ nhiệm!"}
        )

    decision_status = req.decision.upper()
    if decision_status not in ["APPROVED", "REJECTED"]:
        decision_status = "APPROVED"

    # Kiểm tra Single Manager Rule khi duyệt bổ nhiệm Trưởng phòng
    if decision_status == "APPROVED" and record.get("macvmoi") == "TP":
        target_site = get_write_pool(target_branch)
        if employee_repo.check_department_manager_exists(record.get("mapbmoi"), target_site, exclude_ma_nv=record["manv"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "DEPARTMENT_MANAGER_EXISTS", "message": "Phòng ban này đã có Trưởng phòng!"}
            )

    appointment_repo.update_appointment_status(
        decision_id=decision_id,
        new_status=decision_status,
        approver_id=current_user.ma_nv,
        comment=req.comment
    )

    # Nếu phê duyệt thành công -> áp dụng thay đổi vào hồ sơ nhân viên
    if decision_status == "APPROVED":
        appointment_repo.apply_appointment_to_employee(
            ma_nv=record["manv"],
            chuc_vu_moi=record.get("macvmoi", "NV"),
            ma_pb_moi=record.get("mapbmoi"),
            ma_cn_moi=record.get("macnmoi", "HN")
        )
        health_repo.insert_audit_log(
            manv_thuc_hien=current_user.ma_nv,
            tennv_thuc_hien=current_user.full_name,
            thao_tac="PHE_DUYET_BO_NHIEM",
            tac_dong_len_nv=record["manv"],
            chi_tiet=f"Phê duyệt bổ nhiệm {decision_id}: chức vụ {record.get('macvmoi')}, phòng {record.get('mapbmoi')}"
        )

    return AppointmentResponse(
        ma_quyet_dinh=record["maquyetdinh"],
        loai_quyet_dinh=record.get("loaiquyetdinh", "BO_NHIEM"),
        ma_nv=record["manv"],
        ma_pb_cu=record.get("mapbcu"),
        ma_pb_moi=record.get("mapbmoi"),
        ma_cv_cu=record.get("macvcu"),
        ma_cv_moi=record.get("macvmoi"),
        ma_cn_cu=record.get("macncu"),
        ma_cn_moi=record.get("macnmoi"),
        nguoi_de_xuat=record.get("nguoidexuat"),
        nguoi_phe_duyet=current_user.ma_nv,
        trang_thai=decision_status,
        ly_do=record.get("lydo"),
        ngay_de_xuat=record.get("ngaydexuat"),
        ngay_hieu_luc=record.get("ngayhieuluc")
    )


def list_appointments(status_filter: Optional[str] = None) -> List[AppointmentResponse]:
    """Danh sách các phiếu đề xuất bổ nhiệm."""
    rows = appointment_repo.get_appointments(status=status_filter)
    return [
        AppointmentResponse(
            ma_quyet_dinh=r["maquyetdinh"],
            loai_quyet_dinh=r.get("loaiquyetdinh", "BO_NHIEM"),
            ma_nv=r["manv"],
            ma_pb_cu=r.get("mapbcu"),
            ma_pb_moi=r.get("mapbmoi"),
            ma_cv_cu=r.get("macvcu"),
            ma_cv_moi=r.get("macvmoi"),
            ma_cn_cu=r.get("macncu"),
            ma_cn_moi=r.get("macnmoi"),
            nguoi_de_xuat=r.get("nguoidexuat"),
            nguoi_phe_duyet=r.get("nguoipheduyet"),
            trang_thai=r.get("trangthai", "PENDING"),
            ly_do=r.get("lydo"),
            ngay_de_xuat=r.get("ngaydexuat"),
            ngay_hieu_luc=r.get("ngayhieuluc"),
            ngay_phe_duyet=r.get("ngaypheduyet")
        ) for r in rows
    ]

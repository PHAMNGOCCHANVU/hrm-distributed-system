from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status

from app.schemas.auth import CurrentUser
from app.schemas.admin_request import (
    SystemAdminRequestCreate, SystemAdminApproveRequest, SystemAdminRequestResponse
)
import app.repositories.admin_request_repo as admin_repo
import app.repositories.health_repo as health_repo


def create_admin_request(
    req: SystemAdminRequestCreate,
    current_user: CurrentUser
) -> SystemAdminRequestResponse:
    """
    Cán bộ Phòng Vận hành (SYSTEM_OPERATOR) gửi yêu cầu quản trị kỹ thuật.
    """
    payload = {
        "loai_yeu_cau": req.loai_yeu_cau,
        "pham_vi": req.pham_vi.upper().strip(),
        "chi_nhanh": req.chi_nhanh.upper().strip() if req.chi_nhanh else None,
        "ma_nv_yeu_cau": current_user.ma_nv,
        "ly_do": req.ly_do,
        "thong_so_ky_thuat": req.thong_so_ky_thuat
    }

    res = admin_repo.create_admin_request(payload)
    return SystemAdminRequestResponse(
        ma_yeu_cau=res["mayeucau"],
        loai_yeu_cau=res["loaiyeucau"],
        ma_nv_yeu_cau=current_user.ma_nv,
        pham_vi_yeu_cau=res["phamviyeucau"],
        noi_dung_yeu_cau=res.get("noidungyeucau") or {},
        trang_thai="PENDING",
        ngay_tao=res.get("ngaytao")
    )


def approve_admin_request(
    req_id: str,
    payload: SystemAdminApproveRequest,
    current_user: CurrentUser
) -> SystemAdminRequestResponse:
    """
    Lãnh đạo Phê duyệt Yêu cầu Quản trị Kỹ thuật:
    1. Quy tắc Chống tự duyệt (Anti-self-approval Rule):
       - Người gửi yêu cầu tuyệt đối không thể tự phê duyệt yêu cầu của mình -> 403 Forbidden.
    2. Quy tắc Phân định Thẩm quyền (Scope Enforcement):
       - Yêu cầu GLOBAL: Bắt buộc CEO (Group Executive) duyệt.
       - Yêu cầu BRANCH: Giám đốc Chi nhánh tương ứng duyệt (hoặc CEO).
       - Giám đốc chi nhánh khác duyệt yêu cầu: 403 Forbidden.
    """
    req = admin_repo.get_admin_request_by_id(req_id)
    if not req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Không tìm thấy yêu cầu {req_id}"}
        )

    # 1. QUY TẮC CHỐNG TỰ DUYỆT (Anti-self-approval Rule)
    if req.get("manvyeucau") == current_user.ma_nv:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Bạn không thể tự phê duyệt yêu cầu kỹ thuật của chính mình!"}
        )

    # 2. KIỂM TRA THẨM QUYỀN DUYỆT THEO PHẠM VI (GLOBAL vs BRANCH)
    is_ceo = (current_user.role_id == 4 or current_user.role_name == "Tổng giám đốc" or "GROUP_EXECUTIVE" in current_user.system_roles)
    is_branch_dir = (current_user.role_id == 3 or current_user.role_name in ["Giám đốc", "Giám đốc chi nhánh"] or "BRANCH_DIRECTOR" in current_user.system_roles)
    req_scope = req.get("phamviyeucau", "BRANCH").upper()
    req_content = req.get("noidungyeucau") or {}
    req_branch = req_content.get("chi_nhanh") or (req_content.get("node_target", "").replace("site_", "").upper())

    if req_scope == "GLOBAL":
        # Chỉ CEO được duyệt yêu cầu GLOBAL
        if not is_ceo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Chỉ Tổng Giám Đốc (Group Executive) mới có thẩm quyền phê duyệt yêu cầu cấp Tập đoàn!"}
            )
    elif req_scope == "BRANCH":
        if is_ceo:
            pass  # CEO được duyệt cả cấp chi nhánh
        elif is_branch_dir:
            # Giám đốc chi nhánh phải đúng chi nhánh yêu cầu
            if req_branch and req_branch != current_user.branch:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={"code": "FORBIDDEN", "message": "Giám đốc chi nhánh không có quyền phê duyệt yêu cầu kỹ thuật của chi nhánh khác!"}
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Bạn không có quyền phê duyệt yêu cầu kỹ thuật!"}
            )

    decision_status = payload.decision.upper()
    if decision_status not in ["APPROVED", "REJECTED"]:
        decision_status = "APPROVED"

    admin_repo.update_admin_request_status(
        req_id=req_id,
        new_status=decision_status,
        approver_id=current_user.ma_nv,
        reject_reason=payload.comment if decision_status == "REJECTED" else None
    )

    health_repo.insert_audit_log(
        manv_thuc_hien=current_user.ma_nv,
        tennv_thuc_hien=current_user.full_name,
        thao_tac=f"PHE_DUYET_YEU_CAU_KY_THUAT_{decision_status}",
        tac_dong_len_nv=req.get("manvyeucau"),
        chi_tiet=f"Lãnh đạo xử lý yêu cầu {req_id}: {decision_status} - {payload.comment}"
    )

    return SystemAdminRequestResponse(
        ma_yeu_cau=req["mayeucau"],
        loai_yeu_cau=req["loaiyeucau"],
        ma_nv_yeu_cau=req.get("manvyeucau"),
        ma_nv_phe_duyet=current_user.ma_nv,
        pham_vi_yeu_cau=req_scope,
        noi_dung_yeu_cau=req_content,
        trang_thai=decision_status,
        ly_do_tu_choi=payload.comment if decision_status == "REJECTED" else None
    )


def list_admin_requests(status_filter: Optional[str] = None) -> List[SystemAdminRequestResponse]:
    """Danh sách yêu cầu kỹ thuật."""
    rows = admin_repo.get_admin_requests(status=status_filter)
    return [
        SystemAdminRequestResponse(
            ma_yeu_cau=r["mayeucau"],
            loai_yeu_cau=r["loaiyeucau"],
            ma_nv_yeu_cau=r.get("manvyeucau"),
            ma_nv_phe_duyet=r.get("manvpheduyet"),
            pham_vi_yeu_cau=r.get("phamviyeucau", "BRANCH"),
            noi_dung_yeu_cau=r.get("noidungyeucau") or {},
            trang_thai=r.get("trangthai", "PENDING"),
            ly_do_tu_choi=r.get("lydotuchoi"),
            ngay_tao=r.get("ngaytao"),
            ngay_phe_duyet=r.get("ngaypheduyet")
        ) for r in rows
    ]

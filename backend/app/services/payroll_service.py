from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status

from app.core.db_router import get_write_pool, SITE_HN
from app.schemas.auth import CurrentUser
from app.schemas.payroll import PayrollUpdateRequest, PayrollItem, PayrollUpdateResponseData, SalarySlipResponse
import app.repositories.payroll_repo as payroll_repo
import app.repositories.employee_repo as employee_repo
import app.repositories.health_repo as health_repo


def get_payroll_list(
    current_user: CurrentUser,
    month: Optional[int] = None,
    year: Optional[int] = None,
    branch: Optional[str] = None
) -> List[PayrollItem]:
    """
    Tra cứu bảng lương với phân quyền và PII Masking:
    - Chặn Quản trị Kỹ thuật (SYSTEM_OPERATOR) truy cập.
    - Tổng giám đốc: Xem toàn bộ các chi nhánh.
    - Giám đốc chi nhánh: Chỉ xem được chi nhánh mình phụ trách.
    - Phòng Tài Vụ: Xem toàn bộ, nhưng PII của nhân viên các phòng khác bị che (Section 1.3 B).
    """
    # 0. Chặn SYSTEM_OPERATOR không có vai trò tài vụ
    if "SYSTEM_OPERATOR" in current_user.system_roles and not any(r in current_user.system_roles for r in ["FINANCE_SPECIALIST", "GROUP_EXECUTIVE", "BRANCH_DIRECTOR"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Quản trị kỹ thuật (System Operator) không có quyền truy cập bảng lương!"}
        )

    filter_branch = branch

    # 1. Kiểm tra thẩm quyền truy cập
    if current_user.role_name == "Tổng giám đốc" or current_user.role_id == 4 or "GROUP_EXECUTIVE" in current_user.system_roles:
        pass
    elif current_user.role_name in ["Giám đốc", "Giám đốc chi nhánh"] or current_user.role_id == 3 or "BRANCH_DIRECTOR" in current_user.system_roles:
        filter_branch = current_user.branch
    elif "Phòng Tài Vụ" in current_user.department_name or "FINANCE_SPECIALIST" in current_user.system_roles:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Bạn không có quyền truy cập bảng lương!"}
        )

    records = payroll_repo.get_payrolls(
        month=month,
        year=year,
        branch=filter_branch,
        site_key=SITE_HN
    )

    items: List[PayrollItem] = []
    is_finance_user = ("Phòng Tài Vụ" in current_user.department_name or "FINANCE_SPECIALIST" in current_user.system_roles)

    for r in records:
        ho_ten = r.get("hoten")
        sdt = r.get("sodienthoai")
        email = r.get("email")
        is_pii_masked = False

        # 2. PII Masking cho Phòng Tài Vụ:
        if is_finance_user and r.get("mapb") != current_user.department_id:
            ho_ten = "*** Bảo mật ***"
            sdt = "*** Bảo mật ***"
            email = "*** Bảo mật ***"
            is_pii_masked = True

        items.append(PayrollItem(
            ma_luong=r.get("maluong"),
            ma_nv=r.get("manv", ""),
            ho_ten=ho_ten,
            so_dien_thoai=sdt,
            email=email,
            ma_so_thue=r.get("masothue"),
            ten_phong_ban=r.get("tenphongban"),
            chi_nhanh=r.get("chinhanh"),
            thang=r.get("thang", 0),
            nam=r.get("nam", 0),
            luong_co_ban=float(r["luongcoban"]) if r.get("luongcoban") is not None else None,
            phu_cap=float(r["phucap"]) if r.get("phucap") is not None else None,
            thuong=float(r["thuong"]) if r.get("thuong") is not None else None,
            khau_tru=float(r["khautru"]) if r.get("khautru") is not None else None,
            luong_thuc_linh=float(r["luongthuclinh"]) if r.get("luongthuclinh") is not None else None,
            is_pii_masked=is_pii_masked,
            is_salary_masked=False
        ))

    return items


def update_payroll(
    ma_nv: str,
    payload: PayrollUpdateRequest,
    current_user: CurrentUser
) -> PayrollUpdateResponseData:
    """
    Cập nhật lương cho nhân sự:
    - Tổng giám đốc: Cập nhật bất kỳ nhân viên nào.
    - Giám đốc chi nhánh: Chỉ được cập nhật nhân viên cùng chi nhánh. Khác chi nhánh -> 403 Forbidden.
    """
    target_emp = employee_repo.get_employee_by_id(ma_nv, SITE_HN)
    if not target_emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Không tìm thấy nhân viên {ma_nv}"}
        )

    target_branch = target_emp.get("chinhanh", "HN")

    # Kiểm tra thẩm quyền điều chỉnh lương (Section 2.2)
    if current_user.role_name == "Tổng giám đốc" or current_user.role_id == 4 or "GROUP_EXECUTIVE" in current_user.system_roles:
        pass
    elif current_user.role_name in ["Giám đốc", "Giám đốc chi nhánh"] or current_user.role_id == 3 or "BRANCH_DIRECTOR" in current_user.system_roles:
        if target_branch != current_user.branch:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": "Bạn chỉ có quyền cập nhật lương cho nhân sự thuộc chi nhánh quản lý!"
                }
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Bạn không có quyền điều chỉnh lương nhân sự!"}
        )

    target_site = get_write_pool(target_branch)

    res = payroll_repo.upsert_payroll(
        ma_nv=ma_nv,
        branch_code=target_branch,
        month=payload.thang,
        year=payload.nam,
        luong_co_ban=payload.luong_co_ban,
        phu_cap=payload.phu_cap,
        thuong=payload.thuong,
        khau_tru=payload.khau_tru,
        site_key=target_site
    )

    # Ghi log kiểm toán
    health_repo.insert_audit_log(
        manv_thuc_hien=current_user.ma_nv,
        tennv_thuc_hien=current_user.full_name,
        thao_tac="CAP_NHAT_LUONG",
        tac_dong_len_nv=ma_nv,
        chi_tiet=f"Cập nhật lương {payload.thang}/{payload.nam}: CB={payload.luong_co_ban}, PC={payload.phu_cap}, T={payload.thuong}, KT={payload.khau_tru}",
        site_key=target_site
    )

    return PayrollUpdateResponseData(
        ma_luong=res.get("maluong", ""),
        ma_nv=res.get("manv", ma_nv),
        thang=res.get("thang", payload.thang),
        nam=res.get("nam", payload.nam),
        luong_co_ban=float(res.get("luongcoban", payload.luong_co_ban)),
        phu_cap=float(res.get("phucap", payload.phu_cap)),
        thuong=float(res.get("thuong", payload.thuong)),
        khau_tru=float(res.get("khautru", payload.khau_tru)),
        luong_thuc_linh=float(res.get("luongthuclinh", 0))
    )


def get_my_salary_slip(
    current_user: CurrentUser,
    month: Optional[int] = None,
    year: Optional[int] = None
) -> SalarySlipResponse:
    """Lấy phiếu lương cá nhân của nhân viên hiện tại."""
    slip = payroll_repo.get_salary_slip(
        ma_nv=current_user.ma_nv,
        month=month,
        year=year,
        site_key=SITE_HN
    )
    if not slip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Không tìm thấy dữ liệu phiếu lương cho kỳ này"}
        )

    return SalarySlipResponse(
        ma_nv=slip["manv"],
        ho_ten=slip.get("hoten", current_user.full_name),
        ten_phong_ban=slip.get("tenphongban", current_user.department_name),
        chuc_vu=slip.get("chucvu", ""),
        thang=slip["thang"],
        nam=slip["nam"],
        luong_co_ban=float(slip["luongcoban"]),
        phu_cap=float(slip["phucap"]),
        thuong=float(slip["thuong"]),
        khau_tru=float(slip["khautru"]),
        luong_thuc_linh=float(slip["luongthuclinh"])
    )

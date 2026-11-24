import json
from typing import Optional, List, Dict, Any, Tuple
from fastapi import HTTPException, status, UploadFile

from app.core.db_router import get_write_pool, SITE_HN
from app.core.security import hash_password
from app.core.minio_client import upload_file, delete_file, get_public_url
from app.schemas.auth import CurrentUser
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeItem, EmployeeListPagination, EmployeeDetailResponse
import app.repositories.employee_repo as employee_repo
import app.repositories.health_repo as health_repo


def apply_salary_masking(item: Dict[str, Any], current_user: CurrentUser) -> Tuple[Optional[float], bool]:
    """
    Quy tắc Data Masking cột Lương theo ma trận RBAC (Section 1.3 A):
    1. Tổng giám đốc: Xem đầy đủ lương tất cả nhân viên.
    2. Giám đốc chi nhánh: Xem đầy đủ lương nhân viên trong chi nhánh mình; nhân viên chi nhánh khác bị MASK.
    3. Phòng Tài vụ: Xem đầy đủ lương toàn bộ nhân viên.
    4. Trưởng phòng chuyên môn: Xem đầy đủ lương cấp dưới cùng phòng ban và chi nhánh.
    5. Mọi nhân viên (kể cả Nhân sự): Xem đầy đủ lương của CHÍNH MÌNH.
    6. Trường hợp còn lại: Masking -> None, is_masked = True.
    """
    raw_salary = item.get("luongthuclinh")
    if raw_salary is not None:
        try:
            raw_salary = float(raw_salary)
        except (ValueError, TypeError):
            pass

    emp_manv = item.get("manv")
    emp_branch = item.get("chinhanh")
    emp_mapb = item.get("mapb")

    # 1. Tổng giám đốc
    if current_user.role_name == "Tổng giám đốc" or current_user.role_id == 4 or "GROUP_EXECUTIVE" in current_user.system_roles:
        return raw_salary, False

    # 2. Giám đốc chi nhánh
    if current_user.role_name in ["Giám đốc", "Giám đốc chi nhánh"] or current_user.role_id == 3 or "BRANCH_DIRECTOR" in current_user.system_roles:
        if emp_branch == current_user.branch:
            return raw_salary, False
        return None, True

    # 3. Phòng Tài Vụ
    if "Phòng Tài Vụ" in current_user.department_name or "FINANCE_SPECIALIST" in current_user.system_roles:
        return raw_salary, False

    # 4. Trưởng phòng chuyên môn
    if (current_user.role_name == "Trưởng phòng" or current_user.role_id == 2 or "DEPT_MANAGER" in current_user.system_roles) and "Phòng Nhân Sự" not in current_user.department_name:
        if emp_mapb == current_user.department_id and emp_branch == current_user.branch:
            return raw_salary, False
        return None, True

    # 5. Chính bản thân nhân viên
    if emp_manv == current_user.ma_nv:
        return raw_salary, False

    # 6. Che giấu toàn bộ các trường hợp khác
    return None, True


def list_employees(
    current_user: CurrentUser,
    page: int = 1,
    page_size: int = 10,
    branch: Optional[str] = None,
    department_id: Optional[str] = None,
    search: Optional[str] = None,
    kpi_grade: Optional[str] = None
) -> EmployeeListPagination:
    """
    Lấy danh sách nhân sự có Row-level filtering và Data Masking theo Role.
    v_HoSoNhanSu_ToanDien luôn được truy vấn trên Coordinator site_hn.
    """
    filter_branch = branch
    filter_dept = department_id
    exclude_dept = None

    # Phân quyền phạm vi dòng (Row-level filtering):
    # - Giám đốc chi nhánh: Bị khóa cứng theo chi nhánh mình
    if current_user.role_name in ["Giám đốc", "Giám đốc chi nhánh"] or current_user.role_id == 3:
        filter_branch = current_user.branch

    # - Nhân viên phòng Nhân sự (Role 1): Xem các phòng khác, loại trừ chính phòng Nhân Sự
    elif ("Phòng Nhân Sự" in current_user.department_name or "HR_SPECIALIST" in current_user.system_roles) and current_user.role_id == 1:
        exclude_dept = current_user.department_name

    # - Trưởng phòng chuyên môn: Chỉ xem phòng mình và chi nhánh mình
    elif (current_user.role_id == 2 or "DEPT_MANAGER" in current_user.system_roles) and not any(r in current_user.system_roles for r in ["HR_SPECIALIST", "FINANCE_SPECIALIST", "GROUP_EXECUTIVE"]):
        filter_dept = current_user.department_id
        filter_branch = current_user.branch

    # - Nhân viên chuyên môn: Chỉ xem phòng mình và chi nhánh mình
    elif current_user.role_id == 1 and not any(r in current_user.system_roles for r in ["HR_SPECIALIST", "FINANCE_SPECIALIST", "GROUP_EXECUTIVE"]):
        filter_dept = current_user.department_id
        filter_branch = current_user.branch

    # Luôn truy vấn Global View trên SITE_HN (Coordinator Node)
    raw_items, total = employee_repo.get_employees(
        branch=filter_branch,
        department_id=filter_dept,
        search=search,
        kpi_grade=kpi_grade,
        exclude_department_name=exclude_dept,
        page=page,
        page_size=page_size,
        site_key=SITE_HN
    )

    items: List[EmployeeItem] = []
    for raw in raw_items:
        salary, is_masked = apply_salary_masking(raw, current_user)
        items.append(EmployeeItem(
            ma_nv=raw.get("manv", ""),
            ho_ten=raw.get("hoten"),
            phai=raw.get("phai"),
            ngay_sinh=raw.get("ngaysinh"),
            so_dien_thoai=raw.get("sodienthoai"),
            email=raw.get("email"),
            ma_so_thue=raw.get("masothue"),
            ten_phong_ban=raw.get("tenphongban"),
            chuc_vu=raw.get("chucvuhientai"),
            ten_vai_tro=raw.get("tenvaitro"),
            chi_nhanh=raw.get("chinhanh", ""),
            trang_thai=raw.get("trangthai", "DangLamViec"),
            ma_pb=raw.get("mapb"),
            ma_cv=raw.get("macv"),
            ma_vai_tro=raw.get("mavaitro"),
            kpi_q1=raw.get("xeploai_kpi_q1"),
            danh_gia_nhan_xet=raw.get("danhgia_nhanxet"),
            skills=raw.get("danhsachkynang") if isinstance(raw.get("danhsachkynang"), list) else None,
            url_avatar=raw.get("url_anhdaidien"),
            url_cv=raw.get("url_banscan_cv"),
            luong_thuc_linh=salary,
            is_salary_masked=is_masked
        ))

    return EmployeeListPagination(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


def get_employee_detail(ma_nv: str, current_user: CurrentUser) -> EmployeeDetailResponse:
    """Lấy chi tiết 1 hồ sơ nhân sự từ Coordinator SITE_HN."""
    raw = employee_repo.get_employee_by_id(ma_nv, SITE_HN)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Không tìm thấy nhân viên {ma_nv}"}
        )

    salary, is_masked = apply_salary_masking(raw, current_user)
    dulieu_json = raw.get("dulieujson") or {}

    return EmployeeDetailResponse(
        ma_nv=raw["manv"],
        ho_ten=raw.get("hoten"),
        phai=raw.get("phai"),
        ngay_sinh=raw.get("ngaysinh"),
        so_dien_thoai=raw.get("sodienthoai"),
        email=raw.get("email"),
        ma_so_thue=raw.get("masothue"),
        ten_phong_ban=raw.get("tenphongban"),
        chuc_vu=raw.get("chucvuhientai"),
        ten_vai_tro=raw.get("tenvaitro"),
        chi_nhanh=raw.get("chinhanh", ""),
        trang_thai=raw.get("trangthai", "DangLamViec"),
        ma_pb=raw.get("mapb"),
        ma_cv=raw.get("macv"),
        ma_vai_tro=raw.get("mavaitro"),
        kpi_q1=dulieu_json.get("performance_reviews", [{}])[0].get("final_grade") if dulieu_json.get("performance_reviews") else None,
        danh_gia_nhan_xet=dulieu_json.get("performance_reviews", [{}])[0].get("feedback") if dulieu_json.get("performance_reviews") else None,
        skills=dulieu_json.get("skills", []),
        performance_reviews=dulieu_json.get("performance_reviews", []),
        url_avatar=raw.get("url_anhdaidien"),
        url_cv=raw.get("url_banscan_cv"),
        luong_thuc_linh=salary,
        is_salary_masked=is_masked,
        projects=raw.get("projects", [])
    )


def create_employee(
    emp_in: EmployeeCreate,
    avatar_file: Optional[UploadFile],
    cv_file: Optional[UploadFile],
    current_user: CurrentUser
) -> Dict[str, Any]:
    """
    Tạo mới hồ sơ nhân sự với Multi-Model Compensating Transaction.
    Chặn Quản trị Kỹ thuật (SYSTEM_OPERATOR) can thiệp vào hồ sơ.
    """
    # 0. Chặn SYSTEM_OPERATOR
    if "SYSTEM_OPERATOR" in current_user.system_roles and not ("HR_SPECIALIST" in current_user.system_roles or "GROUP_EXECUTIVE" in current_user.system_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Quản trị kỹ thuật (System Operator) không có quyền can thiệp vào hồ sơ nhân sự!"}
        )

    target_site = get_write_pool(emp_in.ma_cn)

    # 1. Kiểm tra trùng lặp trên Coordinator SITE_HN
    err_msg = employee_repo.check_employee_exists(emp_in.ma_nv, emp_in.email, emp_in.username, SITE_HN)
    if err_msg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"code": "DUPLICATE_ERROR", "message": err_msg})

    # 2. Kiểm tra quy tắc 01 Trưởng phòng (Single Manager Rule 2.1)
    if emp_in.ma_vai_tro == 2 or emp_in.ma_cv == "TP":
        if employee_repo.check_department_manager_exists(emp_in.ma_pb, target_site):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "DEPARTMENT_MANAGER_EXISTS", "message": "Phòng ban này đã có Trưởng phòng!"}
            )

    uploaded_keys: List[str] = []

    try:
        avatar_key = None
        cv_pdf_key = None

        # 3. Upload file lên MinIO
        if avatar_file and avatar_file.filename:
            avatar_bytes = avatar_file.file.read()
            avatar_key = upload_file(
                file_bytes=avatar_bytes,
                original_filename=avatar_file.filename,
                folder="avatars",
                content_type=avatar_file.content_type or "image/jpeg"
            )
            uploaded_keys.append(avatar_key)

        if cv_file and cv_file.filename:
            cv_bytes = cv_file.file.read()
            cv_pdf_key = upload_file(
                file_bytes=cv_bytes,
                original_filename=cv_file.filename,
                folder="cv_docs",
                content_type=cv_file.content_type or "application/pdf"
            )
            uploaded_keys.append(cv_pdf_key)

        # 4. Đóng gói dữ liệu JSONB
        dulieu_json = {
            "skills": [s.model_dump() for s in emp_in.skills] if emp_in.skills else [],
            "performance_reviews": [p.model_dump() for p in emp_in.performance_reviews] if emp_in.performance_reviews else [],
            "avatar_key": avatar_key,
            "cv_pdf_key": cv_pdf_key
        }

        # 5. Ghi Shard CSDL
        db_payload = {
            "ma_nv": emp_in.ma_nv,
            "ho_ten": emp_in.ho_ten,
            "phai": emp_in.phai,
            "ngay_sinh": emp_in.ngay_sinh,
            "so_dien_thoai": emp_in.so_dien_thoai,
            "email": emp_in.email,
            "ma_so_thue": emp_in.ma_so_thue,
            "ma_pb": emp_in.ma_pb,
            "ma_cv": emp_in.ma_cv,
            "ma_vai_tro": emp_in.ma_vai_tro,
            "ma_cn": emp_in.ma_cn.upper().strip(),
            "trang_thai": "DangLamViec",
            "username": emp_in.username,
            "password_hash": hash_password(emp_in.password),
            "dulieu_json": dulieu_json
        }

        employee_repo.insert_employee(db_payload, target_site)

        # 6. Ghi Audit Log
        health_repo.insert_audit_log(
            manv_thuc_hien=current_user.ma_nv,
            tennv_thuc_hien=current_user.full_name,
            thao_tac="THEM_NHAN_VIEN",
            tac_dong_len_nv=emp_in.ma_nv,
            chi_tiet=f"Thêm nhân viên mới {emp_in.ho_ten} ({emp_in.ma_nv}) tại chi nhánh {emp_in.ma_cn}",
            site_key=target_site
        )

        return {
            "ma_nv": emp_in.ma_nv,
            "ho_ten": emp_in.ho_ten,
            "email": emp_in.email,
            "chi_nhanh": emp_in.ma_cn,
            "avatar_url": get_public_url(avatar_key),
            "cv_url": get_public_url(cv_pdf_key)
        }

    except Exception as e:
        for key in uploaded_keys:
            delete_file(key)
        raise e


def update_employee(
    ma_nv: str,
    emp_update: EmployeeUpdate,
    avatar_file: Optional[UploadFile],
    cv_file: Optional[UploadFile],
    current_user: CurrentUser
) -> Dict[str, Any]:
    """
    Cập nhật thông tin hồ sơ nhân sự có kiểm soát Manager Equality Rule.
    """
    existing = employee_repo.get_employee_by_id(ma_nv, SITE_HN)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": f"Không tìm thấy nhân viên {ma_nv}"}
        )

    branch = existing.get("chinhanh", "HN")
    target_site = get_write_pool(branch)

    # 1. KIỂM TRA QUY TẮC BÌNH ĐẲNG TRƯỞNG PHÒNG (MANAGER EQUALITY RULE)
    is_editor_manager = (
        current_user.role_id == 2 or 
        current_user.role_name == "Trưởng phòng" or 
        getattr(current_user, "position", "") == "TP" or 
        "DEPT_MANAGER" in getattr(current_user, "system_roles", [])
    )
    is_editor_ceo = (
        current_user.role_id == 4 or 
        current_user.role_name == "Tổng giám đốc" or 
        "GROUP_EXECUTIVE" in getattr(current_user, "system_roles", [])
    )

    target_role = existing.get("mavaitro")
    target_cv = existing.get("macv")
    is_target_manager = (target_role == 2 or target_cv == "TP")

    if is_editor_manager and not is_editor_ceo:
        # Trưởng phòng không được phép sửa Trưởng phòng khác
        if is_target_manager and existing["manv"] != current_user.ma_nv:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Quy tắc bình đẳng: Trưởng phòng không được phép sửa đổi hồ sơ của Trưởng phòng khác!"}
            )
        # Trưởng phòng không được tự ý sửa chức vụ thành TP trực tiếp
        if emp_update.ma_cv == "TP" and target_cv != "TP":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "Thay đổi chức vụ cấp Trưởng phòng phải thông qua quy trình Đề xuất Bổ nhiệm và được Lãnh đạo phê duyệt!"}
            )

    new_role = emp_update.ma_vai_tro if emp_update.ma_vai_tro is not None else existing.get("mavaitro")
    new_cv = emp_update.ma_cv if emp_update.ma_cv is not None else existing.get("macv")
    new_pb = emp_update.ma_pb if emp_update.ma_pb is not None else existing.get("mapb")

    if new_role == 2 or new_cv == "TP":
        if employee_repo.check_department_manager_exists(new_pb, target_site, exclude_ma_nv=ma_nv):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "DEPARTMENT_MANAGER_EXISTS", "message": "Phòng ban này đã có Trưởng phòng!"}
            )

    uploaded_keys: List[str] = []
    try:
        existing_json = existing.get("dulieujson") or {}
        avatar_key = existing_json.get("avatar_key")
        cv_pdf_key = existing_json.get("cv_pdf_key")

        if avatar_file and avatar_file.filename:
            avatar_bytes = avatar_file.file.read()
            new_avatar = upload_file(
                file_bytes=avatar_bytes,
                original_filename=avatar_file.filename,
                folder="avatars",
                content_type=avatar_file.content_type or "image/jpeg"
            )
            uploaded_keys.append(new_avatar)
            avatar_key = new_avatar

        if cv_file and cv_file.filename:
            cv_bytes = cv_file.file.read()
            new_cv_key = upload_file(
                file_bytes=cv_bytes,
                original_filename=cv_file.filename,
                folder="cv_docs",
                content_type=cv_file.content_type or "application/pdf"
            )
            uploaded_keys.append(new_cv_key)
            cv_pdf_key = new_cv_key

        dulieu_json = existing_json.copy()
        if emp_update.skills is not None:
            dulieu_json["skills"] = [s.model_dump() for s in emp_update.skills]
        if emp_update.performance_reviews is not None:
            dulieu_json["performance_reviews"] = [p.model_dump() for p in emp_update.performance_reviews]
        dulieu_json["avatar_key"] = avatar_key
        dulieu_json["cv_pdf_key"] = cv_pdf_key

        update_payload: Dict[str, Any] = {}
        if emp_update.ho_ten is not None: update_payload["ho_ten"] = emp_update.ho_ten
        if emp_update.phai is not None: update_payload["phai"] = emp_update.phai
        if emp_update.ngay_sinh is not None: update_payload["ngay_sinh"] = emp_update.ngay_sinh
        if emp_update.so_dien_thoai is not None: update_payload["so_dien_thoai"] = emp_update.so_dien_thoai
        if emp_update.email is not None: update_payload["email"] = emp_update.email
        if emp_update.ma_so_thue is not None: update_payload["ma_so_thue"] = emp_update.ma_so_thue
        if emp_update.ma_pb is not None: update_payload["ma_pb"] = emp_update.ma_pb
        if emp_update.ma_cv is not None: update_payload["ma_cv"] = emp_update.ma_cv
        if emp_update.ma_vai_tro is not None: update_payload["ma_vai_tro"] = emp_update.ma_vai_tro
        if emp_update.trang_thai is not None: update_payload["trang_thai"] = emp_update.trang_thai
        if emp_update.password: update_payload["password_hash"] = hash_password(emp_update.password)
        update_payload["dulieu_json"] = dulieu_json

        employee_repo.update_employee(ma_nv, update_payload, target_site)

        health_repo.insert_audit_log(
            manv_thuc_hien=current_user.ma_nv,
            tennv_thuc_hien=current_user.full_name,
            thao_tac="CAP_NHAT_NHAN_VIEN",
            tac_dong_len_nv=ma_nv,
            chi_tiet=f"Cập nhật hồ sơ nhân viên {ma_nv}",
            site_key=target_site
        )

        return {"ma_nv": ma_nv, "message": "Cập nhật hồ sơ nhân sự thành công"}

    except Exception as e:
        for k in uploaded_keys:
            delete_file(k)
        raise e


def get_colleagues(current_user: CurrentUser) -> List[Dict[str, Any]]:
    """Lấy danh bạ đồng nghiệp cùng phòng ban (Lương bị che giấu 100%)."""
    return employee_repo.get_colleagues(
        ma_pb=current_user.department_id,
        branch=current_user.branch,
        site_key=SITE_HN
    )

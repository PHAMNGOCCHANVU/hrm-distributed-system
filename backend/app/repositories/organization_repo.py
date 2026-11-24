from typing import Dict, Any, List, Optional
from psycopg2.extras import RealDictCursor
from app.core.db_router import get_db_connection, SITE_HN


def get_organization_tree() -> Dict[str, Any]:
    """
    Truy vấn và xây dựng cây cơ cấu tổ chức phân biệt rõ 2 bộ máy tại Hà Nội:
    - Corporate HQ (Bộ máy Tập đoàn - LoaiDonVi = 'TAP_DOAN')
    - 3 Chi nhánh: HN, DN, HCM (LoaiDonVi = 'CHI_NHANH')
    """
    with get_db_connection(SITE_HN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # 1. Lấy toàn bộ danh sách phòng ban từ v_PhongBan
            cur.execute("""
                SELECT MaPB, TenPB, MaCN, COALESCE(LoaiDonVi, 'CHI_NHANH') as LoaiDonVi, MaDonViCha, ThuTuSapXep
                FROM v_PhongBan
                ORDER BY ThuTuSapXep ASC, MaPB ASC;
            """)
            depts = cur.fetchall()

            # 2. Lấy danh sách Trưởng phòng cho từng phòng ban
            cur.execute("""
                SELECT MaPB, HoTen, MaNV
                FROM v_NhanVien
                WHERE MaCV = 'TP' OR MaVaiTro = 2;
            """)
            managers = {m["mapb"]: m["hoten"] for m in cur.fetchall()}

            # 3. Lấy thông tin Lãnh đạo cấp Tập đoàn (CEO)
            cur.execute("""
                SELECT MaNV, HoTen, ChucVuHienTai
                FROM v_HoSoNhanSu_ToanDien
                WHERE MaCV IN ('CEO', 'TGD') OR MaVaiTro = 4
                LIMIT 1;
            """)
            ceo_row = cur.fetchone()
            ceo_leader = {
                "position": "CEO - Tổng giám đốc",
                "full_name": ceo_row["hoten"] if ceo_row else "Lưu Quang Giáp",
                "ma_nv": ceo_row["manv"] if ceo_row else "NV_HQ_CEO"
            }

            # 4. Lấy thông tin Giám đốc cho từng Chi nhánh
            cur.execute("""
                SELECT ChiNhanh, MaNV, HoTen
                FROM v_HoSoNhanSu_ToanDien
                WHERE MaCV IN ('GD_CN', 'GD') OR MaVaiTro = 3;
            """)
            directors = {d["chinhanh"]: {"full_name": d["hoten"], "ma_nv": d["manv"]} for d in cur.fetchall()}

    # Phân loại phòng ban
    hq_departments = []
    branch_map = {
        "HN": {"branch_code": "HN", "branch_name": "Chi nhánh Hà Nội", "director": directors.get("HN", {"full_name": "Trần Giám Đốc HN", "ma_nv": "NV_HN_DIR_01"}), "departments": []},
        "DN": {"branch_code": "DN", "branch_name": "Chi nhánh Đà Nẵng", "director": directors.get("DN", {"full_name": "Nguyễn Anh Tuấn", "ma_nv": "NV_DN_DIR_02"}), "departments": []},
        "HCM": {"branch_code": "HCM", "branch_name": "Chi nhánh TP.HCM", "director": directors.get("HCM", {"full_name": "Huỳnh Quốc Bảo", "ma_nv": "NV_HCM_DIR_01"}), "departments": []},
    }

    seen_hq_codes = set()
    seen_branch_codes = {"HN": set(), "DN": set(), "HCM": set()}

    for d in depts:
        pb_code = d["mapb"]
        pb_name = d["tenpb"]
        macn = d["macn"]
        loai = d["loaidonvi"]
        manager_name = managers.get(pb_code)

        item = {
            "code": pb_code,
            "name": pb_name,
            "manager": manager_name
        }

        # Phân biệt bộ máy Tập đoàn vs Chi nhánh
        if loai == "TAP_DOAN" or "HQ" in pb_code:
            if pb_code not in seen_hq_codes:
                seen_hq_codes.add(pb_code)
                hq_departments.append(item)
        else:
            if macn in branch_map and pb_code not in seen_branch_codes[macn]:
                seen_branch_codes[macn].add(pb_code)
                branch_map[macn]["departments"].append(item)

    return {
        "corporate_hq": {
            "unit_name": "Bộ Máy Điều Hành Cấp Tập Đoàn (Trụ sở Hà Nội)",
            "leader": ceo_leader,
            "departments": hq_departments
        },
        "branches": [
            branch_map["HN"],
            branch_map["DN"],
            branch_map["HCM"]
        ]
    }


def get_headcount_report_data(scope: str, branch: Optional[str] = None) -> Dict[str, Any]:
    """
    Thống kê số lượng nhân sự và tổng quỹ lương theo từng đơn vị tổ chức.
    """
    with get_db_connection(SITE_HN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    nv.MaNV, 
                    nv.MaCN, 
                    COALESCE(pb.LoaiDonVi, 'CHI_NHANH') AS LoaiDonVi,
                    COALESCE(l.LuongThucLinh, l.LuongCoBan, 15000000) AS Luong
                FROM v_NhanVien nv
                JOIN v_PhongBan pb ON nv.MaPB = pb.MaPB
                LEFT JOIN v_Luong l ON nv.MaNV = l.MaNV AND l.Thang = 3 AND l.Nam = 2026;
            """)
            rows = cur.fetchall()

    breakdown = {
        "TAP_DOAN": {"unit_name": "Bộ máy Tập đoàn", "count": 0, "salary_fund": 0.0},
        "HN": {"unit_name": "Chi nhánh Hà Nội", "count": 0, "salary_fund": 0.0},
        "DN": {"unit_name": "Chi nhánh Đà Nẵng", "count": 0, "salary_fund": 0.0},
        "HCM": {"unit_name": "Chi nhánh TP.HCM", "count": 0, "salary_fund": 0.0},
    }

    total_emp = 0
    for r in rows:
        macn = r["macn"]
        loai = r["loaidonvi"]
        salary = float(r["luong"])

        if loai == "TAP_DOAN":
            breakdown["TAP_DOAN"]["count"] += 1
            breakdown["TAP_DOAN"]["salary_fund"] += salary
        elif macn in breakdown:
            breakdown[macn]["count"] += 1
            breakdown[macn]["salary_fund"] += salary
        total_emp += 1

    if scope == "BRANCH" and branch in breakdown:
        return {
            "scope": "BRANCH",
            "total_employees": breakdown[branch]["count"],
            "breakdown_by_unit": [breakdown[branch]]
        }

    return {
        "scope": "GLOBAL",
        "total_employees": total_emp,
        "breakdown_by_unit": list(breakdown.values())
    }

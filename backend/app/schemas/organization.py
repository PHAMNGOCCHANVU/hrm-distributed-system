from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class OrgLeader(BaseModel):
    position: str = Field(..., description="Chức vụ lãnh đạo")
    full_name: str = Field(..., description="Họ tên")
    ma_nv: str = Field(..., description="Mã nhân viên")


class OrgDepartmentItem(BaseModel):
    code: str = Field(..., description="Mã phòng ban")
    name: str = Field(..., description="Tên phòng ban")
    manager: Optional[str] = Field(None, description="Trưởng phòng")


class CorporateHQData(BaseModel):
    unit_name: str = "Bộ Máy Điều Hành Cấp Tập Đoàn (Trụ sở Hà Nội)"
    leader: Optional[OrgLeader] = None
    departments: List[OrgDepartmentItem] = []


class BranchDirectorInfo(BaseModel):
    full_name: str
    ma_nv: str


class BranchOrgData(BaseModel):
    branch_code: str
    branch_name: str
    director: Optional[BranchDirectorInfo] = None
    departments: List[OrgDepartmentItem] = []


class OrgTreeData(BaseModel):
    corporate_hq: CorporateHQData
    branches: List[BranchOrgData]


class HeadcountUnitBreakdown(BaseModel):
    unit_name: str
    count: int
    salary_fund: float


class HeadcountReportData(BaseModel):
    scope: str
    total_employees: int
    breakdown_by_unit: List[HeadcountUnitBreakdown]

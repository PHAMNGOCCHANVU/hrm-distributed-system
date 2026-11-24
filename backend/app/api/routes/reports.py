from fastapi import APIRouter, Depends

from app.schemas.base import ApiResponse
from app.schemas.auth import CurrentUser
from app.schemas.organization import HeadcountReportData
from app.api.deps import get_current_user
import app.services.organization_service as org_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/headcount", response_model=ApiResponse[HeadcountReportData])
def get_headcount_report(current_user: CurrentUser = Depends(get_current_user)):
    """
    Báo cáo tổng hợp số lượng nhân sự và ngân sách lương phân cấp theo Persona.
    - CEO: Toàn quốc (Bộ máy Tập đoàn, Chi nhánh HN, ĐN, HCM).
    - Giám đốc chi nhánh: Thống kê nội bộ chi nhánh phụ trách.
    """
    report = org_service.get_headcount_report(current_user)
    return ApiResponse(
        success=True,
        data=report,
        message="Lấy báo cáo nhân sự thành công"
    )

from fastapi import APIRouter, Depends

from app.schemas.base import ApiResponse
from app.schemas.auth import CurrentUser
from app.schemas.organization import OrgTreeData
from app.api.deps import get_current_user
import app.services.organization_service as org_service

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/tree", response_model=ApiResponse[OrgTreeData])
def get_organization_tree(current_user: CurrentUser = Depends(get_current_user)):
    """
    Lấy sơ đồ cây cơ cấu tổ chức Tập đoàn:
    - Phân biệt rõ Bộ máy Tập đoàn (Corporate HQ) và Chi nhánh Hà Nội (Branch HN).
    - Danh sách các phòng ban và lãnh đạo tương ứng.
    """
    tree = org_service.get_organization_tree()
    return ApiResponse(
        success=True,
        data=tree,
        message="Lấy cây cơ cấu tổ chức tập đoàn thành công"
    )

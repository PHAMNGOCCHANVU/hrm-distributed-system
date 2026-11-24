from typing import Dict, Any, Optional
from app.schemas.auth import CurrentUser
from app.schemas.organization import OrgTreeData, HeadcountReportData
import app.repositories.organization_repo as org_repo


def get_organization_tree() -> OrgTreeData:
    """Xây dựng sơ đồ cây tổ chức tập đoàn phân tách 2 bộ máy tại HN và các chi nhánh."""
    raw_tree = org_repo.get_organization_tree()
    return OrgTreeData.model_validate(raw_tree)


def get_headcount_report(current_user: CurrentUser) -> HeadcountReportData:
    """Báo cáo thống kê nhân sự và quỹ lương theo phạm vi dữ liệu của người dùng."""
    scope = current_user.scope
    branch = current_user.branch if scope == "BRANCH" else None
    data = org_repo.get_headcount_report_data(scope=scope, branch=branch)
    return HeadcountReportData.model_validate(data)

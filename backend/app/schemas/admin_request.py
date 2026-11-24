from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class SystemAdminRequestCreate(BaseModel):
    loai_yeu_cau: str = Field(..., description="Loại yêu cầu kỹ thuật (CAP_QUYEN_OPERATOR, KHOI_PHUC_NODE, BAO_TRI_HE_THONG, XU_LY_SU_CO)")
    pham_vi: str = Field(..., description="Phạm vi: GLOBAL hoặc BRANCH")
    chi_nhanh: Optional[str] = Field(None, description="Chi nhánh áp dụng (nếu pham_vi=BRANCH)")
    ly_do: str = Field(..., description="Lý do yêu cầu")
    thong_so_ky_thuat: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Các thông số kỹ thuật đính kèm")


class SystemAdminApproveRequest(BaseModel):
    decision: str = Field(..., description="APPROVED hoặc REJECTED")
    comment: Optional[str] = Field(None, description="Ý kiến phê duyệt của Lãnh đạo")


class SystemAdminRequestResponse(BaseModel):
    ma_yeu_cau: str
    loai_yeu_cau: str
    ma_nv_yeu_cau: Optional[str] = None
    ma_nv_phe_duyet: Optional[str] = None
    pham_vi_yeu_cau: str
    noi_dung_yeu_cau: Dict[str, Any] = {}
    trang_thai: str = "PENDING"
    ly_do_tu_choi: Optional[str] = None
    ngay_tao: Optional[datetime] = None
    ngay_phe_duyet: Optional[datetime] = None

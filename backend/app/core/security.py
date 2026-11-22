import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import PyJWTError

from app.core.config import settings


def hash_password(raw_password: str) -> str:
    """
    Băm mật khẩu bằng thuật toán SHA-256 sinh chuỗi Hex 64 ký tự.
    Đồng nhất với digest(..., 'sha256') của CSDL PostgreSQL và dự án gốc.
    """
    if not raw_password:
        return ""
    return hashlib.sha256(raw_password.encode("utf-8")).hexdigest()


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """
    Kiểm tra mật khẩu thô và mật khẩu đã băm.
    """
    if not raw_password or not hashed_password:
        return False
    return hash_password(raw_password).lower() == hashed_password.lower()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT Access Token mã hóa thông tin người dùng:
    { sub, ma_nv, ho_ten, role_id, role_name, department_id, department_name, branch, scope, exp }
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Giải mã và kiểm tra tính hợp lệ của JWT Access Token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except PyJWTError:
        return None

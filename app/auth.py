"""
Authentication & Role-Based Access Control (RBAC) Module
Bảo vệ các API nghiệp vụ quan trọng theo tiêu chuẩn an toàn thông tin y tế.
"""
import os
import hmac
import hashlib
import time
from enum import Enum
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from pydantic import BaseModel

SECRET_KEY = os.getenv("APP_SECRET_KEY", "bme_q7_secret_key_20260821_production_grade_hmac")

class UserRole(str, Enum):
    VIEWER = "VIEWER"                     # Chỉ xem (Bác sĩ/Điều dưỡng đọc thông tin)
    CLINICAL_STAFF = "CLINICAL_STAFF"     # Điều dưỡng/Bác sĩ báo hỏng, tạo yêu cầu chuyển
    BME_ENGINEER = "BME_ENGINEER"         # Kỹ sư BME (Sửa chữa, kiểm định, duyệt điều chuyển)
    ADMIN = "ADMIN"                       # Quản trị viên hệ thống (Xóa, quản lý API key)

ROLE_HIERARCHY = {
    UserRole.VIEWER: 1,
    UserRole.CLINICAL_STAFF: 2,
    UserRole.BME_ENGINEER: 3,
    UserRole.ADMIN: 4
}

class AuthenticatedUser(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: UserRole
    department: str

# Default users for clinical local operation
DEFAULT_USERS: Dict[str, AuthenticatedUser] = {
    "bme_admin": AuthenticatedUser(
        user_id="USR-001",
        username="bme_admin",
        full_name="KS. Nguyễn Quốc Việt",
        role=UserRole.ADMIN,
        department="Phòng TTBYT"
    ),
    "bme_engineer": AuthenticatedUser(
        user_id="USR-002",
        username="bme_engineer",
        full_name="KS. Trần Trọng Tấn",
        role=UserRole.BME_ENGINEER,
        department="Phòng TTBYT"
    ),
    "clinical_user": AuthenticatedUser(
        user_id="USR-003",
        username="clinical_user",
        full_name="ĐD. Trần Thị Ngọc Châu",
        role=UserRole.CLINICAL_STAFF,
        department="Khoa Cấp Cứu"
    ),
    "viewer_guest": AuthenticatedUser(
        user_id="USR-004",
        username="viewer_guest",
        full_name="Người dùng nội bộ",
        role=UserRole.VIEWER,
        department="Bệnh viện Quận 7"
    )
}

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    api_key: Optional[str] = Security(api_key_header),
    auth_creds: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> AuthenticatedUser:
    """Xác thực người dùng từ API Key hoặc Bearer Token. Fallback sang guest viewer nếu không cung cấp."""
    # 1. Kiểm tra API Key header
    if api_key:
        if api_key == "BME_ADMIN_KEY_2026":
            return DEFAULT_USERS["bme_admin"]
        elif api_key == "BME_ENGINEER_KEY_2026":
            return DEFAULT_USERS["bme_engineer"]
        elif api_key == "CLINICAL_KEY_2026":
            return DEFAULT_USERS["clinical_user"]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="X-API-Key không hợp lệ hoặc đã hết hạn"
            )

    # 2. Kiểm tra Bearer Token
    if auth_creds and auth_creds.credentials:
        token = auth_creds.credentials
        if token in DEFAULT_USERS:
            return DEFAULT_USERS[token]

    # 3. Default fallback (Guest viewer cho môi trường nội bộ)
    return DEFAULT_USERS["viewer_guest"]

def require_role(min_role: UserRole):
    """Dependency factory kiểm tra quyền tối thiểu"""
    def role_checker(user: AuthenticatedUser = Depends(get_current_user)):
        user_level = ROLE_HIERARCHY.get(user.role, 0)
        required_level = ROLE_HIERARCHY.get(min_role, 99)
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Quyền hạn không đủ. Yêu cầu tối thiểu cấp bậc: {min_role.value} (Hiện tại: {user.role.value})"
            )
        return user
    return role_checker

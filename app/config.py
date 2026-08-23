"""
Cấu hình vận hành tập trung (đọc từ biến môi trường).

Mục tiêu: cho phép siết bảo mật ở môi trường sản xuất mà không phá vỡ
môi trường demo/nội bộ hiện tại (mặc định an toàn nhưng tương thích ngược).
"""
from __future__ import annotations

import os
from functools import lru_cache


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    """Thiết lập runtime, đọc một lần khi khởi động."""

    def __init__(self) -> None:
        self.environment: str = os.getenv("ENVIRONMENT", "development").strip().lower()

        # CORS: mặc định KHÔNG mở '*' + credentials cùng lúc.
        # - Nếu ALLOWED_ORIGINS được đặt -> chỉ cho phép các origin đó (kèm credentials).
        # - Nếu không đặt và là production -> mặc định same-origin (rỗng, chặn cross-origin).
        # - Nếu không đặt và là development -> cho phép '*' nhưng TẮT credentials (an toàn theo spec).
        self.allowed_origins: list[str] = _split_csv(os.getenv("ALLOWED_ORIGINS"))

        # Bật thực thi RBAC cho các endpoint nhạy cảm (keys/ocr/delete...).
        # Mặc định TẮT để giữ nguyên hành vi demo (UI chưa có luồng đăng nhập).
        self.enforce_rbac: bool = _as_bool(os.getenv("HTM_ENFORCE_RBAC"), default=False)

        # Bật security headers (CSP nhẹ, nosniff, referrer, frame-ancestors).
        self.security_headers: bool = _as_bool(
            os.getenv("HTM_SECURITY_HEADERS"), default=True
        )

    @property
    def is_production(self) -> bool:
        return self.environment in ("production", "prod")

    def cors_config(self) -> dict:
        """Trả về tham số CORSMiddleware an toàn."""
        if self.allowed_origins:
            return {
                "allow_origins": self.allowed_origins,
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            }
        if self.is_production:
            # Không cấu hình origin ở prod -> chặn cross-origin (chỉ same-origin).
            return {
                "allow_origins": [],
                "allow_credentials": False,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            }
        # Development: cho phép mọi origin nhưng KHÔNG kèm credentials (tránh lỗ hổng).
        return {
            "allow_origins": ["*"],
            "allow_credentials": False,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

"""Tests cho các bản vá bảo mật P0/P1: CORS, OCR fail-closed, path traversal, RBAC gated."""
import os

import pytest
from fastapi import HTTPException

os.environ.setdefault("MEDICAL_DEVICE_DOCUMENTS_ROOT", "/workspace/docs_storage")

from app.config import Settings
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


# ---------- CORS config ----------

def test_cors_dev_no_credentials_with_wildcard():
    s = Settings.__new__(Settings)
    s.environment = "development"
    s.allowed_origins = []
    cfg = s.cors_config()
    assert cfg["allow_origins"] == ["*"]
    assert cfg["allow_credentials"] is False  # không bao giờ '*' + credentials


def test_cors_prod_blocks_cross_origin_by_default():
    s = Settings.__new__(Settings)
    s.environment = "production"
    s.allowed_origins = []
    cfg = s.cors_config()
    assert cfg["allow_origins"] == []
    assert cfg["allow_credentials"] is False


def test_cors_explicit_origins_allow_credentials():
    s = Settings.__new__(Settings)
    s.environment = "production"
    s.allowed_origins = ["https://htm.bvq7.local"]
    cfg = s.cors_config()
    assert cfg["allow_origins"] == ["https://htm.bvq7.local"]
    assert cfg["allow_credentials"] is True


# ---------- OCR fail-closed ----------

def test_ocr_process_no_fabricated_clinical_data():
    """OCR không được trả dữ liệu lâm sàng giả khi provider không khả dụng."""
    res = client.post("/api/ocr/process", json={"filename": "gcn_kiem_dinh_test.pdf"})
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is False
    assert body["status"] in ("OCR_UNAVAILABLE", "OCR_FAILED")
    assert body["extracted_fields"] is None
    assert body.get("verified") is False


def test_ocr_process_rejects_system_path():
    """Không nhận đường dẫn hệ thống tùy ý (chống đọc file & SSRF)."""
    res = client.post("/api/ocr/process", json={"file_path": "/etc/passwd"})
    assert res.status_code == 400


# ---------- /api/pdf/view path traversal ----------

def test_pdf_view_rejects_absolute_path():
    res = client.get("/api/pdf/view", params={"filename": "/etc/passwd"})
    assert res.status_code in (400, 404)


def test_pdf_view_rejects_traversal():
    res = client.get("/api/pdf/view", params={"filename": "../../etc/passwd"})
    assert res.status_code in (400, 404)


# ---------- RBAC gated enforcement ----------

def test_require_role_enforced_disabled_allows_guest(monkeypatch):
    import app.auth as auth_mod
    from app.config import Settings as _S

    disabled = _S.__new__(_S)
    disabled.enforce_rbac = False
    monkeypatch.setattr("app.config.get_settings", lambda: disabled)

    checker = auth_mod.require_role_enforced(auth_mod.UserRole.ADMIN)
    user = checker(api_key=None, auth_creds=None)  # guest fallback vẫn hoạt động
    assert user.role == auth_mod.UserRole.VIEWER


def test_require_role_enforced_enabled_blocks_guest(monkeypatch):
    import app.auth as auth_mod
    from app.config import Settings as _S

    enabled = _S.__new__(_S)
    enabled.enforce_rbac = True
    monkeypatch.setattr("app.config.get_settings", lambda: enabled)

    checker = auth_mod.require_role_enforced(auth_mod.UserRole.ADMIN)
    with pytest.raises(HTTPException) as exc:
        checker(api_key=None, auth_creds=None)
    assert exc.value.status_code == 401


def test_keys_config_default_open_backward_compatible():
    """Mặc định (chưa bật RBAC) giữ tương thích: /api/keys/config trả 200."""
    res = client.get("/api/keys/config")
    assert res.status_code == 200

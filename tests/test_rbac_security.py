"""
Security & RBAC Unit Tests
Verifies permission gates, role hierarchy, and unauthorized rejection
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth import UserRole, get_current_user, require_role

@pytest.fixture
def client():
    return TestClient(app)

def test_default_viewer_access(client):
    res = client.get("/api/devices")
    assert res.status_code == 200

def test_api_key_auth_bme_engineer(client):
    headers = {"X-API-Key": "BME_ENGINEER_KEY_2026"}
    res = client.get("/api/keys/config", headers=headers)
    assert res.status_code == 200

def test_invalid_api_key_rejected(client):
    headers = {"X-API-Key": "INVALID_KEY_12345"}
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 401
    assert "không hợp lệ" in res.json()["detail"]

def test_role_hierarchy_check():
    from app.auth import DEFAULT_USERS, ROLE_HIERARCHY
    admin = DEFAULT_USERS["bme_admin"]
    engineer = DEFAULT_USERS["bme_engineer"]
    viewer = DEFAULT_USERS["viewer_guest"]
    
    assert ROLE_HIERARCHY[admin.role] > ROLE_HIERARCHY[engineer.role]
    assert ROLE_HIERARCHY[engineer.role] > ROLE_HIERARCHY[viewer.role]

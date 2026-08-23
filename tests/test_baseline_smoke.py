"""
Baseline Smoke Test Suite
Kiểm tra sức khỏe tổng thể của CSDL và FastAPI routes.
"""
import sqlite3
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

DB_PATH = Path(__file__).parent.parent / "database" / "devices.db"

@pytest.fixture
def client():
    return TestClient(app)

def test_database_integrity():
    conn = sqlite3.connect(DB_PATH)
    integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
    conn.close()
    assert integrity == "ok", f"Integrity check failed: {integrity}"

def test_devices_count():
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM devices;").fetchone()[0]
    conn.close()
    assert count == 1211, f"Expected 1211 devices, got {count}"

def test_required_tables_exist():
    required_tables = [
        "devices", "facilities", "device_categories", "calibration_certificates",
        "maintenance_schedules", "pre_use_inspections", "device_transfers",
        "maintenance_logs", "notifications"
    ]
    conn = sqlite3.connect(DB_PATH)
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    conn.close()
    for t in required_tables:
        assert t in tables, f"Required table '{t}' is missing from database"

def test_api_devices_endpoint(client):
    res = client.get("/api/devices?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert "asset_tag" in data[0]
    assert data[0]["asset_tag"].startswith("BVQ7-TTB-")

def test_api_dashboard_summary(client):
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_devices"] == 1211
    assert "in_service_count" in data
    assert "compliance_rate" in data

def test_api_facilities(client):
    res = client.get("/api/facilities")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 20

if __name__ == "__main__":
    pytest.main(["-v", str(Path(__file__))])

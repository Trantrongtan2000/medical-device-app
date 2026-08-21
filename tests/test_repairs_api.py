"""
Tests for Repairs API (T2.2 Maintenance & Repair Workflow)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_list_repairs(client):
    res = client.get("/api/repairs")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_create_repair_valid(client):
    payload = {
        "device_id": 1,
        "repair_type": "REPAIR",
        "description": "Thay thế cảm biến áp lực SpO2 bị hỏng",
        "actual_cost": 1500000.0,
        "parts_used": "Sensor Module SpO2 Rev 2",
        "technician_name": "Kỹ sư Nguyễn Văn A",
        "reported_by": "Khoa Cấp Cứu",
        "start_date": "2026-08-21",
        "notes": "Kiểm tra sau sửa chữa đạt chuẩn"
    }
    res = client.post("/api/repairs", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "id" in data
    assert data["status"] == "created"
    repair_id = data["id"]

    # Test update repair
    update_payload = {
        "status": "COMPLETED",
        "end_date": "2026-08-21",
        "notes": "Đã bàn giao lại cho khoa sử dụng"
    }
    up_res = client.put(f"/api/repairs/{repair_id}", json=update_payload)
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "updated"

    # Verify updated record
    rep_list = client.get("/api/repairs").json()
    matched = [r for r in rep_list if r["id"] == repair_id]
    assert len(matched) == 1
    assert matched[0]["status"] == "COMPLETED"
    assert matched[0]["updated_at"] is not None
    assert matched[0]["start_date"] == "2026-08-21"

def test_create_repair_invalid_device(client):
    payload = {
        "device_id": 999999,
        "repair_type": "REPAIR",
        "description": "Test repair on non-existent device"
    }
    res = client.post("/api/repairs", json=payload)
    assert res.status_code == 404

def test_create_repair_invalid_type(client):
    payload = {
        "device_id": 1,
        "repair_type": "INVALID_TYPE",
        "description": "Test invalid repair type"
    }
    res = client.post("/api/repairs", json=payload)
    assert res.status_code == 422

def test_repairs_today_stats(client):
    res = client.get("/api/repairs/stats/today")
    assert res.status_code == 200
    data = res.json()
    assert "today" in data
    assert "total" in data

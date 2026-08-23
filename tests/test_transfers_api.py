"""
Tests for Transfers API (QT.08 Workflow & Validation)
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_transfer_valid(client):
    payload = {
        "device_id": 1,
        "to_facility_id": 2,
        "from_facility_id": 1,
        "giver_name": "KTV Nguyễn Văn A",
        "receiver_name": "KTV Trần Thị B",
        "transfer_reason": "Tăng cường máy cho ca cấp cứu",
        "transfer_date": "2026-08-20",
        "form_code": "BM08_TA5.TTBYT.QT.08"
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert "id" in data
    assert data["status"] == "PENDING"
    assert "message" in data

def test_create_transfer_with_null_optionals(client):
    payload = {
        "device_id": 1,
        "to_facility_id": 2,
        "from_facility_id": None,
        "giver_name": None,
        "receiver_name": None,
        "transfer_reason": None,
        "transfer_date": None,
        "form_code": None
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 200, f"Expected 200 with nulls, got {res.status_code}: {res.text}"
    data = res.json()
    assert "id" in data
    assert data["status"] == "PENDING"

def test_create_transfer_missing_required(client):
    # Missing to_facility_id
    payload = {
        "device_id": 1
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 422, f"Expected 422, got {res.status_code}"

def test_create_transfer_nonexistent_device(client):
    payload = {
        "device_id": 999999,
        "to_facility_id": 1
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 404
    assert "không tồn tại" in res.json()["detail"]

def test_create_transfer_nonexistent_facility(client):
    payload = {
        "device_id": 1,
        "to_facility_id": 999999
    }
    res = client.post("/api/transfers", json=payload)
    assert res.status_code == 404
    assert "không tồn tại" in res.json()["detail"]

def test_list_transfers_has_asset_tag(client):
    res = client.get("/api/transfers?limit=5")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "asset_tag" in first
        assert first["asset_tag"].startswith("BVQ7-TTB-")

def test_device_transfer_history(client):
    res = client.get("/api/devices/1/transfers/history")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

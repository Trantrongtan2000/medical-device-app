"""
Transaction & Consistency Tests for Device Transfers
Verifies atomic update between device_transfers and devices.facility_id
"""
import pytest
import sqlite3
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db_connection

@pytest.fixture
def client():
    return TestClient(app)

def test_transfer_confirmation_atomic_success(client):
    # 1. Create transfer for device 1 to facility 2
    create_payload = {
        "device_id": 1,
        "to_facility_id": 2,
        "giver_name": "BS. Nguyễn Văn A",
        "receiver_name": "BS. Trần Văn B",
        "transfer_reason": "Chuyển khoa phục vụ điều trị khẩn cấp"
    }
    create_res = client.post("/api/transfers", json=create_payload)
    assert create_res.status_code == 200
    transfer_id = create_res.json()["id"]

    # 2. Confirm transfer
    conf_res = client.put(f"/api/transfers/{transfer_id}/confirm")
    assert conf_res.status_code == 200
    assert conf_res.json()["status"] == "CONFIRMED"

    # 3. Verify device facility_id has been updated to 2
    with get_db_connection() as db:
        dev = db.execute("SELECT facility_id FROM devices WHERE id = 1").fetchone()
        assert dev["facility_id"] == 2
        
        # Verify transfer status in DB
        t_row = db.execute("SELECT status FROM device_transfers WHERE id = ?", (transfer_id,)).fetchone()
        assert t_row["status"] == "CONFIRMED"

def test_transfer_nonexistent_fails_cleanly(client):
    res = client.put("/api/transfers/999999/confirm")
    assert res.status_code == 404

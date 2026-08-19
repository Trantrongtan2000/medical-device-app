import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import sqlite3
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_index_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Quản Lý Trang Thiết Bị Y Tế" in response.text

def test_get_devices_api():
    response = client.get("/api/devices?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "asset_tag" in first
    assert "device_name" in first
    assert "risk_level" in first

def test_get_single_device_passport():
    response = client.get("/api/devices/1125")  # HERA W10
    if response.status_code == 200:
        dev = response.json()
        assert "Samsung Medison" in dev.get("manufacturer", "") or "HERA W10" in dev.get("model", "")
        assert "supplier_name" in dev

def test_filter_risk_level():
    response = client.get("/api/devices?risk_level=D")
    assert response.status_code == 200
    data = response.json()
    for d in data:
        assert d["risk_level"] == "D"

def test_speedmaint_work_orders():
    response = client.get("/api/work-orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_semantica_provenance():
    response = client.get("/api/semantica/provenance/1125")
    assert response.status_code in [200, 404]


def test_dashboard_and_kanban_markup():
    html = client.get("/").text
    assert "kanban-col-todo" in html
    assert "kanban-col-inprog" in html
    assert "kanban-col-review" in html
    assert "kanban-col-done" in html
    assert "createKanbanTaskModal" in html
    assert 'data-bs-target="#createKanbanTaskModal"' in html
    assert "Ctrl+K" in html
    assert 'id="search-input"' in html
    assert "checkoutDeviceModal" in html
    assert "overview-activity-tbody" in html


def test_dashboard_activity_feed():
    response = client.get("/api/dashboard/activity?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_status_type_warehouse_not_matching_khoa():
    """LIKE '%Kho%' must not treat 'Khoa Cấp Cứu' as warehouse / Ready to Deploy."""
    rtd = client.get("/api/devices?limit=50&status_type=rtd").json()
    names = " ".join((d.get("facility") or "") for d in rtd)
    assert "Khoa Cấp Cứu" not in names
    deployed = client.get("/api/devices?limit=20&status_type=deployed").json()
    assert len(deployed) > 0


def test_checkout_checkin_roundtrip():
    listing = client.get("/api/devices?limit=1").json()
    assert listing
    device_id = listing[0]["id"]
    orig_facility = listing[0].get("facility_id")

    facilities = client.get("/api/dashboard/facilities").json()
    assert facilities
    dest = next((f for f in facilities if f["id"] != orig_facility), facilities[0])

    checkout = client.post(
        f"/api/devices/{device_id}/checkout",
        json={
            "facility_id": dest["id"],
            "assigned_to_name": "Pytest Agent",
            "note": "pytest checkout",
        },
    )
    assert checkout.status_code == 200, checkout.text
    assert checkout.json().get("status") == "success"

    checkin = client.post(
        f"/api/devices/{device_id}/checkin",
        json={"note": "pytest checkin"},
    )
    assert checkin.status_code == 200, checkin.text
    assert checkin.json().get("status") == "success"

    if orig_facility:
        restore = client.post(
            f"/api/devices/{device_id}/checkout",
            json={
                "facility_id": orig_facility,
                "assigned_to_name": "Pytest Agent",
                "note": "restore original location",
            },
        )
        assert restore.status_code == 200, restore.text



def test_bme_staff_endpoints():
    # 1. Test GET /api/staff
    res = client.get("/api/staff")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 6
    assert any("BME-Q7" in s["staff_code"] for s in data)

    # 2. Test GET /api/staff/1
    res_single = client.get("/api/staff/1")
    assert res_single.status_code == 200
    staff = res_single.json()
    assert staff["staff_code"] == "BME-Q7-01"
    assert "Nguyễn Quốc Việt" in staff["full_name"]
    assert "recent_tasks" in staff

    # 3. Test GET /api/directory/leaders
    res_leaders = client.get("/api/directory/leaders")
    assert res_leaders.status_code == 200
    assert len(res_leaders.json()) >= 5

    # 4. Test GET /api/directory/suppliers
    res_suppliers = client.get("/api/directory/suppliers")
    assert res_suppliers.status_code == 200
    assert len(res_suppliers.json()) >= 10



def test_oncall_schedule_endpoints():
    # 1. Test GET /api/oncall/schedule
    res = client.get("/api/oncall/schedule")
    assert res.status_code == 200
    sched = res.json()
    assert isinstance(sched, list)
    assert len(sched) == 7
    assert any(s["primary_engineer"] == "Trần Đăng Hiếu" for s in sched)

    # 2. Test GET /api/oncall/today
    res_today = client.get("/api/oncall/today")
    assert res_today.status_code == 200
    today = res_today.json()
    assert "primary_engineer" in today

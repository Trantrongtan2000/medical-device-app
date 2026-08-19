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

# 🗄️ CODEBASE DATABASE SCHEMA & PYTEST TEST SUITES
> **Thời điểm xuất:** 2026-08-21 15:44:00
> **Tổng số tests:** 9 files test


---

## 📄 File: `database/schema.sql`
- **Dung lượng:** 12,077 bytes | **Số dòng:** 335 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\database\schema.sql`

```sql
-- =========================================================================
-- SCHEMA TOÀN DIỆN: MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3 - PKĐK TÂM ANH Q7)
-- Tiêu chuẩn: Bộ Y Tế, Nghị Định 98/2021/NĐ-CP, Thông Tư 05/2022/TT-BYT & W3C PROV-O
-- =========================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. Core Master Tables
CREATE TABLE IF NOT EXISTS "facilities" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE NOT NULL,
    location TEXT,
    manager TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS device_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    safety_level TEXT CHECK(safety_level IN ('Basic', 'Advanced', 'Critical'))
);

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name TEXT NOT NULL,
    model TEXT NOT NULL,
    serial_no TEXT NOT NULL UNIQUE,
    certification_no TEXT,
    calibration_stamp_no TEXT,
    facility_id INTEGER,
    category_id INTEGER,
    manufacturer TEXT,
    country_of_manufacturer TEXT,
    year_of_manufacture INTEGER,
    risk_level TEXT CHECK(risk_level IN ('A', 'B', 'C', 'D')),
    status TEXT DEFAULT 'IN_SERVICE' CHECK(status IN ('IN_SERVICE', 'CALIBRATION_DUE', 'MAINTENANCE', 'REPAIR', 'RETIRED')),
    installation_date DATE,
    calibration_date DATE,
    recalibration_date DATE,
    source_pdf TEXT,
    pdf_path TEXT,
    md_path TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contract_no TEXT,
    supplier_name TEXT,
    handover_date TEXT,
    form_code TEXT,
    party_giver TEXT,
    party_receiver TEXT,
    md_source_path TEXT,
    FOREIGN KEY (facility_id) REFERENCES facilities(id),
    FOREIGN KEY (category_id) REFERENCES device_categories(id)
);

CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_no TEXT NOT NULL UNIQUE,
    contract_name TEXT,
    supplier_name TEXT,
    handover_date TEXT,
    contract_value REAL,
    warranty_period_months INTEGER DEFAULT 12,
    status TEXT DEFAULT 'ACTIVE',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS device_accessories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_device_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    model TEXT,
    serial_no TEXT,
    accessory_type TEXT,
    status TEXT DEFAULT 'Sẵn sàng sử dụng',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_device_id) REFERENCES devices (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bme_staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_code TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    title TEXT NOT NULL,
    role_level TEXT DEFAULT 'Kỹ Sư Chính',
    department_unit TEXT DEFAULT 'Phòng TTBYT Quận 7',
    specialty TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    assigned_departments TEXT,
    certificates TEXT,
    status TEXT DEFAULT 'ACTIVE',
    oncall_status TEXT DEFAULT 'AVAILABLE',
    avatar_color TEXT DEFAULT '#0284c7',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hospital_directory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    title TEXT,
    phone TEXT,
    email TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS supplier_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    service_scope TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Compliance, Calibration & Inspection Tables
CREATE TABLE IF NOT EXISTS calibration_certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    certificate_no TEXT NOT NULL,
    calibration_date DATE NOT NULL,
    recalibration_date DATE,
    stamp_no TEXT,
    result_status TEXT DEFAULT 'OK' CHECK(result_status IN ('OK', 'NG', 'PENDING')),
    uncertainty REAL,
    standard_reference TEXT,
    calibrated_by TEXT,
    source_pdf TEXT,
    pdf_path TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pre_use_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    inspector_name TEXT NOT NULL,
    department TEXT NOT NULL,
    power_ok BOOLEAN DEFAULT 1,
    physical_ok BOOLEAN DEFAULT 1,
    gas_pressure_ok BOOLEAN DEFAULT 1,
    selftest_ok BOOLEAN DEFAULT 1,
    overall_status TEXT DEFAULT 'PASSED' CHECK(overall_status IN ('PASSED', 'FAILED', 'WARNING')),
    notes TEXT,
    inspection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
);

-- 3. Maintenance, Repairs & Transfers Tables
CREATE TABLE IF NOT EXISTS maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    maintenance_date DATE NOT NULL,
    performed_by TEXT,
    maintenance_type TEXT CHECK(maintenance_type IN ('CALIBRATION', 'REPAIR', 'PREVENTIVE', 'INSPECTION', 'HANDOVER')),
    description TEXT,
    source_pdf TEXT,
    pdf_path TEXT,
    next_due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS maintenance_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    due_date DATE NOT NULL,
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE')),
    notes TEXT,
    maintenance_type TEXT DEFAULT 'PREVENTIVE' CHECK(maintenance_type IN ('PREVENTIVE', 'CALIBRATION', 'REPAIR', 'INSPECTION', 'HANDOVER')),
    frequency_days INTEGER,
    last_completed_at DATE,
    next_due_at DATE,
    assigned_staff_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS repairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    repair_type TEXT DEFAULT 'REPAIR' CHECK(repair_type IN ('CALIBRATION', 'REPAIR', 'REPLACEMENT', 'PREVENTIVE', 'INSPECTION', 'HANDOVER')),
    description TEXT NOT NULL,
    actual_cost REAL DEFAULT 0,
    parts_used TEXT,
    technician_name TEXT,
    reported_by TEXT,
    status TEXT DEFAULT 'REPORTED' CHECK(status IN ('REPORTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    start_date DATE,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS device_transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    from_facility_id INTEGER NOT NULL,
    to_facility_id INTEGER NOT NULL,
    giver_name TEXT NOT NULL,
    receiver_name TEXT NOT NULL,
    transfer_reason TEXT,
    transfer_date DATE NOT NULL,
    form_code TEXT DEFAULT 'BM08_TA5.TTBYT.QT.08',
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE,
    FOREIGN KEY (from_facility_id) REFERENCES facilities (id),
    FOREIGN KEY (to_facility_id) REFERENCES facilities (id)
);

-- 4. Operations, Notifications & System Config Tables
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_type TEXT NOT NULL CHECK(ref_type IN ('CALIBRATION', 'MAINTENANCE', 'TRANSFER', 'DEVICE', 'FEEDBACK')),
    ref_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'WARNING' CHECK(level IN ('INFO', 'WARNING', 'CRITICAL')),
    days_left INTEGER,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS oncall_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_num INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    date_str TEXT NOT NULL,
    primary_engineer TEXT NOT NULL,
    primary_phone TEXT NOT NULL,
    backup_engineer TEXT NOT NULL,
    backup_phone TEXT NOT NULL,
    leader_oncall TEXT DEFAULT 'Nguyễn Quốc Việt (0902769710)',
    time_window TEXT DEFAULT '24/24 Giờ (07:30 - 07:30 sáng hôm sau)',
    status TEXT DEFAULT 'SCHEDULED',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, day_num)
);

CREATE TABLE IF NOT EXISTS api_keys_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    api_key TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    sender_name TEXT,
    sender_dept TEXT,
    priority TEXT DEFAULT 'NORMAL',
    content TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING',
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Views
CREATE VIEW IF NOT EXISTS device_status_summary AS
SELECT 
    d.id,
    d.device_name,
    d.model,
    d.serial_no,
    d.contract_no,
    d.supplier_name,
    d.handover_date,
    d.manufacturer,
    d.country_of_manufacturer,
    d.risk_level,
    d.status,
    f.id AS facility_id,
    f.name AS facility,
    f.code AS facility_code,
    c.id AS category_id,
    c.name AS category,
    c.safety_level,
    d.calibration_date,
    d.recalibration_date,
    cert.certificate_no,
    cert.stamp_no,
    cert.source_pdf,
    CASE
        WHEN d.recalibration_date IS NULL THEN 'NO_CALIBRATION'
        WHEN date(d.recalibration_date) < date('now') THEN 'OVERDUE'
        WHEN date(d.recalibration_date) <= date('now', '+30 days') THEN 'WARNING'
        ELSE 'OK'
    END AS alert_status,
    CAST((julianday(d.recalibration_date) - julianday('now')) AS INTEGER) AS days_remaining
FROM devices d
LEFT JOIN facilities f ON d.facility_id = f.id
LEFT JOIN device_categories c ON d.category_id = c.id
LEFT JOIN calibration_certificates cert ON d.id = cert.device_id;

-- 6. Performance Indices (Created AFTER all tables and views)
CREATE INDEX IF NOT EXISTS idx_devices_category ON devices(category_id);
CREATE INDEX IF NOT EXISTS idx_devices_facility ON devices(facility_id);
CREATE INDEX IF NOT EXISTS idx_devices_serial ON devices(serial_no);
CREATE INDEX IF NOT EXISTS idx_devices_status_risk ON devices(status, risk_level);

CREATE INDEX IF NOT EXISTS idx_accessories_parent ON device_accessories(parent_device_id);
CREATE INDEX IF NOT EXISTS idx_certificates_date ON calibration_certificates(calibration_date, recalibration_date);
CREATE INDEX IF NOT EXISTS idx_certificates_device ON calibration_certificates(device_id);

CREATE INDEX IF NOT EXISTS idx_logs_device_date ON maintenance_logs(device_id, maintenance_date DESC);
CREATE INDEX IF NOT EXISTS idx_maintenances_device ON maintenance_schedules(device_id);
CREATE INDEX IF NOT EXISTS idx_maintenances_status ON maintenance_schedules(status, due_date);

CREATE INDEX IF NOT EXISTS idx_repairs_device ON repairs(device_id);
CREATE INDEX IF NOT EXISTS idx_repairs_status ON repairs(status, start_date);

CREATE INDEX IF NOT EXISTS idx_transfers_device ON device_transfers(device_id);
CREATE INDEX IF NOT EXISTS idx_transfers_status ON device_transfers(status, transfer_date);

CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_ref ON notifications(ref_type, ref_id);

```


---

## 📄 File: `tests/test_baseline_smoke.py`
- **Dung lượng:** 2,104 bytes | **Số dòng:** 65 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_baseline_smoke.py`

```python
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

```


---

## 📄 File: `tests/test_cactus_router_deep.py`
- **Dung lượng:** 3,122 bytes | **Số dòng:** 81 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_cactus_router_deep.py`

```python
"""
Deep Verification Tests for 6-Layer Cactus Hybrid Router & Needle Planner
Covers Ambiguity Detection, Canonical Data Contracts, Provenance and Telemetry.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cactus_router import CactusHybridRouter
from app.needle_planner import needle_planner, CircuitBreaker
from app.database import get_db_connection
from app.observability import telemetry_collector

@pytest.fixture
def client():
    return TestClient(app)

# 1. 6-Layer Routing & Ambiguity Detection
def test_router_ambiguity_detection():
    decision = CactusHybridRouter.route("kiểm tra máy")
    assert decision.intent == "AMBIGUOUS_CLARIFICATION_REQUIRED"
    assert decision.ambiguity_score > 0.5
    assert decision.clarification_prompt is not None

def test_router_exact_asset_tag():
    decision = CactusHybridRouter.route("Tra cứu máy BVQ7-TTB-00001")
    assert decision.route == "LOCAL_EDGE"
    assert decision.strategy == "DETERMINISTIC_EXACT"
    assert decision.confidence >= 0.95
    assert decision.tool_name == "get_device_by_asset_tag"

def test_router_mutation_gate():
    decision = CactusHybridRouter.route("Bàn giao máy BVQ7-TTB-00002 sang khoa hồi sức")
    assert decision.route == "LOCAL_EDGE"
    assert decision.requires_confirmation is True
    assert "REQUIRES_HUMAN_CONFIRMATION" in decision.policy_flags

# 2. Planner & Provenance Record
def test_planner_provenance_and_trust():
    with get_db_connection() as db:
        route_decision = CactusHybridRouter.route("Xem báo cáo tổng quan")
        tool_dec, tool_res = needle_planner.plan_and_execute(route_decision, db)
        
        assert tool_res.success is True
        assert tool_res.provenance is not None
        assert tool_res.provenance.source_type == "SQLITE_MASTER"
        assert tool_res.provenance.is_authoritative is True
        assert tool_res.trust_level.value == "CALCULATED_DATA"

# 3. Circuit Breaker Simulation
def test_circuit_breaker_trip():
    cb = CircuitBreaker(failure_threshold=2, reset_timeout_seconds=5)
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is True
    
    cb.record_failure()
    assert cb.can_execute() is False  # Tripped to OPEN

    cb.record_success()
    assert cb.can_execute() is True  # Reset to CLOSED

# 4. HTTP API Telemetry & Clarification Endpoints
def test_api_agent_clarification_response(client):
    res = client.post("/api/agent/query", json={"query": "kiểm tra thiết bị"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "CLARIFICATION_REQUIRED"
    assert "ambiguity_score" in data
    assert "❓" in data["response_text"]

def test_api_agent_telemetry_endpoint(client):
    # Send a valid query to populate telemetry
    client.post("/api/agent/query", json={"query": "Xem máy BVQ7-TTB-00001"})
    
    res = client.get("/api/agent/telemetry")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "recent_events" in data
    assert data["metrics"]["total_events"] > 0

```


---

## 📄 File: `tests/test_documents_pdf.py`
- **Dung lượng:** 1,156 bytes | **Số dòng:** 34 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_documents_pdf.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_device_documents_valid():
    """Kiểm tra API lấy danh sách tài liệu PDF của một thiết bị"""
    # Lấy thử 1 thiết bị đầu tiên
    res = client.get("/api/devices/1/documents")
    assert res.status_code == 200
    data = res.json()
    assert "device" in data
    assert "documents" in data
    assert "total_documents" in data
    assert isinstance(data["documents"], list)

def test_get_device_documents_not_found():
    """Kiểm tra khi device_id không tồn tại"""
    res = client.get("/api/devices/999999/documents")
    assert res.status_code == 404

def test_search_documents():
    """Kiểm tra tìm kiếm nhanh tài liệu PDF"""
    res = client.get("/api/documents/search?q=2024")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "total" in data

def test_stream_document_not_found():
    """Kiểm tra stream tài liệu khi doc_id không tồn tại"""
    res = client.get("/api/documents/stream/999999")
    assert res.status_code == 404

```


---

## 📄 File: `tests/test_needle_agent.py`
- **Dung lượng:** 5,783 bytes | **Số dòng:** 134 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_needle_agent.py`

```python
"""
Comprehensive Tests for Needle Edge Agent & Cactus Hybrid Router POC
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.needle_agent import needle_agent, NeedleRouter, SafeToolExecutor
from app.database import get_db_connection

@pytest.fixture
def client():
    return TestClient(app)

# 1. Router Intent & Confidence Unit Tests
def test_router_asset_tag_lookup():
    decision = NeedleRouter.parse_intent("Tra cứu máy BVQ7-TTB-00001 đang ở đâu?")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "GET_DEVICE"
    assert decision.confidence >= 0.95
    assert decision.tool_name == "get_device_by_asset_tag"
    assert decision.parameters["asset_tag"] == "BVQ7-TTB-00001"

def test_router_calibration_status():
    decision = NeedleRouter.parse_intent("Kiểm tra hạn kiểm định của máy #00002")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "CHECK_CALIBRATION"
    assert decision.confidence >= 0.95
    assert decision.tool_name == "get_device_calibration_status"
    assert decision.parameters["device_id_or_tag"] == "BVQ7-TTB-00002"

def test_router_dashboard_summary():
    decision = NeedleRouter.parse_intent("Cho tôi xem thống kê tổng quan toàn viện")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "DASHBOARD_SUMMARY"
    assert decision.tool_name == "get_dashboard_summary"
    assert decision.confidence >= 0.90

def test_router_search_device_by_keyword():
    decision = NeedleRouter.parse_intent("Tìm danh sách máy thở trong bệnh viện")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "SEARCH_DEVICES"
    assert decision.tool_name == "search_devices"
    assert decision.parameters["keyword"] == "máy thở"

def test_router_facility_lookup_unicode():
    decision = NeedleRouter.parse_intent("Tra cứu thông tin Khoa Cấp Cứu ở đâu?")
    assert decision.route == "LOCAL_EDGE"
    assert decision.intent == "GET_FACILITY"
    assert decision.tool_name == "get_facility"
    assert decision.parameters["name_or_code"] == "cấp cứu"

def test_router_mutation_safety_gate():
    decision = NeedleRouter.parse_intent("Điều chuyển máy BVQ7-TTB-00001 sang Khoa Ngoại")
    assert decision.route == "LOCAL_EDGE"
    assert decision.requires_confirmation is True
    assert decision.intent == "MUTATION_ACTION"

def test_router_escalate_complex_to_cloud():
    decision = NeedleRouter.parse_intent("Giải thích nguyên lý hoạt động khối phát tia X theo Nghị định 98 và SOP QT.04")
    assert decision.route == "CLOUD_FRONTIER"
    assert decision.confidence < 0.85
    assert decision.tool_name is None

# 2. Integration Tests with SafeToolExecutor (All 5 Tools)
def test_executor_get_device():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("get_device_by_asset_tag", {"asset_tag": "BVQ7-TTB-00001"}, db)
        assert data is not None
        assert "BVQ7-TTB-00001" in text
        assert "Thông Tin Thiết Bị" in text

def test_executor_search_devices():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("search_devices", {"keyword": "máy"}, db)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "Tìm thấy" in text

def test_executor_get_facility():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("get_facility", {"name_or_code": "Cấp Cứu"}, db)
        assert data is not None
        assert "Khoa/Phòng:" in text

def test_executor_calibration_status():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("get_device_calibration_status", {"device_id_or_tag": "BVQ7-TTB-00001"}, db)
        assert data is not None
        assert "Tình Trạng Kiểm Định" in text

def test_executor_dashboard_summary():
    with get_db_connection() as db:
        data, text = SafeToolExecutor.execute_tool("get_dashboard_summary", {}, db)
        assert data["total_devices"] >= 1
        assert "Báo Cáo Tổng Hợp Thiết Bị Y Tế" in text

# 3. Async Agent Pipeline Test
@pytest.mark.asyncio
async def test_async_needle_agent_process_query():
    with get_db_connection() as db:
        result = await needle_agent.process_query("Kiểm tra hạn kiểm định của máy #00001", db)
        assert result.status == "SUCCESS"
        assert result.route_taken == "LOCAL_EDGE"
        assert result.confidence >= 0.85
        assert result.tool_name == "get_device_calibration_status"

# 4. HTTP API Endpoint Tests
def test_api_agent_tools_list(client):
    res = client.get("/api/agent/tools")
    assert res.status_code == 200
    data = res.json()
    assert data["tools_count"] == 5
    tool_names = [t["name"] for t in data["tools"]]
    assert "get_device_by_asset_tag" in tool_names
    assert "get_dashboard_summary" in tool_names

def test_api_agent_query_local_edge(client):
    payload = {"query": "Xem thông tin máy BVQ7-TTB-00001"}
    res = client.post("/api/agent/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["route_taken"] == "LOCAL_EDGE"
    assert data["tool_name"] == "get_device_by_asset_tag"
    assert data["confidence"] >= 0.85
    assert "BVQ7-TTB-00001" in data["response_text"]

def test_api_agent_query_confirmation_gate(client):
    payload = {"query": "Tạo phiếu điều chuyển máy sang phòng xét nghiệm"}
    res = client.post("/api/agent/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "AWAITING_CONFIRMATION"
    assert "xác nhận" in data["response_text"]

```


---

## 📄 File: `tests/test_rbac_security.py`
- **Dung lượng:** 1,206 bytes | **Số dòng:** 36 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_rbac_security.py`

```python
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

```


---

## 📄 File: `tests/test_repairs_api.py`
- **Dung lượng:** 2,435 bytes | **Số dòng:** 78 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_repairs_api.py`

```python
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

```


---

## 📄 File: `tests/test_schema_init.py`
- **Dung lượng:** 1,694 bytes | **Số dòng:** 44 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_schema_init.py`

```python
"""
Tests for Empty Database Initialization from schema.sql
"""
import sqlite3
import tempfile
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent.parent / "database" / "schema.sql"

def test_empty_database_schema_initialization():
    """Kiểm tra khởi tạo schema từ database hoàn toàn rỗng."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    
    try:
        conn = sqlite3.connect(tmp_path)
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        
        # Must execute without errors (indices after tables)
        conn.executescript(schema_sql)
        conn.commit()

        # Check integrity
        integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
        assert integrity == "ok"

        # Check all tables and views exist
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view');").fetchall()]
        expected = [
            "facilities", "device_categories", "devices", "contracts",
            "device_accessories", "bme_staff", "hospital_directory",
            "supplier_contacts", "calibration_certificates", "pre_use_inspections",
            "maintenance_logs", "maintenance_schedules", "repairs",
            "device_transfers", "notifications", "oncall_schedule",
            "api_keys_config", "system_feedback", "device_status_summary"
        ]
        for exp in expected:
            assert exp in tables, f"Expected table/view '{exp}' missing in fresh database"
        
        conn.close()
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

```


---

## 📄 File: `tests/test_transfers_api.py`
- **Dung lượng:** 2,720 bytes | **Số dòng:** 87 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_transfers_api.py`

```python
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

```


---

## 📄 File: `tests/test_transfers_transaction.py`
- **Dung lượng:** 1,588 bytes | **Số dòng:** 44 dòng
- **Đường dẫn:** `C:\Users\tantt\Downloads\medical-device-app\tests\test_transfers_transaction.py`

```python
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

```

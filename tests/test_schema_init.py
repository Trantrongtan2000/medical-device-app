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

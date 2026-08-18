#!/usr/bin/env python3
"""Test database queries directly"""

import sqlite3
from pathlib import Path
from datetime import date, timedelta

db_path = Path("C:/Users/tantt/Downloads/medical-device-app/database/devices.db")

print("Testing database queries...\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test query 1: Dashboard summary
print("Test 1: Dashboard Summary")
try:
    queries = {
        "total": "SELECT COUNT(*) as count FROM devices",
        "overdue": """
            SELECT COUNT(*) as count FROM devices d
            JOIN calibration_certificates c ON d.id = c.device_id
            WHERE c.recalibration_date < DATE('now')
        """,
        "warning": """
            SELECT COUNT(*) as count FROM devices d
            JOIN calibration_certificates c ON d.id = c.device_id
            WHERE c.recalibration_date >= DATE('now') 
            AND c.recalibration_date <= DATE('now', '+30 days')
        """,
        "ok": """
            SELECT COUNT(*) as count FROM devices d
            JOIN calibration_certificates c ON d.id = c.device_id
            WHERE c.recalibration_date > DATE('now', '+30 days')
        """
    }
    
    for key, query in queries.items():
        result = cursor.execute(query).fetchone()
        print(f"  {key}: {result[0]}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

# Test query 2: Devices voi row_factory
print("\nTest 2: Devices list (with Row factory)")
try:
    conn.row_factory = sqlite3.Row
    query = """
        SELECT 
            d.id, d.device_name, d.model, d.serial_no,
            f.name as facility, c.name as category,
            cc.calibration_date, cc.recalibration_date, cc.result_status,
            CASE 
                WHEN cc.recalibration_date < DATE('now') THEN 'OVERDUE'
                WHEN cc.recalibration_date <= DATE('now', '+30 days') THEN 'WARNING'
                ELSE 'OK'
            END as alert_status
        FROM devices d
        LEFT JOIN facilities f ON d.facility_id = f.id
        LEFT JOIN device_categories c ON d.category_id = c.id
        LEFT JOIN calibration_certificates cc ON d.id = cc.device_id 
            AND cc.id = (SELECT MAX(id) FROM calibration_certificates WHERE device_id = d.id)
        ORDER BY d.device_name
    """
    result = cursor.execute(query).fetchall()
    print(f"  Found {len(result)} devices")
    for row in result:
        # Convert Row to dict manually
        d = dict(zip([column[0] for column in cursor.description], row))
        print(f"    - {d}")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback
    traceback.print_exc()

conn.close()
print("\nDone!")
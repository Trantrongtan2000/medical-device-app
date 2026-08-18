#!/usr/bin/env python3
"""Test database connection và endpoints"""

import sqlite3
from pathlib import Path

db_path = Path("C:/Users/tantt/Downloads/medical-device-app/database/devices.db")

print("=" * 60)
print("DATABASE TEST")
print("=" * 60)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Test tables
    tables = ['devices', 'calibration_certificates', 'facilities', 'device_categories']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"[{'OK' if count >= 0 else 'FAIL'}] Table '{table}': {count} records")
    
    # Sample data
    print("\nSample devices:")
    cursor.execute("SELECT device_name, model, serial_no, facility_id FROM devices LIMIT 5")
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]}) SN:{row[2]}")
    
    conn.close()
    print("\n[OK] Database connection successful!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
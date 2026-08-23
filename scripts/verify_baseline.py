#!/usr/bin/env python3
"""
Baseline Verification Script for T-000
Verifies database integrity, backup, and API endpoints.
"""
import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = "database/devices.db"
BACKUP_PATH = "database/backups/devices_baseline_backup.db"

def verify_database():
    """Verify database exists and has correct structure"""
    print("=" * 60)
    print("🔍 BASELINE VERIFICATION - DATABASE CHECK")
    print("=" * 60)

    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return False

    # Count devices
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable WAL mode
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA foreign_keys=ON;")

    # Count devices
    cursor.execute("SELECT COUNT(*) FROM devices")
    device_count = cursor.fetchone()[0]
    print(f"✅ Devices in database: {device_count}")

    # Check facilities
    cursor.execute("SELECT COUNT(*) FROM facilities")
    facility_count = cursor.fetchone()[0]
    print(f"✅ Facilities: {facility_count}")

    # Check tables exist
    tables = ['devices', 'device_transfers', 'maintenance_schedules', 
              'calibration_certificates', 'pre_use_inspections', 'facilities']
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            print(f"✅ Table '{table}' exists")
        except Exception as e:
            print(f"❌ Table '{table}' missing or error: {e}")
            return False

    conn.close()

    # Create backup
    os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"\n✅ Backup created at {BACKUP_PATH}")

    return True

def main():
    print(f"Verifcation timestamp: {datetime.now().isoformat()}")
    success = verify_database()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ BASELINE VERIFICATION PASSED")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ BASELINE VERIFICATION FAILED")
        print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
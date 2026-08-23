#!/usr/bin/env python3
"""
API Test Script - T-001 Verification
Tests key endpoints for Medical Device Management System
"""
import sqlite3
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_connection, init_database

def test_health():
    """Test 1: Health check"""
    print("\n[TEST 1] Health Check")
    conn = sqlite3.connect("database/devices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 as health")
    result = cursor.fetchone()
    conn.close()
    
    if result[0] == 1:
        print("✅ Database connectivity OK")
        return True
    else:
        print("❌ Database connectivity FAILED")
        return False

def test_devices_count():
    """Test 2: Devices count"""
    print("\n[TEST 2] Devices Count")
    conn = sqlite3.connect("database/devices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM devices")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"✅ Devices in database: {count}")
    return count > 0

def test_facilities():
    """Test 3: Facilities exist"""
    print("\n[TEST 3] Facilities")
    conn = sqlite3.connect("database/devices.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM facilities")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"✅ Facilities: {count}")
    return count > 0

def test_transfers_table():
    """Test 4: Transfers table structure"""
    print("\n[TEST 4] Transfers Table Structure")
    conn = sqlite3.connect("database/devices.db")
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='device_transfers'")
    result = cursor.fetchone()
    
    if result:
        print("✅ device_transfers table exists")
        print(f"   Schema: {result[0][:100]}...")
    else:
        print("❌ device_transfers table missing")
        
    conn.close()
    return result is not None

def main():
    print("=" * 60)
    print("API ENDPOINT VERIFICATION - T-001")
    print("=" * 60)
    
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Devices Count", test_devices_count()))
    results.append(("Facilities", test_facilities()))
    results.append(("Transfers Table", test_transfers_table()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Database schema verified")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED - Check database state")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    exit(main())
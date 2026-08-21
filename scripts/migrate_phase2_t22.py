#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T2.2 Migration — tạo bảng repairs kết hợp với logic tách maintenance_logs"""
import sqlite3
from pathlib import Path

DB = Path(r'C:\Users\tantt\Downloads\medical-device-app\database\devices.db')

with sqlite3.connect(DB) as con:
    cur = con.cursor()
    
    # Kiểm tra bảng repairs có tồn tại
    exists = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repairs'").fetchone()
    if exists:
        print("[SKIP] repairs table đã tồn tại")
    else:
        cur.executescript("""
        CREATE TABLE repairs (
            id INTEGER PRIMARY KEY,
            device_id INTEGER NOT NULL,
            repair_type TEXT NOT NULL CHECK(repair_type IN ('CALIBRATION','REPAIR','REPLACEMENT','PREVENTIVE','INSPECTION','HANDOVER')),
            description TEXT NOT NULL,
            actual_cost REAL,
            parts_used TEXT,
            technician_name TEXT,
            reported_by TEXT,
            status TEXT DEFAULT 'REPORTED' CHECK(status IN ('REPORTED','IN_PROGRESS','COMPLETED','CANCELLED')),
            start_date DATE,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_repairs_device ON repairs(device_id);
        CREATE INDEX IF NOT EXISTS idx_repairs_status ON repairs(status, start_date);
        """)
        print("[OK] Tạo bảng repairs + indexes")
        con.commit()

# Verify
tbl = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(f"[VERIFY] tổng bảng: {len(tbl)}, repairs có trong danh sách: {'repairs' in(tbl)}")

# Test sample insert
cur.execute("INSERT INTO repairs (device_id, repair_type, description) VALUES (1, 'REPAIR', 'Test migration check')")
print(f"[OK] Sample insert repairs ok, id={cur.lastrowid}")
con.commit()
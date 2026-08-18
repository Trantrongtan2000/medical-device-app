#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seed du lieu mau cho he thong"""

import sys
import io
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

db_path = "C:/Users/tantt/Downloads/medical-device-app/database/devices.db"

# Du lieu mau tu file MD da phan tich
sample_devices = [
    {
        "device_name": "May tho chuc nang cao TV-100",
        "model": "TV-100", 
        "serial_no": "TX2301031",
        "cert_no": "B.2100535DKLH/BYT-TB-CT",
        "stamp_no": "5508",
        "facility": "Cap cuc",
        "category": "Respiratory Equipment",
        "calibration_date": "2025-01-07",
        "recalibration_date": "2026-01-06",
        "status": "OK",
        "manufacturer": "Philips"
    },
    {
        "device_name": "May chay than nhan tao chu ky HD 4008S",
        "model": "HD 4008S",
        "serial_no": "4SXA5JRR",
        "cert_no": "C.20200590-ADJVINA/170000008/PCBPL-BYT",
        "stamp_no": "00450", 
        "facility": "Cap cuc - Don vi loc may",
        "category": "Dialysis Machine",
        "calibration_date": "2025-02-07",
        "recalibration_date": "2026-02-06",
        "status": "OK",
        "manufacturer": "Baxter"
    },
    {
        "device_name": "Dao mo dien cao tan luong cuc ZEUS-150",
        "model": "ZEUS-150",
        "serial_no": "A07COAT0484",
        "cert_no": "14616/210725",
        "stamp_no": "00444",
        "facility": "Kham beh - PK Nhi",
        "category": "Surgical Instrument",
        "calibration_date": "2025-07-21",
        "recalibration_date": "2026-07-21",
        "status": "PENDING",  # WARNING -> PENDING (valid status)
        "manufacturer": "Erbe"
    },
    {
        "device_name": "Ap ke Loa xo P014632",
        "model": "Loa xo",
        "serial_no": "P014632",
        "cert_no": "056-1000/01.26P",
        "stamp_no": "26A 101562",
        "facility": "Kham behn",
        "category": "Blood Pressure Monitor",
        "calibration_date": "2026-01-30",
        "recalibration_date": "2027-01-31",
        "status": "OK",
        "manufacturer": "YAMASU"
    }
]

def seed_data():
    print("\n" + "="*60)
    print("SEED DU LIEU MAU")
    print("="*60)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for device in sample_devices:
        # Insert facility
        cursor.execute("SELECT id FROM facilities WHERE name = ?", (device['facility'],))
        result = cursor.fetchone()
        if result:
            facility_id = result[0]
        else:
            code = f"FAC{cursor.execute('SELECT COUNT(*) FROM facilities').fetchone()[0] + 1:03d}"
            cursor.execute("INSERT INTO facilities (name, code) VALUES (?, ?)", (device['facility'], code))
            facility_id = cursor.lastrowid
        
        # Insert category
        cursor.execute("SELECT id FROM device_categories WHERE name = ?", (device['category'],))
        result = cursor.fetchone()
        if result:
            category_id = result[0]
        else:
            cursor.execute("INSERT INTO device_categories (name, description) VALUES (?, ?)", (device['category'], device['category']))
            category_id = cursor.lastrowid
        
        # Insert device
        device_data = {
            'device_name': device['device_name'],
            'model': device['model'],
            'serial_no': device['serial_no'],
            'certification_no': device['cert_no'],
            'calibration_stamp_no': device['stamp_no'],
            'facility_id': facility_id,
            'category_id': category_id,
            'manufacturer': device['manufacturer'],
            'calibration_date': device['calibration_date'],
            'recalibration_date': device['recalibration_date']
        }
        
        cursor.execute("""
            INSERT INTO devices 
            (device_name, model, serial_no, certification_no, calibration_stamp_no,
             facility_id, category_id, manufacturer, calibration_date, recalibration_date)
            VALUES 
            (:device_name, :model, :serial_no, :certification_no, :calibration_stamp_no,
             :facility_id, :category_id, :manufacturer, :calibration_date, :recalibration_date)
        """, device_data)
        
        device_id = cursor.lastrowid
        
        # Insert certificate
        cursor.execute("""
            INSERT INTO calibration_certificates
            (device_id, certificate_no, calibration_date, recalibration_date,
             stamp_no, result_status, calibrated_by)
            VALUES
            (?, ?, ?, ?, ?, ?, ?)
        """, (
            device_id, device['cert_no'], device['calibration_date'],
            device['recalibration_date'], device['stamp_no'], device['status'], ''
        ))
        
        print(f"[OK] {device['device_name']} (SN: {device['serial_no']})")
    
    conn.commit()
    conn.close()
    print("\n[SUCCESS] Seed du lieu thanh cong!")
    print("="*60)

if __name__ == "__main__":
    seed_data()
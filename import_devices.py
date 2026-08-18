#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to import medical device data from MD files with YAML frontmatter
into SQLite database.
"""
import sys
import io

# Force UTF-8 encoding for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import sqlite3
import os
import re
from pathlib import Path
from datetime import datetime

# Configuration
SOURCE_DIR = r"G:\BV QUẬN 7_OCR_WORK_20260712\md\05_KIEM DINH\backup_original"
DB_PATH = r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db"
MAX_FILES = 30

def parse_yaml_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None
    
    yaml_text = match.group(1)
    result = {}
    
    # Parse YAML-like key-value pairs
    for line in yaml_text.split('\n'):
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            result[key] = value
    
    return result

def get_device_type(device_name):
    """Determine device category based on device name."""
    device_name_lower = device_name.lower()
    
    if 'huyết áp' in device_name_lower or 'blood pressure' in device_name_lower:
        return 'Blood Pressure Monitor'
    elif 'nhiệt ẩm' in device_name_lower or 'humidity' in device_name_lower:
        return 'Temperature/Humidity Meter'
    elif 'nhiệt âm' in device_name_lower or 'thermometer' in device_name_lower or 'temp' in device_name_lower:
        return 'Thermometer'
    elif 'cân' in device_name_lower or 'weight' in device_name_lower:
        return 'Weighing Scale'
    elif 'ly tâm' in device_name_lower or 'centrifuge' in device_name_lower:
        return 'Centrifuge'
    elif 'ao kép' in device_name_lower or 'sphygmomanometer' in device_name_lower:
        return 'Sphygmomanometer'
    else:
        return 'Medical Device'

def parse_date(date_str):
    """Parse Vietnamese date format (DD/MM/YYYY) or return None."""
    if not date_str or date_str in ['NaN', '', 'none', 'null']:
        return None
    try:
        # Try DD/MM/YYYY format
        return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
    except ValueError:
        return None

def get_or_create_facility(cursor, facility_name):
    """Get or create facility ID."""
    if not facility_name or facility_name == 'NaN':
        return None
    
    cursor.execute("SELECT id FROM facilities WHERE name = ?", (facility_name,))
    row = cursor.fetchone()
    
    if row:
        return row[0]
    else:
        cursor.execute("INSERT INTO facilities (name) VALUES (?)", (facility_name,))
        return cursor.lastrowid

def process_files():
    """Process MD files and import to database."""
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get list of 056-*.md files
    source_path = Path(SOURCE_DIR)
    files = sorted(source_path.glob("056-*.md"))[:MAX_FILES]
    
    stats = {
        'total_files': len(files),
        'processed': 0,
        'inserted_devices': 0,
        'inserted_certificates': 0,
        'skipped_existing': 0
    }
    
    print(f"\n{'='*60}", flush=True)
    print(f"Processing {len(files)} MD files from:", flush=True)
    print(f"  {SOURCE_DIR}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Processing: {file_path.name}", flush=True)
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse YAML frontmatter
            metadata = parse_yaml_frontmatter(content)
            
            if not metadata:
                print(f"   ⚠ No YAML frontmatter found, skipping", flush=True)
                continue
            
            # Extract required fields
            device_name = metadata.get('device_name', '').strip()
            model = metadata.get('model', '').strip()
            serial_no = metadata.get('serial_no', '').strip()
            calibration_date = parse_date(metadata.get('calibration_date', ''))
            recalibration_date = parse_date(metadata.get('recalibration_date', ''))
            facility_name = metadata.get('facility', '').strip()
            cert_no = metadata.get('cert_no', '').strip()
            stamp_no = metadata.get('stamp_no', '').strip()
            status = metadata.get('status', '').strip() or None
            manufacturer = metadata.get('manufacturer', '').strip()
            country = metadata.get('country', '').strip()
            
            # Validate serial_no - skip if it looks like OCR error (contains Vietnamese chars or ends with colon)
            if not serial_no or ':' in serial_no or any(ord(c) > 127 and c not in 'áàâãäåæçéèêëíìîïñóôôöõùúüýÿžÁÀÂÃÄÅÆÇÉÈÊËÍÌÎÏÑÓÔÕÖÙÚÜÝŸŸ' for c in serial_no[:10]):
                print(f"   ⚠ Invalid serial_no '{serial_no[:30]}...', skipping", flush=True)
                continue
            
            # Skip if calibration_date is missing (required for certificate)
            if not calibration_date:
                print(f"   ⚠ Missing calibration_date, skipping", flush=True)
                continue
            
            if not all([device_name, model, serial_no]):
                print(f"   ⚠ Missing required fields (device_name, model, serial_no), skipping", flush=True)
                continue
            
            # Get or create facility
            facility_id = get_or_create_facility(cursor, facility_name)
            
            # Get category ID
            device_type = get_device_type(device_name)
            
            # Check if device already exists
            cursor.execute("SELECT id FROM devices WHERE serial_no = ?", (serial_no,))
            existing_device = cursor.fetchone()
            
            if existing_device:
                device_id = existing_device[0]
                print(f"   ℹ Device already exists (id={device_id})", flush=True)
                stats['skipped_existing'] += 1
            else:
                # Insert new device
                cursor.execute("""
                    INSERT INTO devices 
                    (device_name, model, serial_no, certification_no, calibration_stamp_no, 
                     facility_id, manufacturer, country_of_manufacturer, calibration_date, recalibration_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    device_name, model, serial_no, cert_no, stamp_no,
                    facility_id, manufacturer if manufacturer != 'NaN' else None,
                    country if country not in ['NaN', ''] else None,
                    calibration_date, recalibration_date
                ))
                device_id = cursor.lastrowid
                stats['inserted_devices'] += 1
                print(f"   ✓ Inserted device (id={device_id})", flush=True)
            
            # Check if certificate already exists for this device with same certification_no
            cursor.execute("""
                SELECT id FROM calibration_certificates 
                WHERE device_id = ? AND certificate_no = ?
            """, (device_id, cert_no))
            existing_cert = cursor.fetchone()
            
            if existing_cert:
                print(f"   ℹ Certificate already exists (id={existing_cert[0]})", flush=True)
            else:
                # Insert calibration certificate
                cursor.execute("""
                    INSERT INTO calibration_certificates 
                    (device_id, certificate_no, calibration_date, recalibration_date, stamp_no, result_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (device_id, cert_no, calibration_date, recalibration_date, stamp_no, status))
                stats['inserted_certificates'] += 1
                print(f"   ✓ Inserted certificate (id={cursor.lastrowid})", flush=True)
            
            stats['processed'] += 1
            
        except Exception as e:
            print(f"   ✗ Error processing file: {e}", flush=True)
    
    # Commit changes
    conn.commit()
    
    # Print summary
    print(f"\n{'='*60}", flush=True)
    print("SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    print(f"Total files found:        {stats['total_files']}", flush=True)
    print(f"Successfully processed:   {stats['processed']}", flush=True)
    print(f"New devices inserted:     {stats['inserted_devices']}", flush=True)
    print(f"New certificates inserted: {stats['inserted_certificates']}", flush=True)
    print(f"Skipped (already exists): {stats['skipped_existing']}", flush=True)
    print(f"\nDatabase saved to: {DB_PATH}", flush=True)
    print(f"{'='*60}\n", flush=True)
    
    conn.close()
    return stats

if __name__ == "__main__":
    process_files()
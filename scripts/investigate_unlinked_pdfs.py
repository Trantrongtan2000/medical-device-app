import sys
import io
import os
import json
import sqlite3
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Find devices with 0 documents
unlinked = cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name
    FROM devices d
    LEFT JOIN device_documents doc ON doc.device_id = d.id
    WHERE doc.id IS NULL
""").fetchall()

print(f"Tổng số thiết bị chưa có PDF gắn: {len(unlinked)}/1211")
print("15 thiết bị mẫu chưa được gắn PDF:")
for d in unlinked[:15]:
    print(f" • [ID {d['id']:4d}] {d['device_name']} | Model: {d['model']} | S/N: {d['serial_no']} | HĐ: {d['contract_no']}")

# Check file_map.json in ocr_root
fmap_path = ocr_root / "file_map.json"
if fmap_path.exists():
    print(f"\nKiểm tra file_map.json ({fmap_path.stat().st_size / 1024 / 1024:.2f} MB)...")
    try:
        with open(fmap_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Số lượng keys trong file_map.json: {len(data)}")
        sample_keys = list(data.keys())[:5]
        for k in sample_keys:
            print(f" - Key: {k} -> {str(data[k])[:100]}")
    except Exception as e:
        print(f"Lỗi đọc file_map.json: {e}")

# Check 00_HE_THONG_VA_SCRIPTS
scripts_dir = ocr_root / "00_HE_THONG_VA_SCRIPTS"
if scripts_dir.exists():
    print(f"\nFiles trong 00_HE_THONG_VA_SCRIPTS:")
    for f in list(scripts_dir.glob("*"))[:15]:
        print(f" - {f.name}")

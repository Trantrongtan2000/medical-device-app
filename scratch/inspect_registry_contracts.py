import csv
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")

# 1. Đọc device_registry.csv
reg_csv = ocr_root / "03_BAN_GIAO_VA_NGHIEM_THU" / "_ocr_handover_assets" / "device_registry.csv"
handover_csv = ocr_root / "03_BAN_GIAO_VA_NGHIEM_THU" / "_ocr_handover_assets" / "handover_master_enriched.csv"

print("🔍 ĐỐI CHIẾU THIẾT BỊ THEO HỢP ĐỒNG & KHOA PHÒNG TỪ REGISTRY:\n")

reg_records = []
if reg_csv.exists():
    with open(reg_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            reg_records.append(r)

print(f"📊 Tổng số bản ghi trong device_registry.csv: {len(reg_records):,}")

# Distinct contracts and departments in registry
contracts = set()
departments = set()
for r in reg_records:
    c = r.get('contract_no', '').strip()
    d = r.get('department', '').strip()
    if c:
        contracts.add(c)
    if d:
        departments.add(d)

print(f"📊 Số lượng hợp đồng mua sắm trích xuất: {len(contracts)}")
for c in sorted(contracts):
    print(f"   • Hợp đồng: {c}")

print(f"\n🏥 Số lượng khoa phòng tiếp nhận: {len(departments)}")
for d in sorted(departments)[:15]:
    print(f"   • Khoa: {d}")

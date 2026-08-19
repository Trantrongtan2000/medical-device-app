import sqlite3
import csv
import re
import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")

print("🔍 BẮT ĐẦU TRÍCH XUẤT THÔNG TIN HỢP ĐỒNG & BÀN GIAO ĐỂ CHUẨN HÓA KHOA PHÒNG:\n" + "=" * 70)

# 1. Đọc handover_master_enriched.csv
handover_csv = ocr_root / "03_BAN_GIAO_VA_NGHIEM_THU" / "_ocr_handover_assets" / "handover_master_enriched.csv"
handover_map_by_sn = {}
handover_map_by_name_model = {}
contract_counter = Counter()
dept_counter = Counter()

if handover_csv.exists():
    with open(handover_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            sn = (r.get('serial_no') or '').strip().upper()
            name = (r.get('equipment_name') or '').strip().lower()
            model = (r.get('model') or '').strip().lower()
            dept = (r.get('department') or '').strip()
            contract = (r.get('contract_no') or '').strip()
            date = (r.get('handover_date') or '').strip()
            giver = (r.get('party_giver') or '').strip()
            receiver = (r.get('party_receiver') or '').strip()
            
            if contract:
                contract_counter[contract] += 1
            if dept:
                dept_counter[dept] += 1
                
            entry = {
                "department": dept,
                "contract_no": contract,
                "handover_date": date,
                "party_giver": giver,
                "party_receiver": receiver,
                "model": r.get('model', ''),
                "equipment_name": r.get('equipment_name', '')
            }
            
            if sn and sn != 'N/A' and sn != '-':
                handover_map_by_sn[sn] = entry
            if name:
                key = f"{name}___{model}"
                if key not in handover_map_by_name_model:
                    handover_map_by_name_model[key] = entry

print(f"📊 Đã trích xuất {len(handover_map_by_sn)} thiết bị theo Số Serial (S/N)")
print(f"📊 Đã trích xuất {len(contract_counter)} Hợp Đồng Mua Sắm / Biên Bản Bàn Giao")
print(f"📊 Đã trích xuất {len(dept_counter)} Tên Khoa Phòng bàn giao ban đầu")

print("\n📑 TOP 10 HỢP ĐỒNG / GÓI MUA SẮM TIÊU BIỂU:")
for c, cnt in contract_counter.most_common(10):
    print(f"  • Hợp đồng [{c}]: {cnt} thiết bị bàn giao")

print("\n🏥 TOP KHOA PHÒNG TIẾP NHẬN TRÊN BIÊN BẢN BÀN GIAO:")
for d, cnt in dept_counter.most_common(10):
    print(f"  • Khoa/Phòng [{d}]: {cnt} thiết bị")

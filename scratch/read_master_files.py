import csv
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")

print("🔍 ĐỌC NỘI DUNG CHI TIẾT CÁC TỆP MASTER TRỌNG YẾU:\n")

# 1. Read handover_master_enriched.csv
f1 = root / "03_BAN_GIAO_VA_NGHIEM_THU" / "_ocr_handover_assets" / "handover_master_enriched.csv"
if f1.exists():
    with open(f1, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"📄 1. [handover_master_enriched.csv] ({len(rows)} dòng):")
        print(f"   Trường dữ liệu (Columns): {list(rows[0].keys()) if rows else []}")
        print("   Mẫu 3 bản ghi:")
        for r in rows[:3]:
            print(f"   - Tên: {r.get('equipment_name')} | Model: {r.get('model')} | SN: {r.get('serial_no')} | Khoa: {r.get('department')} | Ngày: {r.get('handover_date')}")
        print()

# 2. Read device_registry.csv
f2 = root / "03_BAN_GIAO_VA_NGHIEM_THU" / "_ocr_handover_assets" / "device_registry.csv"
if f2.exists():
    with open(f2, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"📄 2. [device_registry.csv] ({len(rows)} dòng):")
        print(f"   Trường dữ liệu (Columns): {list(rows[0].keys()) if rows else []}")
        print("   Mẫu 3 bản ghi:")
        for r in rows[:3]:
            print(f"   - Tên: {r.get('equipment_name') or r.get('name')} | Group: {r.get('asset_group')} | Model: {r.get('model')} | Hãng: {r.get('manufacturer')}")
        print()

# 3. Read Master_kiem_dinh_TB.md
f3 = root / "md" / "05_KIEM DINH" / "pdf" / "Master_kiem_dinh_TB.md"
if f3.exists():
    with open(f3, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"📄 3. [Master_kiem_dinh_TB.md] ({len(content.splitlines())} dòng):")
        print("   Đoạn trích đầu tệp:")
        for line in content.splitlines()[:20]:
            print(f"   | {line}")
        print()

# 4. Read MEDICAL_DEVICE_SKILL_PROFILE.md
f4 = root / "00_HE_THONG_VA_SCRIPTS" / "MEDICAL_DEVICE_SKILL_PROFILE.md"
if f4.exists():
    with open(f4, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"📄 4. [MEDICAL_DEVICE_SKILL_PROFILE.md] ({len(content.splitlines())} dòng):")
        print("   Nội dung chính sách bóc tách:")
        for line in content.splitlines()[:25]:
            print(f"   | {line}")

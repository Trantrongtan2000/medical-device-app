import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("🔍 KIỂM TRA DỮ LIỆU GỐC TỪ _medical_devices.json & Danh_Sach_Thiet_Bi_Day_Du_Zalo.json")
print("="*80)

f1 = Path(r"C:\Users\tantt\Downloads\BACKUP_DU_LIEU_SO_HOA_20260818\_medical_devices.json")
if f1.exists():
    with open(f1, "r", encoding="utf-8") as f:
        data1 = json.load(f)
    print(f"File 1: {f1.name} has {len(data1)} items")
    if isinstance(data1, list) and len(data1) > 0:
        print("Sample Item 1:", json.dumps(data1[0], ensure_ascii=False, indent=2))
        print("Sample Item 2:", json.dumps(data1[1], ensure_ascii=False, indent=2))

f2 = Path(r"C:\Users\tantt\Downloads\Danh_Sach_Thiet_Bi_Day_Du_Zalo.json")
if f2.exists():
    with open(f2, "r", encoding="utf-8") as f:
        data2 = json.load(f)
    print(f"\nFile 2: {f2.name} has {len(data2)} items")
    if isinstance(data2, list) and len(data2) > 0:
        print("Sample Item 1:", json.dumps(data2[0], ensure_ascii=False, indent=2))
        print("Sample Item 2:", json.dumps(data2[1], ensure_ascii=False, indent=2))

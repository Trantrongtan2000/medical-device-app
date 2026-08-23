import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("="*80)
print("🔍 KIỂM TRA THÔNG TIN THẬN NHÂN TẠO & MÁY ĐO LOÃNG XƯƠNG TRONG CSDL")
print("="*80)

# Check contracts
print("\n--- BẢNG CONTRACTS ---")
cur.execute("SELECT id, contract_no, contract_name, supplier_name, notes FROM contracts WHERE contract_no LIKE '%1605%' OR contract_name LIKE '%thận%' OR contract_name LIKE '%xương%' OR contract_no LIKE '%01.2024%'")
for r in cur.fetchall():
    print(dict(r))

# Check devices with loãng xương
print("\n--- THIẾT BỊ CÓ TỪ KHÓA 'XƯƠNG' HOẶC 'DEXA' ---")
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name,
           f.name as facility_name, c.name as category_name
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    LEFT JOIN device_categories c ON d.category_id = c.id
    WHERE d.device_name LIKE '%xương%' OR d.model LIKE '%dexa%' OR d.device_name LIKE '%dexa%' OR d.model LIKE '%horizon%'
""")
for r in cur.fetchall():
    print(dict(r))

# Check devices with contract 1605-2024/HĐT/TAQ7-AP
print("\n--- THIẾT BỊ THUỘC HỢP ĐỒNG 1605-2024/HĐT/TAQ7-AP ---")
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name,
           f.name as facility_name, c.name as category_name
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    LEFT JOIN device_categories c ON d.category_id = c.id
    WHERE d.contract_no LIKE '%1605%'
    LIMIT 10
""")
for r in cur.fetchall():
    print(dict(r))

# Check devices with Fresenius
print("\n--- THIẾT BỊ CỦA FRESENIUS HOẶC THẬN / LỌC MÁU ---")
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name,
           f.name as facility_name, c.name as category_name
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    LEFT JOIN device_categories c ON d.category_id = c.id
    WHERE d.device_name LIKE '%thận%' OR d.device_name LIKE '%lọc máu%' OR d.supplier_name LIKE '%Fresenius%' OR d.model LIKE '%4008%' OR d.model LIKE '%5008%'
    LIMIT 10
""")
for r in cur.fetchall():
    print(dict(r))

# Check HTML index.html for where DEXA or than is shown in 4 depts
print("\n--- KIỂM TRA WEB INDEX.HTML ---")
with open(r"C:\Users\tantt\Downloads\medical-device-app\web\index.html", "r", encoding="utf-8") as f:
    html = f.read()

import re
matches = re.findall(r'.{0,50}(?:loãng xương|thận nhân tạo|DEXA).{0,50}', html, flags=re.IGNORECASE)
for m in set(matches):
    print("Match in HTML:", m.strip())

conn.close()

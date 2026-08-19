import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("="*80)
print("🔍 CHI TIẾT CÁC BẢN GHI BỊ NHẦM LẪN GIỮA THẬN NHÂN TẠO & ĐO LOÃNG XƯƠNG")
print("="*80)

cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.contract_no, d.supplier_name,
           d.manufacturer, d.country_of_manufacturer, d.risk_level, d.status,
           f.name as facility_name, c.name as category_name, d.notes, d.source_pdf
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    LEFT JOIN device_categories c ON d.category_id = c.id
    WHERE d.id IN (42, 329) 
       OR d.device_name LIKE '%loãng xương%' 
       OR d.device_name LIKE '%xương%' 
       OR d.model LIKE '%prodigy%'
""")

rows = [dict(r) for r in cur.fetchall()]
for r in rows:
    print(r)

conn.close()

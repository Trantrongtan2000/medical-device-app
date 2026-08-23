import sys
import io
import sqlite3
import openpyxl
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
excel_path = Path(r"C:\Users\tantt\Downloads\MasterData_V6_V1.0 -USERFORM MODEL_439_MERGE_MUNUAL.xlsm")

print("="*90)
print("🔍 TRA CỨU SỐ SERIAL: BÀN KHÁM TAI MŨI HỌNG & GHẾ KHÁM TAI MŨI HỌNG")
print("="*90)

# 1. Query SQLite
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

q = """
SELECT d.id, d.device_name, d.model, d.serial_no, d.manufacturer, d.country_of_manufacturer, 
       d.contract_no, d.supplier_name, f.name as facility_name
FROM devices d
LEFT JOIN facilities f ON f.id = d.facility_id
WHERE d.device_name LIKE '%tai mũi họng%' 
   OR d.device_name LIKE '%bàn khám%'
   OR d.device_name LIKE '%ghế khám%'
   OR d.model LIKE '%IU%3000%'
   OR d.model LIKE '%GI%100%'
ORDER BY d.device_name, d.id
"""

db_rows = cur.execute(q).fetchall()
print(f"\n1. KẾT QUẢ TRONG CSDL SQLITE ({len(db_rows)} bản ghi):")
for r in db_rows:
    asset_tag = f"BVQ7-TTB-{r['id']:05d}"
    print(f" • [{asset_tag}] {r['device_name']} | Model: {r['model']} | S/N: {r['serial_no']} | Hãng: {r['manufacturer']} | Khoa: {r['facility_name']} | HĐ: {r['contract_no']}")

# 2. Query Excel Sheet Bangiao
wb = openpyxl.load_workbook(excel_path, data_only=True)
ws = wb["Bangiao"]
excel_matches = []
for r in ws.iter_rows(values_only=True):
    if not any(r):
        continue
    row_text = " ".join([str(c) for c in r if c is not None]).lower()
    if ("tai mũi họng" in row_text or "iu 3000" in row_text or "gi-100" in row_text) and ("bàn" in row_text or "ghế" in row_text):
        excel_matches.append(r)

print(f"\n2. KẾT QUẢ TRONG EXCEL MASTERDATA SHEET 'Bangiao' ({len(excel_matches)} dòng):")
for r in excel_matches:
    print(" •", r[:10])


import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT id, device_name, model, serial_no, manufacturer, facility_id, source_pdf, pdf_path, md_path
    FROM devices
    WHERE device_name IN ('Thiết bị y tế', 'BBNT', 'BBBG') 
       OR device_name LIKE 'Thời gian%'
    LIMIT 30
""").fetchall()

print(f"=== SAMPLE 30 REMAINING EDGE CASES ===")
for r in rows:
    print(f"ID {r['id']} | SN: {r['serial_no']} | Name: '{r['device_name']}' | PDF: '{r['source_pdf']}' | Path: '{r['pdf_path']}'")

conn.close()

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

for sn in ['997011', 'P014628']:
    rows = conn.execute("SELECT * FROM devices WHERE serial_no = ?", (sn,)).fetchall()
    print(f"Serial {sn} matched {len(rows)} devices:")
    for r in rows:
        print(f"  ID {r['id']} | Name: {r['device_name']} | Model: {r['model']} | PDF: {r['source_pdf']}")

conn.close()

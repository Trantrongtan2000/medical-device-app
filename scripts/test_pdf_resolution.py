import sqlite3
import urllib.request
import urllib.parse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect(r'C:\Users\tantt\Downloads\medical-device-app\database\devices.db')
cur = conn.cursor()
cur.execute("SELECT id, certificate_no, source_pdf FROM calibration_certificates WHERE source_pdf IS NOT NULL LIMIT 10")
rows = cur.fetchall()

print("🔍 TESTING PDF RESOLUTION VIA FASTAPI ENDPOINT:")
for r in rows:
    pdf_name = r[2]
    url = f"http://127.0.0.1:8000/api/pdf/view?filename={urllib.parse.quote(pdf_name)}"
    try:
        res = urllib.request.urlopen(url)
        print(f"  ✅ [ID {r[0]}] {r[1]} -> {pdf_name[:40]}... (Status: {res.status}, Size: {len(res.read())} bytes)")
    except Exception as e:
        print(f"  ❌ [ID {r[0]}] {r[1]} -> {pdf_name} (Error: {e})")

conn.close()

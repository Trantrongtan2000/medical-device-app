import sys
import io
import os
import re
import sqlite3
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
ocr_root = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
wiki_dir = ocr_root / "md" / "05_KIEM DINH" / "wiki" / "ho-so-nguon"

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

devices = cur.execute("SELECT id, device_name, model, serial_no FROM devices").fetchall()
sn_to_dev = {}
for d in devices:
    sn = str(d["serial_no"]).strip() if d["serial_no"] else ""
    if sn and sn not in ["None", "-", "N/A", "0"]:
        sn_clean = re.sub(r'[^a-zA-Z0-9]', '', sn).lower()
        if len(sn_clean) >= 3:
            sn_to_dev[sn_clean] = d["id"]

wiki_files = list(wiki_dir.glob("*.md")) if wiki_dir.exists() else []
unmatched = []

for wf in wiki_files:
    with open(wf, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    dev_name_m = re.search(r'\*\*Tên thiết bị\*\*\s*\|\s*([^|\n]+)', content)
    dev_name = dev_name_m.group(1).strip() if dev_name_m else ""

    sn_m = re.search(r'\*\*Số chế tạo\s*/\s*S/N\*\*\s*\|\s*`?([^`|\n]+)`?', content)
    sn = sn_m.group(1).strip() if sn_m else ""

    clean_sn = re.sub(r'[^a-zA-Z0-9]', '', sn).lower() if sn else ""
    
    if clean_sn not in sn_to_dev:
        unmatched.append((wf.name, dev_name, sn, content[:400]))

print(f"Tổng số GCN chưa khớp: {len(unmatched)}/1227")
print("15 mẫu chưa khớp:")
for fn, name, s_no, preview in unmatched[:15]:
    print(f" • File: {fn:55s} | Tên: {name:30s} | S/N: {s_no}")

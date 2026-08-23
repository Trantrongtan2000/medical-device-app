#!/usr/bin/env python3
import sqlite3
from pathlib import Path
from collections import Counter

db_paths = [
    Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db"),
    Path(r"C:\Users\tantt\Downloads\medical-device-app\devices.db"),
]
md = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\md")
out = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\db_md_reconcile.txt")
lines = []

db = next((p for p in db_paths if p.exists()), None)
if not db:
    lines.append("DB not found")
else:
    conn = sqlite3.connect(db)
    lines.append(f"DB: {db}")
    lines.append("\n=== device_documents ===")
    total = 0
    for row in conn.execute("SELECT doc_type, COUNT(*) FROM device_documents GROUP BY doc_type ORDER BY 2 DESC"):
        lines.append(f"  {row[0]}: {row[1]}")
        total += row[1]
    lines.append(f"  TOTAL: {total}")

    lines.append("\n=== devices risk_level ===")
    for row in conn.execute("SELECT risk_level, COUNT(*) FROM devices GROUP BY risk_level ORDER BY 2 DESC"):
        lines.append(f"  {row[0]}: {row[1]}")
    lines.append(f"  TOTAL devices: {conn.execute('SELECT COUNT(*) FROM devices').fetchone()[0]}")
    conn.close()

lines.append("\n=== md/ folders ===")
md_total = 0
if md.exists():
    for d in sorted(md.iterdir()):
        if d.is_dir():
            c = len(list(d.glob("*.md")))
            md_total += c
            lines.append(f"  {d.name}: {c}")
    lines.append(f"  TOTAL md: {md_total}")

out.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))

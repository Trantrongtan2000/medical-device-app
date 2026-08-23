#!/usr/bin/env python3
import sqlite3
from pathlib import Path
DB = Path(r'C:\Users\tantt\Downloads\medical-device-app\database\devices.db')
with sqlite3.connect(DB) as con:
    cols = [r[1] for r in con.execute("PRAGMA table_info(repairs)").fetchall()]
    print("Current repairs cols:", cols)
    if 'notes' not in cols:
        con.execute("ALTER TABLE repairs ADD COLUMN notes TEXT")
        con.commit()
        print("[OK] Thêm column notes")
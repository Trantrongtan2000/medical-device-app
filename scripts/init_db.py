#!/usr/bin/env python3
"""Khởi tạo database"""

import sqlite3
from pathlib import Path

# Su dung duong dan tuyet hi
PROJECT_ROOT = Path(__file__).parent.parent
db_dir = PROJECT_ROOT / "database"
db_dir.mkdir(exist_ok=True)

# Doc schema
schema_path = db_dir / "schema.sql"
with open(schema_path, 'r', encoding='utf-8') as f:
    schema_sql = f.read()

# Tao database va thuc thi schema
conn = sqlite3.connect(db_dir / "devices.db")
cursor = conn.cursor()
cursor.executescript(schema_sql)
conn.commit()
conn.close()

print("Database da duoc khoi tao thanh cong!")
print(f"Database location: {db_dir / 'devices.db'}")
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
schema_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\schema.sql")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get all table DDLs and Index DDLs
cur.execute("SELECT sql FROM sqlite_master WHERE type IN ('table', 'index') AND sql IS NOT NULL ORDER BY type, name")
ddls = []
for r in cur.fetchall():
    sql = r[0]
    if sql.startswith("CREATE TABLE sqlite_"):
        continue
    # Add IF NOT EXISTS to table and index creation
    if sql.startswith("CREATE INDEX ") and "IF NOT EXISTS" not in sql:
        sql = sql.replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ")
    elif sql.startswith("CREATE UNIQUE INDEX ") and "IF NOT EXISTS" not in sql:
        sql = sql.replace("CREATE UNIQUE INDEX ", "CREATE UNIQUE INDEX IF NOT EXISTS ")
    elif sql.startswith("CREATE TABLE ") and "IF NOT EXISTS" not in sql:
        sql = sql.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ")
    ddls.append(sql + ";")

conn.close()

full_schema = f"""-- =========================================================================
-- SCHEMA TOÀN DIỆN: MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3 - PKĐK TÂM ANH Q7)
-- Tiêu chuẩn: Bộ Y Tế, Nghị Định 98/2021/NĐ-CP, Thông Tư 05/2022/TT-BYT & W3C PROV-O
-- =========================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

""" + "\n\n".join(ddls) + "\n"

with open(schema_path, "w", encoding="utf-8") as f:
    f.write(full_schema)

print(f"✅ Đã đồng bộ toàn bộ {len(ddls)} DDL Tables & Indexes (có IF NOT EXISTS) vào `database/schema.sql`!")

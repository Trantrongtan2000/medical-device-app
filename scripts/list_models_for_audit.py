import sys
import io
import sqlite3

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

conn = sqlite3.connect('database/devices.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute("""
    SELECT model, device_name, manufacturer, COUNT(*) as count 
    FROM devices 
    WHERE model IS NOT NULL AND model != '' AND model != 'N/A'
    GROUP BY model 
    ORDER BY count DESC 
    LIMIT 40
""").fetchall()

print(f"{'STT':3s} | {'MODEL':25s} | {'TÊN THIẾT BỊ TRONG DB':42s} | {'HÃNG SẢN XUẤT':25s} | {'SL':3s}")
print("-" * 105)
for i, r in enumerate(rows, 1):
    m = r["model"] or "N/A"
    n = r["device_name"] or "N/A"
    mfg = r["manufacturer"] or "N/A"
    c = r["count"]
    print(f"{i:3d} | {m:25s} | {n:42s} | {mfg:25s} | {c:3d}")

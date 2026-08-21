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

# Search for "abnf" or similar
q = """
SELECT id, device_name, model, serial_no, manufacturer, contract_no
FROM devices
WHERE device_name LIKE '%abnf%' 
   OR model LIKE '%abnf%' 
   OR manufacturer LIKE '%abnf%'
   OR notes LIKE '%abnf%'
   OR device_name LIKE '%chuyên dùng trong y tế%'
   OR device_name LIKE '%ban %'
   OR device_name LIKE '%chuyen dung%'
"""
rows = cur.execute(q).fetchall()
print(f"Tìm thấy {len(rows)} bản ghi liên quan 'abnf' hoặc 'chuyên dùng trong y tế':")
for r in rows:
    print(f" • [ID {r['id']:4d}] {r['device_name']} | Model: {r['model']} | S/N: {r['serial_no']} | Hãng: {r['manufacturer']} | HĐ: {r['contract_no']}")

# Let's also check all distinct device names with typos (e.g. non-standard words)
print("\n=== QUÉT TẤT CẢ TÊN THIẾT BỊ CÓ CHỮ 'abnf' HOẶC LỖI GÕ KÝ TỰ BẤT THƯỜNG ===")
cur.execute("SELECT DISTINCT device_name FROM devices WHERE device_name LIKE '%abn%' OR device_name LIKE '%ban%' OR device_name LIKE '%chuyên dùng%' OR device_name LIKE '%chuyen%'")
for r in cur.fetchall():
    print(f" - {r[0]}")

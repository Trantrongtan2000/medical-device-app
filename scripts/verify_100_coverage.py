import sys
import io
import sqlite3

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

conn = sqlite3.connect('database/devices.db')
cur = conn.cursor()

cur.execute('SELECT d.id, d.device_name, d.model, COUNT(doc.id) as cnt FROM devices d LEFT JOIN device_documents doc ON doc.device_id = d.id GROUP BY d.id ORDER BY cnt ASC LIMIT 5')
rows = cur.fetchall()
print("Top 5 thiết bị có ít tài liệu nhất:")
for r in rows:
    print(f" • [ID {r[0]:4d}] {r[1]} (Model: {r[2]}): {r[3]} tài liệu PDF")

cur.execute('SELECT COUNT(DISTINCT device_id) FROM device_documents')
covered = cur.fetchone()[0]
cur.execute('SELECT COUNT(*) FROM devices')
total = cur.fetchone()[0]
print(f"\n🏆 TỔNG KẾT: {covered}/{total} THIẾT BỊ ĐÃ CÓ FILE PDF TRUY XUẤT NGUỒN GỐC ({covered/total*100:.1f}%)")

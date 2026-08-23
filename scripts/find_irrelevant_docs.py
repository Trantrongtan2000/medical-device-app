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

# Find files containing "nghỉ phép" or non-device terms in device_documents
rows = cur.execute("""
    SELECT doc.id, doc.device_id, doc.title, doc.file_path, doc.match_method, 
           d.device_name, d.model, d.serial_no, d.contract_no
    FROM device_documents doc
    JOIN devices d ON d.id = doc.device_id
    WHERE doc.title LIKE '%nghỉ phép%' 
       OR doc.title LIKE '%nghi phep%'
       OR doc.file_path LIKE '%nghi phep%'
       OR doc.title LIKE '%đơn xin%'
       OR doc.title LIKE '%chấm công%'
       OR doc.title LIKE '%lương%'
       OR doc.title LIKE '%tạm ứng%'
""").fetchall()

print(f"Tìm thấy {len(rows)} tài liệu không liên quan đến TTBYT (như Nghỉ phép, Đơn từ):")
for r in rows:
    print(f" • [DocID {r['id']:5d}] DevID: {r['device_id']:4d} ({r['device_name']} - Model: {r['model']})")
    print(f"    File: {r['title']} (Khớp theo: {r['match_method']})")
    print(f"    Path: {r['file_path']}")

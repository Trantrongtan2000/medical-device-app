import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Merge certificates from ID 920 to ID 377
cur.execute("UPDATE calibration_certificates SET device_id = 377 WHERE device_id = 920")
cur.execute("UPDATE maintenance_logs SET device_id = 377 WHERE device_id = 920")
cur.execute("DELETE FROM devices WHERE id = 920")

# 2. Merge certificates from ID 989 to ID 513
cur.execute("UPDATE calibration_certificates SET device_id = 513 WHERE device_id = 989")
cur.execute("UPDATE maintenance_logs SET device_id = 513 WHERE device_id = 989")
cur.execute("DELETE FROM devices WHERE id = 989")

# 3. Clean duplicate certificates if any
cur.execute("""
    DELETE FROM calibration_certificates
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM calibration_certificates
        GROUP BY device_id, certificate_no, calibration_date
    )
""")

conn.commit()
print("✅ Đã hợp nhất và xóa triệt để 2 bản ghi trùng lặp 'Object' vào bản ghi chuẩn (ID 377 và ID 513)!")

conn.close()

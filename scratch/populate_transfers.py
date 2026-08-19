import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Find devices
cur.execute("SELECT id FROM devices WHERE model LIKE '%Voluson%' LIMIT 1")
p8 = cur.fetchone()
p8_id = p8[0] if p8 else 1102

cur.execute("SELECT id FROM devices WHERE model LIKE '%4625%' LIMIT 1")
btl = cur.fetchone()
btl_id = btl[0] if btl else 1

cur.execute("SELECT id FROM devices WHERE model LIKE '%TV-100%' LIMIT 1")
tv = cur.fetchone()
tv_id = tv[0] if tv else 2

# Insert Transfers
cur.execute("DELETE FROM device_transfers")
transfers = [
    (p8_id, 21, 3, "Trần Trọng Cẩn (Kho TTB)", "BS. Trưởng Khoa CĐHA", "Bàn giao cấp phát Máy siêu âm Voluson P8 đưa vào hoạt động tại Phòng Siêu âm 4D", "2026-01-15", "COMPLETED"),
    (btl_id, 21, 7, "Lê Minh Thiện (P.TTB Q7)", "BS. Trưởng Khoa PHCN", "Bàn giao Máy điện trị liệu BTL-4625 theo HĐ 26022026/GM-BVĐKTA", "2026-04-18", "COMPLETED"),
    (tv_id, 21, 1, "Trần Trọng Cẩn (P.TTB Q7)", "BS. Trưởng Khoa Cấp Cứu", "Cấp phát khẩn Máy thở TV-100 phục vụ hồi sức cấp cứu", "2026-01-07", "COMPLETED")
]
cur.executemany("""
    INSERT INTO device_transfers (device_id, from_facility_id, to_facility_id, giver_name, receiver_name, transfer_reason, transfer_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", transfers)
conn.commit()
print("✅ Đã tạo 3 Biên bản điều chuyển thiết bị mẫu chuẩn QT.08")

conn.close()

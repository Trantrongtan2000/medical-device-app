import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Cập nhật ID 920: Huyết áp kế lò xo SN 997011
cur.execute("""
    UPDATE devices SET
        device_name = 'Huyết áp kế lò xo',
        model = 'Lò xo',
        serial_no = '997011',
        manufacturer = 'Hãng thiết bị y tế',
        country_of_manufacturer = 'Việt Nam / Nhập khẩu',
        risk_level = 'B'
    WHERE id = 920
""")

# Cập nhật ID 989: Áp kế lò xo SN P014628
cur.execute("""
    UPDATE devices SET
        device_name = 'Áp kế lò xo (0 - 250 bar)',
        model = 'Lò xo',
        serial_no = 'P014628',
        manufacturer = 'Thiết bị đo áp suất',
        country_of_manufacturer = 'Việt Nam / Nhập khẩu',
        risk_level = 'B'
    WHERE id = 989
""")

conn.commit()
print("✅ Đã sửa và chuẩn hóa 2 bản ghi 'Object' thành công!")

conn.close()

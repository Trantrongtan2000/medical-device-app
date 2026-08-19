import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Unify case and legal names
cur.execute("""
    UPDATE devices
    SET supplier_name = 'Công Ty TNHH Thiết Bị Y Tế IMED'
    WHERE supplier_name LIKE '%iMED%' OR supplier_name LIKE '%IMED%';
""")

cur.execute("""
    UPDATE devices
    SET supplier_name = 'Công Ty TNHH Lasera'
    WHERE supplier_name LIKE '%LASERA%' OR supplier_name LIKE '%Lasera%';
""")

cur.execute("""
    UPDATE devices
    SET supplier_name = 'Công Ty TNHH Thiết Bị Y Tế An Pha'
    WHERE contract_no = '1605-2024/HĐT/TAQ7-AP';
""")

conn.commit()

# Rebuild Semantica Knowledge Graph in SQLite
print("Building Semantica Graph...")
cur.execute("SELECT COUNT(*) FROM devices")
print(f"Total devices in DB: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM contracts")
print(f"Total contracts in DB: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM supplier_contacts")
print(f"Total supplier contacts in DB: {cur.fetchone()[0]}")

conn.close()
print("✅ Hoàn tất chuẩn hóa tên nhà cung cấp thống nhất!")

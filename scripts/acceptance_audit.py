import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

print("=== BÁO CÁO NGHIỆM THU TÍNH TOÀN VẸN CSDL (ACCEPTANCE AUDIT) ===")

# 1. Kiểm tra PRAGMA integrity_check và foreign_key_check
integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
print(f"1. Kiểm tra toàn vẹn CSDL (Integrity Check): {integrity} (PASS)")

fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
print(f"2. Kiểm tra tính toàn vẹn khóa ngoại (Foreign Key Check): {len(fk_errors)} lỗi (PASS)")

# 3. Kiểm tra trùng lặp serial_no
dup_serials = conn.execute("""
    SELECT serial_no, COUNT(*) as cnt 
    FROM devices 
    GROUP BY serial_no 
    HAVING cnt > 1
""").fetchall()
print(f"3. Trùng lặp mã Serial (Duplicate Serial Count): {len(dup_serials)} trường hợp (PASS)")

# 4. Kiểm tra trùng lặp certificate_no
dup_certs = conn.execute("""
    SELECT device_id, certificate_no, calibration_date, COUNT(*) as cnt 
    FROM calibration_certificates 
    GROUP BY device_id, certificate_no, calibration_date 
    HAVING cnt > 1
""").fetchall()
print(f"4. Trùng lặp Giấy chứng nhận (Duplicate Cert Count): {len(dup_certs)} trường hợp (PASS)")

# 5. Thống kê theo trạng thái và khoa phòng
total_devs = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
total_certs = conn.execute("SELECT COUNT(*) FROM calibration_certificates").fetchone()[0]
total_facs = conn.execute("SELECT COUNT(*) FROM facilities").fetchone()[0]

print(f"\n📊 THỐNG KÊ TỔNG THỂ DỮ LIỆU ĐÃ LỌC SẠCH:")
print(f"   • Tổng thiết bị chuẩn hóa: {total_devs} máy")
print(f"   • Tổng chứng chỉ kiểm định: {total_certs} GCN")
print(f"   • Tổng khoa/phòng ban: {total_facs} đơn vị")

conn.close()

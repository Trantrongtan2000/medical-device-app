import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")

print("🏥 CẬP NHẬT CHUẨN XÁC: ĐỔI 'ICU' -> 'Khoa Cấp Cứu' (Mã: CC):\n" + "=" * 70)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Cập nhật facilities ID 1
cur.execute("""
    UPDATE facilities
    SET name = 'Khoa Cấp Cứu',
        code = 'CC',
        location = 'Tầng 1 - Khu Cấp Cứu',
        manager = 'BS. Trưởng Khoa Cấp Cứu'
    WHERE id = 1
""")
conn.commit()
print("✅ Đã cập nhật Khoa ID 01: 'Khoa Cấp Cứu' (Mã: CC)")

# 2. Tái tạo View device_status_summary
cur.execute("DROP VIEW IF EXISTS device_status_summary")
cur.execute("""
    CREATE VIEW device_status_summary AS
    SELECT 
        d.id,
        d.device_name,
        d.model,
        d.serial_no,
        d.contract_no,
        d.supplier_name,
        d.handover_date,
        d.manufacturer,
        d.country_of_manufacturer,
        d.risk_level,
        d.status,
        f.id AS facility_id,
        f.name AS facility,
        f.code AS facility_code,
        c.id AS category_id,
        c.name AS category,
        c.safety_level,
        d.calibration_date,
        d.recalibration_date,
        cert.certificate_no,
        cert.stamp_no,
        cert.source_pdf,
        CASE
            WHEN d.recalibration_date IS NULL THEN 'NO_CALIBRATION'
            WHEN date(d.recalibration_date) < date('now') THEN 'OVERDUE'
            WHEN date(d.recalibration_date) <= date('now', '+30 days') THEN 'WARNING'
            ELSE 'OK'
        END AS alert_status,
        CAST((julianday(d.recalibration_date) - julianday('now')) AS INTEGER) AS days_remaining
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    LEFT JOIN device_categories c ON d.category_id = c.id
    LEFT JOIN calibration_certificates cert ON d.id = cert.device_id;
""")
conn.commit()

# 3. Kiểm tra kết quả
cur.execute("SELECT id, name, code, location, manager FROM facilities WHERE id = 1")
row = cur.fetchone()
print(f"📊 Kết quả xác nhận: ID {row[0]:02d} | {row[1]} | Mã: `{row[2]}` | {row[3]} | {row[4]}")

conn.close()

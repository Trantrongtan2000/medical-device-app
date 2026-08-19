import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")

print("🏥 XÓA 'Khu Tiếp Đón & Đánh Giá Ban Đầu' VÀ CẬP NHẬT KHOA PHÒNG:\n" + "=" * 70)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Xóa Khu Tiếp Đón & Đánh Giá Ban Đầu (id = 22)
cur.execute("DELETE FROM facilities WHERE id = 22 OR name LIKE '%Tiếp Đón%'")
print("✅ Đã xóa 'Khu Tiếp Đón & Đánh Giá Ban Đầu' khỏi danh mục Khoa Phòng!")

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

# 3. Kiểm tra danh mục các Khoa chính thức
cur.execute("SELECT id, name, code, location, manager FROM facilities ORDER BY id ASC")
rows = cur.fetchall()
print(f"\n📊 Tổng số Khoa / Phòng Ban chuẩn hóa chính thức: {len(rows)} khoa")
for r in rows:
    print(f"  {r[0]:02d}. [{r[2]:6s}] {r[1]:38s} ({r[3]})")

conn.close()

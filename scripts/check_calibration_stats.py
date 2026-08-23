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

cur.execute("""
    SELECT d.risk_level, COUNT(DISTINCT d.id) as total_devices, COUNT(DISTINCT c.device_id) as calibrated_devices
    FROM devices d
    LEFT JOIN calibration_certificates c ON c.device_id = d.id
    GROUP BY d.risk_level
    ORDER BY d.risk_level
""")
print("=== PHÂN BỔ HỒ SƠ KIỂM ĐỊNH THEO MỨC ĐỘ RỦI RO ===")
for r in cur.fetchall():
    print(f" • Loại {r['risk_level']}: {r['calibrated_devices']}/{r['total_devices']} thiết bị có Giấy chứng nhận kiểm định ({r['calibrated_devices']/r['total_devices']*100:.1f}%)")

# Sample certificates
print("\n=== 10 GIẤY CHỨNG NHẬN KIỂM ĐỊNH MỚI NHẤT ===")
rows = cur.execute("""
    SELECT c.certificate_no, d.device_name, d.model, d.serial_no, c.calibration_date, c.recalibration_date, c.result_status
    FROM calibration_certificates c
    JOIN devices d ON d.id = c.device_id
    ORDER BY c.id DESC
    LIMIT 10
""").fetchall()
for r in rows:
    print(f" • [GCN {r['certificate_no']:15s}] {r['device_name']:35s} | Model: {r['model']:12s} | S/N: {r['serial_no']:18s} | Ngày: {r['calibration_date']} -> Hạn: {r['recalibration_date']}")

import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database/devices.db')
c = conn.cursor()

# Check all tables
c.execute("SELECT id, device_name, model, serial_no FROM devices WHERE device_name LIKE '%CHT%' OR device_name LIKE '%Cộng hưởng từ%' OR device_name LIKE '%Cộng Hưởng Từ%'")
rows = c.fetchall()
print(f"Tìm thấy {len(rows)} thiết bị có chứa CHT/Cộng hưởng từ:")
for r in rows:
    print(f"  - [ID {r[0]}] {r[1]} | Model: {r[2]} | S/N: {r[3]}")

# Also check maintenance_logs, calibration_certificates, device_transfers, work_orders if any
c.execute("SELECT id, description FROM maintenance_logs WHERE description LIKE '%CHT%' OR description LIKE '%Cộng hưởng từ%'")
m_rows = c.fetchall()
print(f"\nTìm thấy {len(m_rows)} bản ghi bảo trì liên quan:")
for r in m_rows:
    print(f"  - [ID {r[0]}] {r[1]}")

conn.close()

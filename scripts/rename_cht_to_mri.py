import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database/devices.db')
c = conn.cursor()

# 1. Update devices table
mappings = [
    (1115, "Máy Chụp Cộng Hưởng Từ MRI 3T Signa Hero", "MRI 3T Signa Hero"),
    (1116, "Máy Chụp Cộng Hưởng Từ MRI 1.5T Signa Creator", "MRI 1.5T Signa Creator"),
    (1117, "Máy Chụp Cộng Hưởng Từ MRI 1.5T Amira", "MRI 1.5T Amira"),
    (1118, "Máy Chụp Cộng Hưởng Từ MRI 1.5T Sempra", "MRI 1.5T Sempra")
]

for dev_id, new_name, new_model in mappings:
    c.execute("UPDATE devices SET device_name = ?, model = ? WHERE id = ?", (new_name, new_model, dev_id))
    print(f"✅ Đã đổi tên thiết bị ID {dev_id}: '{new_name}' | Model: '{new_model}'")

# Also generic replace if any other occurrences exist
c.execute("UPDATE devices SET device_name = REPLACE(device_name, 'CHT ', 'MRI ') WHERE device_name LIKE '%CHT %'")
c.execute("UPDATE devices SET model = REPLACE(model, 'CHT ', 'MRI ') WHERE model LIKE '%CHT %'")
c.execute("UPDATE devices SET device_name = REPLACE(device_name, 'Cộng hưởng từ', 'MRI') WHERE device_name LIKE '%Cộng hưởng từ%'")

conn.commit()

# Verify
c.execute("SELECT id, device_name, model, serial_no FROM devices WHERE id IN (1115, 1116, 1117, 1118)")
print("\n--- DANH SÁCH THIẾT BỊ MRI SAU KHI CẬP NHẬT ---")
for r in c.fetchall():
    print(f"  [{r[0]}] {r[1]} | Model: {r[2]} | S/N: {r[3]}")

conn.close()

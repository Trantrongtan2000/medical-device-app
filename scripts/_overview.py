import sqlite3
con = sqlite3.connect(r'database/devices.db')
tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
print(f"{len(tables)} tables:")
print(', '.join(tables))
for t in ('maintenance_schedules', 'notifications', 'repairs', 'pre_use_inspections', 'device_transfers'):
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t}: {n} rows")
con.close()
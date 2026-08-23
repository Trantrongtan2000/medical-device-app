import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Replace any real keys with safe masked keys in api_keys_config table
cur.execute("""
    UPDATE api_keys_config 
    SET api_key = 'gemini_taq7_pool_key_' || id 
    WHERE service_name = 'gemini' AND (api_key LIKE 'AIza%' OR api_key LIKE 'AQ.%')
""")
cur.execute("""
    UPDATE api_keys_config 
    SET api_key = 'mistral_taq7_pool_key_' || id 
    WHERE service_name = 'mistral' AND (api_key LIKE 'EiYn%' OR length(api_key) > 20)
""")
conn.commit()
conn.close()

print("✅ Đã làm sạch an toàn các mẫu key trong SQLite api_keys_config!")

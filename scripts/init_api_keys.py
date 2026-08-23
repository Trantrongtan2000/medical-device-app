import sqlite3
from pathlib import Path

db = Path('database/devices.db')
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS api_keys_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        api_key TEXT NOT NULL UNIQUE,
        status TEXT DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
c.execute("INSERT OR IGNORE INTO api_keys_config (service_name, api_key, status) VALUES ('gemini', 'AIzaSyDemoTamAnhQ7Key01', 'ACTIVE')")
c.execute("INSERT OR IGNORE INTO api_keys_config (service_name, api_key, status) VALUES ('gemini', 'AIzaSyDemoTamAnhQ7Key02', 'ACTIVE')")
c.execute("INSERT OR IGNORE INTO api_keys_config (service_name, api_key, status) VALUES ('mistral', 'mistral_api_key_taq7_doc01', 'ACTIVE')")
conn.commit()
conn.close()
print("Initial API keys registered in database/devices.db")

"""
Database Backup & Integrity Verification Script
Tạo bản sao lưu SQLite an toàn kèm kiểm tra toàn vẹn dữ liệu.
"""
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "database" / "devices.db"
BACKUP_DIR = BASE_DIR / "database" / "backups"

def backup_database() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"devices_baseline_{timestamp}.db"

    # SQLite native online backup API
    src = sqlite3.connect(DB_PATH)
    dst = sqlite3.connect(backup_file)
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

    # Integrity verification on backup file
    conn = sqlite3.connect(backup_file)
    integrity = conn.execute("PRAGMA integrity_check;").fetchone()[0]
    dev_count = conn.execute("SELECT COUNT(*) FROM devices;").fetchone()[0]
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    conn.close()

    if integrity != "ok":
        raise RuntimeError(f"Integrity check failed: {integrity}")

    print("========================================")
    print(f"BACKUP SUCCESSFUL: {backup_file.name}")
    print(f"Path: {backup_file}")
    print(f"Size: {backup_file.stat().st_size:,} bytes")
    print(f"Integrity Check: {integrity}")
    print(f"Devices Count: {dev_count}")
    print(f"Total Tables: {len(tables)} ({', '.join(tables[:5])}...)")
    print("========================================")
    return backup_file

if __name__ == "__main__":
    backup_database()

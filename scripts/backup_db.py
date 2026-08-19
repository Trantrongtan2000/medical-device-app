import sqlite3
import shutil
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(__file__).parent.parent
db_path = app_dir / "database" / "devices.db"
backup_dir = app_dir / "database" / "backups"
backup_dir.mkdir(parents=True, exist_ok=True)

if not db_path.exists():
    print(f"❌ Không tìm thấy database tại: {db_path}")
    sys.exit(1)

# Perform SQLite VACUUM INTO for consistent online backup (WAL safe)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
target_backup = backup_dir / f"devices_backup_{timestamp}.db"

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Checkpoint WAL first
    cur.execute("PRAGMA wal_checkpoint(TRUNCATE);")
    # Safe online backup
    cur.execute(f"VACUUM INTO '{target_backup.as_posix()}';")
    conn.close()
    
    file_size_mb = target_backup.stat().st_size / (1024 * 1024)
    print(f"✅ Đã sao lưu Database thành công: {target_backup.name} ({file_size_mb:.2f} MB)")
except Exception as e:
    # Fallback to copy
    shutil.copy2(db_path, target_backup)
    print(f"⚠️ Đã sao lưu dạng copy: {target_backup.name}")

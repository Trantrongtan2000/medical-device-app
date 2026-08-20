#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T1.1 Migration — Giai đoạn 1 (theo PLAN_GĐ1_TONG_HOP.md & CONTEXT_DIGEST_5AI.md)
- ALTER maintenance_schedules: thêm maintenance_type, frequency_days, last_completed_at, next_due_at, assigned_staff_id
- CREATE bảng notifications (cảnh báo hết hạn kiểm định/bảo trì)
- Bọc transaction, idempotent (chạy lại an toàn), backup DB trước khi migrate
- WAL mode đã có sẵn trong schema.sql/init_database
"""
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB = BASE / "database" / "devices.db"
BACKUP_DIR = BASE / "database" / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# --- 1. Backup ---
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = BACKUP_DIR / f"devices_before_phase1_{stamp}.db"
shutil.copy2(DB, backup_path)
print(f"[OK] Backup -> {backup_path.name} ({backup_path.stat().st_size} bytes)")

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# --- 2. Kiểm tra cột hiện có ---
existing = {r["name"] for r in cur.execute("PRAGMA table_info(maintenance_schedules)")}
print(f"[INFO] maintenance_schedules có sẵn: {sorted(existing)}")

ADD_COLUMNS = [
    ("maintenance_type", "TEXT DEFAULT 'PREVENTIVE' CHECK(maintenance_type IN ('PREVENTIVE','CALIBRATION','REPAIR','INSPECTION','HANDOVER'))"),
    ("frequency_days", "INTEGER"),
    ("last_completed_at", "DATE"),
    ("next_due_at", "DATE"),
    ("assigned_staff_id", "INTEGER"),
]

try:
    for name, ddl in ADD_COLUMNS:
        if name not in existing:
            cur.execute(f"ALTER TABLE maintenance_schedules ADD COLUMN {name} {ddl}")
            print(f"[OK] maintenance_schedules += {name}")
        else:
            print(f"[SKIP] {name} đã có")

    # --- 3. Bảng notifications ---
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_type TEXT NOT NULL CHECK(ref_type IN ('CALIBRATION','MAINTENANCE','TRANSFER','DEVICE','FEEDBACK')),
        ref_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        level TEXT NOT NULL DEFAULT 'WARNING' CHECK(level IN ('INFO','WARNING','CRITICAL')),
        days_left INTEGER,
        is_read INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read, created_at);
    CREATE INDEX IF NOT EXISTS idx_notifications_ref ON notifications(ref_type, ref_id);
    """)
    print("[OK] bảng notifications sẵn sàng")

    conn.commit()
    print("[OK] Migration hoàn tất, đã commit")
except Exception as e:
    conn.rollback()
    print(f"[FAIL] {e} — rollback, DB giữ nguyên")
    raise
finally:
    conn.close()

# --- 4. Verify ---
conn = sqlite3.connect(DB)
cols = [r[1] for r in conn.execute("PRAGMA table_info(maintenance_schedules)")]
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
conn.close()
print(f"\n[VERIFY] maintenance_schedules cột: {cols}")
print(f"[VERIFY] notifications tồn tại: {'notifications' in tables}")
print(f"[VERIFY] tổng bảng: {len(tables)}")
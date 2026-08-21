"""
Database Service cho Medical Device Management System
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
import os

DATABASE_PATH = Path(__file__).parent.parent / "database" / "devices.db"
SCHEMA_PATH = Path(__file__).parent.parent / "database" / "schema.sql"


def init_database(force: bool = False):
    """Khởi tạo database và áp dụng schema SQLite"""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Kích hoạt Foreign Keys & WAL mode
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    
    if SCHEMA_PATH.exists():
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            cursor.executescript(schema_sql)
    
    # Safe column migrations if tables were created in earlier revisions
    tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    if "repairs" in tables:
        repair_cols = [r[1] for r in cursor.execute("PRAGMA table_info(repairs)").fetchall()]
        if "updated_at" not in repair_cols:
            cursor.execute("ALTER TABLE repairs ADD COLUMN updated_at TIMESTAMP")
            cursor.execute("UPDATE repairs SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL")
    
    conn.commit()
    conn.close()


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Tạo và quản lý kết nối SQLite thread-safe"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Dependency cho FastAPI routes"""
    with get_db_connection() as conn:
        yield conn
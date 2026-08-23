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

    # Ensure document_segments exists even when device_documents was created by older scripts
    if "document_segments" not in tables:
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS document_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                page_start INTEGER NOT NULL CHECK (page_start >= 1),
                page_end INTEGER NOT NULL CHECK (page_end >= page_start),
                doc_type TEXT NOT NULL,
                form_code TEXT,
                title TEXT,
                extracted_serial TEXT,
                confidence REAL DEFAULT 0.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
                md_anchor TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES device_documents(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_doc_segments_document ON document_segments(document_id);
            CREATE INDEX IF NOT EXISTS idx_doc_segments_pages ON document_segments(document_id, page_start);
            """
        )
    
    conn.commit()
    conn.close()


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Tạo và quản lý kết nối SQLite thread-safe"""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 10000;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    try:
        yield conn
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Dependency cho FastAPI routes"""
    with get_db_connection() as conn:
        yield conn
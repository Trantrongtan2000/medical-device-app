#!/usr/bin/env python3
"""
Startup script cho Medical Device Management System
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# Import app
from app.main import app
import uvicorn
import sqlite3

def init_db():
    """Khởi tạo database"""
    from app.database import init_database
    db_path = project_root / "database" / "devices.db"
    
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True)
    
    if not db_path.exists():
        print("🔧 Đang tạo database mới...")
        init_database()
        print("✅ Database đã được khởi tạo")
    else:
        print("✅ Database đã tồn tại")

def main():
    print("\n" + "="*60)
    print("🏥 MEDICAL DEVICE MANAGEMENT SYSTEM")
    print("   Quận 7 - TP.HCM")
    print("="*60)
    
    # Initialize database
    init_db()
    
    print("\n🚀 Server khởi động...")
    print("📍 Truy cập: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🛑 Nhấn Ctrl+C để dừng server\n")
    
    # Run server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
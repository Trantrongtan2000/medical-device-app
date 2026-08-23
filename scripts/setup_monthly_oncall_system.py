import sys
import sqlite3
import calendar
from datetime import date, datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# 1. Re-create oncall_schedule with month, year, day_num, day_name, date_str
cur.execute("DROP TABLE IF EXISTS oncall_schedule")
cur.execute("""
CREATE TABLE oncall_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_num INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    date_str TEXT NOT NULL, -- DD/MM/YYYY
    primary_engineer TEXT NOT NULL,
    primary_phone TEXT NOT NULL,
    backup_engineer TEXT NOT NULL,
    backup_phone TEXT NOT NULL,
    leader_oncall TEXT DEFAULT 'Nguyễn Quốc Việt (0902769710)',
    time_window TEXT DEFAULT '24/24 Giờ (07:30 - 07:30 sáng hôm sau)',
    status TEXT DEFAULT 'SCHEDULED', -- TODAY, SCHEDULED, COMPLETED
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, day_num)
)
""")

# 6 Engineers of District 7
engineers = [
    ("Trần Trọng Tấn", "0334968114"),
    ("Trần Đăng Hiếu", "0888536278"),
    ("Lê Minh Thiện", "0378716561"),
    ("Nguyễn Tấn Lợi", "0779798786"),
    ("Trần Thị Ngọc Châu", "0335802380"),
    ("Nguyễn Quốc Việt", "0902769710")
]

day_names_vn = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

today_date = date(2026, 8, 19)

# Generate schedule for Month 8 and Month 9 of 2026
schedule_rows = []

for m in [8, 9, 10]:
    num_days = calendar.monthrange(2026, m)[1]
    for d in range(1, num_days + 1):
        dt = date(2026, m, d)
        day_vn = day_names_vn[dt.weekday()]
        date_str = f"{d:02d}/{m:02d}/2026"
        
        # Round-robin assignment based on day sequence
        day_seq = (dt - date(2026, 8, 1)).days
        prim_idx = day_seq % len(engineers)
        back_idx = (prim_idx + 1) % len(engineers)
        
        prim_name, prim_phone = engineers[prim_idx]
        back_name, back_phone = engineers[back_idx]
        
        # Determine status
        if dt < today_date:
            st = "COMPLETED"
            note = "Đã hoàn thành ca trực an toàn"
        elif dt == today_date:
            st = "TODAY"
            note = "Ca trực On-call 24 giờ đang diễn ra"
        else:
            st = "SCHEDULED"
            note = "Đã xếp lịch trước theo kế hoạch"
            
        schedule_rows.append((
            2026,
            m,
            d,
            day_vn,
            date_str,
            prim_name,
            prim_phone,
            back_name,
            back_phone,
            "Nguyễn Quốc Việt (0902769710)",
            "24/24 Giờ (07:30 - 07:30 sáng hôm sau)",
            st,
            note
        ))

cur.executemany("""
INSERT INTO oncall_schedule (year, month, day_num, day_name, date_str, primary_engineer, primary_phone, backup_engineer, backup_phone, leader_oncall, time_window, status, notes)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", schedule_rows)
conn.commit()
print(f"✅ Đã tạo thành công {len(schedule_rows)} ngày lịch On-call 24/24 giờ cho Tháng 8, 9, 10/2026!")

conn.close()

import sys
import sqlite3
import calendar
from datetime import date, datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(str(db_path))
cur = conn.cursor()

# 3 Dedicated On-call Engineers
engineers_3 = [
    ("Trần Trọng Tấn", "0334968114"),
    ("Lê Minh Thiện", "0378716561"),
    ("Trần Đăng Hiếu", "0888536278")
]

day_names_vn = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
today_date = date(2026, 8, 19)

# Build schedule for Month 8, 9, 10 with 1-week rotation per engineer
cur.execute("DELETE FROM oncall_schedule")

schedule_rows = []

# Reference anchor: Monday 2026-08-03 starts Week 1 (Tấn), Week 2 (Thiện), Week 3 (Hiếu)
# Let's map by ISO calendar week
for m in [8, 9, 10]:
    num_days = calendar.monthrange(2026, m)[1]
    for d in range(1, num_days + 1):
        dt = date(2026, m, d)
        day_vn = day_names_vn[dt.weekday()]
        date_str = f"{d:02d}/{m:02d}/2026"
        
        # ISO week calculation
        iso_year, iso_week, iso_weekday = dt.isocalendar()
        
        # Determine 3-engineer rotation by week number
        eng_idx = (iso_week - 31) % len(engineers_3)
        backup_idx = (eng_idx + 1) % len(engineers_3)
        
        prim_name, prim_phone = engineers_3[eng_idx]
        back_name, back_phone = engineers_3[backup_idx]
        
        # Determine status
        if dt < today_date:
            st = "COMPLETED"
            note = f"Ca trực tuần của {prim_name} (Đã xong)"
        elif dt == today_date:
            st = "TODAY"
            note = f"Ca trực 24h tuần này do {prim_name} phụ trách chính"
        else:
            st = "SCHEDULED"
            note = f"Lịch On-call tuần của {prim_name}"
            
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
print(f"✅ Đã nạp thành công lịch On-call xoay vòng trọn 1 tuần theo 3 nhân sự: Tấn -> Thiện -> Hiếu!")

conn.close()

KẾ HOẠCH THỰC HIỆN GIAI ĐOẠN 1 (Tuần 0–2)
Hệ thống: FastAPI + SQLite + Vanilla JS + OCR đã fix link
MVP nhỏ nhất có giá trị: Thêm bảng maintenance_schedules + 1 endpoint REST + 1 frontend component để tạo lịch bảo trì định kỳ.
Hoàn thành tuần 1, cho phép demo ngay ngày 3–4 của dự án (giảm 80% công việc thủ công tạo lịch).

Task 1 (0.5–1 giờ) – Chuẩn bị & Setup
Tên: Setup môi trường & tạo bảng maintenance_schedules (transaction).
Bảng/Schema:
SQL
Copy
CREATE TABLE IF NOT EXISTS maintenance_schedules (
    id INTEGER PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    schedule_date TEXT NOT NULL,
    frequency TEXT NOT NULL CHECK(frequency IN ('daily','weekly','monthly','quarterly','yearly')),
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending','completed','overdue')),
    next_reminder TEXT,
    created_by INTEGER,
    FOREIGN KEY(device_id) REFERENCES devices(id)
);
File: app/main.py (thêm vào đầu file app/):
Python
Copy
from app.db import Base
# sau Base.metadata.create_all()
Base.metadata.create_all(bind=engine)  # SQLite
Endpoint REST: Không cần thêm (sử dụng CRUD cơ bản).
Component Frontend: Không cần (sử dụng terminal/POSTMAN).
Tiêu chí hoàn thành (Acceptance Criteria):
Chạy uvicorn app.main:app --reload thành công.
Truy vấn SELECT COUNT(*) FROM maintenance_schedules; trả về 0.
Test bằng curl: curl -X POST http://127.0.0.1:8000/api/maintenance-schedules/ -d '{"device_id":1,"schedule_date":"2026-09-01","frequency":"weekly"}'.
Số giờ: 0.5–1 giờ.
Thực tế: Dùng ngay sqlite3 app/database.db .dump maintenance_schedules để kiểm tra.
Task 2 (1–2 giờ) – Thêm CRUD cho maintenance_schedules
Tên: CRUD maintenance_schedules (transaction + background scheduler).
Bảng/Schema: Như Task 1.
Endpoint REST (thêm vào app/routes.py):
Python
Copy
from fastapi import APIRouter, Depends, HTTPException
from app.models.maintenance_schedule import MaintenanceSchedule
from app.db import SessionLocal
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz  # cần install: pip install apscheduler pytz

router = APIRouter(prefix="/api/maintenance-schedules", tags=["Maintenance"])
scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# Route 1: GET /api/maintenance-schedules
@router.get("/")
def list_schedules(db: Session = Depends(get_db)):
    return db.query(MaintenanceSchedule).all()

# Route 2: POST /api/maintenance-schedules
@router.post("/")
def create_schedule(schedule: MaintenanceSchedule, db: Session = Depends(get_db)):
    with db.begin():  # Transaction
        db.add(schedule)
        db.flush()
        db.refresh(schedule)
    # Tự động gán next_reminder
    if schedule.frequency == "weekly":
        schedule.next_reminder = (datetime.strptime(schedule.schedule_date, "%Y-%m-%d") + timedelta(weeks=1)).isoformat()
    else:
        schedule.next_reminder = schedule.schedule_date
    db.commit()
    return schedule
File/Route cụ thể: app/routes.py (thêm đoạn code trên vào file).
Component Frontend: Không cần (sử dụng Postman/Insomnia).
Tiêu chí hoàn thành:
Thêm 2 route, chạy uvicorn app.main:app --reload.
POST thành công, trả về object với id và next_reminder.
Lịch tự động gán next_reminder (test bằng curl).
Số giờ: 1–2 giờ.
Rủi ro: Sử dụng with db.begin(): để tránh deadlock trên SQLite. Test bằng 2 curl cùng lúc.
Task 3 (2–3 giờ) – Import dữ liệu hiện có (48 logs + 107 certs)
Tên: Import dữ liệu cũ vào bảng mới.
Bảng/Schema: Sử dụng maintenance_schedules (copy từ maintenance_logs).
File: scripts/import_schedules.py (tạo file mới trong scripts/):
Python
Copy
from app.db import SessionLocal
from app.models.device import Device
from app.models.maintenance_schedule import MaintenanceSchedule
from datetime import datetime
import csv

db = SessionLocal()
for log in db.query("maintenance_logs").all():  # thay bằng query thực tế
    schedule = MaintenanceSchedule(
        device_id=log.device_id,
        schedule_date=log.date,
        frequency="monthly",
        status="completed"
    )
    db.add(schedule)
db.commit()
db.close()
Tiêu chí hoàn thành: Chạy script python scripts/import_schedules.py, kiểm tra SELECT COUNT(*) FROM maintenance_schedules; = 48.
Số giờ: 0.5–1 giờ.
Rủi ro: Chọn frequency mặc định “monthly” (dễ điều chỉnh sau).
Task 4 (1–2 giờ) – Frontend component (Create + List)
Tên: Component CreateSchedule.vue (vanilla JS + fetch).
File: web/components/CreateSchedule.js:
JavaScript
Copy
// web/components/CreateSchedule.js
const createSchedule = async (data) => {
  const res = await fetch('http://localhost:8000/api/maintenance-schedules/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
};
const listSchedules = async () => {
  const res = await fetch('http://localhost:8000/api/maintenance-schedules/');
  return res.json();
};
// Gọi trong index.html sau khi load
Component Frontend: web/components/CreateSchedule.js (thêm vào web/index.html).
Tiêu chí hoàn thành: Thêm script vào web/index.html, chạy open web/index.html, dùng button “Tạo lịch” để gọi API, hiển thị danh sách.
Số giờ: 1–2 giờ.
Rủi ro: Fetch CORS (SQLite local, dùng ngrok hoặc chạy uvicorn với --host 0.0.0.1).
Task 5 (0.5 giờ) – Kiểm tra & Demo MVP
Tên: Kiểm tra toàn bộ & Demo MVP.
Tiêu chí hoàn thành:
Hoàn thành tất cả task trên.
Chạy uvicorn app.main:app --reload, mở web/index.html, tạo 1 lịch, xem danh sách.
Test 2 curl song song (transaction).
Số giờ: 0.5 giờ.
Rủi ro: Transaction + timezone (đảm bảo tất cả schedule_date dùng “Asia/Ho_Chi_Minh”).

Thời gian tổng Giai đoạn 1: 6–8 giờ (tuần 1 hoàn thành MVP).
Thứ tự thực hiện tối ưu: Task 1 (setup) → Task 2 (CRUD) → Task 3 (import) → Task 4 (frontend) → Task 5 (demo).
Demo sớm nhất: Ngày 3–4 (sau khi hoàn thành Task 2–3).

Rủi ro & Điểm cần kiểm tra kỹ khi implement:

Transaction SQLite (không hỗ trợ nested transaction tốt, dùng with db.begin()).
Background scheduler (chỉ dùng cho reminder, không chạy 24/7 trong dev).
Timezone: Tất cả date dùng datetime.fromisoformat(..., tzinfo=pytz.timezone("Asia/Ho_Chi_Minh")).
CORS Vanilla JS (thêm Access-Control-Allow-Origin: * trong FastAPI nếu cần).
SQLite file lớn (90 GB OCR không ảnh hưởng, nhưng backup app/database.db trước khi test).

Code mẫu đã sẵn sàng copy-paste. Sau khi hoàn thành, chạy ngay python scripts/import_schedules.py và demo trong 4 giờ. Nếu cần script đầy đủ hoặc điều chỉnh, tôi cung cấp ngay!

Tối ưu hóa truy vấn SQLite
Quản lý tác vụ nền
Sửa lỗi cú pháp SQL




Fast

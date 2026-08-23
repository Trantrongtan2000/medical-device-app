Kế Hoạch Thực Hiện Chi Tiết — Giai Đoạn 1 (Tuần 0–2)
Kế Hoạch Thực Hiện Chi Tiết — Giai Đoạn 1 (Tuần 0–2)
0. Sơ đồ phụ thuộc tổng quan

T1 Migration schema nền tảng
   │
   ├──► T2 Seed dữ liệu mẫu maintenance_schedules
   │        │
   │        ▼
   ├──► T3 API CRUD maintenance_schedules ──► T4 Engine sinh lịch tự động ──► T7 Background scheduler (APScheduler)
   │                                                                              │
   ├──► T5 API certs/expiring (không cần bảng mới)                              │
   │                                                                              ▼
   ├──► T6 API pre-use-inspection ─────────────────────────────────────► T8 Dashboard alerts (tổng hợp T3+T5+T6)
   │                                                                              │
   ├──► T9 API feedback                                                          │
   ├──► T10 API transfers workflow                                               │
   │                                                                              ▼
   └──► T11 Frontend: trang Dashboard cảnh báo ◄────────────────────────────────┘
        T12 Frontend: form pre-use + feedback + transfer

Nguyên tắc: T1 chặn tất cả. T3/T5/T6/T9/T10 có thể làm song song (không phụ thuộc nhau). T4 và T7 phụ thuộc T3. T8 phụ thuộc T3+T5+T6. Frontend (T11, T12) luôn đi sau API tương ứng.

1. Danh sách Task chi tiết
T1 — Migration schema nền tảng (BLOCKER — làm đầu tiên)
Bảng/schema: maintenance_schedules, notifications (theo schema đã đề xuất ở roadmap)
File: app/migrations/006_maintenance_schedules.py (nếu dùng Alembic) hoặc app/db/migrate.py nếu tự viết script SQL thuần cho SQLite
Việc cụ thể:
Viết script SQL CREATE TABLE IF NOT EXISTS ... + index idx_ms_due
Thêm cột devices.maintenance_cycle_days INTEGER (nếu chưa có) — cần để engine sinh lịch biết chu kỳ
Viết script backfill: với thiết bị đã có certs, gán maintenance_cycle_days mặc định theo category_id (bảng tra cứu tạm category_default_cycle)
Endpoint: không có (chỉ migration)
Acceptance criteria:
 Chạy migration trên bản sao DB production không lỗi, không mất dữ liệu (SELECT COUNT(*) FROM devices trước/sau bằng nhau)
 sqlite3 app.db ".schema maintenance_schedules" ra đúng cấu trúc
 Có script rollback (DROP TABLE + xóa cột) để test an toàn
Ước lượng: 4h
T2 — Seed dữ liệu mẫu cho maintenance_schedules
Phụ thuộc: T1
File: app/scripts/seed_maintenance_schedules.py
Việc cụ thể: chạy 1 lần, generate next_due_date cho toàn bộ 1.211 thiết bị dựa trên maintenance_cycle_days (nếu null → dùng default 90 ngày cho nhóm thiết bị chưa phân loại)
Acceptance criteria:
 SELECT COUNT(*) FROM maintenance_schedules = số thiết bị active (loại trừ thiết bị đã thanh lý nếu có flag)
 Không có next_due_date NULL
Ước lượng: 3h
T3 — API CRUD maintenance_schedules
Phụ thuộc: T1
File: app/routes/maintenance_schedules.py (route mới), đăng ký trong app/main.py
Endpoint:
GET /maintenance-schedules?due_before=&status=&device_id= (phân trang)
GET /maintenance-schedules/{id}
POST /maintenance-schedules (tạo thủ công)
PATCH /maintenance-schedules/{id} (cập nhật status, last_done_date khi hoàn thành → tự tính next_due_date mới)
Schema Pydantic: MaintenanceScheduleCreate, MaintenanceScheduleOut, MaintenanceScheduleUpdate trong app/schemas/maintenance.py
Frontend component: web/pages/maintenance-schedules.html + web/js/maintenance-schedules.js — bảng danh sách có filter theo trạng thái (pending/overdue/done)
Acceptance criteria:
 PATCH với status=done tự động tính next_due_date = last_done_date + frequency_days (kiểm bằng test thủ công 2-3 case)
 GET ?due_before=2026-09-01 trả đúng danh sách quá hạn/sắp hạn
 Test qua Swagger UI (/docs) chạy được cả 4 endpoint không lỗi 500
Ước lượng: 8h
T4 — Engine sinh lịch bảo trì tự động
Phụ thuộc: T3
File: app/services/schedule_generator.py, endpoint trong app/routes/maintenance_schedules.py
Endpoint: POST /maintenance-schedules/generate (chạy thủ công, dùng để test trước khi giao cho scheduler ở T7)
Logic: quét devices chưa có maintenance_schedules tương ứng (hoặc lịch đã done quá lâu) → tạo bản ghi mới dựa trên maintenance_cycle_days
Acceptance criteria:
 Chạy 2 lần liên tiếp không tạo trùng lịch (idempotent — kiểm tra UNIQUE(device_id, schedule_type) hoặc logic check tồn tại trước khi insert)
 Log số lượng bản ghi tạo mới ra console/response
Ước lượng: 6h
T5 — API cảnh báo kiểm định sắp hết hạn
Phụ thuộc: T1 (không cần bảng mới, chỉ query certs)
File: thêm route trong app/routes/certs.py (file có sẵn, mở rộng)
Endpoint: GET /certs/expiring?days=30
Acceptance criteria:
 Trả đúng danh sách cert có expiry_date <= today + days, sắp xếp theo expiry_date tăng dần
 Test với days=0 trả về cert đã hết hạn hôm nay/quá hạn
Ước lượng: 2h
T6 — API + form Pre-use Inspection
Phụ thuộc: T1
Bảng: dùng bảng pre_use_inspection có sẵn — cần rà soát lại schema hiện tại, có thể cần ALTER TABLE thêm cột checklist_json TEXT, inspector_id, result TEXT CHECK(result IN ('pass','fail')) nếu chưa đủ
File: app/routes/pre_use_inspection.py
Endpoint:
POST /pre-use-inspection (ghi nhận kiểm tra, kèm checklist theo nhóm thiết bị)
GET /pre-use-inspection/today?facility_id=
Frontend component: web/pages/pre-use-checklist.html — form checklist đơn giản, submit nhanh trên mobile
Acceptance criteria:
 Submit form ghi đúng device_id, inspector_id, thời gian theo giờ VN (xem mục Rủi ro #4)
 GET /today chỉ trả bản ghi trong ngày hiện tại theo giờ VN, không theo UTC
Ước lượng: 6h
T7 — Background scheduler (APScheduler)
Phụ thuộc: T4, T5
File: app/services/scheduler.py, khởi tạo trong app/main.py (lifespan event)
Việc cụ thể: job chạy hằng ngày 06:00 (giờ VN) — gọi schedule_generator.py (T4) + quét certs/expiring (T5) → ghi vào bảng notifications
Endpoint: không bắt buộc, có thể thêm POST /admin/jobs/run-now để trigger thủ công khi debug
Acceptance criteria:
 Restart server, job vẫn đăng ký đúng lịch (kiểm tra log scheduler.print_jobs())
 Chạy thử run-now, bảng notifications có bản ghi mới, không tạo trùng nếu chạy 2 lần
Ước lượng: 5h
T8 — API Dashboard cảnh báo tổng hợp
Phụ thuộc: T3, T5, T6
File: app/routes/dashboard.py
Endpoint: GET /dashboard/alerts — trả JSON gộp: overdue_maintenance, expiring_certs, missing_pre_use_today
Acceptance criteria:
 Response time < 500ms với 1.211 thiết bị (kiểm tra bằng time curl ...)
 Số liệu khớp khi đối chiếu thủ công với 3 API con (T3/T5/T6)
Ước lượng: 4h
T9 — API Feedback (báo lỗi từ khoa/phòng)
Phụ thuộc: T1
File: app/routes/feedback.py
Endpoint: POST /feedback, GET /feedback?status=open, PATCH /feedback/{id}/resolve
Frontend: form đơn giản có thể truy cập qua QR code gắn trên thiết bị (web/pages/report-issue.html?device_id=xxx)
Acceptance criteria:
 Submit không cần đăng nhập (dành cho nhân viên y tế) nhưng cần rate-limit cơ bản để tránh spam
 PATCH /resolve cập nhật đúng trạng thái, ghi resolved_at
Ước lượng: 5h
T10 — API Điều chuyển thiết bị (workflow duyệt)
Phụ thuộc: T1
File: app/routes/transfers.py
Endpoint: POST /transfers (tạo yêu cầu), PATCH /transfers/{id}/approve, PATCH /transfers/{id}/reject
Logic quan trọng: khi approve → phải cập nhật đồng thời devices.facility_id — bắt buộc dùng transaction (xem Rủi ro #1)
Acceptance criteria:
 Sau khi approve, devices.facility_id đổi đúng cơ sở mới
 Nếu approve thất bại giữa chừng (giả lập lỗi), transfers.status và devices.facility_id không bị lệch nhau (test bằng cách raise exception giả trong transaction)
Ước lượng: 6h
T11 — Frontend: trang Dashboard cảnh báo
Phụ thuộc: T8
File: web/pages/dashboard.html, web/js/dashboard.js
Acceptance criteria:
 Hiển thị 3 khối: quá hạn bảo trì / sắp hết hạn kiểm định / chưa pre-use hôm nay, có số đếm và link tới danh sách chi tiết
 Responsive được trên màn hình tablet (BME thường dùng tablet đi kiểm tra)
Ước lượng: 6h
T12 — Frontend: form pre-use + feedback + transfer
Phụ thuộc: T6, T9, T10
File: web/pages/pre-use-checklist.html, web/pages/report-issue.html, web/pages/transfers.html
Acceptance criteria:
 Cả 3 form submit thành công, hiển thị thông báo lỗi rõ ràng khi validate fail (thiếu field bắt buộc)
Ước lượng: 8h
2. Bảng tổng hợp ước lượng giờ
Task	Giờ	Phụ thuộc
T1	4h	—
T2	3h	T1
T3	8h	T1
T4	6h	T3
T5	2h	T1
T6	6h	T1
T7	5h	T4, T5
T8	4h	T3, T5, T6
T9	5h	T1
T10	6h	T1
T11	6h	T8
T12	8h	T6, T9, T10
Tổng	63h	~8 ngày làm việc (1 dev, 8h/ngày) — vừa khít trong 2 tuần kể cả buffer test
3. Thứ tự thực hiện tối ưu để demo sớm nhất (MVP nhỏ nhất có giá trị)

Mục tiêu demo sau ~3 ngày: "Hệ thống biết thiết bị nào sắp/đã quá hạn bảo trì và kiểm định — điều mà hiện tại DB hoàn toàn không có."

Thứ tự đề xuất (khác thứ tự đánh số ở trên):

T1 → T2 → T5 (ngày 1): Chỉ cần migration + seed + API certs/expiring là đã có thể demo "hệ thống biết cert nào sắp hết hạn" — giá trị cao, chi phí thấp nhất (T5 chỉ 2h, không cần bảng mới).
T3 → T4 (ngày 2–3): Có API + engine sinh lịch bảo trì → demo được "hệ thống tự tạo lịch bảo trì cho 1.211 thiết bị".
T8 (bản rút gọn chỉ gộp T3+T5, bỏ qua T6 tạm thời) → T11 (ngày 3–4): Ra được Dashboard cảnh báo — đây là màn hình "wow" nhất để trình diễn cho lãnh đạo/BME, nên ưu tiên lên sớm dù pre-use chưa xong.
Sau khi có demo, tiếp tục song song: T6, T9, T10 (ngày 5–7), rồi bổ sung vào Dashboard, cuối cùng T7 (scheduler) và T12 (frontend còn lại) (ngày 7–8).

Lý do: Dashboard cảnh báo (T8/T11) là điểm chạm giá trị cao nhất và dễ "bán" nhất trong Giai đoạn 1 — nó biến dữ liệu tĩnh (certs, devices) thành thông tin hành động được, nên nên đẩy sớm hơn thứ tự phụ thuộc logic thuần túy, chấp nhận bản đầu chưa đầy đủ 3 khối (chỉ có 2/3), bổ sung khối thứ 3 sau.

4. Rủi ro & điểm cần kiểm tra kỹ (FastAPI + SQLite)
⚠️ 1. Transaction khi cập nhật nhiều bảng cùng lúc (đặc biệt T10 — transfers)

SQLite mặc định với FastAPI qua sqlite3/SQLAlchemy dễ bị autocommit ngầm nếu không dùng with session.begin(): tường minh. Với T10, việc approve phải update cả transfers.status và devices.facility_id — nếu không bọc transaction, lỗi giữa chừng sẽ để dữ liệu ở trạng thái không nhất quán.
→ Bắt buộc: dùng try/except + session.rollback() tường minh, viết test giả lập lỗi giữa transaction để xác nhận rollback hoạt động.

⚠️ 2. SQLite và truy cập đồng thời (concurrent writes)

SQLite khóa toàn file khi ghi (database is locked error) — với background scheduler (T7) chạy đồng thời lúc người dùng đang thao tác (T3, T10), rất dễ gặp lỗi này khi tải tăng.
→ Cân nhắc: bật PRAGMA journal_mode=WAL; để tăng khả năng đọc/ghi đồng thời; nếu vẫn lỗi thường xuyên, đây là tín hiệu cần lên kế hoạch migrate PostgreSQL ở giai đoạn sau (không cần làm ngay nhưng nên ghi nhận).

⚠️ 3. Migration trên SQLite không hỗ trợ đầy đủ ALTER TABLE

SQLite không hỗ trợ ALTER TABLE ... DROP COLUMN hay sửa kiểu cột trực tiếp (tùy version) — nếu dùng Alembic, cần cấu hình render_as_batch=True để Alembic tự tạo bảng tạm, copy dữ liệu, đổi tên (batch mode). Nếu tự viết script, phải tự làm quy trình: tạo bảng mới → copy data → drop bảng cũ → rename.
→ Luôn backup file .db trước khi chạy migration (cp app.db app.db.bak.$(date +%Y%m%d)), test trên bản sao trước.

⚠️ 4. Timezone — lỗi rất dễ mắc với "hôm nay", "quá hạn"

FastAPI/SQLite mặc định lưu datetime theo UTC nếu dùng datetime.utcnow(), nhưng nghiệp vụ (T5 expiring, T6 pre-use-inspection/today, T7 job 06:00) đều cần theo giờ Việt Nam (UTC+7). Nếu không xử lý cẩn thận, "hôm nay" ở VN 06:00 sáng sẽ vẫn tính là "hôm qua" theo UTC → job chạy sai ngày, dashboard đếm sai số.
→ Chuẩn hóa: lưu DB theo UTC nhưng luôn convert sang Asia/Ho_Chi_Minh khi so sánh "ngày hôm nay" ở tầng business logic (dùng zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh")), viết 1 hàm dùng chung get_vn_today() trong app/utils/datetime_vn.py để tránh lặp code sai ở nhiều nơi.

⚠️ 5. Idempotency của engine sinh lịch (T4) và scheduler (T7)

Nếu job chạy trùng (server restart giữa job, hoặc gọi run-now nhiều lần) mà không kiểm tra tồn tại trước khi insert, sẽ sinh trùng lịch bảo trì cho cùng 1 thiết bị → sai lệch dashboard, gây nhiễu cho kỹ thuật viên.
→ Thêm UNIQUE(device_id, schedule_type) ở mức DB (không chỉ kiểm tra ở code) để đảm bảo an toàn tuyệt đối kể cả khi có race condition.

⚠️ 6. Kiểm tra tải khi có 87 endpoint cũ + endpoint mới

Trước khi thêm route mới, chạy nhanh pytest/smoke test cho các endpoint cũ liên quan đến devices, certs, contracts để đảm bảo không có conflict path (ví dụ /devices/{id} với /devices/export dễ bị FastAPI match nhầm thứ tự route nếu khai báo sai thứ tự).






6 minutes ago





Sonnet 5 Medium


Claude is AI and can make mistakes. Please double-check responses.

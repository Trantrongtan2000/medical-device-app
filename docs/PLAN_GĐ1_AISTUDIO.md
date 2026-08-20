 AM
Thoughts

Expand to view model thoughts

chevron_right
more_vert

Dưới đây là Kế hoạch Thực hiện Chi tiết từng bước cho GIAI ĐOẠN 1 (Tuần 0–2) dành cho đội ngũ phát triển. Kế hoạch được thiết kế tối ưu cho stack FastAPI + SQLite + Vanilla JS, chia nhỏ thành các task độc lập, có mã endpoint, schema và tiêu chí nghiệm thu (Acceptance Criteria) cụ thể để lập trình viên có thể code và tự test ngay.

1. Sơ đồ phụ thuộc & Thứ tự thực thi tối ưu (Demo sớm nhất)
code
Code
download
content_copy
expand_less
[Task 1.1: Migration Schema & Base Models] (Bắt buộc đầu tiên)
       │
       ├───► [Task 1.3: Engine Cảnh báo Hạn Kiểm định] ──► [Task 1.5: UI Dashboard Cảnh báo] ──► 🎯 DEMO 1 (Ngày 3)
       │
       ├───► [Task 1.2: Engine Tự sinh Lịch PM]       ──► [Task 1.6: UI Lịch Bảo trì PM]     ──► 🎯 DEMO 2 (Ngày 6)
       │
       └───► [Task 1.4: API Sinh mã QR & Lookup]       ──► [Task 1.7: UI In Tem & Mobile Scan] ──► 🎯 DEMO 3 (Ngày 8)
                                                                 │
[Task 1.8: APScheduler Tự động hóa & Kiểm tra tích hợp] ◄────────┘ ───────────────────────────► 🚀 HOÀN TẤT TUẦN 2
2. Chi tiết từng Task thực hiện
TASK 1.1: Database Migration & Cấu hình SQLite Connection

Thứ tự phụ thuộc: Không phụ thuộc (Làm đầu tiên).

Thời gian ước lượng: 4 giờ.

Tệp/Route cần chỉnh sửa:

app/database.py (cấu hình WAL mode, connection pragma).

app/models.py (bổ sung/chỉnh sửa Model).

scripts/migrate_phase1.py (script chạy migration độc lập).

Bảng/Schema cần bổ sung & cập nhật:

code
SQL
download
content_copy
expand_less
-- Bổ sung trường quản lý rủi ro và chu kỳ bảo dưỡng vào bảng devices
ALTER TABLE devices ADD COLUMN risk_level TEXT CHECK(risk_level IN ('A', 'B', 'C', 'D')) DEFAULT 'B';
ALTER TABLE devices ADD COLUMN pm_frequency_months INTEGER DEFAULT 6;
ALTER TABLE devices ADD COLUMN last_pm_date DATE;
ALTER TABLE devices ADD COLUMN next_pm_date DATE;

-- Nâng cấp bảng maintenance_schedules
CREATE TABLE IF NOT EXISTS maintenance_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    scheduled_date DATE NOT NULL,
    assigned_bme_id INTEGER,
    status TEXT CHECK(status IN ('PENDING', 'OVERDUE', 'COMPLETED', 'SKIPPED')) DEFAULT 'PENDING',
    completed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (assigned_bme_id) REFERENCES bme_staff(id)
);
CREATE INDEX IF NOT EXISTS idx_maint_sched_date_status ON maintenance_schedules(scheduled_date, status);

Tiêu chí hoàn thành (Acceptance Criteria - AC):

Chạy file python scripts/migrate_phase1.py thành công không lỗi, bảo toàn nguyên vẹn 1.211 bản ghi devices.

Bảng maintenance_schedules và các cột mới trong devices tồn tại khi kiểm tra bằng DB Browser/SQLite CLI.

app/database.py tự động kích hoạt PRAGMA foreign_keys = ON; và PRAGMA journal_mode = WAL;.

TASK 1.2: Engine & API Tự sinh Lịch Bảo trì Dự phòng (PM Scheduler)

Thứ tự phụ thuộc: Sau Task 1.1.

Thời gian ước lượng: 8 giờ.

Tệp/Route cần chỉnh sửa:

app/services/pm_service.py (Tạo mới: logic tính toán ngày kế tiếp).

app/routes/maintenance.py (Bổ sung endpoint).

app/schemas/maintenance.py (Pydantic models).

REST Endpoints cần thêm:

POST /api/v1/maintenance-schedules/bulk-generate: Quét 1.211 thiết bị, sinh lịch bảo dưỡng cho năm hiện tại/kế tiếp dựa trên pm_frequency_months.

GET /api/v1/maintenance-schedules: Lọc danh sách lịch bảo dưỡng theo month, year, facility_id, status, assigned_bme_id.

PATCH /api/v1/maintenance-schedules/{id}/complete: Đánh dấu đã làm, tự động cập nhật devices.last_pm_date và tính devices.next_pm_date, sinh tiếp 1 bản ghi schedule mới cho chu kỳ tiếp theo.

Tiêu chí hoàn thành (AC):

Gọi POST /api/v1/maintenance-schedules/bulk-generate tạo thành công lịch cho toàn bộ thiết bị đang hoạt động (status = ACTIVE).

Không tạo trùng lịch nếu thiết bị đã có schedule ở trạng thái PENDING trong tương lai gần.

Khi gọi PATCH .../complete, trạng thái chuyển sang COMPLETED, đồng thời sinh ngay 1 record schedule mới sau đúng số tháng pm_frequency_months.

TASK 1.3: Compliance Alert Engine (Kiểm định/Hiệu chuẩn theo NĐ 98)

Thứ tự phụ thuộc: Sau Task 1.1.

Thời gian ước lượng: 6 giờ.

Tệp/Route cần chỉnh sửa:

app/routes/alerts.py (Tạo mới hoặc bổ sung vào app/routes.py).

app/services/compliance_service.py (Logic phân nhóm hạn 30-60-90 ngày).

REST Endpoints cần thêm:

GET /api/v1/alerts/compliance-summary: Trả về số lượng: Đã quá hạn, Hết hạn trong 30 ngày, 60 ngày, 90 ngày của (1) Kiểm định/Hiệu chuẩn và (2) Bảo trì PM.

GET /api/v1/alerts/certs-expiring: Trả về danh sách chi tiết các thiết bị có chứng chỉ kiểm định/hiệu chuẩn hết hạn kèm thông tin: tên máy, model, serial, khoa phòng, ngày hết hạn, đơn vị kiểm định.

Tiêu chí hoàn thành (AC):

Query SQLite lọc chính xác các bản ghi trong certs có expiry_date so với ngày hiện tại (múi giờ GMT+7).

Phản hồi JSON trả về < 100ms với 1.211 thiết bị và 107 certs.

TASK 1.4: Endpoint Sinh mã QR & Tra cứu nhanh (Mobile Asset Profile)

Thứ tự phụ thuộc: Sau Task 1.1.

Thời gian ước lượng: 6 giờ.

Tệp/Route cần chỉnh sửa:

app/utils/qr_generator.py (Sử dụng thư viện qrcode sinh SVG/Base64 PNG).

app/routes/devices.py.

REST Endpoints cần thêm:

GET /api/v1/devices/{id}/qr: Trả về ảnh PNG/SVG mã QR chứa link: https://[domain-tam-anh]/m/devices/{id}.

GET /api/v1/devices/{id}/quick-view: Trả về payload rút gọn tối ưu cho mobile: Tên máy, Mã quản lý, Serial, Khoa/Phòng hiện tại, Hạn kiểm định, Tình trạng bảo trì gần nhất, Thông tin hotline BME on-call.

Tiêu chí hoàn thành (AC):

API sinh mã QR quét được bằng ứng dụng Camera/Zalo trên điện thoại thật.

Endpoint /quick-view không yêu cầu header quá phức tạp (hỗ trợ mở nhanh qua web nội bộ).

TASK 1.5: Frontend - Dashboard Cảnh báo Tuân thủ (Compliance Widget)

Thứ tự phụ thuộc: Sau Task 1.3.

Thời gian ước lượng: 8 giờ.

Tệp Frontend:

web/index.html (Thêm hàng thẻ KPI cảnh báo).

web/js/alerts_widget.js (Gọi API Task 1.3 và render DOM thuần).

web/css/alerts.css (Màu cảnh báo chuẩn: Đỏ = Quá hạn, Vàng cam = <30 ngày, Vàng = <60 ngày).

Giao diện/Tính năng:

4 thẻ KPI đầu trang: Quá hạn kiểm định | Sắp hết hạn (30 ngày) | Quá hạn PM | Lịch PM trong tuần.

Bảng danh sách cảnh báo có bộ lọc nhanh theo Khoa/Phòng (facilities) và nút Export ra Excel/CSV (dùng JS Table2Excel).

Tiêu chí hoàn thành (AC):

Load trang chủ index.html hiển thị số liệu tức thì.

Nhấp vào thẻ "Quá hạn kiểm định" sẽ tự động filter bảng bên dưới hiển thị đúng danh sách máy đó.

TASK 1.6: Frontend - Giao diện Lịch Bảo trì Dự phòng (PM Calendar & Action)

Thứ tự phụ thuộc: Sau Task 1.2.

Thời gian ước lượng: 12 giờ.

Tệp Frontend:

web/pages/maintenance_plan.html (Trang chuyên trách lịch bảo dưỡng).

web/js/maintenance_plan.js.

web/components/calendar_view.js (Render bảng lịch tháng hoặc tuần không dùng thư viện ngoài nặng nề).

Giao diện/Tính năng:

Nút "Khởi tạo lịch bảo dưỡng tự động" (gọi API bulk-generate).

Khung nhìn Lịch (Tháng/Danh sách): Phân màu theo trạng thái (Xanh lá: Đã xong, Đỏ: Trễ hạn, Xanh dương: Sắp tới).

Modal Action: Bấm vào 1 lịch 
→
→
 Hiện popup thông tin máy 
→
→
 Chọn kỹ sư BME thực hiện 
→
→
 Nhấn "Xác nhận đã bảo trì" hoặc "Bỏ qua (có lý do)".

Tiêu chí hoàn thành (AC):

Kỹ sư BME bấm "Xác nhận đã bảo trì", record biến mất khỏi tab Chờ xử lý, nhảy sang tab Đã hoàn thành, API lưu thành công vào SQLite.

TASK 1.7: Frontend - In Tem QR Hàng loạt & Giao diện Mobile Scan

Thứ tự phụ thuộc: Sau Task 1.4.

Thời gian ước lượng: 10 giờ.

Tệp Frontend:


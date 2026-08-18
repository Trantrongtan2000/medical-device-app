# Tasks Breakdown: 001 - Medical Device Management System

## Phase 1: Database & Core Ingestion
- [x] **TASK-001**: Cập nhật `database/schema.sql` với bảng `devices`, `calibration_certificates`, `facilities`, `device_categories`, triggers và `device_status_summary` view.
- [x] **TASK-002**: Nâng cấp `scripts/import_md_data.py` quét toàn bộ 7.715 file MD từ `G:\BV QUẬN 7_OCR_WORK_20260712\md`.
- [x] **TASK-003**: Nạp thành công 1.101 thiết bị y tế, 329 chứng chỉ kiểm định và 22 khoa phòng vào `database/devices.db`.

## Phase 2: Backend REST APIs & PDF Streaming
- [x] **TASK-004**: Cập nhật `app/models.py` với Pydantic v2 schemas đầy đủ.
- [x] **TASK-005**: Sửa lỗi SQL parameter binding và hoàn thiện các API filter trong `app/routes.py`.
- [x] **TASK-006**: Xây dựng endpoint `/api/pdf/view` kết nối mở tệp PDF gốc từ ổ `G:\BV QUẬN 7_OCR_WORK_20260712`.
- [x] **TASK-007**: Cấu hình `app/main.py` phục vụ web frontend tĩnh và Swagger API documentation.

## Phase 3: Frontend Web UI (Snipe-IT & SpeedMaint UX)
- [x] **TASK-008**: Thiết kế giao diện `web/index.html` với 4 thẻ KPI, thanh lọc đa năng và bảng dữ liệu hiện đại.
- [x] **TASK-009**: Viết stylesheet `web/css/style.css` chuẩn màu sắc cảnh báo y tế (Đỏ, Vàng, Xanh) và badge rủi ro A/B/C/D.
- [x] **TASK-010**: Hoàn thiện `web/js/api.js` và `web/js/app.js` (tìm kiếm debounce, lọc khoa/phòng, modal lý lịch máy, sinh QR code).

## Phase 4: Verification & Testing
- [x] **TASK-011**: Khởi chạy máy chủ FastAPI/Uvicorn trên cổng 8000.
- [x] **TASK-012**: Kiểm thử các endpoint `/api/dashboard/summary`, `/api/devices`, `/api/dashboard/facilities`.
- [x] **TASK-013**: Kiểm thử giao diện web trên trình duyệt và xác nhận luồng xem PDF.

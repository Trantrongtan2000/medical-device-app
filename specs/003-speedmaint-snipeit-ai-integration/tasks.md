# Tasks & Verification: 003 - SpeedMaint CMMS, Snipe-IT, Gemini AI & Mistral OCR Integration

- [x] **Task 1: Thiết kế giao diện tinh gọn (Less, but better UI)**
  - Tối giản Sidebar về 5 menu cốt lõi.
  - Tinh gọn bảng danh mục thiết bị từ 11 cột xuống 6 cột trọng tâm.
  - Xây dựng modal chi tiết lý lịch máy đầy đủ 3 khối thông tin.

- [x] **Task 2: Triển khai tính năng Nhập Mới Thiết Bị (TLHD Mục 2a, 3 & NĐ 98)**
  - Xây dựng endpoint `POST /api/devices` kiểm tra trùng Serial.
  - Tự động sinh mã Asset Tag `BVQ7-TTB-XXXXX` và SpeedMaint `BM/BVQ7/XXXXX`.
  - Tự động khởi tạo chứng chỉ kiểm định và nhật ký bàn giao ban đầu.
  - Xây dựng Modal giao diện nhập thiết bị với đầy đủ trường lâm sàng.

- [x] **Task 3: Triển khai Cơ Chế Xoay API Key Tự Động (Multi-Key Rotation Pool)**
  - Xây dựng `KeyPool` trong `app/key_rotator.py`.
  - Hỗ trợ lưu trữ SQLite `api_keys_config` và biến môi trường.
  - Triển khai thuật toán Round-Robin & Auto-Failover khi gặp HTTP 429 / Quota Exhaustion.
  - Xây dựng các endpoints `/api/keys/config`, `/api/keys/add`, `/api/keys/remove`.
  - Xây dựng Modal quản lý key thời gian thực trên giao diện web.

- [x] **Task 4: Tích hợp Trợ Lý Gemini AI & Mistral OCR Engine**
  - Tích hợp Google Gemini Interactions API (`google-genai`) với ngữ cảnh 1.049 thiết bị BV Quận 7.
  - Tích hợp Mistral OCR-4 API (`mistralai`) bóc tách văn bản scan sang Markdown & JSON Schema.
  - Tích hợp cơ chế Fallback Rule Engine thông minh.

- [x] **Task 5: Kiểm Thử Toàn Diện & Tự Động Hóa**
  - Suite test tự động `scripts/test_api.py` vượt qua 100% endpoints.
  - Script test nhập mới thiết bị `scripts/test_create_device.py` hoạt động hoàn hảo.
  - Kiểm thử trực quan với `browsermcp`.

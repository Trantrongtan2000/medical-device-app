# 🗺️ LỘ TRÌNH THỰC HIỆN THEO GIAI ĐOẠN (PHASED ROADMAP)
## MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3) — BV QUẬN 7

> **Nguyên tắc thực thi:** Thực hiện tuần tự từ Phase 0 đến Phase 9. Không thực hiện các giai đoạn sau nếu giai đoạn trước chưa đạt tiêu chuẩn nghiệm thu (Definition of Done). Tuyệt đối không implement trong giai đoạn lập kế hoạch này.

---

## 1. TỔNG QUAN LỘ TRÌNH 10 GIAI ĐOẠN (10-PHASE MASTER ROADMAP)

```mermaid
graph LR
    P0["PHASE 0<br>Baseline & Backup"] --> P1["PHASE 1<br>Data Integrity"]
    P1 --> P2["PHASE 2<br>Backend Architecture"]
    P2 --> P3["PHASE 3<br>Frontend Architecture"]
    P3 --> P4["PHASE 4<br>Document / OCR"]
    P4 --> P5["PHASE 5<br>AI Architecture"]
    P5 --> P6["PHASE 6<br>Security & Auth"]
    P6 --> P7["PHASE 7<br>Testing Suite"]
    P7 --> P8["PHASE 8<br>Performance"]
    P8 --> P9["PHASE 9<br>Production Hardening"]
```

---

## 2. CHI TIẾT TỪNG GIAI ĐOẠN & ĐIỀU KIỆN HOÀN THÀNH (DEFINITION OF DONE)

### 📌 PHASE 0 — BASELINE + SAO LƯU + KHÓA SOURCE OF TRUTH (0.5 Ngày)
* **Mục tiêu**: Thiết lập mốc cơ sở an toàn, khóa CSDL 1.211 thiết bị và dọn dẹp các tệp CSDL rác.
* **Nhiệm vụ cụ thể**:
  1. Tạo bản sao lưu đầy đủ `database/backups/devices_backup_baseline.db`.
  2. Xóa bỏ tệp database rác `app/medical_devices.db`.
  3. Cập nhật `README.md` và `docs/` đồng bộ con số chính thức: **1.211 Thiết bị, 198 Hợp đồng, 102 Nhà thầu, 39 Khoa phòng**.
* **Definition of Done (DoD)**:
  - [x] Có bản backup SQLite được kiểm tra tính toàn vẹn (`PRAGMA integrity_check = ok`).
  - [x] Không còn tệp CSDL dư thừa trong thư mục `app/`.
  - [x] Số liệu trên tài liệu khớp 100% với CSDL.

---

### 📌 PHASE 1 — CHUẨN HÓA TOÀN VẸN DỮ LIỆU (DATA INTEGRITY) (1.0 Ngày)
* **Mục tiêu**: Bổ sung bảng `work_orders`, kích hoạt Foreign Keys, khởi tạo trạng thái động cho thiết bị.
* **Nhiệm vụ cụ thể**:
  1. Chạy migration tạo bảng `work_orders` và `device_documents`.
  2. Xây dựng logic chuyển đổi trạng thái động (`IN_SERVICE`, `UNDER_MAINTENANCE`, `CALIBRATION_PENDING`).
  3. Liên kết có cấu trúc giữa thiết bị và hồ sơ tài liệu.
* **Definition of Done (DoD)**:
  - [x] `PRAGMA foreign_key_check` trả về 0 lỗi.
  - [x] Bảng `work_orders` hoạt động và có khóa ngoại trỏ về `devices.id` và `bme_staff.id`.

---

### 📌 PHASE 2 — TÁI CẤU TRÚC BACKEND (LAYERED ARCHITECTURE) (2.5 Ngày)
* **Mục tiêu**: Phân rã `app/routes.py` (2.016 dòng) thành Router $\rightarrow$ Service $\rightarrow$ Repository.
* **Nhiệm vụ cụ thể**:
  1. Tạo thư mục `app/api/v1/`, `app/services/`, `app/repositories/`, `app/core/`.
  2. Di chuyển logic nghiệp vụ ra khỏi router vào Service Layer.
  3. Đóng gói các truy vấn SQL vào Repository Layer.
  4. Thay thế toàn bộ hardcoded paths bằng Pydantic BaseSettings đọc từ `.env`.
* **Definition of Done (DoD)**:
  - [x] `app/routes.py` được thay thế hoàn toàn bởi các sub-routers.
  - [x] Không còn tệp backend nào dài quá 400 dòng code.
  - [x] Không còn chuỗi raw SQL nằm trực tiếp trong API Routers.

---

### 📌 PHASE 3 — TÁI CẤU TRÚC FRONTEND (MODULAR JAVASCRIPT) (2.5 Ngày)
* **Mục tiêu**: Phân rã `web/js/app.js` (3.776 dòng) thành các ES6 Modules; kích hoạt `client.js`.
* **Nhiệm vụ cụ thể**:
  1. Tách `web/js/app.js` thành `web/js/modules/` (dashboard, devices, device-modal, contracts, maintenance).
  2. Kích hoạt `web/js/api/client.js` làm HTTP Client tập trung.
  3. Xóa bỏ 59 lệnh `fetch()` trực tiếp rải rác trong giao diện.
  4. Hợp nhất `web/sops.html` và `web/quy_trinh_ttbyt.html` để loại bỏ 14.765 dòng HTML trùng lặp.
* **Definition of Done (DoD)**:
  - [x] Không còn tệp monolithic `app.js` 3.776 dòng.
  - [x] 100% cuộc gọi API đi qua `client.js`.
  - [x] Toàn bộ tính năng giao diện (Search, Modal 5 tabs, Filter, Kanban) hoạt động trơn tru.

---

### 📌 PHASE 4 — CHUẨN HÓA DOCUMENT & OCR PIPELINE (1.5 Ngày)
* **Mục tiêu**: Xây dựng luồng xử lý tài liệu có mã băm SHA-256 và truy vết W3C PROV-O.
* **Nhiệm vụ cụ thể**:
  1. Tính mã băm SHA-256 cho toàn bộ tệp scan PDF trong kho lưu trữ.
  2. Tạo bản ghi có cấu trúc trong bảng `device_documents`.
  3. Thiết lập cơ chế chống Path Traversal an toàn trong việc tải và xem tài liệu.
* **Definition of Done (DoD)**:
  - [x] Mọi tài liệu số hóa đều có định danh bất biến (Content-Addressable).
  - [x] Không hardcode ký tự ổ đĩa trong CSDL.

---

### 📌 PHASE 5 — CHUẨN HÓA AI HUB & KEY ROTATION (1.0 Ngày)
* **Mục tiêu**: Cách ly an toàn API Keys, tự động xoay key và chống ảo tưởng (Zero Hallucination).
* **Nhiệm vụ cụ thể**:
  1. Tái cấu trúc `app/key_rotator.py` thành `KeyManagementService` thread-safe.
  2. Tự động mask toàn bộ API keys trước khi ghi log.
  3. Tích hợp trích dẫn chứng cứ gốc (Evidence Citation) cho câu trả lời của AI.
* **Definition of Done (DoD)**:
  - [x] Không còn rò rỉ token trong log hệ thống.
  - [x] Cơ chế auto-failover và cooldown timer hoạt động ổn định khi gặp mã lỗi 429.

---

### 📌 PHASE 6 — AN NINH & BẢO MẬT (SECURITY & AUTH) (2.0 Ngày)
* **Mục tiêu**: Triển khai xác thực JWT và phân quyền 4 vai trò (Admin, BME, Clinical Staff, Auditor).
* **Nhiệm vụ cụ thể**:
  1. Xây dựng module `app/core/security.py` (Password Hashing bcrypt, JWT generation).
  2. Bảo vệ toàn bộ các endpoint POST/PUT/DELETE bằng dependency kiểm tra quyền.
  3. Cấu hình CORS an toàn theo danh sách domain cho phép.
* **Definition of Done (DoD)**:
  - [x] Các thao tác sửa/xóa dữ liệu bắt buộc phải có Bearer Token hợp lệ.
  - [x] Người dùng không đủ quyền bị chặn với mã lỗi HTTP `403 Forbidden`.

---

### 📌 PHASE 7 — HẠ TẦNG KIỂM THỬ TỰ ĐỘNG (TESTING SUITE) (2.0 Ngày)
* **Mục tiêu**: Xây dựng bộ test suite `pytest` đạt độ bao phủ >85% cho các nghiệp vụ trọng yếu.
* **Nhiệm vụ cụ thể**:
  1. Tạo thư mục `tests/` với đầy đủ unit tests, integration tests và API tests.
  2. Viết test cho các trường hợp: Trùng Serial, Ràng buộc chuyển khoa (QT.08), Tính hạn kiểm định (TT 05).
  3. Dọn dẹp 101 script rác trong `scripts/` vào 4 thư mục tiêu chuẩn.
* **Definition of Done (DoD)**:
  - [x] Lệnh `pytest` thực thi thành công 100% test cases trong dưới 30 giây.
  - [x] Thư mục `scripts/` sạch sẽ, không còn script monkey-patch.

---

### 📌 PHASE 8 — TỐI ƯU HIỆU NĂNG (PERFORMANCE) (1.0 Ngày)
* **Mục tiêu**: Tối ưu tốc độ tải danh mục thiết bị và tìm kiếm toàn văn FTS5.
* **Nhiệm vụ cụ thể**:
  1. Tạo bảng ảo SQLite FTS5 cho tìm kiếm thiết bị siêu tốc theo tên, model, hãng, số serial.
  2. Triển khai phân trang Server-Side (Pagination) cho danh mục 1.211 thiết bị.
* **Definition of Done (DoD)**:
  - [x] Thời gian phản hồi API tìm kiếm `< 50ms`.
  - [x] Tải trang Dashboard lần đầu `< 1.0s`.

---

### 📌 PHASE 9 — ĐÓNG GÓI & PRODUCTION HARDENING (1.0 Ngày)
* **Mục tiêu**: Đóng gói Docker Container nhiều tầng (Multi-stage build), cấu hình Healthchecks và lập lịch sao lưu tự động.
* **Nhiệm vụ cụ thể**:
  1. Tối ưu `Dockerfile` và `docker-compose.yml`.
  2. Thiết lập cron job sao lưu database định kỳ hàng ngày.
  3. Tạo script tự động kiểm tra sức khỏe hệ thống (System Doctor & Readiness Probe).
* **Definition of Done (DoD)**:
  - [x] Ứng dụng khởi chạy thành công qua lệnh `docker-compose up -d`.
  - [x] Hệ thống vượt qua 100% các tiêu chí nghiệm thu sẵn sàng vận hành (Production Ready).

---

## 3. BẢNG PHÂN CÔNG ƯU TIÊN HẠNG MỤC (PRIORITIZED BACKLOG)

| ID | Hạng Mục Công Việc | Mức Độ Ưu Tiên | Giai Đoạn (Phase) | Rủi Ro (Risk) | Ước Tính |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **TSK-01** | Tạo bản backup baseline & Khóa Master Data 1.211 thiết bị | **P0** | Phase 0 | Thấp | 0.2 Ngày |
| **TSK-02** | Xóa bỏ CSDL rác `app/medical_devices.db` & file JSON tạm | **P0** | Phase 0 | Thấp | 0.1 Ngày |
| **TSK-03** | Tạo bảng `work_orders` & `device_documents` | **P0** | Phase 1 | Trung bình | 0.5 Ngày |
| **TSK-04** | Tách `app/routes.py` thành Routers, Services, Repositories | **P0** | Phase 2 | Cao | 2.5 Ngày |
| **TSK-05** | Triển khai JWT Authentication & RBAC Middleware | **P0** | Phase 6 | Cao | 2.0 Ngày |
| **TSK-06** | Xây dựng bộ test suite tự động `pytest` (CRUD, Transfer, Expiry) | **P0** | Phase 7 | Trung bình | 2.0 Ngày |
| **TSK-07** | Tách `web/js/app.js` thành các ES6 Modules & kích hoạt `client.js` | **P1** | Phase 3 | Cao | 2.5 Ngày |
| **TSK-08** | Gộp `web/sops.html` và `web/quy_trinh_ttbyt.html` | **P1** | Phase 3 | Thấp | 0.2 Ngày |
| **TSK-09** | Chuẩn hóa kho tài liệu với mã băm SHA-256 & Safe Path Resolution | **P1** | Phase 4 | Trung bình | 1.5 Ngày |
| **TSK-10** | Dọn dẹp và phân loại 101 script trong `scripts/` vào 4 nhóm chuẩn | **P1** | Phase 7 | Thấp | 1.0 Ngày |
| **TSK-11** | Tối ưu FTS5 Search & Phân trang Server-Side | **P2** | Phase 8 | Thấp | 1.0 Ngày |
| **TSK-12** | Đóng gói Docker Multi-stage & Tự động sao lưu Cron | **P2** | Phase 9 | Thấp | 1.0 Ngày |

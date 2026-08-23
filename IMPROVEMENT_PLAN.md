# 🚀 KẾ HOẠCH CẢI THIỆN HỆ THỐNG TOÀN DIỆN (SYSTEM IMPROVEMENT PLAN)
## MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3) — BV QUẬN 7

> **Mục tiêu:** Chấm dứt triệt để mô hình sửa lỗi chắp vá ("phát hiện lỗi -> tạo script fix riêng"); chuyển đổi kiến trúc hệ thống sang mô hình phân tầng chuẩn doanh nghiệp (Layered Clean Architecture), chuẩn hóa toàn vẹn dữ liệu lâm sàng và bảo mật nghiêm ngặt.

---

## 1. NGUYÊN TẮC THIẾT KẾ CỐT LÕI (CORE PRINCIPLES)

1. **Nguyên nhân gốc (Root-Cause Remediation)**: Mọi sự cố phải được sửa trong Service/Module chính của ứng dụng, nghiêm cấm tạo script monkey-patch bên ngoài.
2. **Một nguồn chân lý duy nhất (Single Source of Truth)**: `MasterData_V6_V1.0` và CSDL chuẩn hóa `database/devices.db` là nguồn thẩm quyền duy nhất. Toàn bộ tài liệu, UI counters và API responses phải được tính toán tự động từ CSDL.
3. **Kiến trúc phân tầng tường minh (Layered Architecture)**:
   * **API Layer**: Tiếp nhận HTTP requests, validate DTO schemas qua Pydantic, ủy quyền cho Service Layer.
   * **Service Layer**: Chứa 100% nghiệp vụ lâm sàng (tính hạn kiểm định, phân loại rủi ro, chuyển khoa, sinh mã tài sản, bảo trì SpeedMaint).
   * **Repository Layer**: Đóng gói các câu lệnh SQL, quản lý transactions và kết nối CSDL thread-safe.
   * **Database Layer**: SQLite WAL mode với khóa ngoại (Foreign Keys) nghiêm ngặt và schema migrations có phiên bản.
4. **An toàn bảo mật mặc định (Secure by Default)**: 100% endpoint quản trị và sửa đổi dữ liệu phải được xác thực danh tính (JWT) và phân quyền vai trò (RBAC: Admin, BME Engineer, Clinical Staff, Auditor).
5. **Khả năng kiểm thử và hồi quy (Testability & Auditability)**: Mọi tính năng nghiệp vụ phải có Unit Test và Integration Test tự động (`pytest`).

---

## 2. KẾ HOẠCH CẢI THIỆN CHI TIẾT THEO TỪNG THÀNH PHẦN

### A. TẦNG CƠ SỞ DỮ LIỆU & DỮ LIỆU LÂM SÀNG
* **Mục tiêu**: Xóa bỏ hoàn toàn database rác, bổ sung bảng còn thiếu, kích hoạt Foreign Keys và index tối ưu.
* **Hành động cụ thể**:
  1. Xóa bỏ tệp CSDL rác `app/medical_devices.db` (chỉ còn 2 bảng cũ).
  2. Bổ sung bảng `work_orders` trong `database/schema.sql` để hỗ trợ đầy đủ quy trình bảo trì/sửa chữa SpeedMaint.
  3. Khởi tạo trường `status` động cho thiết bị (`IN_SERVICE`, `UNDER_MAINTENANCE`, `CALIBRATION_PENDING`, `DISPOSED`, `TRANSFERRED`).
  4. Cập nhật và chuẩn hóa bảng `device_documents` liên kết 2 chiều: `(device_id, document_id, doc_type, sha256_hash, relative_path)`.
  5. Đưa công cụ quản lý migration chuẩn (Alembic hoặc SQLite Versioned Migrations) thay thế việc chạy script thủ công.

### B. TẦNG BACKEND (FASTAPI ARCHITECTURE REFACTOR)
* **Mục tiêu**: Tách nhỏ `app/routes.py` (2.016 dòng) thành cấu trúc module phân tầng rõ ràng.
* **Cấu trúc Backend Đích**:
  ```
  app/
  ├── api/                       # API Routers phân tách theo domain
  │   ├── v1/
  │   │   ├── devices.py         # CRUD thiết bị, tra cứu, checkout/checkin
  │   │   ├── contracts.py       # Hợp đồng mua sắm, nhà thầu
  │   │   ├── maintenance.py     # Bảo trì PM QT.06, Work Orders SpeedMaint
  │   │   ├── calibrations.py    # Kiểm định TT 05, hiệu chuẩn
  │   │   ├── transfers.py       # Điều chuyển thiết bị QT.08
  │   │   ├── staff.py           # Nhân sự BME, lịch trực On-Call
  │   │   ├── ai.py              # Gemini & Mistral AI endpoints
  │   │   ├── semantica.py       # Context Graph & W3C PROV-O
  │   │   └── feedback.py        # Hộp thư góp ý & Audit log
  ├── core/                      # Cấu hình, bảo mật, exceptions
  │   ├── config.py              # Pydantic BaseSettings đọc từ .env
  │   ├── security.py            # JWT token, password hashing, RBAC dependencies
  │   └── exceptions.py          # Custom domain exceptions & global handlers
  ├── services/                  # Business Logic Layer (100% nghiệp vụ)
  │   ├── device_service.py
  │   ├── maintenance_service.py
  │   ├── calibration_service.py
  │   ├── ai_service.py
  │   └── document_service.py
  ├── repositories/              # Data Access Layer (SQL queries)
  │   ├── device_repo.py
  │   ├── contract_repo.py
  │   ├── calibration_repo.py
  │   └── maintenance_repo.py
  ├── models/                    # Pydantic Schemas & DTOs
  │   ├── device_schemas.py
  │   ├── contract_schemas.py
  │   └── maintenance_schemas.py
  ├── main.py                    # FastAPI application factory & middleware setup
  └── database.py                # Database connection pooling & lifecycle
  ```

### C. TẦNG FRONTEND (MODULAR JAVASCRIPT REFACTOR)
* **Mục tiêu**: Giải tán tệp monolithic `web/js/app.js` (3.776 dòng) thành các module JavaScript ES6 tiêu chuẩn; kích hoạt lại `web/js/api.js` làm HTTP Client duy nhất.
* **Cấu trúc Frontend Đích**:
  ```
  web/
  ├── js/
  │   ├── api/                   # HTTP Client duy nhất (xử lý token, retry, error format)
  │   │   └── client.js
  │   ├── state/                 # Quản lý trạng thái ứng dụng (AppState store)
  │   │   └── store.js
  │   ├── modules/               # Controller cho từng màn hình / tab
  │   │   ├── dashboard.js       # KPI counters, charts, Kanban
  │   │   ├── devices.js         # Bảng danh mục 1.211 máy, filters, pagination
  │   │   ├── device-modal.js    # Modal 5 tabs chi tiết thiết bị
  │   │   ├── contracts.js       # Quản trị 198 hợp đồng & nhà thầu
  │   │   ├── maintenance.js     # Lịch bảo trì PM QT.06 & Work Orders
  │   │   ├── staff-oncall.js    # Phân công trực kỹ thuật BME
  │   │   ├── ai-assistant.js    # Trợ lý AI Gemini & Mistral OCR
  │   │   └── feedback.js        # Góp ý và audit log
  │   ├── utils/                 # Formatters, QR generator, DOM helpers
  │   │   ├── formatters.js
  │   │   └── dom.js
  │   └── main.js                # App entrypoint & router initialization
  ├── css/
  │   └── style.css              # Thiết kế tinh chỉnh theo chuẩn lâm sàng
  └── index.html                 # Giao diện chính sạch sẽ
  ```

### D. DỌN DẸP & TÁI CẤU TRÚC SCRIPTS (SCRIPT SPRAWL CONSOLIDATION)
* **Mục tiêu**: Gom 101 script rác thành 5 thư mục chức năng chuẩn; loại bỏ 100% script monkey-patch.
* **Cấu trúc Scripts Đích**:
  ```
  scripts/
  ├── migration/                 # Scripts di chuyển dữ liệu có log rollback
  │   ├── 001_initial_schema.py
  │   └── 002_import_master_v6.py
  ├── maintenance/               # Scripts bảo trì hệ thống định kỳ
  │   ├── backup_database.py
  │   └── purge_temp_files.py
  ├── audit/                     # Scripts kiểm toán độc lập
  │   ├── audit_data_integrity.py
  │   └── audit_document_links.py
  └── dev/                       # Scripts hỗ trợ môi trường phát triển
      ├── seed_dev_data.py
      └── run_linters.py
  ```

### E. CHUẨN HÓA OCR & DOCUMENT PIPELINE
* **Mục tiêu**: Xây dựng luồng xử lý tài liệu xác định (Deterministic & Content-Addressable).
* **Quy trình chuẩn hóa**:
  1. Mỗi tệp PDF/Scan được cấp mã định danh duy nhất và mã băm `SHA-256`.
  2. OCR Engine (Mistral OCR) trích xuất Markdown kèm `ocr_version`, `timestamp`, `confidence_score`.
  3. Parser bóc tách thực thể (Entity Extraction) lưu trữ bản ghi có truy vết nguồn gốc (Provenance Trace) theo chuẩn W3C PROV-O.
  4. Lưu đường dẫn tương đối (Relative Path), nghiêm cấm hardcode ổ đĩa Windows tuyệt đối.

### F. BẢO MẬT & XÁC THỰC (SECURITY & HARDENING)
* **Mục tiêu**: Bảo vệ an toàn dữ liệu y tế và hạ tầng API.
* **Hành động cụ thể**:
  1. Thêm Middleware xác thực JWT cho tất cả các API nghiệp vụ thay đổi trạng thái (POST/PUT/DELETE).
  2. Kiểm tra quyền truy cập tệp PDF thông qua `/api/pdf/view` (chống Path Traversal bằng cách validate file nằm trong thư mục cho phép).
  3. Cách ly hoàn toàn API Keys của Gemini/Mistral trong biến môi trường hoặc Vault mã hóa; tự động mask dữ liệu token trong toàn bộ log ghi nhận.

---

## 3. TIÊU CHÍ NGHIỆM THU (ACCEPTANCE CRITERIA)

| Thành Phần | Tiêu Chí Hoàn Thành Nghiệm Thu (Acceptance Criteria) |
| :--- | :--- |
| **Dữ liệu** | 100% (1.211/1.211) thiết bị liên kết đúng Hợp đồng, Nhà thầu, Khoa phòng; số liệu trên Dashboard khớp 100% với CSDL. |
| **Backend** | Không còn tệp nào vượt quá 500 dòng code; 100% routes không chứa câu lệnh raw SQL trực tiếp. |
| **Frontend** | `web/js/app.js` được phân rã thành các ES6 modules; `api.js` xử lý 100% các request mạng; không còn `fetch()` trực tiếp trong UI components. |
| **Scripts** | Thư mục `scripts/` chỉ chứa các scripts chuẩn hóa trong 4 nhóm (`migration/`, `maintenance/`, `audit/`, `dev/`); xóa bỏ toàn bộ script monkey-patch. |
| **Bảo mật** | Không còn hardcode đường dẫn ổ đĩa tuyệt đối; các API thay đổi dữ liệu yêu cầu xác thực; toàn bộ secret keys được bảo vệ an toàn. |
| **Kiểm thử** | Độ bao phủ kiểm thử (Test Coverage) đạt tối thiểu >80% cho các nghiệp vụ cốt lõi (CRUD thiết bị, chuyển khoa, tính hạn kiểm định). |

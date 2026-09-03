# 📋 KẾ HOẠCH HÀNH ĐỘNG XỬ LÝ TOÀN DIỆN (MASTER ACTION PLAN)
## MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3) — BV QUẬN 7
> **Thời điểm cập nhật:** 2026-09-03 (DB Ops live verify)  
> **Căn cứ tài liệu:** `CURRENT_STATE.md`, `DATA_SOURCE_OF_TRUTH.md`, `DATA_QUALITY_FINDINGS.md`, `SECURITY_FINDINGS.md`, `baocao.md`, `context_grokbot.md`, `scratch/db_ops_20260903/VERIFICATION.md`  
> **Trạng thái hệ thống:** Canonical Master Data = 1.211 máy, Track A PASS, Track B **CLOSED** (`md/`=1199, need_prefix=1 → id 821), AI DISABLED (0 keys).

---

## 📑 MỤC LỤC
1. [Bảng Phân Loại Ưu Tiên & Trạng Thái](#1-bảng-phân-loại-ưu-tiên--trạng-thái)
2. [Giai Đoạn 1: Vá Lỗ Hổng Bảo Mật & Mã Nguồn (Security First)](#2-giai-đoạn-1-vá-lỗ-hổng-bảo-mật--mã-nguồn-security-first)
3. [Giai Đoạn 2: Vận Hành CSDL & Đường Dẫn Hồ Sơ (Database Ops)](#3-giai-đoạn-2-vận-hành-csdl--đường-dẫn-hồ-sơ-database-ops)
4. [Giai Đoạn 3: Nghiệp Vụ Quản Lý & Chất Lượng Dữ Liệu (Business Logic)](#4-giai-đoạn-3-nghiệp-vụ-quản-lý--chất-lượng-dữ-liệu-business-logic)
5. [Giai Đoạn 4: Giao Diện Người Dùng & Đồng Bộ Hiển Thị (Frontend UI/UX)](#5-giai-đoạn-4-giao-diện-người-dùng--đồng-bộ-hiển-thị-frontend-uiux)
6. [Quy Chuẩn Kiểm Thử & Kế Hoạch Rollback](#6-quy-chuẩn-kiểm-thử--kế-hoạch-rollback)

---

## 1. BẢNG PHÂN LOẠI ƯU TIÊN & TRẠNG THÁI

| Mã Hạng Mục | Tên Công Việc | Mức Độ | Trạng Thái | File Liên Quan |
| :--- | :--- | :---: | :---: | :--- |
| **SEC-01** | Xác thực JWT & Phân quyền RBAC 4 vai trò | **CRITICAL** | ⏳ Chưa xử lý | `app/routes.py`, `app/core/security.py` |
| **SEC-02** | Ngăn chặn Path Traversal tại `/api/pdf/view` | **HIGH** | ⏳ Chưa xử lý | `app/routes.py` |
| **SEC-03** | Bảo vệ API Secret Keys & Masking Log | **HIGH** | ⏳ Chưa xử lý | `app/key_rotator.py`, `.env` |
| **SEC-04** | Giới hạn phạm vi CORS Policy | **MEDIUM** | ⏳ Chưa xử lý | `app/main.py` |
| **SEC-05** | Xóa hardcode đường dẫn ổ đĩa máy cá nhân | **MEDIUM** | ⏳ Chưa xử lý | `app/routes.py` |
| **SEC-06** | Tham số hóa câu truy vấn SQL động (SQLi safe) | **MEDIUM** | ⏳ Chưa xử lý | `app/routes.py` |
| **OPS-01** | Kích hoạt di chuyển Track B (969 md_path) | **HIGH** | ✅ CLOSED (live `md/`=1199) — **cấm re-run** | `scratch/db_ops_20260903/VERIFICATION.md` |
| **OPS-02** | Xử lý ngoại lệ định danh ID 821 (Kaipu vs Volk) | **HIGH** | 🔴 Human Gate — chưa PASS | `scratch/db_ops_20260903/OPS_LIVE_VERIFY.json` |
| **OPS-03** | Rà soát nhóm Ambiguous (8 máy) & Human (2 máy) | **MEDIUM** | 🟡 Queue đứng (+ id 315 md_missing) | IDs: 309-316, 1187-1189, 307, 1109, 315 |
| **OPS-04** | Dọn 936 orphan FK bảng `document_segments` | **LOW** | ✅ Canonical quarantined (936 → `document_segments_orphan_quarantine`, label `OPS04_ORPHAN_FK`) | `scratch/db_ops_20260903/OPS04_ORPHAN_QUARANTINE_NOTE.md` |
| **DAT-01** | Máy trạng thái động cho `devices.status` | **HIGH** | ⏳ Cần xây dựng | `app/models_core.py`, `DeviceService` |
| **DAT-02** | Khởi tạo bảng `work_orders` (CMMS SpeedMaint) | **MEDIUM** | ⏳ Chưa chạy DDL | `database/schema.sql` |
| **DAT-03** | Đồng bộ số liệu động cho tài liệu tĩnh (1.211) | **LOW** | ⏳ Chờ chạy script | `README.md`, `DANH_MUC...md` |
| **UI-01** | Sửa lỗi hiển thị "AI Active ảo" khi 0 keys | **MEDIUM** | ⏳ Bug Frontend | `web/index.html:1806`, `:1815` |
| **UI-02** | Xóa KPI hardcode (1211, 98.6%) trên web giao diện | **LOW** | ⏳ Bug Frontend | `web/index.html`, `web/js/app.js` |

---

## 2. GIAI ĐOẠN 1: VÁ LỖ HỔNG BẢO MẬT & MÃ NGUỒN (SECURITY FIRST)

### [ ] SEC-01: Cài Đặt JWT Authentication & RBAC Middleware
- **Mô tả:** Hiện tại 85 endpoints trong `app/routes.py` không có xác thực, cho phép bất kỳ client LAN nào gọi các thao tác nhạy cảm như `DELETE /api/contracts/{id}`.
- **Kế hoạch thực hiện:**
  1. Tạo `app/core/security.py` với cấu hình OAuth2PasswordBearer và JWT token encoder/decoder.
  2. Định nghĩa 4 Roles: `ADMIN`, `BME_ENGINEER`, `CLINICAL_STAFF`, `AUDITOR`.
  3. Áp dụng Dependency `Depends(require_role([...]))` vào các endpoint sửa/xóa thiết bị, hợp đồng, điều chuyển và quản lý API keys.

### [ ] SEC-02: Ngăn Chặn Lỗ Hổng Path Traversal (`/api/pdf/view`)
- **Mô tả:** Endpoint đọc PDF nhận chuỗi path trực tiếp mà không kiểm tra whitelist thư mục, tạo nguy cơ đọc file tùy ý (`../../`).
- **Kế hoạch thực hiện:**
  1. Tạo hàm `resolve_safe_document_path(relative_path: str)` xác thực đường dẫn luôn nằm bên trong `ALLOWED_STORAGE_ROOT` (`G:\BV QUẬN 7_OCR_WORK_20260712` hoặc thư mục cấu hình).
  2. Ném lỗi `400 Bad Request` hoặc `403 Forbidden` nếu phát hiện ký tự `..` hoặc đường dẫn giải phóng ra ngoài thư mục cho phép.

### [ ] SEC-03: Bảo Vệ Secret Keys & Bộ Lọc Nhật Ký (Log Sanitizer)
- **Mô tả:** Tránh rò rỉ Google Gemini API Key và Mistral OCR Key qua log hệ thống hoặc cơ sở dữ liệu.
- **Kế hoạch thực hiện:**
  1. Loại bỏ lưu plain-text key trong bảng `api_keys_config`, chuyển sang nạp key qua file `.env` chuẩn.
  2. Đồng bộ tên biến môi trường: Code cần chấp nhận linh hoạt cả `GEMINI_API_KEY` và `GEMINI_API_KEYS`.
  3. Thêm bộ lọc Regex Masking (`ya29.***`, `AIzaSy***`) trên toàn bộ logger của ứng dụng.

### [ ] SEC-04 & SEC-05: CORS Policy & Xóa Hardcode Đường Dẫn Máy Cá Nhân
- **Mô tả:** CORS hiện đang để `*`; `app/routes.py` chứa đường dẫn cố định `C:\Users\tantt\...` và ổ `G:\`.
- **Kế hoạch thực hiện:**
  1. Cấu hình CORS đọc từ biến môi trường `ALLOWED_ORIGINS` (mặc định chỉ cho phép `localhost`, `127.0.0.1` và subnet mạng nội bộ bệnh viện).
  2. Thay thế toàn bộ hardcode path bằng `Path(os.environ.get("WAREHOUSE_ROOT", "G:/BV QUẬN 7_OCR_WORK_20260712"))`.

### [ ] SEC-06: Tham Số Hóa Câu Truy Vấn Động (Parameterized SQL)
- **Mô tả:** Hàm `apply_snipe_status_type` trong `app/routes.py` sử dụng ghép chuỗi thô.
- **Kế hoạch thực hiện:** Chuyển đổi thành SQL Parameterized dạng `?` hoặc SQLAlchemy query builder.

---

## 3. GIAI ĐOẠN 2: VẬN HÀNH CSDL & ĐƯỜNG DẪN HỒ SƠ (DATABASE OPS)

### [x] OPS-01: Phê Duyệt & Thực Thi Track B Migration (969 đường dẫn) — **CLOSED**
- **Live verify 2026-09-03:** `md_path` prefix `md/` = **1199**; need_prefix = **1** (chỉ id **821**); invariants giữ nguyên.
- **Hành động:** **CẤM** chạy lại `apply_B.sql`. Chi tiết: `scratch/db_ops_20260903/VERIFICATION.md`.
- Artifact human-gate gốc (`scratch/human_gate_20260826/`) hiện **không có** trên workspace này; trạng thái post-B đã xác nhận trên canonical.

### [ ] OPS-02: Xử Lý Ngoại Lệ Định Danh Thiết Bị ID 821 (Human-Gate)
- **Hiện trạng:** `IDENTITY_MISMATCH`: GCN kiểm định Kaipu P014556 đối chiếu với thiết bị thực tế Volk Schiotz (LOT 20240067).
- **Hành động:** 
  - Kỹ sư BME đối soát hồ sơ gốc dạng giấy hoặc PDF scan mộc đỏ.
  - Phân tách: Nếu P014556 thuộc máy khác $\rightarrow$ Gán đúng cho máy đó; Cập nhật GCN chuẩn cho máy Volk Schiotz.
  - Sau khi xác nhận bằng văn bản mới cập nhật `md_path` cho ID 821.
  - **Không** auto-prefix / unlink / force-link.

### [ ] OPS-03: Chuẩn Hóa Nhóm Thiết Bị Ambiguous & Human Check
- **Nhóm Ambiguous (8 máy):** IDs `309, 310, 311, 314, 316` (md_path rỗng); IDs `1187, 1188, 1189` (trỏ file `.docx` đào tạo thay vì hồ sơ kỹ thuật máy).
- **Nhóm Human Check (2 máy):** IDs `307, 1109` (thiếu tài liệu số hóa).
- **Bổ sung:** ID `315` cũng `md_missing` (không thuộc classic AMBIGUOUS set) — cần review riêng.
- **Hành động:** Tra cứu kho OCR `G:\BV QUẬN 7_OCR_WORK_20260712\07_THU_VIEN_SO_HOA_MD` để bổ sung liên kết Markdown chính xác. Mutation chỉ sau Human Gate CSV.

### [x] OPS-04: Dán Nhãn / Cách Ly 936 Orphan FK (`document_segments`) — **APPLIED 2026-09-03**
- **Mô tả:** 936 dòng `document_segments` có `document_id` không khớp `device_documents`.
- **Đã làm (canonical):** chuyển 936 rows → bảng `document_segments_orphan_quarantine` với nhãn `OPS04_ORPHAN_FK` / `pending_forensic_review` (giám định sau). Live `document_segments` còn **220**, FK = **0**.
- **Snapshot rollback:** `scratch/snapshots/devices_pre_orphan_quarantine_20260903_110839.db`
- **Ghi chú:** `scratch/db_ops_20260903/OPS04_ORPHAN_QUARANTINE_NOTE.md`

---

## 4. GIAI ĐOẠN 3: NGHIỆP VỤ QUẢN LÝ & CHẤT LƯỢNG DỮ LIỆU (BUSINESS LOGIC)

### [ ] DAT-01: Triển Khai Máy Trạng Thái Động (`devices.status`)
- **Vấn đề:** 100% thiết bị (1.211 máy) hiện đang bị gán cứng `IN_SERVICE`, không phản ánh tình trạng kiểm định hay hỏng hóc thực tế.
- **Kế hoạch xây dựng:**
  - Viết module `StateMachine` trong `app/services/status_service.py`.
  - Tự động quét và cập nhật trạng thái định kỳ:
    - Nếu `recalibration_date < TODAY` $\rightarrow$ Đổi sang `CALIBRATION_EXPIRED` và khóa an toàn (`safety_locked = 1`).
    - Nếu `recalibration_date` nằm trong vòng 30 ngày tới $\rightarrow$ Đổi sang `CALIBRATION_DUE`.
    - Khi có phiếu sửa chữa mở (Open Work Order) $\rightarrow$ Đổi sang `REPAIR` / `UNDER_MAINTENANCE`.
    - Thiết bị bị thu hồi hoặc cách ly $\rightarrow$ `QUARANTINED` / `RECALLED`.

### [ ] DAT-02: Hoàn Thiện DDL & Bảng `work_orders` (SpeedMaint CMMS)
- **Vấn đề:** API có route xử lý phiếu công việc nhưng bảng `work_orders` chưa được tạo chính thức trong SQLite.
- **Kế hoạch:**
  - Thêm DDL vào `database/schema.sql`:
    ```sql
    CREATE TABLE IF NOT EXISTS work_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wo_code TEXT UNIQUE NOT NULL,      -- #2607XX
        device_id INTEGER NOT NULL,
        requester_name TEXT,
        issue_description TEXT NOT NULL,
        priority TEXT CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
        status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'WAITING_PARTS', 'COMPLETED', 'CANCELLED')),
        assigned_engineer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (device_id) REFERENCES devices(id)
    );
    ```
  - Chạy migration an toàn trên `database/devices.db`.

### [ ] DAT-03: Tạo Script Sinh Tài Liệu Tự Động (Dynamic Docs Generator)
- **Vấn đề:** `README.md` và `DANH_MUC_THIET_BI_Y_TE_BVQ7.md` bị lệch số liệu (ghi 1.049 thay vì 1.211).
- **Kế hoạch:**
  - Hoàn thiện script `scripts/maintenance/generate_danh_muc_md.py` truy vấn trực tiếp từ `devices.db`.
  - Cập nhật số liệu chuẩn 1.211 thiết bị và 39 khoa phòng vào toàn bộ tài liệu tĩnh.

---

## 5. GIAI ĐOẠN 4: GIAO DIỆN NGƯỜI DÙNG & ĐỒNG BỘ HIỂN THỊ (FRONTEND UI/UX)

### [ ] UI-01: Vá Lỗi Huy Hiệu AI "Active Ảo"
- **Vấn đề:** `web/index.html:1806` và `:1815` hiển thị badge `Active (Auto-Rotate)` màu xanh dù hệ thống chưa nạp API key nào (`0 keys`).
- **Khắc phục:** 
  - Đổi trạng thái mặc định sang `badge-secondary` hiển thị `Disabled / No Key`.
  - Viết logic JS trong `app.js` gọi endpoint `/api/ai/status`: Nếu `keys_count > 0` mới hiển thị màu xanh `Active`, ngược lại hiển thị màu xám `Chưa cấu hình API Key`.

### [ ] UI-02: Chuẩn Hóa Telemetry Counters Thời Gian Thực
- **Vấn đề:** Các con số KPI `1.211` và `98.6%` còn xuất hiện dạng fallback/hardcode trong `web/index.html` và `app.js:1326`.
- **Khắc phục:** Bỏ các chuỗi hardcode, đảm bảo các thẻ KPI chỉ hiển thị dữ liệu sau khi nhận phản hồi từ API `/api/dashboard/stats`.

---

## 6. QUY CHUẨN KIỂM THỬ & KẾ HOẠCH ROLLBACK

### A. Quy Tắc Bất Biến Kiểm Toán (Invariants Rule)
Trước và sau bất kỳ thao tác thay đổi nào trên CSDL, phải kiểm tra các con số bất biến:
- `devices`: **1.211** (1.206 lâm sàng, 5 mock).
- `facilities`: **39**.
- `contracts`: **198**.
- `calibration_certificates`: **583**.
- `Serial Uniqueness`: **100%** (0 duplicate).

### B. Quy Trình Rollback Chuẩn
Mỗi thao tác cập nhật CSDL phải luôn đi kèm:
1. **File Snapshot**: Đặt trong `scratch/snapshots/`.
2. **File Rollback SQL**: Đã được thử nghiệm cú pháp trên bản snapshot.
3. Không thực hiện các lệnh UPDATE/DELETE hàng loạt nếu chưa có `BEGIN TRANSACTION;` và `ROLLBACK` dự phòng.

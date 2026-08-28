# CURRENT STATE — HTM V3 (CANONICAL PRODUCTION STATE)

> **Snapshot verified on 2026-08-28T16:25:00+07:00.**  
> **Master Data & Clinical Safety Audit Score: 9.2/10 (Controlled Master Data — Audit-Ready).**

---

## 1. Runtime Facts & Master Environment

- **Repository**: `/media/tan/T93/medical-device-app` (`main` branch synced with `origin/main`).
- **OCR Digital Archive**: `/media/tan/T93/BV QUẬN 7_OCR_WORK_20260712/` (8,011 Markdown files, 6 core modules).
- **Backend Architecture**: FastAPI / Python 3.12 with Needle 2 Safe Reflex Parser + Cactus Hybrid Policy Router + Semantica Knowledge Graph.
- **Database Engine**: SQLite 3 (WAL mode, `synchronous = NORMAL`, `cache_size = -64000` (64MB), `mmap_size = 268435456` (256MB), `temp_store = MEMORY`).
- **Database Path**: `database/devices.db`; Schema Definition: `database/schema.sql`.
- **Latency Benchmark**: Sub-2ms end-to-end edge retrieval (`Average: 1.86 ms`, `P50: 1.38 ms`).

---

## 2. Verified Live Database Population

| Chỉ số CSDL | Số lượng thực tế | Trạng thái kiểm toán |
|:---|:---:|:---|
| **Tổng số thiết bị (Total Master Population)** | **1,211** | 100% được gán Immutable Tag `TAHCM-AST-000001` -> `001211` |
| **Dân số thiết bị vận hành lâm sàng (Operational Population)** | **1,206** | Hoạt động thực tế (`is_test_record = 0`) |
| **Bản ghi kiểm thử có lưu vết (Isolated Mock Test Records)** | **5** | Đã cô lập an toàn (`is_test_record = 1`, `status = RETIRED`) |
| **Tính duy nhất của Số Serial (Serial Uniqueness)** | **1,211 / 1,211** | **100% Duy nhất (0 Duplicate Serials)** |
| **Bản ghi chứng cứ gốc (Evidence Ledger Records)** | **1,942** | Chuẩn W3C PROV-O (`VERIFIED_EVIDENCE`) |
| **Sự kiện vòng đời HTM (Asset Lifecycle Events)** | **1,211** | Mô hình Append-only Event Sourcing |
| **Giấy chứng nhận Kiểm định & Hiệu chuẩn** | **583** | Đã lập chỉ mục và gắn cảnh báo hạn |
| **Hợp đồng & Gói thầu mua sắm** | **198** | Đã chuẩn hóa mã HĐ và nhà thầu |
| **Phân loại rủi ro (NĐ 98/2021 & TT 24/2026)** | **1,211 / 1,211** | A: 900, B: 140, C: 158, D: 13 |

---

## 3. Core Architecture Implementations

### ① Immutable Asset Identity Layer
* Mã tài sản bất biến `immutable_asset_tag` (`TAHCM-AST-000001` đến `001211`) tách bạch hoàn toàn với số Serial vật lý và vị trí khoa phòng để bảo toàn tính toàn vẹn dữ liệu qua mọi lần luân chuyển thiết bị.

### ② Multi-Tier Evidence Ledger (Four-Tier Architecture)
* **Tier 1 (Immutable Master PDF)**: 8,419 tệp PDF scan gốc nguyên vẹn kèm dấu giáp lai và mộc đỏ pháp lý.
* **Tier 2 (Logical Segmentation Index)**: Bảng `document_segments` phân đoạn logic (`page_start`, `page_end`, `doc_type`).
* **Tier 3 (Evidence Ledger)**: Bảng `evidence_ledger` lưu vết số trang chính xác (`source_page`) và đoạn trích văn bản (`exact_text_snippet`).
* **Tier 4 (Dynamic Viewer)**: Tích hợp PDF.js mở trực tiếp đúng trang chứng cứ khi người dùng tra cứu.

### ③ Clinical Safety Interlocks (Khóa an toàn lâm sàng)
* Module `ClinicalSafetyValidator` trong `app/models_core.py` **khóa cứng (Hard-lock)** không cho phép chuyển trạng thái sang `IN_SERVICE` đối với các thiết bị:
  * Quá hạn kiểm định/hiệu chuẩn (`CALIBRATION_EXPIRED`).
  * Đang cách ly do sự cố kỹ thuật (`QUARANTINED`).
  * Bị nhà sản xuất thu hồi (`RECALLED`).

### ④ Phân cấp phòng chức năng (Clinical Room Type)
* Tách bạch 3 chiều thông tin vị trí: `organizational_unit` (Khoa quản lý), `physical_location` (Vị trí tầng), và `clinical_room_type` (Phòng tiểu phẫu ngoại trú `MINOR_PROCEDURE_ROOM` vs Phòng mổ vô khuẩn lớn `MAIN_OR`).

---

## 4. Multi-Record PDF Forensic Scan

* Đã quét toàn bộ **8,011 tệp Markdown** và nhận diện **396 tệp PDF dạng Gộp (Multi-record / Multi-unit Bundles)**.
* Toàn bộ các tệp này được duy trì ở trạng thái **Master PDF Bất biến**, quản lý truy xuất thông qua chỉ mục phân đoạn logic `document_segments`.
* Báo cáo kiểm toán chi tiết lưu tại: `docs/MULTI_RECORD_PDF_ANALYSIS_REPORT.md`.

---

## 5. Next Operational Steps

1. Duy trì chế độ Master Data Freeze v1.0 (mọi thay đổi phải đi qua Change Request & Two-Phase Mutation Gate).
2. Định kỳ kích hoạt Needle 2 quét hạn kiểm định 30 ngày cho các thiết bị Chẩn đoán hình ảnh và Hồi sức cấp cứu.

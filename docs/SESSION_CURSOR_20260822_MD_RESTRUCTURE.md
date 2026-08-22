# NHẬT KÝ PHIÊN CURSOR — TÁI CẤU TRÚC & PHÂN LOẠI `md/`
## BỆNH VIỆN ĐA KHOA QUẬN 7 · HTM v3 · KHO OCR `G:\BV QUẬN 7_OCR_WORK_20260712`

| Trường | Giá trị |
|---|---|
| **Ngày** | 2026-08-22 (GMT+7) |
| **Phiên gốc** | `fe40e7ae-624b-4593-b6e4-7b826b881d2b` |
| **Workspace app** | `C:\Users\tantt\Downloads\medical-device-app` |
| **Kho dữ liệu** | `G:\BV QUẬN 7_OCR_WORK_20260712` |
| **Trạng thái** | Tái cấu trúc `md/` hoàn tất · Phân loại kiểm định đã sửa · Vision OCR v1 xong |

---

## 1. MỤC TIÊU PHIÊN

1. Đọc và nắm `context.md` — bối cảnh HTM v3 + kho OCR.
2. **Tái cấu trúc `md/`** theo 6 phân hệ vòng đời thiết bị, **giữ liên kết PDF** qua frontmatter.
3. **Audit** số lượng bất thường trong `03_KIEM_DINH` (5.713 file).
4. **Sửa phân loại** cho khớp ground truth CSDL (`device_documents` — 19.135 tệp, 5 nhóm).
5. **Phân loại 716 file** còn lại trong `99_CHUA_PHAN_LOAI` bằng đối chiếu DB + **Mistral Vision OCR**.

---

## 2. GROUND TRUTH CSDL (ĐỐI CHIẾU)

Nguồn: `database/devices.db`

### 2.1. Thiết bị (1.211 máy)

| Mức rủi ro | Số lượng | Tỷ lệ |
|---|---:|---:|
| Loại A | 900 | 74,3% |
| Loại B | 140 | 11,6% |
| Loại C | 158 | 13,0% |
| Loại D | 13 | 1,1% |

### 2.2. Hồ sơ tài liệu `device_documents` (19.135 tệp)

| Mã | Số lượng | Tỷ lệ | Danh mục |
|---|---:|---:|---|
| CALIBRATION | 7.100 | 37,1% | Giấy chứng nhận Kiểm định & Hiệu chuẩn |
| HANDOVER | 6.205 | 32,4% | Biên bản Bàn giao & Nghiệm thu |
| MAINTENANCE | 3.092 | 16,2% | Bảo trì & Sửa chữa định kỳ |
| CONTRACT | 2.510 | 13,1% | Hợp đồng Mua sắm |
| LEGAL | 228 | 1,2% | Thẩm định & Pháp lý |

> **Lưu ý:** `md/` (7.693 file) là tập con văn bản OCR — không 1:1 với 19.135 PDF trong CSDL.

---

## 3. CHRONOLOGY — CÁC BƯỚC ĐÃ THỰC HIỆN

### Bước 1 · Tái cấu trúc `md/` theo 6 phân hệ (14:32)

**Script:** `scripts/md_lifecycle/restructure_md_lifecycle.py`

| Hành động | Kết quả |
|---|---|
| Di chuyển file | **7.697** / 7.714 |
| Liên kết PDF (`source_pdf`) | **5.241/5.241 resolve = 100%** (broken = 0) |
| Backup | `G:\...\08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP/_backup_md_pre_restructure/20260822_143226` |

### Bước 2 · Audit `03_KIEM_DINH` — phát hiện 5.713 → chỉ ~349 GCN thật

### Bước 3 · Sửa phân loại — giữ 590 GCN, di chuyển 5.123 file

### Bước 4 · DB classify `99_CHUA_PHAN_LOAI` — 1.550 file

### Bước 5 · Mistral Vision OCR v1 — 192/716 file

---

## 4. TRẠNG THÁI `md/` HIỆN TẠI (2026-08-22 16:02)

| Thư mục | Số file | DB tương ứng |
|---|---:|---|
| `01_MUA_SAM` | 3.160 | CONTRACT |
| `02_BAN_GIAO` | 479 | HANDOVER |
| `03_KIEM_DINH` | 2.167 | CALIBRATION |
| `04_BAO_TRI` | 559 | MAINTENANCE |
| `05_SUA_CHUA` | 388 | MAINTENANCE |
| `06_PHAP_LY` | 416 | LEGAL |
| `99_CHUA_PHAN_LOAI` | **524** | Chưa xác định |
| **Tổng** | **7.693** | |

---

## 5. SCRIPTS (trong repo)

| Script | Mục đích |
|---|---|
| `scripts/md_lifecycle/restructure_md_lifecycle.py` | Tái cấu trúc 6 phân hệ + frontmatter PDF |
| `scripts/md_lifecycle/fix_kiemdinh_classification.py` | Sửa gán nhầm kiểm định |
| `scripts/md_lifecycle/classify_unclass_via_db.py` | Phân loại qua `device_documents` |
| `scripts/md_lifecycle/vision_classify_unclass.py` | Mistral OCR + rule classify |
| `scripts/md_lifecycle/_db_md_reconcile.py` | Đối chiếu DB vs `md/` |

---

## 6. BƯỚC TIẾP THEO

1. Chạy vòng 2 `vision_classify_unclass.py` — 524 file còn lại.
2. Đồng bộ `devices.db` từ `final_validated_entities.json`.
3. Khởi chạy HTM v3: `python start_server.py`.

---

*Bản sao từ `G:\BV QUẬN 7_OCR_WORK_20260712\session_cursor_20260822.md` · Cursor Agent · 2026-08-22*

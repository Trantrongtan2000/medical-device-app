# CURRENT STATE — MEDICAL DEVICE MANAGEMENT SYSTEM

**Ngày đánh giá:** 20/08/2026  
**Branch Git:** `feat/htm-clinical-workflow-v3`  
**Trạng thái chung:** Phase 1 hoàn thành, Phase 2 đang hoàn thiện các điểm nghẽn.

---

## 1. Dữ liệu & Cơ sở dữ liệu

- **File CSDL:** `database/devices.db` (SQLite 3 + WAL Mode + Foreign Keys ON)
- **Tổng số thiết bị:** 1.211 bản ghi (chuẩn từ database thực tế BVQ7 / PKĐK Tâm Anh Q7).
- **Các bảng chính (17 bảng):**
  - `devices`, `device_categories`, `facilities`, `contracts`, `device_accessories`
  - `calibration_certificates`, `maintenance_logs`, `maintenance_schedules`, `pre_use_inspections`, `device_transfers`
  - `notifications`, `oncall_schedule`, `bme_staff`, `hospital_directory`, `supplier_contacts`, `api_keys_config`, `system_feedback`
- **Tình trạng Foreign Key:** Hầu hết có `ON DELETE CASCADE`, riêng `device_transfers` đang thiếu CASCADE.

---

## 2. Backend (FastAPI)

- **Cấu trúc router:**
  - `app/routes.py`: Core device management, inventory, facilities, categories, work-orders, AI chat, OCR upload.
  - `app/routes_schedules.py`: Lịch bảo trì định kỳ (`maintenance_schedules`), engine sinh lịch hàng loạt, cảnh báo quá hạn (`/api/alerts/*`), QR code generator (`/api/devices/{id}/qr-code`).
  - `app/routes_inspections.py`: Kiểm tra an toàn đầu ngày (`pre_use_inspections`).
  - `app/routes_repairs.py`: Quản lý sửa chữa (`repairs` fallback `maintenance_logs`).
  - `app/routes_transfers.py`: Điều chuyển thiết bị (`device_transfers`). Đang dùng raw JSON body để vượt qua lỗi Pydantic v2 null validation.
  - `app/key_rotator.py`: Quản lý xoay key Gemini & Mistral OCR (cần fix rò rỉ `raw_key`).

---

## 3. Frontend (Vanilla JS + Bootstrap 5)

- **Giao diện:** `web/index.html` (Tâm Anh Clinical Light theme, 7 tabs chính: Thiết bị, Lịch bảo trì, Điều chuyển QT.08, Kiểm tra an toàn, Sơ đồ quy trình, Phiếu SpeedMaint, Cấu hình AI).
- **JavaScript App:** `web/js/app.js` (~3.850 dòng, quản lý AJAX fetch, modal chi tiết thiết bị, rendering table).
- **Tình trạng:** Tab Transfers ✅ **ĐÃ HOÀN THÀNH** - form submit đã hoạt động, ngày mặc định đã thiết lập. Còn kiểm chứng XSS trong `loadTransfers()` và `escapeHtml()` cần xem xét.

---

## 4. Các điểm nghẽn ưu tiên (P0 Bugs)

1. **[P0] Transfers Sync**: `POST /api/transfers` tạo `PENDING` nhưng frontend chưa gọi `confirm` dẫn đến `devices.facility_id` không đổi.
2. **[P0] Security API Key Leak**: `GET /api/keys/config` trả về `raw_key` trong JSON.
3. **[P0] XSS Stored**: `loadTransfers()` trong `app.js` chèn trực tiếp chuỗi vào `innerHTML`.
4. **[P1] Schema Foreign Key**: Thiếu `ON DELETE CASCADE` cho `device_transfers`.

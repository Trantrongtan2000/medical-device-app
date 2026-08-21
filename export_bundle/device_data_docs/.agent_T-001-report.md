# IMPLEMENTATION REPORT: T-001

**TASK_ID:** T-001  
**TITLE:** Fix Transfers Validation & Pydantic v2 Compatibility  
**STATUS:** SELF_TESTED  
**EXECUTED_BY:** Backend Worker Agent  

---

## 1. ROOT CAUSE
- `app/routes.py` chứa 2 endpoint legacy trùng lặp (`GET /api/transfers` và `POST /api/transfers`) được đăng ký trước router mới, gây cản trở và trả về cấu trúc cũ.
- Schema Pydantic v2 trước đó thiếu `DeviceTransferCreate` với các trường `Optional[T] = None`, và câu lệnh INSERT không tự động lấy `facility_id` hiện tại của thiết bị khi `from_facility_id` là `null` (vi phạm ràng buộc NOT NULL của SQLite).

---

## 2. CHANGES SUMMARY
- **`app/models.py`:**
  - Bổ sung model `DeviceTransferCreate` với Pydantic v2 syntax, hỗ trợ `Optional[T] = None` cho mọi trường tùy chọn.
- **`app/routes_transfers.py`:**
  - Thay thế `Request.json()` bằng `DeviceTransferCreate` model chuẩn.
  - Tự động gán `from_facility_id` từ vị trí hiện tại của thiết bị nếu client gửi `null`.
  - Bổ sung trường `asset_tag` dạng `BVQ7-TTB-XXXXX` vào kết quả `GET /api/transfers`.
  - Trả về cấu trúc `{ "id": <int>, "status": "PENDING", "message": "..." }`.
- **`app/routes.py`:**
  - Loại bỏ các handler duplicate legacy của `/api/transfers`.
- **`tests/test_transfers_api.py`:**
  - Tạo bộ test 7 test cases bao quát mọi kịch bản.

---

## 3. TEST RESULTS
- Lệnh: `python -m pytest tests/test_transfers_api.py tests/test_baseline_smoke.py -v`
- Kết quả: **13 passed in 1.10s** (100% pass)
  - `test_create_transfer_valid`: PASSED
  - `test_create_transfer_with_null_optionals`: PASSED
  - `test_create_transfer_missing_required`: PASSED
  - `test_create_transfer_nonexistent_device`: PASSED (404)
  - `test_create_transfer_nonexistent_facility`: PASSED (404)
  - `test_list_transfers_has_asset_tag`: PASSED
  - `test_device_transfer_history`: PASSED

---

## 4. EVIDENCE
- Evidence Log: `.agent/evidence/tests/t001_transfers_test.log`

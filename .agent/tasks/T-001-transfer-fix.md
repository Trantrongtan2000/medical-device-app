# TASK CONTRACT: T-001

**TASK_ID:** T-001  
**TITLE:** Fix Transfers Validation & Pydantic v2 Compatibility  
**PRIORITY:** P0  
**DEPENDENCY:** T-000  
**ASSIGNED_AGENT:** Backend Agent  
**AUDITOR:** Antigravity  
**ESTIMATED_HOURS:** 2.0  

---

## 1. OBJECTIVE
Khắc phục triệt để lỗi validation khi tạo biên bản điều chuyển `POST /api/transfers` theo Pydantic v2 model chuẩn (chấp nhận null/optional fields an toàn), đảm bảo status mặc định `PENDING` và trả về đúng schema.

---

## 2. ALLOWED_FILES
- `app/routes_transfers.py`
- `app/models.py`
- `tests/test_transfers_api.py`

## 3. FORBIDDEN_FILES
- `web/*` (Frontend do task T-003 đảm nhiệm)
- `database/schema.sql` (Schema không thay đổi ở task này)

---

## 4. ACCEPTANCE CRITERIA
1. [ ] `POST /api/transfers` với payload hợp lệ trả về HTTP 200 hoặc 201 kèm `{ "id": <number>, "status": "PENDING" }`.
2. [ ] `POST /api/transfers` với các trường optional mang giá trị `null` hoặc chuỗi rỗng không bị lỗi 422 Unprocessable Entity.
3. [ ] `POST /api/transfers` với `device_id` hoặc `to_facility_id` không tồn tại trả về đúng mã lỗi 404 / 422 có thông điệp rõ ràng (không sinh lỗi 500 Internal Server Error).
4. [ ] `GET /api/transfers` trả về danh sách có chứa `asset_tag` chuẩn `BVQ7-TTB-XXXXX`.

---

## 5. TEST COMMANDS
```bash
python scripts/test_t23_v3.py
```

---

## 6. EVIDENCE REQUIRED
- Git diff của `app/routes_transfers.py` và `app/models.py`.
- Test execution output cho cả 3 trường hợp (Valid, Null Optional, Invalid ID).
- JSON response thực tế từ `GET /api/transfers?limit=1`.

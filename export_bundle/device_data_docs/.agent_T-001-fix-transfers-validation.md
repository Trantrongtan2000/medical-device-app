# TASK T-001 - Fix Transfers Validation (Backend)

## TASK INFORMATION

| Field | Value |
|-------|-------|
| TASK_ID | T-001 |
| TITLE | Fix Transfers Validation (Pydantic v2) |
| PRIORITY | 🔴 P0 |
| DEPENDENCY | T-000 ✓ (Baseline Verified) |
| ASSIGNED_AGENT | Backend Coding Agent |
| AUDITOR | Antigravity |
| ESTIMATED_HOURS | 2-4h |

---

## OBJECTIVE

Xác minh và sửa bất kỳ validation issue nào với POST `/api/transfers`. Frontend đã hoàn thành gửi form, nhưng cần backend xác thực hoạt động đúng.

---

## SCOPE

### ✅ ALLOWED FILES
```
app/routes_transfers.py
app/models.py (read-only)
app/database.py (read-only)
tests/test_transfers.py
```

### ❌ FORBIDDEN FILES
```
web/js/app.js
database/schema.sql  
database/devices.db
```

---

## CONTEXT & ANALYSIS

### Database Connection
- `database.py` dòng 38: `conn.row_factory = sqlite3.Row`
- Điều này giúp `dev_row["facility_id"]` hoạt động như dict

### Models
- `DeviceTransferCreate` có các trường:
  - `device_id: int` (required)
  - `to_facility_id: int` (required)
  - `from_facility_id: Optional[int] = None`
  - `giver_name`, `receiver_name`, `transfer_reason`, `transfer_date`, `form_code`

### Transaction Flow
1. Tạo transfer: INSERT vào `device_transfers` với status `PENDING`
2. Xác nhận: UPDATE `devices.facility_id` + UPDATE `device_transfers.status = CONFIRMED`

---

## IMPLEMENTATION PLAN

### STEP 1: Run API Check
```bash
# Start API server
uvicorn app.main:app --reload --port 8000

# Test health
curl http://localhost:8000/api/devices/count
```

### STEP 2: Test Transfer Creation
```bash
# POST transfer
curl -X POST http://localhost:8000/api/transfers \
  -H "Content-Type: application/json" \
  -d '{"device_id": 1001, "to_facility_id": 2, "giver_name": "Test"}'
```

### STEP 3: Test Edge Cases
```bash
# Device không tồn tại
# Facility không tồn tại  
# from_facility_id = null
# transfer_date = null
```

### STEP 4: Test Confirm Transfer
```bash
curl -X PUT http://localhost:8000/api/transfers/{id}/confirm
```

---

## ACCEPTANCE CRITERIA

| # | Criterion | Expected Result |
|---|-----------|-----------------|
| 1 | POST với valid data | Return 201, PENDING status |
| 2 | POST với null optional fields | No validation error |
| 3 | POST với device không có facility_id | Fallback về facility_id mặc định |
| 4 | POST với facility nhận không tồn tại | HTTP 404 |
| 5 | PUT confirm update đúng | devices.facility_id = to_facility_id |
| 6 | Transaction hoạt động | Không có orphan data |
| 7 | Existing tests pass | pytest tests/test_transfers.py |

---

## TEST COMMANDS

```bash
# Chạy tests
pytest tests/test_transfers.py -v

# Hoặc nếu chưa có test:
python -c "
import requests
# Test POST then PUT
"
```

---

## EVIDENCE REQUIRED

1. **Git diff** - files thay đổi
2. **API Response** - JSON output 200/201
3. **Database State** - SELECT sau khi tạo/xác nhận
4. **Test Output** - pytest results

---

## ROLLBACK PLAN

Nếu có bug:
```bash
git checkout T-001-feature-branch
# Hoặc revert commit
git revert HEAD
```

---

## STATUS

- [ ] Implement
- [ ] Self-test
- [ ] PASS → Antigravity audit
- [ ] Antigravity audit

---

*Created: 2026-08-20*
*Taught by: DeepSeek Orchestrator*
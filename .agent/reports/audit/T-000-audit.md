# AUDIT REPORT: T-000

**AUDITOR:** Antigravity (Independent Technical Auditor)  
**TASK_ID:** T-000  
**TITLE:** Baseline Verification & Database Backup  
**DATE:** 2026-08-20  

---

## 1. SCOPE AUDIT
- [x] Sửa đổi nằm hoàn toàn trong `ALLOWED_FILES` (`scripts/backup_db.py`, `tests/test_baseline_smoke.py`, `database/backups/`).
- [x] Không can thiệp `FORBIDDEN_FILES` (`app/routes*.py`, `database/devices.db` schema).

---

## 2. ACCEPTANCE MATRIX

| Tiêu chí | Kết quả | Bằng chứng |
|---|---|---|
| 1. Backup file nguyên vẹn & integrity check | **PASS** | `database/backups/devices_baseline_20260820_164204.db` (integrity: ok, 1.077.248 bytes) |
| 2. FastAPI khởi động bình thường | **PASS** | `TestClient(app)` import và load thành công |
| 3. CSDL có đúng 1.211 thiết bị | **PASS** | `test_devices_count` & `test_api_dashboard_summary` = 1.211 |
| 4. Endpoints cốt lõi phản hồi 200 | **PASS** | `test_api_devices_endpoint`, `test_api_facilities` 200 OK |

---

## 3. SECURITY & INTEGRITY
- Cơ chế backup sử dụng SQLite Online Backup API (`src.backup(dst)`), không gây khóa write trên database chính.
- `PRAGMA foreign_keys = ON;` và `PRAGMA journal_mode = WAL;` được bảo toàn.

---

## 4. VERDICT: **PASS**

**Hành động tiếp theo:**
1. Đánh dấu `T-000` = **PASS** trong `TASK_BOARD.md`.
2. Chuyển `T-001` (Fix Transfers Validation) từ **BLOCKED** → **READY**.

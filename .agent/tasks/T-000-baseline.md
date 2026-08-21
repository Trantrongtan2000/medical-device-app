# TASK CONTRACT: T-000

**TASK_ID:** T-000  
**TITLE:** Baseline Verification & Database Backup  
**PRIORITY:** P0  
**DEPENDENCY:** None  
**ASSIGNED_AGENT:** QA / DevOps Agent  
**AUDITOR:** Antigravity  
**ESTIMATED_HOURS:** 1.0  

---

## 1. OBJECTIVE
Xác thực toàn bộ trạng thái baseline của repository, tạo bản sao lưu an toàn cho `database/devices.db` trước khi thực hiện các task sửa đổi tiếp theo, và kiểm tra sức khỏe của 87 API endpoints hiện có.

---

## 2. ALLOWED_FILES
- `scripts/backup_db.py`
- `database/backups/*`
- `tests/test_baseline_smoke.py`

## 3. FORBIDDEN_FILES
- `app/routes*.py`
- `web/*`
- `database/devices.db` (chỉ đọc, không ghi đè cấu trúc)

---

## 4. ACCEPTANCE CRITERIA
1. [ ] Có bản sao lưu `database/backups/devices_baseline_<timestamp>.db` nguyên vẹn và xác thực được tính toàn vẹn (integrity check).
2. [ ] Server FastAPI khởi động bình thường không có lỗi import hoặc syntax error.
3. [ ] Endpoint `GET /api/devices` và `GET /api/dashboard/summary` phản hồi 200 OK với dữ liệu 1.211 thiết bị.

---

## 5. TEST COMMANDS
```bash
python -c "import sqlite3; conn = sqlite3.connect('database/devices.db'); print('Device count:', conn.execute('SELECT count(*) FROM devices').fetchone()[0])"
pytest tests/ -v  # hoặc script smoke test tương đương
```

---

## 6. EVIDENCE REQUIRED
- Đường dẫn file backup đã tạo.
- Output kiểm tra `PRAGMA integrity_check;` trên file backup.
- Output kiểm tra số lượng thiết bị = 1.211.

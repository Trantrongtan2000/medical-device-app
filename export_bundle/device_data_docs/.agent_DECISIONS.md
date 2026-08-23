# ARCHITECTURAL DECISIONS RECORD (ADR)

## ADR-001: Multi-Agent Topology & Independent Auditor Model
- **Status:** APPROVED
- **Date:** 2026-08-20
- **Context:** Cần sự phối hợp giữa nhiều mô hình AI mà không gây xung đột code hoặc tự tuyên bố hoàn thành sai lệch.
- **Decision:**
  - **DeepSeek Harness (http://127.0.0.1:3080/)**: Đóng vai trò Orchestrator / Project Manager (quản lý state, task contract, dependency graph, không tự code).
  - **Worker Agents (Codex / Claude / OpenCode / QA)**: Thực thi code theo contract và scope chỉ định trong `ALLOWED_FILES`.
  - **Antigravity**: Đóng vai trò **Independent Auditor** (kiểm tra bằng chứng, diff, test execution, regression, đưa ra phán quyết PASS / REWORK / BLOCKED mà không tự code feature).
  - **Browser QA (`agent-browser-cli`)**: Tự động hóa kiểm thử trên Chrome thật.

---

## ADR-002: SQLite Concurrency, WAL Mode & Transaction Safety
- **Status:** APPROVED
- **Context:** SQLite có thể bị lock database khi có nhiều request ghi đồng thời.
- **Decision:**
  - Kích hoạt `PRAGMA journal_mode = WAL;` và `PRAGMA foreign_keys = ON;` trên mọi kết nối.
  - Mọi thao tác ghi nhiều bảng (ví dụ: xác nhận transfer cập nhật `devices.facility_id` và `device_transfers.status`) bắt buộc phải bọc trong atomic transaction (`BEGIN ... COMMIT / ROLLBACK`).

---

## ADR-003: Asset-Centric vs Document-Centric Storage
- **Status:** APPROVED
- **Context:** Kho OCR và tài liệu PDF ban đầu có dung lượng >60GB.
- **Decision:**
  - Database `devices.db` là Master Asset Database (chứa metadata, serial, trạng thái, chu kỳ bảo trì, đường dẫn tham chiếu).
  - Không lưu file PDF nhị phân trong SQLite.
  - Sử dụng Document Gateway URI để liên kết tài liệu từ kho lưu trữ vật lý.

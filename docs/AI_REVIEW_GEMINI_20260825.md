# Gemini Review — 2026-08-25
## Verdict: Roadmap: B → D → A → C → E

### A. Context & cấu trúc
1. **Reading Hierarchy chuẩn hóa**: DATA_SOURCE_OF_TRUTH.md (đọc ĐẦU TIÊN — ranh giới dữ liệu) → AGENTS.md/context.md (quy tắc bất khả xâm phạm) → HANDOVER_P2 (hiện trạng FAIL) → schema.sql + main.py (xác minh thực tế)
2. **Mâu thuẫn số liệu**: 19.135 (bản C cũ) vs 6.330 (DB G:) vs 20.804 PDFs (kho vật lý) — cần dán nhãn deprecated rõ ràng mọi doc còn nhắc 19.135
3. **Mâu thuẫn mutation/schema**: transfers (code sinh) vs device_transfers (schema gốc); asset_tag chỉ là display format nhưng Executor gọi như SQL field
4. **Thiếu**: đặc tả path resolver specification giữa đường dẫn tuyệt đối G:\ và container mount paths
5. **Archive**: commit ngay cleanup + .gitignore → tạo "clean baseline" cho main branch

### B. Roadmap: **P2-B → P2-D → P2-A → P2-C → P2-E** (dependency-driven)
- **Bước 1 B (Critical Safety)**: fix NameError Path routes_agent.py:158; auth middleware /api/agent/*; execute_draft tuyệt đối không CREATE TABLE transfers, chuyển sang mutation draft trên device_transfers
- **Bước 2 D (Data Integrity)**: dọn 936 orphan FK; chuẩn hóa kiểm tra file tồn tại ổ G:; bỏ fallback ID=1
- **Bước 3 A (Tool Dispatch)**: helper parse_asset_tag_to_id() query theo id, triệt tiêu SELECT d.asset_tag; hoàn thiện 4 tool dispatch thiếu
- **Bước 4 C (Provenance)**: SHA-256 thật thay hash() Python; chuẩn hóa Mistral/Gemini fallback trả unavailable có cấu trúc
- **Bước 5 E (Performance)**: telemetry /api/agent/query + pytest-benchmark (p50 ≤ 5ms router, p50 ≤ 25ms local edge)

### Port từ bản C: làm SONG SONG ngay tại P2-B, trước P2-D
"Lý do: các thay đổi từ bản C chủ yếu là code fixes phòng thủ (bỏ hardcode, fix fallback mock, regression tests). Nếu không port test hồi quy vào trước, P2-D và P2-A sẽ thiếu test harness để verify."

### Hidden Traps
1. **SQLite lock khi Agent mutation**: WAL vẫn gặp "database is locked" nếu transaction ghi kéo dài trong khi router khác stream/đọc đồng thời
2. **File Path Portability**: G:\ là Windows absolute path — Docker Compose (Linux container) không volume mount + path mapping nhất quán → 6.330 tài liệu báo "File Not Found"
3. **Mất toàn vẹn khi dọn orphan**: xóa/cập nhật 936 document_segments không kèm backup snapshot → mất dấu vết trích dẫn ngữ cảnh OCR đã xử lý

# DeepSeek Review — 2026-08-25
## Verdict: Roadmap: D → B → A/C → E

### A. Context & cấu trúc
1. **Onboarding đạt cơ bản, thiếu Quickstart**: bổ sung 3 lệnh đầu vào RUNBOOK.md (venv + pip install; docker compose up; pytest thấy đỏ để bắt tay sửa)
2. **Router list gây nhiễu**: rút gọn thành bảng "nhóm router chính" — agent cần biết mutation nào đi file nào, không cần 130 endpoints
3. **Mâu thuẫn orphan**: 1.156 segments, 936 orphan FK → 220 còn lại trỏ đi đâu? Thêm query kiểm tra orphan vào DATA_SOURCE_OF_TRUTH.md
4. **"Bản C đã xóa" = red flag lớn nhất**: không có commit history/diff reference, viết tay dễ sai sót — cần nêu rõ là nhóm rủi ro cao nhất
5. **Archive**: commit cleanup NGAY ("dọn nhà" tách khỏi "sửa nhà", giữ commit history sạch)

### B. Roadmap: **P2-D → P2-B → P2-A → P2-C → P2-E**
- **D FIRST**: "Nếu fix provenance/benchmark mà chưa fix orphan, ta đang validate ghost data". Fix orphan trước khi tạo asset_tag (tránh tag lên broken records)
- **B SECOND**: không thể mutate DB an toàn khi chưa sửa transfers table + default ID=1 + Path import
- **A THIRD**: asset_tag resolve qua view/computed column, KHÔNG migration ban đầu; cần data sạch (từ D) mới pass benchmark
- **C FOURTH** (chạy song song A được): sau khi D làm sạch evidence mới implement hash + metadata sạch
- **E LAST**: observability, không phải functional blocker

### Port từ bản C: sau D và B (vì phụ thuộc live data count + transaction logic). Port trước D sẽ perpetuate counting discrepancies.

### Rủi ro bị đánh giá thấp
1. **930 missing PDFs**: nếu ổ G: unavailable hoặc relative/absolute path lẫn lộn → streaming endpoints vỡ. Verify G: mount stability
2. **Migration transfers → device_transfers**: drop table cũ + sửa code phải map SQL cẩn thận; tests phụ thuộc bảng cũ sẽ break
3. **AI hallucination**: parser fallback ID=1 là "security/accuracy nightmare" — sửa bằng JSON schema validation + raise INVALID_INPUT thay vì default. Đánh giá thấp thời gian fine-tune prompt+parser
4. **Rollback plan thiếu**: AGENTS.md nói backup trước, nhưng remediation scripts phải idempotent + test trên DB clone TRƯỚC khi chạy trên devices.db thật. Roadmap chưa có bước backup-restore-test tường minh

### Kết luận
"D → B là non-negotiable": chưa sửa orphan thì AI query (A) kéo garbage; chưa sửa mutation safety (B) thì script remediation có thể nuke DB.

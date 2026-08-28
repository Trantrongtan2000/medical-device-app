# ChatGPT Review — 2026-08-25
## Verdict: Context ~8.5/10 | Roadmap: B → A → D → C → E

### A. Context & cấu trúc
1. **Thứ tự onboarding đề xuất**: AGENTS.md → DATA_SOURCE_OF_TRUTH.md → context.md → HANDOVER_P2 → DATA_QUALITY/SECURITY_FINDINGS → code/tests
2. **Nên thêm CURRENT_STATE.md ở root (30-60 dòng)**: "Hiện tại là gì → P2 fail ở đâu → canonical DB nào → commit hiện tại → việc tiếp theo → việc cấm làm"
3. **3 điểm cần làm rõ**:
   - maintenance_schedules=1.211 là count rows, không phải "100% thiết bị có lịch hợp lệ"
   - 6.330 documents ≠ 6.330 evidence usable (936 orphan, 930 broken paths)
   - asset_tag: thêm vào DATA_SOURCE_OF_TRUTH dòng "DO NOT QUERY devices.asset_tag"
4. **Bảng số liệu stale**: 6.330 (✅ canonical) vs 19.135/10.564/7.693 (❌) — ghi dataset + timestamp + source
5. **Archive**: commit ngay phần structural cleanup; KHÔNG commit zip/backup/extracts; thêm archive/README.md: "Archive is historical/reference material only. Never authoritative."

### B. Roadmap: **P2-B → P2-A → P2-D → P2-C → P2-E**
- **B Safety (P0 trong P2)**: fallback ID=1 nguy hiểm hơn lỗi SQL (SQL fail-closed, fallback ghi nhầm thiết bị thật). Mọi parse failure → REQUIRES_HUMAN_CONFIRMATION
- **A Benchmark**: khóa safety xong mới sửa asset_tag + 4 tool dispatch + Path import
- **D Evidence**: ưu tiên TRƯỚC C — provenance trên evidence graph bẩn là vô nghĩa. Classification: VALID → BROKEN_PATH → ORPHAN → DUPLICATE → MISSING → NEEDS_RELINK, không auto-relink không human gate
- **C Provenance**: SHA-256, OCR run, bỏ hash() + hardcode "1.211" + claim "Zero Hallucination" → dùng "Evidence-grounded; unsupported claims are rejected or marked uncertain"
- **E Latency**: cuối cùng

### Port từ bản C:
- **Port ngay (sau B/A, trước D)**: provenance live-data, Mistral fallback unavailable, regression tests, bỏ claim không chứng minh
- **Port sau D**: phần phụ thuộc document identity/file hash/OCR metadata
- **Nguyên tắc**: "C-port correctness → trước D; C-port provenance/data model → sau D". Đừng cherry-pick nguyên bản C (kéo theo assumptions stale)

### 5 rủi ro bị đánh giá thấp
1. 🔴 Mutation safety: execute_draft commit DB thật + default ID=1 = data-integrity/security violation. Kiến trúc bắt buộc: Parse → Validate → Draft → Human Confirm → Transaction → Audit
2. 🔴 936 orphan chỉ là triệu chứng — phải tìm root cause (import pipeline? migration? deletion?) nếu không sẽ tiếp tục sinh orphan mới
3. 🟠 Schema drift: audit toàn bộ Agent Tool Schema ↔ SQL ↔ schema.sql ↔ production DB; thêm schema contract test
4. 🟠 73/73 tests PASS ≠ P2 PASS — thiếu contract/data-integrity/safety tests
5. 🟠 Archive che mất dependency: 210 scripts có thể vẫn reference file đã archive — cần dependency inventory

### Kết luận
"Không remediation provenance/performance trên một execution path chưa safety, và không xây provenance trên evidence graph chưa được reconciliation."

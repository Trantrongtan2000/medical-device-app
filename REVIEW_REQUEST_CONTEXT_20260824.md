# REVIEW REQUEST — HTM v3: Hệ thống Quản lý Trang thiết bị Y tế (BV Đa khoa Q7 / PKĐK Tâm Anh Q7)

Bạn là reviewer độc lập. Đọc context dưới đây (đã kiểm chứng bằng tool trên chính repo), sau đó:
1. **Đánh giá context & cấu trúc tài liệu**: agent mới đọc vào có nắm được dự án nhanh không? Thiếu gì, thừa gì, mâu thuẫn gì?
2. **Đề xuất roadmap remediation P2**: thứ tự ưu tiên hợp lý cho 5 nhóm blocker P2-A→E? Có rủi ro nào bị bỏ sót?

Trả lời ngắn gọn, có cấu trúc, tiếng Việt.

---

## 1. Dự án là gì

Web app quản lý vòng đời thiết bị y tế (HTM — Healthcare Technology Management) cho Bệnh viện Đa khoa Quận 7 / Phòng khám Đa khoa Tâm Anh Q7.
- Tuân thủ **NĐ 98/2021/NĐ-CP** (phân loại rủi ro A/B/C/D) và **TT 05/2022/TT-BYT** (kiểm định an toàn, hiệu chuẩn).
- Gắn với **kho tài liệu OCR ~91 GB** tại `G:\BV QUẬN 7_OCR_WORK_20260712` (20.804 PDF scan + 30.406 MD): DB chỉ lưu metadata + đường dẫn, KHÔNG nhúng binary vào SQLite.

## 2. Kiến trúc (đã xác minh trên code)

| Layer | Công nghệ | File chính |
|---|---|---|
| Backend | FastAPI + SQLite (WAL, FK ON), Python 3.13 | `app/main.py` + 10 router module (~130 endpoints) |
| Frontend | Vanilla JS ES6 + Bootstrap 5 ("Tâm Anh Clinical Light"), KHÔNG framework mới | `web/index.html`, `web/js/app.js` ~3.850 dòng |
| Database | `database/devices.db` + `database/schema.sql` (18 bảng, 1 view, indices) | |
| AI Core | Cactus Router (policy 3 tầng: Local Edge → Semantica Graph → Cloud Gemini) → Needle Agent (11 read tools + 2 mutation draft tools, two-phase confirm) → Semantica Engine (knowledge graph) | `app/cactus_router.py`, `app/needle_agent.py`, `app/semantica_engine.py` |
| Cloud AI | Gemini Interactions API + Mistral OCR, key rotation pool | `app/ai_services.py`, `app/key_rotator.py` |
| Deploy | Docker Compose (app + nginx), healthcheck `/health/live`, `/health/ready` | |

Routers: `routes.py` (devices CRUD, dashboard, staff, on-call, contracts, suppliers, keys, OCR upload, check-in/out) · `routes_schedules.py` (lịch bảo trì + generate engine + alerts 90/60/30 ngày + QR) · `routes_inspections.py` · `routes_repairs.py` · `routes_transfers.py` (confirm cập nhật facility trong transaction) · `routes_documents.py` (Document Hub, stream PDF theo segment) · `routes_audit_capa.py` · `routes_agent.py` (`/api/agent/query` + confirm/cancel mutation).

## 3. Số liệu DB thực tế (vừa query mode=ro trên bản G:, ngày 2026-08-24)

- devices=**1.211** (Risk A=900, B=140, C=158, D=13) · facilities=39 · categories=10 · contracts=198 · suppliers=102
- calibration_certificates=583 · maintenance_schedules=1.211 · maintenance_logs=58 · repairs=45 · device_transfers=143 · pre_use_inspections=4 · notifications=37
- device_documents=6.330 · document_segments=1.156 (**936 orphan FK**)
- Asset tag là quy ước suy diễn `BVQ7-TTB-{id:05d}` — **schema KHÔNG có cột `asset_tag`**
- ⚠️ Bản C: (đã bị xóa) từng lệch G:: 1.212 devices, 19.135 documents — mọi số liệu cũ trong docs ghi 19.135 là stale.

## 4. Trạng thái Git & việc đang dở

Branch `main`, commit cuối `44b604e feat(agent): implement P0/P1/P2 HTM V3 next-gen BME copilot (73/73 tests)`.

Vừa hoàn thành **dọn dẹp repo** để agent sau dễ nắm context:
- Xóa cache: `.pytest_cache`, `__pycache__`, `.codegraph`
- Tạo `archive/` (gitignored): 4 zip bundle ~65MB, `export_bundle/`, `extracted_context/` (bản sao docs), 37 file temp `scripts/_*`, 20 docs stale (session transcript 5MB ×2, 5-AI aux plans, screenshot review), 7 root planning docs lỗi thời
- Root còn lại chỉ giữ: README.md, AGENTS.md, context.md, session.md, HANDOVER_P2_DRY_RUN_20260824.md, DATA_SOURCE_OF_TRUTH.md, DATA_QUALITY_FINDINGS.md, SECURITY_FINDINGS.md, DESIGN.md, code + config

## 5. Blocker đã xác minh (từ HANDOVER_P2_DRY_RUN_20260824.md — dry-run P2 toàn FAIL)

| Track | Verdict | Bằng chứng chính |
|---|---|---|
| P2-A Benchmark | FAIL | Subset 14 test: 12 pass / 2 fail (`no such column: d.asset_tag`); 4 tool có registry nhưng KHÔNG có dispatch trong Executor |
| P2-B Safety | FAIL | `/api/agent/*` chưa gắn auth; role lowercase ↔ enum uppercase mismatch; `execute_draft` tự CREATE TABLE `transfers` (schema chuẩn là `device_transfers`) + COMMIT vào DB thật; parser fallback ID=1 khi lỗi parse |
| P2-C Provenance | FAIL | DB không lưu hash/OCR-run metadata; các báo cáo lệch nhau (10.564 vs 7.693 vs 6.330 vs 19.135); serial fallback `hash()` không ổn định |
| P2-D Evidence Audit | FAIL | foreign_key_check = **936 orphan document_segments**; 930/6.330 PDF paths không tồn tại; 241 devices thiếu md_path; ≥9 nhóm duplicate file_path |
| P2-E Latency | NOT READY | `/api/agent/query` chưa emit telemetry; chưa có pytest-benchmark |

Blocker kỹ thuật cụ thể:
1. `routes_agent.py:158` dùng `Path(...)` mà không import → NameError ở confirm endpoint
2. Executor SQL giả định cột `asset_tag` ở `devices` và `device_documents` — đúng hướng: tra cứu theo `id`, parse tag→id, render f-string; KHÔNG thêm cột nếu không có migration+backfill+rollback
3. `execute_draft` (needle_agent ~186-247) ghi thẳng DB thật, tạo bảng `transfers` sai schema
4. Parser default device/facility = 1 khi lỗi; duplicate flag REQUIRES_HUMAN_CONFIRMATION
5. Phần việc chưa commit từng nằm ở bản C: (provenance live-data thay vì hardcode "1.211", bỏ claim "Zero Hallucination"/"W3C PROV-O", Mistral fallback trả status:"unavailable" thay vì mock, 10 regression test `tests/test_ai_code_mismatch_fixes.py`) — cần viết lại tay trên bản G:

## 6. Quy tắc làm việc bắt buộc (AGENTS.md + .agent/GOAL.md)

- **Code + Database thắng** khi tài liệu mâu thuẫn; verify bằng tool trước khi trả lời; sửa surgical, không placeholder
- Không đổi schema nếu chưa có migration + backup DB trước; multi-bảng phải atomic; timezone Asia/Ho_Chi_Minh; scheduler không duplicate notification
- Workflow: PLAN → IMPLEMENT → TEST → AUDIT độc lập → REWORK nếu fail
- KHÔNG chạy script mutating trên kho G: (`run_agent_tests.py`, import/restructure) tới khi có remediation plan
- Tiêu chí PASS chi tiết từng track (P2-C/D/E latency budgets p50≤5ms router, e2e LOCAL_EDGE p50≤25ms…) trong `HANDOVER_P2_DRY_RUN_20260824.md`

## 7. Cấu trúc thư mục hiện tại

```
G:\medical-device-app\
├── app/            # FastAPI backend (17 module .py)
├── web/            # Vanilla JS frontend + pdfjs viewer
├── database/       # devices.db (canonical) + schema.sql + backup 20260823
├── docs/           # docs hiện hành (RUNBOOK, DEPLOYMENT, PHASE2_DELIVERY, ROADMAP_TONG_HOP_4AI, CONTEXT_DIGEST_5AI...)
├── tests/          # 13 pytest files
├── scripts/        # 210 scripts vận hành (md_lifecycle/, audit, import...)
├── specs/          # 4 speckit features
├── .agent/         # GOAL.md, CURRENT_STATE.md, TASK_BOARD.md (round 22/256)
├── archive/        # [gitignored] bundle zip, docs stale, temp scripts
└── AGENTS.md, README.md, context.md, session.md, HANDOVER_P2_DRY_RUN_20260824.md ...
```

---

## CÂU HỎI REVIEW

**A. Context & cấu trúc tài liệu:**
1. Bộ entry-point (AGENTS.md → context.md → HANDOVER_P2 → DATA_SOURCE_OF_TRUTH) đã đủ để agent mới onboard chưa? Thứ tự đọc nên là gì?
2. Có điểm mâu thuẫn/thiếu sót nào trong các con số và mô tả trên không?
3. Việc archive (giữ trên disk, khỏi git) có rủi ro gì? Nên commit phần dọn dẹp này ngay hay chờ?

**B. Roadmap remediation P2:**
4. Thứ tự ưu tiên đề xuất cho P2-A/B/C/D/E? Việc nào blocking việc nào?
5. Nhóm blocker số 5 (port tay phần chưa commit từ bản C:) — nên làm trước hay sau P2-D data reconciliation?
6. Rủi ro nào trong kế hoạch này dễ bị đánh giá thấp?

# HTM v3 — context_grokbot.md

Handoff cho AI chat khác. Cập nhật 2026-08-26 ~14:28 ICT.
Orchestrator phiên này: **Culi cao cấp**. Không suy diễn thêm; số dưới đã RO-verify trừ khi ghi DELTA.

---

## 1. Dự án là gì

**HTM v3** — hệ thống quản lý trang thiết bị y tế (CMMS) **PKĐK / BV Tâm Anh Quận 7**.

FastAPI + SQLite + UI vanilla (Bootstrap). Không React/Vite. Auth nhẹ, demo keys — không coi là production-hardening.

Mục tiêu vận hành hiện tại: pointer hồ sơ đúng máy, identity queue cho người, AI tắt, không rebuild.

---

## 2. Nguồn sự thật (bắt buộc)

| Thứ | Path |
|---|---|
| Source code | `G:\medical-device-app` |
| Canonical DB | `G:\medical-device-app\database\devices.db` |
| Kho OCR / PDF | `G:\BV QUẬN 7_OCR_WORK_20260712` |
| Báo cáo ops | `G:\medical-device-app\baocao.md` |
| File này | `G:\medical-device-app\context_grokbot.md` |

**OBSOLETE — cấm dùng làm SoT:** `C:\Users\tantt\Downloads\medical-device-app` (feat-branch cũ, DB ~23MB / 19k links).

GitHub: `https://github.com/Trantrongtan2000/medical-device-app.git`

Chạy app (khi cần): `run_windows.bat` (PORT 8000, OCR root = kho G:). `python start_server.py` không set PORT thì default **8080**. **Không boot uvicorn trong QA** nếu `lifespan` → `init_database()` (`executescript` + `COMMIT`) — sẽ ghi DB.

---

## 3. Canonical DB (live)

- SHA-256: `A670CA54AFFC7833D8BE1905C7DF131FC3792EEE3F32B0DA7C457936CE5165B4`
- Size ~3.76 MB
- `PRAGMA integrity_check` = **ok**
- Journal: WAL
- `PRAGMA foreign_key_check` = **936** — toàn `document_segments.document_id` → `device_documents` (P2-D known). Không sửa canonical.

Inventory RO (Phase 0 lock 12:17 ICT):

| Entity | Count |
|---|---:|
| devices | 1,211 |
| contracts | 198 |
| facilities | 39 |
| calibration_certificates | 583 |
| device_documents | 6,330 |
| maintenance_schedules | 1,211 |
| document_segments | 1,156 |
| maintenance_logs | **60** (một số báo cáo ghi 58–60) |
| repairs | **46** (plan từng ghi 45) |
| device_transfers | **148** (plan từng ghi 143–144) |

Rủi ro thiết bị (báo cáo ops, không re-count phút này): A 900 / B 140 / C 158 / D 13.

Pointer live sau Track A+B:

| Metric | Value |
|---|---:|
| pdf_missing | 0 |
| pdf_set | 1,211 |
| md_missing | 11 |
| md_set | 1,200 |
| md_path prefix `md/` | 1,199 |
| need_prefix | 1 (= device **821**) |

`md_missing=11` **không** phải lỗi Track B. B chỉ prepend `md/` cho path đã có; không fill md trống. Plan cũ `md_missing=1` sau B là **sai scope**.

---

## 4. Kho OCR

`G:\BV QUẬN 7_OCR_WORK_20260712`

- `md/` ~8,011 file / 6 bucket vòng đời, 0 unclassified (dọn 2026-08-23).
- Phần lớn file tổng (~53k+) nằm `08_KHO` backup/trùng — không phải hồ sơ mới.
- Live truth kho: `context.md` (23/8). `REPORT.md` / `file_map.json` / vision DRY_RUN = stale 22/8.
- Có folder tên gần trùng ASCII `G:\BV QUan 7_OCR_WORK_20260712` — decoy, không dùng.

---

## 5. Tiến độ execution

### Track A — Pointer fill — **CLOSED**

- Fill `pdf_path`/`md_path` từ 1 `device_documents.file_path` tồn tại (230 máy, 34 PDF shared).
- APPROVED + EXECUTED + RO VERIFIED PASS.
- Snapshot: `scratch\human_gate_20260826\snapshots\devices_pre_A_20260826_090844.db`
- SQL: `scratch\human_gate_20260826\apply_A.sql` / `rollback_A.sql`
- **Cấm chạy lại.**

### Track B — Prefix `md/` — **CLOSED**

- Prepend `md/` cho 969 VALID md_path. **821 excluded.**
- EXECUTED + Cuk/Bob RO PASS. `md/` 230→1199. need_prefix 970→1 (821).
- Snapshot: `scratch\human_gate_20260826\snapshots\devices_pre_B_20260826_111500.db`
- `apply_B.sql` lần nữa = **REJECT** (Human Gate Bob).
- **Cấm chạy lại.**

### P2-D orphan segments — **CLONE-ONLY / RETURN_FOR_REVIEW**

- Clone: `scratch\p2d_orphan_reconcile\devices_clone.db` (segments 220, FK 0).
- Canonical: 1,156 segments, FK 936.
- **Không** apply `orphan_quarantine.sql` lên canonical.

### AI BME — **DISABLED**

- 0 key env + `api_keys_config` = 0. Không file `.env`.
- `.env.example` số nhiều (`GEMINI_API_KEYS`) lệch code số ít (`GEMINI_API_KEY` / `GOOGLE_API_KEY`).
- `start_server.py` không `load_dotenv`.
- Activation = **REJECT**.
- UI badge: đã vá (không còn hardcode `Active (Auto-Rotate)`). 0 key → DISABLED; key>0 → ACTIVE; fetch lỗi → NOT READY/ERROR. Files: `web\index.html` ~1806/1815, `web\js\app.js` `paintAiKeyBadge`.
- KPI hardcode trong `index.html` / `app.js` — **chỉ audit**, chưa sửa hàng loạt.

### Code extras (Captain / P2, không đổi hash canonical)

Route dedup, Semantica method, SOP Path fallback, mutation-draft safety, telemetry (query redacted), provenance fail-closed. Tests in-memory. Không opportunistic-fix thêm.

---

## 6. Human review queue (11 ca) — đứng

CSV quyết định: `scratch\identity_review_20260826\HTM_v3_Audit_Decisions_20260826.csv`  
Workbench: `G:\medical-device-app\web\audit_review.html` (standalone ~2.8MB, nhúng data, không fetch API/DB, localStorage + xuất CSV).

Human Gate (Bob) trên CSV này: **11/11, 0 PASS**. APPROVE *giữ queue*. REJECT mọi SQL/unlink/force-link từ CSV.

| id | Class | Ghi chú |
|---|---|---|
| 821 | IDENTITY_MISMATCH | Máy: Nhãn áp kế Schiotz/Volk PMS, LOT 20240067, HĐ `0507_TTC` Thiên Trường (hàng tặng). PDF/MD đang trỏ GCN Áp kế lò xo **Kaipu P014556** (`056-1001`). Cấm prefix/copy/gỡ-link tự động. GCN đúng LOT = UNRESOLVED trong kho. |
| 309, 310, 311 | REVIEW / AMBIGUOUS | Fresenius 4008S/5008S; BBBG 3 SN dùng chung; nhiều GCN OCR trùng |
| 314 | REVIEW / AMBIGUOUS | GCN `04664` REJECT (thân file `5SXA6AYT`); BBBG chung 315 |
| 316 | REVIEW / AMBIGUOUS | GCN khớp serial; pdf=BBBG vs md=GCN |
| 1187, 1188, 1189 | REVIEW / AMBIGUOUS | Tủ lạnh MPR-715F-PE; `pdf_path` = `.docx` đào tạo nội bộ; serial có trong GCN tủ lạnh |
| 307, 1109 | HUMAN REVIEW | md trống; 08_KHO low-conf |

Không biến AMBIGUOUS → RESOLVED để KPI. Không biến MISMATCH → LINKED vì thiếu pointer.

---

## 7. Closure guardrails (cho AI nhận file này)

1. Canonical DB **read-only** trừ khi Human Gate APPROVE một mutation *mới*, có snapshot + rollback + exact ID list.
2. Không re-run Track A / Track B / `apply_B.sql`.
3. Không quarantine P2-D lên canonical.
4. Không tạo/đoán/expose API key, không `.env`, không activate AI.
5. Không boot app theo cách `init_database()` ghi DB khi đang QA.
6. Không sửa schema, không rebuild, không đổi `IN_SERVICE` hàng loạt.
7. Mỗi mutation một task, một cổng. Không opportunistic-fix 821/307/309–316/1109/1187–1189.
8. Evidence > KPI. Human Gate > automation.

---

## 8. Nhân sự bot (Grok Bot room BVQ7)

| Tên | Vai trò hiện tại | Được | Cấm |
|---|---|---|---|
| **Culi cao cấp** | Operations Lead / Orchestrator | Plan, dispatch, cross-review, STOP, escalate, ghi báo cáo | Tự mutation DB/identity/hồ sơ/AI; tự suy diễn approval |
| **Cuk** | Pointer Reconciliation | READ, scan, match deterministic, manifest RESOLVED/AMBIGUOUS/UNRESOLVED | Sửa DB, force-link, xử lý identity mismatch |
| **Trẻ trâu lớp lá** | Evidence & Identity | Đọc PDF/MD/GCN/HĐ, đối chiếu serial/model/cert, class MISMATCH/AMBIGUOUS | Force-link, sửa identity/hồ sơ |
| **Hô mô xa pi ần** | App QA & Runtime | Health/API/UI/viewer, invariant, AI badge vs runtime | Ghi production data |
| **Niubi** | AI BME Readiness | Audit config/key/runtime/UI boundary, readiness report | Tạo key, sửa `.env`, activate AI, gọi production AI |
| **Bob** | Human Gate & Safety | APPROVE / REJECT / RETURN_FOR_REVIEW | Tự execute SQL, mở rộng scope |

Chuỗi identity hiện tại: workbench → CSV → Bob. Chưa có mutation từ queue.

---

## 9. Artifact quan trọng

```
G:\medical-device-app\
  baocao.md
  context_grokbot.md          (file này)
  web\audit_review.html
  web\index.html
  web\js\app.js
  database\devices.db
  scratch\human_gate_20260826\
    HUMAN_GATE_PACKAGE.md
    phase0_baseline_lock.json
    apply_A.sql  rollback_A.sql  ids_A.txt  preflight_A.md
    apply_B.sql  rollback_B.sql  ids_B.txt  preflight_B.md
    snapshots\devices_pre_A_20260826_090844.db
    snapshots\devices_pre_B_20260826_111500.db
  scratch\identity_review_20260826\
    identity_review_821.md
    identity_review_1187_1189.md
    identity_review_309_316.md
    HTM_v3_Audit_Decisions_20260826.csv
  scratch\app_qa_20260826\
  scratch\ai_readiness_20260826\
  scratch\p2d_orphan_reconcile\devices_clone.db
  scratch\pointer_audit_20260825\
```

---

## 10. Việc còn lại (gợi ý cho AI nhận handoff)

1. Human review 11 ca trên `audit_review.html` (người), không SQL từ CSV đã REJECT.
2. P2-D **decision package** (canonical vs clone) — chờ cổng riêng; không apply.
3. KPI hardcode audit (không sửa hàng loạt).
4. Giữ AI DISABLED.
5. Không re-open A/B.

Nếu baseline live **khác** bảng §3: STOP, đừng đoán, đừng “fix cho khớp”.

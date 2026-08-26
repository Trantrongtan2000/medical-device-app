# HTM v3 OPERATIONS STATUS

Cập nhật: 2026-08-26 ~09:46 ICT. Orchestrator: Culi cao cấp.
Nguồn: `G:\medical-device-app\database\devices.db` (RO confirm trên `Q7-4A-TTB001`).

> **Verification update — 2026-08-26 (~10:30 ICT), team `baocao-verify`:** toàn bộ mục này đã được kiểm tra lại READ-ONLY độc lập (4 auditor, zero mutation). Chi tiết xem **Mục 11. VERIFICATION UPDATE** cuối báo cáo. Kết luận ngắn: A PASS lại 100%, B READY_FOR_HUMAN_APPROVAL, AI DISABLED xác nhận 0 key, integrity DB PASS, invariants giữ nguyên.

---

## 1. Current State

Track A: APPROVED + EXECUTED + **RO VERIFIED PASS** (Culi, live SELECT).
Track B: APPROVED, **chưa execute**.
AI = NO. Identity queue đứng. Downloads obsolete.

Invariant live:
- devices = 1.211
- contracts = 198
- facilities = 39
- calibration_certificates = 583
- device_documents = 6.330

Snapshot A: `scratch\human_gate_20260826\snapshots\devices_pre_A_20260826_090844.db`

## 2. Work Completed

- Cuk: preflight A/B. RO sau A từng blocked G:; giờ ổ lên.
- Trẻ trâu lớp lá: identity 821 / 1187–1189 / 309–316.
- Bob: QA plan; post-apply A còn mẫu 230/máy 17.
- Niubi: AI DISABLED.
- Hô mô xa pi ần: A executed; B đứng.
- Culi: RO count live; ghi `baocao.md`. Không mutate.

## 3. Pointer Statistics

Trước A: pdf 980/230/1 ; md 970/241/0.

Sau A (live RO):
- pdf_missing = **0** (230→0)
- pdf_set = 1.211
- md_missing = **11** (241→11)
- md_set = 1.200
- md_path prefix `md/` = **230** (đúng lô A)
- id 821: pdf cây cũ `BV QUẬN 7/05_KIEM DINH/…P014556…`, md không prefix — **không đổi**

## 4. Resolved

Lô 230 pointer-fill EXECUTED + VERIFIED. Không phải identity resolution.
Lô 969 prefix: chưa apply.

## 5. Ambiguous

309–316, 1187–1189 AMBIGUOUS. 307/1109 HUMAN. Không trong A.

## 6. Unresolved / Identity

821 IDENTITY_MISMATCH. GCN đúng UNRESOLVED. `d821_md_has_prefix=false`. Cấm B.

## 7. Critical Findings

1. A khớp expected. Invariant giữ.
2. B sẵn sàng sau Bob mẫu 230/máy 17 (không bắt buộc chặn nếu RO PASS — vẫn chờ Bob theo plan).
3. Prefix 821 vẫn cấm.
4. AI badge cứng, 0 key.

## 8. Human Approval Required

- A YES → EXECUTED → VERIFIED
- B YES → **chưa EXECUTED**
- AI / IN_SERVICE = NO

## 9. Recommended Next Step

@Bob probe máy 17 + mẫu 230 (không boot). PASS → @Hô mô xa pi ần snapshot + Track B (loại 821). FAIL → `rollback_A.sql`. Không opportunistic-fix.

## 10. Scope Check

- Rebuild required: **NO**
- Schema change required: **NO**
- DB mutation required: **YES** (B còn lại)
- Mutation approved: A YES / B YES
- A executed: **YES**
- A verified: **YES** (RO live)
- B executed: **NO**
- AI activation required: **NO**
- AI activated: **NO**

---

## 11. VERIFICATION UPDATE — 2026-08-26 ~10:30 ICT (team baocao-verify, READ-ONLY)

Kiểm tra độc lập lại toàn bộ báo cáo trên bằng 4 audit read-only (sqlite3 `mode=ro`, zero mutation, không ghi file vào repo, không chạy rollback/apply).

### 11.1 DB Integrity — PASS

| Check | Kết quả |
|---|---|
| `PRAGMA integrity_check` | **ok** |
| Journal mode | WAL |
| File size | 3.756.032 B (917 pages × 4096), freelist = 0 |
| `PRAGMA foreign_key_check` | **936 violations**, 100% là `document_segments.document_id → device_documents` (orphan P2-D đã biết, LEFT JOIN confirm = 936). Không có violation mới sau Track A ở bất kỳ bảng nào. |

### 11.2 Invariants — ZERO DRIFT (khớp 100% Mục 1)

devices **1.211** · contracts **198** · facilities **39** · calibration_certificates **583** · device_documents **6.330** · maintenance_logs **58** · maintenance_schedules **1.211** · repairs **45** · device_transfers **143** · document_segments **1.156**

### 11.3 Track A — RE-VERIFIED PASS

| Metric | Expected (Mục 3) | Live RO re-check | Match |
|---|---:|---:|:-:|
| pdf_missing | 0 | **0** | ✅ |
| pdf_set | 1.211 | **1.211** | ✅ |
| md_missing | 11 | **11** | ✅ |
| md_set | 1.200 | **1.200** | ✅ |
| md_path prefix `md/` | 230 | **230** | ✅ |

Bằng chứng scope:
- `ids_A.txt` (230 unique id) == tập id có prefix trong DB **230/230 SET_MATCH**; banned ids **0 hit**; row-level diff script ↔ DB = **0 sai lệch** trên cả 230 dòng.
- Device **821 KHÔNG ĐỔI**: pdf còn trỏ cây cũ `BV QUẬN 7/05_KIEM DINH/…P014556…`, md KHÔNG prefix (`821_unchanged=true`).
- Sample máy **17 PASS**: PDF (1.484.589 B) + MD (5.078 B) tồn tại trong warehouse `G:\BV QUẬN 7_OCR_WORK_20260712`. Lưu ý: pointer là **warehouse-relative** (theo `preflight_A.md` L16), không phải relative với `docs_storage`.
- Snapshot `devices_pre_A_20260826_090844.db` TỒN TẠI (3.678.208 B, quick_check=ok, đúng trạng thái pre-A: pdf_missing=230/md_missing=241/prefix=0).
- `rollback_A.sql` TỒN TẠI (230 UPDATE→NULL khớp ids_A.txt, kết thúc ROLLBACK) — chỉ kiểm tra, KHÔNG chạy.

### 11.4 Track B — READY_FOR_HUMAN_APPROVAL (chưa execute)

| Điều kiện gate | Trạng thái |
|---|---|
| Scope n=969 (969 UPDATE / 969 unique id trong apply_B.sql) | ✅ verified programmatic |
| Loại 821 (`821_in_B=false`) | ✅ verified |
| Banned list {821,307,309–311,314–316,1109,1187–1189} trong B | ✅ **0 hit** |
| Overlap A∩B | ✅ = 0 (disjoint theo thiết kế) |
| Blockers | ✅ = 0, linux_path = 0 |
| QA probe mẫu 230/máy 17 | ✅ PASS (RO-side, t3) |
| Rollback B | ✅ `rollback_B.sql` restore đúng chuỗi md_path cũ per-id |
| **Caveat** | ⚠️ Chưa có scan conflict/traversal độc lập lần 2 ngoài assertion của preflight_B.md — đánh giá non-blocking vì preflight đã assert blockers=0 |

Sau B (expected): prefix `md/` = **969**; need_prefix global 970→**1** (chỉ còn 821); invariants giữ nguyên.

### 11.5 AI & Identity Queue — xác nhận DISABLED

| Hạng mục | Kết quả |
|---|---|
| AI state | **DISABLED — YES**: GEMINI_API_KEY / GOOGLE_API_KEY / MISTRAL_API_KEY (+*_KEYS) đều NOT SET; không có file `.env`; `api_keys_config` = **0 rows** |
| Key count | env 0 + DB 0 = **0** |
| RBAC | `HTM_ENFORCE_RBAC` NOT SET → default **False** (app/config.py:39 — demo mode) |
| IDENTITY_MISMATCH | {**821**}: GCN Kaipu P014556 vs máy Volk Schiotz LOT 20240067 — vẫn UNRESOLVED, vẫn cấm prefix |
| AMBIGUOUS | {309,310,311,314,316,1187,1188,1189} = 8 (md_path rỗng; 1187–89 sai loại tài liệu .docx đào tạo) |
| HUMAN | {307,1109} (md rỗng, không thuộc track SQL) |
| Lưu ý `.env.example` | Tên biến số nhiều (`GEMINI_API_KEYS`) lệch với code đọc số ít (`GEMINI_API_KEY`/`GOOGLE_API_KEY`, key_rotator.py:336–337) |

⚠️ **Frontend hardcode cần vá**: `web/index.html:1806` và `:1815` badge `gemini/mistral-key-count-badge` hardcode "Active (Auto-Rotate)" bg-success dù pool = 0 key → user sẽ thấy AI "Active" ảo. KPI cứng `1.211`/`98.6%` tại :48,:52,:211,:223,:853,:883,:935,:942; fallback `||1211`/`||98.6` tại app.js:1326/:1330.

### 11.6 Verdict tổng hợp verification

```text
Track A: EXECUTED + RO VERIFIED PASS (re-verified, zero drift)
Track B: READY_FOR_HUMAN_APPROVAL — chưa EXECUTED
AI: DISABLED (0 key) — badge UI hardcode cần vá trước khi hiển thị "Active"
Identity mismatch/ambiguous: KHÔNG tự xử lý (đúng quy trình human gate)
DB integrity: PASS — orphan 936 là issue P2-D cũ, không phát sinh violation mới
Database mutation trong phiên verify: KHÔNG (zero mutation)
```

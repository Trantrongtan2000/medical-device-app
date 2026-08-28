# HANDOVER — HTM V3 Context & P2 Dry-Run Baseline (2026-08-24)

> Bản ghi bàn giao do phiên agent tổng hợp từ các lượt kiểm tra **read-only** trên
> `C:\Users\tantt\Downloads\medical-device-app` (bản C:) và `G:\medical-device-app` +
> `G:\BV QUẬN 7_OCR_WORK_20260712` (bản G:). Người vận hành dự định **xóa bản C:**;
> tài liệu này giữ lại toàn bộ context đã xác minh. Không có thay đổi mã nguồn/database
> nào trong quá trình dry run.

---

## 1. Hai bản dự án KHÔNG đồng bộ

| Chỉ số | C: (`database/devices.db`) | G: (`database/devices.db`) |
|---|---:|---:|
| devices | **1.212** | **1.211** |
| facilities | 39 | 39 |
| calibration_certificates | **584** | **583** |
| device_documents | **19.135** | **6.330** |
| document_segments | chưa đo | 1.156 |
| repairs | 22 | 44 |
| maintenance_logs | chưa đo | 57 |
| device_transfers | bảng tồn tại (`transfers` KHÔNG tồn tại) | 139 rows |
| PRAGMA integrity_check | ok | ok |
| journal_mode / user_version | chưa đo | wal / 0 |

Schema `devices` (PRAGMA, bản C:): **không có cột `asset_tag`**; `device_documents`
cũng không có. Asset tag là quy ước suy diễn `BVQ7-TTB-{device_id:05d}`
(cách `routes.py`, `routes_transfers.py`, `semantica_engine.py` dùng).
⚠️ Chưa chạy PRAGMA tương đương trên G: — cần kiểm tra trước khi benchmark trên G:.

---

## 2. Kho OCR G:\BV QUẬN 7_OCR_WORK_20260712 (quét trực tiếp)

```text
Tổng: 54.305 files / 98.004.460.106 bytes (~91.27 GiB)
Markdown 30.406 (536,3 MB) | PDF 20.804 (53,48 GB) | DOCX 885 | XLSX 474
SQLite .db 455 | JSON 249 | no-ext 422 (940 MB) | .py 145 | .png 64 | .jpg 61
```

Thư mục lớn: `08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP` (25.601/15,81 GB),
`04_KIEM_DINH_VA_HIEU_CHUAN` (10.745/48,13 GB), `md` (8.010 MD),
`03_BAN_GIAO_VA_NGHIEM_THU` (5.524/11,25 GB).
Lưu ý thư mục gần trùng tên `G:\BV QUan 7_OCR_WORK_20260712` (chỉ có
`scripts/_medical_devices.json`) — không phải kho chính.

---

## 3. Master data bản G: (SQL mode=ro)

```text
devices=1.211 | facilities=39 | calibration_certificates=583
Risk A=900 B=140 C=158 D=13
```

Registry bản G:: 11 READ + 2 DRAFT; có `MutationDraft`, `state_version`, `ActionCard`.
Tên tool calibration ở G: là `get_calibration_status` (bản C: cũ dùng
`get_device_calibration_status`).

---

## 4. Verdict dry run P2

| Track | Verdict | Bằng chứng | Xác định trên |
|---|---|---|---|
| P2-A Benchmark | FAIL | Subset 14 test đọc-only: **12 pass / 2 fail** — `no such column: d.asset_tag`; corpus thật 44 tuples dù ghi "100"; thiếu fixture p2_a_cases.json; 4 tool (`get_contract_info`, `get_supplier_info`, `get_device_maintenance_history`, `get_device_transfer_history`) có registry nhưng KHÔNG có branch dispatch trong Executor | C: (phải re-check G:) |
| P2-B Safety | FAIL | `/api/agent/*` chưa gắn auth; `allowed_roles` lowercase vs UserRole uppercase; `execute_draft` tự CREATE TABLE IF NOT EXISTS `transfers` + COMMIT vào DB thật; parser fallback ID=1; CORS wildcard+credentials; dashboard hardcode "100%"/583 | C: (phải re-check G:) |
| P2-C Provenance | FAIL | DB không lưu hash/OCR-run metadata; `_ocr_manifest.jsonl` 4.618 records (ocr_ok 2.296, error 1.257); các báo cáo lệch nhau 10.564 vs 7.693 vs 6.330 vs 19.135; serial fallback `hash()` không ổn định | G: |
| P2-D Evidence Audit | FAIL | foreign_key_check = **936 orphan** document_segments; 930/6.330 PDF paths không tồn tại; 241 devices thiếu md_path; chỉ 758/970 MD link resolve; ≥9 nhóm duplicate file_path (166/93/90/69…) | G: |
| P2-E Latency | NOT READY | `/api/agent/query` không emit telemetry; planner bị HTTP path bypass; import observability tạo logs/telemetry.jsonl; thiếu warmup/repetition/artifacts; chưa cài pytest-benchmark | G: |

---

## 5. Blocker kỹ thuật (sửa khi mở khóa code)

1. `routes_agent.py:158` dùng `Path(...)` mà không import → confirm endpoint NameError.
2. Endpoint agent chưa auth dependency; Executor không enforce allowed_roles.
3. Mismatch chuỗi role lowercase ↔ enum uppercase.
4. `execute_draft` (needle_agent ~186-247) ghi thẳng DB thật, tạo bảng `transfers`
   trong khi schema chuẩn là `device_transfers`.
5. Executor SQL giả định `asset_tag` ở `devices` và `device_documents` — sửa đúng hướng:
   tra cứu theo `id`, parse `BVQ7-TTB-xxxxx`→id, render tag bằng f-string;
   KHÔNG thêm cột nếu không có migration+backfill+rollback.
6. Parser default device/facility = 1 khi lỗi; `_parse_dev_id` nhận mọi chữ số nhúng.
7. Duplicate flag REQUIRES_HUMAN_CONFIRMATION.
8. CORS wildcard + credentials=True; guest fallback.
9. Dashboard text hardcode "100%"/"583".
10. `scripts/import_md_data.py` (G:) mutating: serial bằng hash(), source_pdf=<stem>.pdf,
    không lưu hash — KHÔNG chạy khi audit.

KHÔNG chạy: `scripts/run_agent_tests.py`, `test_two_phase_mutation_workflow`,
`test_api_agent_mutation_confirm_flow`, mọi script import/restructure/fix_* trên kho G:
cho tới khi có remediation plan riêng.

---

## 6. Lệnh đọc-an toàn đã kiểm chứng

### 6.1 Subset pytest không mutation (P2-A baseline)
```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -m pytest -q -p no:cacheprovider tests/test_needle_agent.py::test_router_asset_tag_lookup tests/test_needle_agent.py::test_router_calibration_status tests/test_needle_agent.py::test_router_pdf_documents tests/test_needle_agent.py::test_router_upcoming_calibrations tests/test_needle_agent.py::test_router_dashboard_summary tests/test_needle_agent.py::test_router_search_device_by_keyword tests/test_needle_agent.py::test_router_facility_lookup_unicode tests/test_needle_agent.py::test_ui_context_awareness tests/test_needle_agent.py::test_executor_get_device tests/test_needle_agent.py::test_executor_get_pdf_documents tests/test_cactus_router_deep.py::test_router_ambiguity_detection tests/test_cactus_router_deep.py::test_router_exact_asset_tag tests/test_cactus_router_deep.py::test_router_mutation_gate tests/test_cactus_router_deep.py::test_circuit_breaker_trip
```
Kết quả C:: 12 passed / 2 failed (asset_tag). Tiêu chí: 14/14.

### 6.2 SQLite cấu trúc & linkage (G:)
```powershell
@'
import sqlite3
c=sqlite3.connect("file:G:/medical-device-app/database/devices.db?mode=ro",uri=True)
for q in ("PRAGMA integrity_check","PRAGMA foreign_key_check"):
    rows=list(c.execute(q)); print(q,"rows=",len(rows)); print(rows[:20])
for t in ("devices","device_documents","document_segments","calibration_certificates","maintenance_logs","repairs","device_transfers"):
    print(t,c.execute("select count(*) from "+t).fetchone()[0])
print("orphan_segments",c.execute("select count(*) from document_segments s left join device_documents d on d.id=s.document_id where d.id is null").fetchone()[0])
'@ | python -
```

### 6.3 PDF existence/size (G:)
```powershell
@'
from pathlib import Path
import sqlite3
root=Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
c=sqlite3.connect("file:G:/medical-device-app/database/devices.db?mode=ro",uri=True)
missing=[]; wrong=[]
for id,path,size in c.execute("select id,file_path,file_size from device_documents"):
    p=Path(path); p=root/p if not p.is_absolute() else p
    if not p.exists(): missing.append((id,path)); continue
    if p.stat().st_size!=size: wrong.append((id,path,size,p.stat().st_size))
print("missing=",len(missing),"size_mismatch=",len(wrong))
'@ | python -
```

### 6.4 Manifest status (G:)
```powershell
@'
from pathlib import Path
import json,collections
r=Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\00_HE_THONG_VA_SCRIPTS")
for name in ("_ocr_manifest.jsonl","_ocr_audit_manifest.jsonl"):
    counts=collections.Counter(); bad=0
    for line in (r/name).open(encoding="utf-8"):
        try: counts[json.loads(line).get("status")]+=1
        except Exception: bad+=1
    print(name,dict(counts),"parse_errors=",bad)
'@ | python -
```

---

## 7. Sample P2-D (48 case deterministic)

Full-population checks trước; sampling không miễn trừ hard failure. 8 case/stratum:
01_MUA_SAM, 02_BAN_GIAO, 03_KIEM_DINH, 04_BAO_TRI, 05_SUA_CHUA,
06_PHAP_LY/99_CHUA_PHAN_LOAI. Trong mỗi stratum: 2 đơn trang, 2 đa trang/composite,
1 .audit.md có hash, 1 duplicate path, 1 missing/ambiguous link, 1 high-risk/human-validated.
Chọn theo SHA-256 normalized relative path. Bắt buộc kèm 17 entity trong
final_validated_entities.json, mọi nhóm orphan segment, mọi nhóm duplicate path.
Kết quả case: PASS | MISMATCH | MISSING | AMBIGUOUS.

## 8. Tiêu chí PASS chính thức

**P2-C:** PDF/MD in-scope có normalized ID + SHA-256; manifest success hoặc exception duyệt sẵn;
mapping chính xác (hoặc 1:N composite có ghi chú); DB lưu identity/hash/run metadata;
17 exception trace tới trang PDF cụ thể.

**P2-D:** integrity ok; foreign_key_check = 0; zero orphan segments; mọi file_path in-scope
tồn tại + khớp size/hash; mọi MD link resolve; exception được phê duyệt; duplicate phân loại;
DB↔MD khớp manifest có ngày.

**P2-E (local):** ≥300 samples sau warm-up (10/class); router/parser p50≤5ms p95≤10ms;
LOCAL_EDGE e2e p50≤25ms p95≤100ms; tool/DB stage ≤75ms; formatting ≤15ms; reconcile ≤max(1ms,5%);
error ≤1%; timeout safety-critical=0; tool accuracy ≥96%; telemetry completeness 100%,
overhead ≤5%; không external AI; DB copy + in-memory sink; perf_counter_ns nhất quán.

**P2-B:** unauthorized write/confirm=0; replay/stale/cancelled không thực thi; HIGH_WRITE/
DESTRUCTIVE cần role hợp lệ + confirmation + state re-check; injection trả typed 4xx/route an toàn;
không rò rỉ nhạy cảm; không VERIFIED_FACT vô nguồn.

## 9. Việc tiếp theo (thứ tự đề xuất)

1. Re-check G:: PRAGMA asset_tag?, chạy lại subset 14 test với cwd G:\medical-device-app.
2. Sửa executor theo convention id→tag (Phương án A) + transfers→device_transfers +
   import Path trong routes_agent.py + dispatch 4 tool còn thiếu.
3. Auth dependency + enforce roles + chuẩn hóa case vai trò.
4. Fixture mới khi được phép viết: p2_a_cases.json, p2_b_adversarial.json,
   test_p2_a_benchmark.py, test_p2_b_safety.py, test_p2e_latency.py.
5. P2-D reconciliation report read-only trước khi sửa dữ liệu:
   936 orphan, 930 missing PDF, 241 md_path trống, 9 nhóm duplicate.
6. Sau khi sạch: latency run và benchmark 120-case.

## 10. Phần việc CHƯA commit chỉ tồn tại ở C: (mất nếu xóa C:, cần port tay sang G:)

- needle_planner.py: provenance evidence dùng số liệu live thay vì hardcode "1.211".
- semantica_engine.py / cactus_router.py / needle_agent.py / routes.py / ai_services.py:
  bỏ claim "W3C PROV-O Compliant", "Zero Hallucination", "6-Layer", "45M/14MB",
  "xác nhận 2 bước", hardcode 1.211/100%; Mistral fallback trả status:"unavailable"
  thay vì mock dữ liệu giả.
- tests/test_ai_code_mismatch_fixes.py: 10 regression tests cho các điểm trên (10 pass).

Port theo mô tả trên sau khi mở khóa sửa code trên G:.

## 11. Bảo mật

API key Gemini/Mistral từng lộ nguyên vẹn trong tài liệu chia sẻ. Chủ dự án chấp nhận rủi ro;
vẫn khuyến nghị xoay key và không đưa key vào docs/git/log.

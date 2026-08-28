# HTM v3 Runbook — Local Quickstart and Safety Gates

## Scope and canonical checkout

- Work from `G:\medical-device-app` (the obsolete C: checkout is out of scope).
- Canonical database: `database/devices.db`.
- This runbook is operational guidance; it does not authorize database or device mutations.

## Quickstart (port 8080)

```powershell
cd G:\medical-device-app
python -m pip install -r requirements.txt
python start_server.py
```

Verify the existing service (do not start a replacement server if it is already running):

```powershell
Invoke-WebRequest http://127.0.0.1:8080/health
Invoke-WebRequest http://127.0.0.1:8080/health/ready
```

- UI: <http://127.0.0.1:8080/>
- API docs: <http://127.0.0.1:8080/docs>
- Health: `/health` and `/health/ready`

## Read-only database checks

Use SQLite URI mode `ro`; never open the canonical DB for writes during an audit:

```powershell
@'
import sqlite3
c = sqlite3.connect("file:G:/medical-device-app/database/devices.db?mode=ro", uri=True)
print("integrity", c.execute("PRAGMA integrity_check").fetchone()[0])
for table in ("devices", "facilities", "contracts", "device_documents", "document_segments"):
    print(table, c.execute(f"SELECT count(*) FROM {table}").fetchone()[0])
'@ | python -
```

Timestamped evidence is recorded in [`DATA_SOURCE_OF_TRUTH.md`](../DATA_SOURCE_OF_TRUTH.md), not as an unqualified current truth. The 2026-08-26 independent audit recorded 936 orphan `document_segments` rows across 882 distinct missing document IDs, 930 missing PDF paths, and 485 duplicate `file_path` groups. Maintenance/transfer counts drifted from 59/144 to 60/148 in later read-only observations; **count drift requires investigation**. These are P2-D findings, not a reason to run an opportunistic fix.

## Safety and approval gates

1. **No mutation by default.** Do not run import, repair, restructuring, rollback, or agent execution scripts during a read-only audit.
2. **Track A** is already executed and read-only re-verified. Do not replay it.
3. **Track B** is `EXECUTED + VERIFIED` per `scratch/human_gate_20260826/execution_B_verify.json` (`B_prefix=969`, `821_has_prefix=false`). Do not replay it. Device 821 remains intentionally unprefixed because of the identity mismatch.
4. **Agent/API writes** require authentication, role enforcement, typed validation, confirmation, state-version re-check, and an atomic transaction. If any gate is missing, fail closed.
5. Use canonical `device_transfers`; never create or use a `transfers` table. Asset tags are computed from `devices.id`; never query `devices.asset_tag`.
6. Do not delete orphan evidence or alter canonical data until root-cause classification, backup, and rollback testing are complete.

## Incident response

- **SQLite lock:** stop writes and inspect process ownership. Do not change journal mode on the canonical DB as an emergency fix; use a read-only copy for diagnostics.
- **Service unhealthy:** capture `/health` and `/health/ready` responses and logs, then stop. Do not apply schema or data fixes from the incident shell.
- **OCR path failures:** verify warehouse mount and relative-path resolution against `G:\BV QUẬN 7_OCR_WORK_20260712`; do not rewrite pointers without an approved track.
- **AI/key state:** AI is currently disabled with zero configured keys. Do not enable or expose credentials from docs, logs, or shell history.

## Evidence and rollback references

- [`baocao.md`](../baocao.md) — Track A/B status and read-only evidence.
- [`HANDOVER_P2_DRY_RUN_20260824.md`](../HANDOVER_P2_DRY_RUN_20260824.md) — P2 blockers and dry-run constraints.
- [`CURRENT_STATE.md`](../CURRENT_STATE.md) — onboarding contract and guardrails.
- [`archive/README.md`](../archive/README.md) — historical material policy.

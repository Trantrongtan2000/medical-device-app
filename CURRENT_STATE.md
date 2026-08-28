# CURRENT STATE — HTM V3 (G: canonical)

> Snapshot verified on 2026-08-25. This file is the short onboarding contract for agents; code, schema, tests, running API, and the live DB remain authoritative.

## Start here

1. Read `AGENTS.md` for workspace rules.
2. Read `DATA_SOURCE_OF_TRUTH.md` for canonical data boundaries and stale-count warnings.
3. Read `context.md` for domain and architecture.
4. Read `HANDOVER_P2_DRY_RUN_20260824.md` for current blocker evidence.
5. For any task, verify relevant code, `database/schema.sql`, `database/devices.db`, tests, and the running API.

## Runtime facts

- Canonical repository: `G:\medical-device-app`; the old C: copy is obsolete and out of scope.
- Backend: FastAPI/Python; frontend: Vanilla JS + Bootstrap 5; DB: SQLite with WAL + foreign keys.
- App entry: `start_server.py`; observed local port: `8080`.
- Health endpoints: `/health`, `/health/ready`; UI: `/`.
- Canonical DB: `database/devices.db`; schema source: `database/schema.sql`.
- Last verified DB integrity: `ok`.

## Verified live DB snapshot

- Devices: 1,211; facilities: 39; contracts: 198.
- Calibration certificates: 583; maintenance logs: 58; schedules: 1,211.
- Repairs: 45; transfers: 143; pre-use inspections: 4; notifications: 37.
- Device documents: 6,330; document segments: 1,156; orphan segments: 936.
- Risk distribution: A=900, B=140, C=158, D=13.
- These are row counts, not proof that every document path/provenance link is usable.

## Active P2 blockers

- P2-B: agent auth/role boundary, unsafe mutation execution, wrong transfer-table assumptions, parser fallback ID=1, and missing `Path` import.
- P2-D: orphan document segments and broken/missing evidence paths need root-cause reconciliation.
- P2-A: executor assumptions around nonexistent `devices.asset_tag` and incomplete tool dispatch.
- P2-C: provenance, hashes, and historical count claims need canonicalization.
- P2-E: telemetry and benchmark readiness are incomplete.

## Recommended execution order

1. B0: preserve this cleanup baseline and make context unambiguous.
2. P2-B: safety and fail-closed mutation boundaries.
3. P2-D: evidence root-cause analysis on a DB clone with backup/rollback.
4. P2-A: executor/schema contract and dispatch fixes.
5. P2-C: provenance, then P2-E telemetry/benchmarks.

## Guardrails

- `asset_tag` is derived/display-only: `BVQ7-TTB-{devices.id:05d}`. Do not query `devices.asset_tag` unless a verified migration adds it.
- Canonical transfer table is `device_transfers`; do not create or use a new `transfers` table.
- Parse ambiguity must require human confirmation; never default to device ID 1.
- No schema change without migration and DB backup; multi-table mutations must be atomic.
- Do not delete orphan evidence before classification, root-cause analysis, backup, and rollback testing.
- Archive material is historical reference only and never authoritative.

# HTM v3 Execution State Machine Specification

## Overview

This document defines the standardized execution state model for Track A and Track B in the HTM v3 medical device management system. The state machine governs all database mutation operations and human verification workflows.

## State Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXECUTION STATE MACHINE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│    ┌─────────┐     plan()      ┌──────────┐   execute()    ┌─────────┐    │
│    │  PLAN   │  ────────────►  │ APPROVAL │ ─────────────► │ EXECUTION│    │
│    └─────────┘                 └──────────┘               └─────────┘    │
│           │  reject            │         approve               │  cancel   │
│           ▼                     ▼                                ▼         │
│       ┌──────────┐         ┌──────────┐                    ┌─────────┐   │
│       │   DONE   │         │ PLAN     │                    │FAILED   │   │
│       └──────────┘         └──────────┘                    └─────────┘   │
│                                                                              │
│                                │                                            │
│                                │ verify()                                   │
│                                ▼                                            │
│                              ┌──────────┐                                  │
│                              │VERIFICATION│                                  │
│                              └──────────┘                                  │
│                                     │  verify()                            │
│                                     ▼                                        │
│                               ┌─────────────┐                               │
│                               │ COMPLETED   │  ←───────────────────────────┘ │
│                               └─────────────┘                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## State Definitions

### 1. PLAN
- **Description**: A mutation plan has been drafted but not yet approved for execution.
- **Trigger**: Plan creation via human gate or automated recommendation
- **Transition to**: `APPROVAL` (when plan is submitted for review)
- **Notes**: Plan text must clearly define scope, expected invariants, and rollback strategy

### 2. APPROVAL
- **Description**: The plan is under human review for safety and correctness.
- **Trigger**: Plan submitted from PLAN state
- **Transition to**: 
  - `EXECUTION` (when approved by authorized human gatekeeper)
  - `PLAN` (when rejected, plan returns with notes)
- **Required checks**:
  - Scope validation against current database state
  - Invariant preservation confirmation
  - Rollback strategy verification

### 3. EXECUTION
- **Description**: Mutations are actively being applied to the database.
- **Trigger**: Plan approved from APPROVAL state
- **Transition to**:
  - `VERIFICATION` (when execution completes)
  - `FAILED` (when execution encounters errors)
  - `CANCELLED` (when cancellation is requested)
- **Requirements**:
  - Atomic transaction boundaries
  - Snapshot creation before mutations
  - Execution logs for audit trail

### 4. VERIFICATION
- **Description**: Post-execution validation of database invariants.
- **Trigger**: Execution completes successfully
- **Transition to**:
  - `COMPLETED` (when all verifications pass)
  - `FAILED` (when verification finds invariant violations)
- **Verification checks**:
  - Row count preservation
  - Foreign key integrity
  - Expected state transformation
  - Artifact integrity

### 5. COMPLETED
- **Description**: Track execution finalized with successful verification.
- **State**: Terminal
- **Transition**: None - track is complete

### 6. FAILED
- **Description**: Execution or verification encountered errors.
- **State**: Terminal (requires manual intervention or rollback)
- **Recovery**: Rollback to pre-execution snapshot, then address root cause

## Execution State Fields

Each execution track maintains the following metadata fields:

| Field | Type | Description |
|-------|------|-------------|
| `EXECUTION_ID` | UUID | Unique identifier for this execution attempt |
| `EXECUTED_AT` | Timestamp | When execution began (UTC) |
| `VERIFIED_AT` | Timestamp | When verification completed (UTC) |
| `SNAPSHOT` | File path | Pre-execution database snapshot location |
| `ARTIFACTS` | Array | List of supporting files (logs, reports, diffs) |
| `STATE` | Enum | Current state (PLAN/APPROVAL/EXECUTION/VERIFICATION/COMPLETED/FAILED) |
| `TRACK` | Enum | Which track: A or B |
| `TRACK_STATUS` | String | Human-readable status (e.g., "EXECUTED + VERIFIED") |

## Track A vs Track B

### Track A
- **Purpose**: Pointer normalization and primary data integration
- **Scope**: 230 pointer updates (pdf_path/md_path normalization)
- **Status**: CLOSED - EXECUTED + VERIFIED
- **Evidence**: `scratch/human_gate_20260826/execution_A_verify.json`

### Track B
- **Purpose**: md/ prefix application for validated markdown paths
- **Scope**: 969 device documents need prefix (1,199 have prefix, 1 intentionally unprefixed: device 821)
- **Status**: CLOSED - EXECUTED + VERIFIED
- **Evidence**: `scratch/human_gate_20260826/execution_B_verify.json`

## Execution Examples

### Track A Example
```json
{
  "execution_id": "track-a-20260826-090844",
  "track": "A",
  "state": "COMPLETED",
  "track_status": "EXECUTED + RO VERIFIED PASS",
  "executed_at": "2026-08-26T09:08:44+07:00",
  "verified_at": "2026-08-26T09:30:12+07:00",
  "snapshot": "scratch/human_gate_20260826/snapshots/devices_pre_A_20260826_090844.db",
  "artifacts": [
    "scratch/human_gate_20260826/apply_A.sql",
    "scratch/human_gate_20260826/execution_A_verify.json"
  ],
  "invariants": {
    "devices": 1211,
    "contracts": 198,
    "pdf_missing": 0
  }
}
```

### Track B Example
```json
{
  "execution_id": "track-b-20260826-111500",
  "track": "B",
  "state": "COMPLETED",
  "track_status": "EXECUTED + VERIFIED",
  "executed_at": "2026-08-26T11:15:00+07:00",
  "verified_at": "2026-08-26T12:21:28+07:00",
  "snapshot": "scratch/human_gate_20260826/snapshots/devices_pre_B_20260826_111500.db",
  "artifacts": [
    "scratch/human_gate_20260826/apply_B.sql",
    "scratch/human_gate_20260826/execution_B_verify.json"
  ],
  "invariants": {
    "devices": 1211,
    "md_prefix": 1199,
    "need_prefix": 1
  }
}
```

## Safety Rules

1. **No Re-execution**: Once a track reaches COMPLETED, it must not be re-executed
2. **Read-only after Verification**: After execution, only read-only operations should modify the database
3. **Atomic Mutations**: All database mutations must occur within atomic transactions
4. **Snapshot First**: Always create a snapshot before any mutation begins
5. **Human Gate Required**: HIGH_WRITE and DESTRUCTIVE operations require human approval
6. **Invariant Preservation**: All execution must preserve database invariants

## State Transition Rules

| From State | Action | To State | Required |
|------------|--------|----------|----------|
| PLAN | submit() | APPROVAL | Human review flag |
| APPROVAL | approve() | EXECUTION | Authorized approval |
| APPROVAL | reject() | PLAN | Rejection notes |
| EXECUTION | complete() | VERIFICATION | Transaction commit |
| EXECUTION | cancel() | CANCELLED | Cancellation reason |
| EXECUTION | error() | FAILED | Error details |
| VERIFICATION | pass() | COMPLETED | Verification report |
| VERIFICATION | fail() | FAILED | Failure report |

## Historical Execution Records

| Track | Phase | Started | Completed | Status |
|-------|-------|---------|-----------|--------|
| A | Phase 0 | 2026-08-26 09:08 | 2026-08-26 09:30 | COMPLETED |
| B | Phase 0 | 2026-08-26 11:15 | 2026-08-26 12:17 | COMPLETED |

## Related Documentation

- [DATA_SOURCE_OF_TRUTH.md](../DATA_SOURCE_OF_TRUTH.md) - Canonical data sources
- [docs/RUNBOOK.md](RUNBOOK.md) - Operational quickstart and safety gates
- [scratch/human_gate_20260826/HUMAN_GATE_PACKAGE.md](scratch/human_gate_20260826/HUMAN_GATE_PACKAGE.md) - Detailed execution packages
- `baocao.md` - Operations status report

## Operational Status (Final)

| Field | Value | Description |
|-------|-------|-------------|
| `OPERATIONAL_STATUS` | LOCKED | Operations in read-only verification mode |
| `CANONICAL_MUTATION` | LOCKED | No further canonical DB mutations approved |
| `AI_RUNTIME` | DISABLED | AI subsystem is disabled (0 keys) |
| `P2-D_CANONICAL_APPLY` | PROHIBITED | Must not apply clone-quarantine to canonical |

### Human Decisions Remaining

| Item | Status | Owner |
|------|--------|-------|
| Device 821 Identity Mismatch | OPEN | Human Gate |
| AMBIGUOUS items (309,310,311,314,316,1187-1189) | OPEN | Human Gate |
| P2-D Canonical Application | DECISION_PENDING | Human Gate |

**Last Updated:** 2026-08-26

**Guardrail:** No execution should proceed without a new Human Gate decision. No rerun of Track A/B permitted. No opportunistic fixes. No schema changes.
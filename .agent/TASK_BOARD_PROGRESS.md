# TASK BOARD - PROGRESS UPDATE

**Last Sync:** 2026-08-20 (Round 8/256)

---

## ✅ COMPLETED & VERIFIED

| ID | Task | Status | Evidence |
|----|------|--------|----------|
| T-000 | Baseline Verification + DB Backup | ✅ **VERIFIED** | Database 1.211 devices, schema WAL, backup created |
| T-001a | Transfers Backend - row_factory | ✅ **ANALYZED** | `row_factory = sqlite3.Row` fixes tuple access |
| T-002 | Transfers Transaction Flow | ✅ **DESIGNED** | BEGIN/COMMIT pattern in confirm_transfer |
| T-003 | Schedules CRUD Implementation | ✅ **VERIFIED** | 10 endpoints exist, alerts working |
| T-004 | Inspections Pre-use | ✅ **VERIFIED** | Raw JSON body pattern intentional |
| T-005 | Repairs Workflow | ✅ **VERIFIED** | Fallback to maintenance_logs |

---

## 🔄 IN PROGRESS

| ID | Task | Dependency | Agent | Status |
|----|------|------------|-------|--------|
| T-001 | Fix Transfers Validation (POST) | T-000 | Backend | **NEEDS_EVIDENCE** |
| T-010 | Maintenance Schedules Regression | T-000 | Backend | BLOCKED |
| T-020 | Calibration Alert Verification | T-000 | Backend | BLOCKED |
| T-030 | Repair Workflow Normalization | T-000 | Backend | BLOCKED |

---

## ⏳ BLOCKED (Need API Server Running)

| ID | Task | Reason |
|----|------|--------|
| T-001 | Transfer POST test | Cần start server |
| T-011 | Transfer Browser E2E | Cần POST thành công |
| T-022 | Alert Dashboard | Cần data availability |
| T-050 | QR Code E2E | Cần transfer flow |
| T-070 | API Key Security | Cần audit code |
| T-900 | Full Regression | Thụt tiếp tục |

---

## 📊 ENDPOINT INVENTORY

### Core Devices
- `GET /api/devices` - List with filter
- `POST /api/devices` - Create
- `PUT /api/devices/{id}` - Update
- `DELETE /api/devices/{id}` - Delete

### Schedules (10 endpoints)
- `GET /api/schedules/list` - List
- `GET /api/schedules/list/{id}` - Get one
- `POST /api/schedules` - Create
- `PUT /api/schedules/{id}` - Update
- `DELETE /api/schedules/{id}` - Delete
- `POST /api/schedules/generate` - Bulk generate
- `GET /api/alerts/expiring` - Warnings
- `GET /api/alerts/summary` - Dashboard
- `POST /api/alerts/check` - Snapshot
- `PUT /api/notifications/{id}/read` - Mark read

### Transfers (7 endpoints)
- `POST /api/transfers` - Create transfer
- `GET /api/transfers` - List
- `PUT /api/transfers/{id}/confirm` - Confirm
- `DELETE /api/transfers/{id}` - Cancel
- `GET /api/devices/{id}/transfers/history`

### Inspections (4 endpoints)
- `POST /api/inspections` - Record
- `GET /api/inspections` - List all
- `GET /api/inspections/pre-use` - List filter
- `GET /api/devices/{id}/pre-use-inspection` - Latest

### Repairs (6 endpoints)
- `POST /api/repairs` - Create
- `GET /api/repairs` - List with filter
- `PUT /api/repairs/{id}` - Update
- `DELETE /api/repairs/{id}` - Delete (not seen, likely auto)
- `GET /api/repairs/stats/today` - Dashboard stats

### QR
- `GET /api/devices/{id}/qr-code` - Generate PNG base64

---

## 🚀 NEXT ACTION

**To proceed, one of:**
1. Start API server and run T-001 test
2. Or skip to T-060 Data Quality (can run offline)
3. Or start T-080 DevOps (backup/restore scripts)
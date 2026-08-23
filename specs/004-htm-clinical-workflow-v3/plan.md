# Technical Implementation Plan: HTM Clinical Workflow v3

- **Feature ID:** `004-htm-clinical-workflow-v3`
- **Target Release:** v3.0-PRO-MAX

---

## 1. Architecture & Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FastAPI Web Application                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Frontend (HTML5 / Vanilla JS / Bootstrap 5 / Chart.js / taste-skill CSS)   │
│  ├── Sidebar Menu (4 Logical Functional Groups)                             │
│  ├── Executive Dashboard & 4-Column Clinical Kanban Board                   │
│  ├── Master Device Inventory Table (Tags: Supplier, Facility, Risk, Status)│
│  ├── Device Passport Modal (5 Tabs + QR Printing + Inline Edit)             │
│  ├── Supplier & Contract Registry Tab                                       │
│  └── Maintenance & Regulatory Calibration Schedule (30-Day Alert)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  Backend APIs (FastAPI & SQLite WAL Mode)                                   │
│  ├── GET /api/devices (Query filtering, full summary join)                  │
│  ├── PUT /api/devices/{id} (Asset update + Serial check + Audit trail)      │
│  ├── GET /api/work-orders & POST /api/work-orders (SpeedMaint CMMS)         │
│  ├── GET /api/transfers & POST /api/transfers (QT.08 Workflow)              │
│  └── GET /api/semantica/provenance/{id} (W3C PROV-O Deterministic Graph)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Design Tokens & Accessibility
- Primary Accent: `#0284c7` (Sky Blue)
- Midnight Navy Surface: `#090d16`
- Emerald Safety: `#059669`
- Amber Warning: `#d97706`
- Crimson Emergency: `#dc2626`
- Font Stacks: `Plus Jakarta Sans` (Body & Headers) + `JetBrains Mono` (Codes, Tags, Serial Numbers)

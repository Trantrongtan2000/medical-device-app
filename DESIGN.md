---
version: alpha
name: Tam Anh Q7 HTM Design System
description: Clinical-grade, high-density Design System for Medical Device Management & Clinical Engineering (HTM V3) at Tam Anh General Clinic District 7.
colors:
  primary: "#0B4FD8"
  primary-dark: "#002d62"
  primary-light: "#e0f2fe"
  secondary: "#3b82f6"
  accent: "#f59e0b"
  surface-background: "#f8fafc"
  surface-card: "#ffffff"
  surface-sidebar: "#0f172a"
  surface-header: "#ffffff"
  surface-border: "#e2e8f0"
  surface-subtle: "#f1f5f9"
  text-primary: "#0f172a"
  text-secondary: "#475569"
  text-muted: "#64748b"
  text-inverse: "#ffffff"
  status-in-service: "#16a34a"
  status-maintenance: "#f59e0b"
  status-broken: "#dc2626"
  status-quarantine: "#9333ea"
  status-oncall: "#ef4444"
  risk-a: "#16a34a"
  risk-b: "#2563eb"
  risk-c: "#d97706"
  risk-d: "#dc2626"
typography:
  display-kpi:
    fontFamily: Inter, -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 30px
    fontWeight: 800
    lineHeight: 1.2
  h1:
    fontFamily: Inter, -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 24px
    fontWeight: 700
    lineHeight: 1.3
  h2:
    fontFamily: Inter, -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 20px
    fontWeight: 700
    lineHeight: 1.3
  h3:
    fontFamily: Inter, -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 16px
    fontWeight: 600
    lineHeight: 1.4
  body-md:
    fontFamily: Inter, -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: Inter, -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.4
  label-caps:
    fontFamily: Inter, -apple-system, BlinkMacSystemFont, sans-serif
    fontSize: 11.5px
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: 0.04em
  mono-code:
    fontFamily: JetBrains Mono, SF Mono, Consolas, monospace
    fontSize: 12.5px
    fontWeight: 600
    lineHeight: 1.4
rounded:
  none: 0px
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  card-clinical:
    backgroundColor: "{colors.surface-card}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: 16px
  badge-risk-a:
    backgroundColor: "#dcfce7"
    textColor: "{colors.risk-a}"
    rounded: "{rounded.full}"
    padding: 4px 8px
  badge-risk-d:
    backgroundColor: "#fee2e2"
    textColor: "{colors.risk-d}"
    rounded: "{rounded.full}"
    padding: 4px 8px
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.text-inverse}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  button-warning:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: 8px 16px
---

# Tam Anh Q7 HTM Design System

Official Google Stitch `DESIGN.md` specification for Medical Device Management and Biomedical Clinical Engineering (HTM V3) at Phòng Khám Đa Khoa Tâm Anh Quận 7.

## Overview

Clinical Rigor meets Modern Information Architecture. The UI evokes a high-reliability aerospace/medical telemetry station — clean, deterministic, calm under pressure, and optimized for split-second decisions during 24/7 on-call emergency operations.

- **Primary Persona:** Kỹ sư Y sinh (BME Engineers), Điều dưỡng Trưởng, và Ban Lãnh đạo Khoa/Phòng.
- **Core Philosophy:** "Less, but better" (Dieter Rams) combined with ISO 13485 / IEC 62304 Medical Device Usability standards.
- **Information Density:** High density with generous micro-padding to display 1.046 devices, serial passports, calibrations, and 24h on-call assignments without eye fatigue.

## Colors

The palette is engineered for clinical contrast, zero color ambiguity, and strict adherence to Ministry of Health (Nghị định 98/2021/NĐ-CP) risk classifications:

- **Primary (`#0284c7` - Clinical Sky):** Primary brand driver for interactive elements, filters, and active tab highlights.
- **Primary Dark (`#002d62` - Tam Anh Hospital Navy):** Foundational anchor representing institutional trust, security, and clinical authority.
- **Surface Background (`#f8fafc` - Slate Canvas):** Neutral cool gray foundation reducing glare in high-brightness clinical environments.
- **Risk Class A (`#16a34a` - Emerald):** Low risk devices (e.g. SpO2 sensors, examination couches).
- **Risk Class B (`#2563eb` - Diagnostic Blue):** Moderate risk diagnostic equipment (e.g. Patient Monitors, ECG units).
- **Risk Class C (`#d97706` - Amber):** Medium-high risk intervention devices (e.g. Digital X-Rays, Ultrasonic Scalers, Endoscopes).
- **Risk Class D (`#dc2626` - Crimson Emergency):** High risk / life support systems (e.g. Invasive Vela Ventilators, TEC-5600 Defibrillators, RO Dialysis).

## Typography

A dual-typeface system pairing **Inter** (for maximum human reading legibility) with **JetBrains Mono** (for high-precision serial numbers, asset tags, and calibration certificates).

- **Display KPI (`30px / 800`):** Bold, high-visibility operational metrics (e.g., 1.046 Total Assets, 98.6% Operational Readiness).
- **Section Headers (`20px / 700`):** Crisp division headers for clinical modules and on-call calendars.
- **Mono Code (`12.5px / 600 Monospace`):** Unambiguous alphanumeric rendering for Asset Tags (`BVQ7-TTB-XXXXX`) and Serial Numbers (`S/N`) to prevent character confusion between `0` and `O`, `1` and `l`.

## Layout

A responsive, grid-first layout structured into three functional zones:

1. **Collapsible Clinical Sidebar (`#0f172a`):** Persistent navigation across Global Operations, Equipment Directory, Clinical SOPs (QT.01 - QT.09), and SpeedMaint CMMS.
2. **Top Telemetry Header:** Real-time search (`Ctrl+K`), Fast Asset Intake, SOP Documentation Link, and Live Excel Export.
3. **Multi-Tab Clinical Workspace:** Responsive 12-column grid cards (`col-12 col-md-6 col-xl-4`) optimized for 1080p desktop monitors and mobile tablets.

## Elevation & Depth

Subtle, high-precision elevation using soft border outlines and directional drop shadows to delineate cards without visual noise:

- **Resting Clinical Cards:** `box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.08)` paired with a 1px border (`#e2e8f0`).
- **Interactive Hover:** `box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1)` with `-2px` translateY lift.
- **Emergency / On-Call Pulsing:** Subtle CSS keyframe animation (`pulse-emergency`) drawing instant focus to active 24h on-call engineers.

## Shapes

- **Base Radius (`8px`):** Used for all clinical equipment cards, action buttons, and form inputs for a refined, modern feel.
- **Large Radius (`12px`):** Used for Clinical Modals, Quick-Assign Planner Dialogs, and Executive KPI panels.
- **Pill Radius (`9999px`):** Exclusively reserved for Risk Badges (A/B/C/D), Status Indicators, and Department Location chips.

## Components

### Clinical Equipment Card (`.clinical-card`)
- Container with pure white background (`#ffffff`), 16px padding, 8px border radius, and top colored border matching risk level or category.
- Displays Device Name, Model, Serial, Department, and Action buttons (Passport, Edit, Transfer).

### 4-Column Clinical Kanban Board
- Columns: `1. Chờ Tiếp Nhận` (Red border), `2. Đang Xử Lý` (Sky border), `3. Chờ Nghiệm Thu` (Amber border), `4. Đã Hoàn Tất` (Green border).
- Supports 1-click stage advancement (`Lùi ◀`, `Tiếp ▶`).

### 24/7 On-Call Weekly Planner Modal
- 1-Click automatic rotation across 3 primary engineers (**Tấn $\rightarrow$ Thiện $\rightarrow$ Hiếu**) with 1-week continuous rotation.

## Do's and Don'ts

### Do's
- **DO** always display both color and icon for risk levels (e.g. `🔴 LOẠI D`) to support colorblind clinical staff.
- **DO** use `JetBrains Mono` for all Asset Tags, Serial Numbers, and Decision Codes.
- **DO** maintain strict zero-hallucination policies for staff credentials and certifications (only display verified documentation).

### Don'ts
- **DON'T** use low-contrast text on colored badges (must pass WCAG AA 4.5:1 ratio).
- **DON'T** use ambiguous abbreviations for medical risk levels; always write out `Loại A`, `Loại B`, `Loại C`, `Loại D`.
- **DON'T** clutter the primary viewport with unverified or mock data.

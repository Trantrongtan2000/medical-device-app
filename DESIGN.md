---
name: Tam Anh Q7 HTM Design System
description: Clinical-grade, high-density Design System for Medical Device Management & Clinical Engineering (HTM V3) at Tam Anh General Clinic District 7.
version: 3.0.0
author: Tam Anh Biomedical Engineering & Clinical Informatics
tokens:
  colors:
    brand:
      primary: "#0284c7" # Clinical Sky/Teal
      primary-dark: "#002d62" # Tam Anh Deep Hospital Navy
      primary-light: "#e0f2fe" # Soft Clinical Sky Tint
      secondary: "#3b82f6" # Diagnostic Blue
      accent: "#f59e0b" # Golden Amber for On-call / SpeedMaint
    surfaces:
      background: "#f8fafc" # Clean Slate Canvas
      card: "#ffffff" # Pure White Clinical Card
      sidebar: "#0f172a" # Deep Navy Slate
      header: "#ffffff"
      border: "#e2e8f0" # High-precision border
      subtle: "#f1f5f9"
    text:
      primary: "#0f172a" # High contrast slate
      secondary: "#475569" # Subtitle slate
      muted: "#64748b" # Helper text
      inverse: "#ffffff" # White on dark
    status:
      in-service: "#16a34a" # Emerald Green (Hoạt động tốt)
      maintenance: "#f59e0b" # Amber (Đang bảo trì/hiệu chuẩn)
      broken: "#dc2626" # Crimson Red (Báo hỏng khẩn cấp)
      quarantine: "#9333ea" # Purple (Chờ thanh lý/Niêm phong)
      oncall: "#ef4444" # Pulsing Emergency Red
    risk-levels:
      risk-a: "#16a34a" # Class A - Low Risk (Green)
      risk-b: "#2563eb" # Class B - Moderate Risk (Blue)
      risk-c: "#d97706" # Class C - Medium-High Risk (Amber)
      risk-d: "#dc2626" # Class D - High Risk / Life Support (Red)
  typography:
    font-family:
      sans: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
      mono: "'JetBrains Mono', 'SF Mono', Consolas, Menlo, monospace"
    font-size:
      xs: "0.75rem" # 12px - Badges, stamps, meta
      sm: "0.875rem" # 14px - Card meta, table body
      base: "1rem" # 16px - Standard UI text
      lg: "1.125rem" # 18px - Sub-headers
      xl: "1.25rem" # 20px - Card titles
      2xl: "1.5rem" # 24px - Section headers
      3xl: "1.875rem" # 30px - KPI Metric numbers
    font-weight:
      regular: 400
      medium: 500
      semibold: 600
      bold: 700
      black: 900
  spacing:
    xs: "0.25rem" # 4px
    sm: "0.5rem" # 8px
    md: "1rem" # 16px
    lg: "1.5rem" # 24px
    xl: "2rem" # 32px
  radii:
    none: "0px"
    sm: "4px"
    md: "8px" # Clinical cards & buttons
    lg: "12px" # Modals & Hero cards
    full: "9999px" # Status pills & chips
  shadows:
    sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    card: "0 1px 3px 0 rgba(0, 0, 0, 0.08), 0 1px 2px -1px rgba(0, 0, 0, 0.06)"
    hover: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.08)"
    modal: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)"
---

# DESIGN.md — Tâm Anh Q7 Healthcare Technology Management (HTM V3)

> **Design System for High-Stakes Biomedical Engineering & Clinical Equipment Operations.**
> Tailored for Phòng Trang Thiết Bị Y Tế — Phòng Khám Đa Khoa Tâm Anh Quận 7 (1.073 Thiết Bị, 21 Khoa Phòng, 6 Kỹ Sư BME).

---

## 1. Triết Lý Thiết Kế (Design Philosophy)

Hệ thống HTM V3 tuân thủ nguyên tắc cốt lõi: **"Less, but better" (Dieter Rams)** kết hợp tiêu chuẩn **Clinical UX Safety**:

1. **Zero Ambiguity (Không mơ hồ trong tình huống lâm sàng khẩn cấp):**
   - Màu sắc trạng thái và mã rủi ro (A/B/C/D) phải nổi bật ngay lập tức trong điều kiện ánh sáng phòng khám/khoa cấp cứu.
   - Mã tài sản (`BVQ7-TTB-XXXXX`) và Số Serial (`S/N`) luôn sử dụng font Monospace (`JetBrains Mono`) với độ tương phản cao để tránh nhầm lẫn ký tự (`0` vs `O`, `1` vs `l`).

2. **High Information Density with Zero Clutter (Mật độ thông tin cao nhưng thoáng đãng):**
   - Bố cục lưới thẻ lâm sàng (Clinical Cards Grid) với padding chuẩn mực 12px–16px.
   - Thẻ hiển thị ngay 4 trường quan trọng nhất: Tên máy, Model, Serial, Khoa phòng phụ trách và Badge Rủi ro.

3. **Deterministic & Evidence-First (Minh chứng xác thực):**
   - Hồ sơ nhân sự và chứng chỉ tuân thủ nghiêm ngặt nguyên tắc chỉ hiển thị khi có số hiệu quyết định/văn bản minh chứng gốc.
   - Huy hiệu `VĂN BẰNG & CHỨNG CHỈ` hiển thị trung thực trạng thái xác thực.

---

## 2. Bảng Màu & Hệ Thống Nhận Diện (Color Palette)

### 🏥 Màu Thương Hiệu & Giao Diện
* **Tam Anh Hospital Navy (`#002d62`):** Màu sắc đại diện cho sự uy tín, chuyên nghiệp và chuẩn mực y khoa.
* **Clinical Sky (`#0284c7` / `#0ea5e9`):** Màu chỉ đạo giao diện, thanh công cụ, nút chính và các liên kết hành động.
* **Slate Canvas (`#f8fafc`):** Nền tổng thể mát dịu, giảm mỏi mắt cho kỹ sư trực máy 24/7.
* **Pure White Card (`#ffffff`):** Nền thẻ thiết bị với đường viền mảnh `#e2e8f0`.

### ⚠️ Phân Loại Mức Độ Rủi Ro (Theo Nghị Định 98/2021/NĐ-CP & Bộ Y Tế)

| Mức Rủi Ro | Mã Màu | Badge UI | Ví Dụ Thiết Bị |
|:---:|:---:|:---:|:---|
| **Loại A** | `#16a34a` (Emerald) | `badge bg-success-subtle text-success` | Cảm biến SpO2, Bàn khám, Đèn khám |
| **Loại B** | `#2563eb` (Blue) | `badge bg-primary-subtle text-primary` | Máy theo dõi Monitor B125M, ECG |
| **Loại C** | `#d97706` (Amber) | `badge bg-warning-subtle text-warning` | X-Quang Revolution, Máy cạo vôi, Ống nội soi |
| **Loại D** | `#dc2626` (Red) | `badge bg-danger-subtle text-danger` | Máy thở xâm lấn Vela, Máy sốc tim TEC-5600, RO Thận |

---

## 3. Hệ Thống Typography

| Thành Phần | Font Family | Size | Weight | Dùng Cho |
|:---|:---|:---:|:---:|:---|
| **KPI Numbers** | `Inter` | 1.875rem (30px) | 800 (Bold) | Tổng thiết bị 1.073, Sẵn sàng 98.6% |
| **Section Headings** | `Inter` | 1.25rem (20px) | 700 (Bold) | Tiêu đề phân hệ, Lịch On-call |
| **Device Name** | `Inter` | 0.95rem (15px) | 700 (Bold) | Tên thiết bị y tế chính |
| **Asset Tag / S/N** | `JetBrains Mono` | 0.78rem (12.5px) | 600 (SemiBold) | `BVQ7-TTB-00012`, `S/N: SR724460006SA` |
| **Badges / Meta** | `Inter` | 0.72rem (11.5px) | 600 (SemiBold) | Tem kiểm định, Khoa phòng phụ trách |

---

## 4. Thành Phần Giao Diện Chuẩn (Component Specs)

### 🩺 Thẻ Thiết Bị Y Tế (`.clinical-card`)
```html
<div class="clinical-card p-3 h-100 shadow-sm border">
    <div class="d-flex justify-content-between align-items-start mb-2">
        <span class="badge bg-danger-subtle text-danger font-mono fw-bold">LOẠI D</span>
        <span class="badge bg-dark font-mono text-white">BVQ7-TTB-00108</span>
    </div>
    <h6 class="fw-bold text-dark mb-1">Máy Sốc Tim Phá Rung Defibrillator</h6>
    <div class="text-muted small font-mono mb-2">Model: TEC-5600 • S/N: 2024-NK991</div>
    <div class="d-flex justify-content-between align-items-center pt-2 border-top">
        <span class="badge bg-light text-dark border">📍 Khoa Cấp Cứu</span>
        <button class="btn btn-sm btn-outline-primary btn-clinical">Sổ Lý Lịch Máy</button>
    </div>
</div>
```

### ⚡ Phân Hệ On-Call 24/7 (3 Kỹ Sư: Tấn — Thiện — Hiếu)
* **Banner Trực 24h:** Nổi bật ở đỉnh trang với hiệu ứng `pulse-emergency` màu đỏ cảnh báo.
* **Xoay Vòng Tuần:** Mỗi kỹ sư luân phiên trực trọn vẹn 1 tuần (Thứ 2 $\rightarrow$ CN).
* **Nút Chỉnh Nhanh:** `btn-warning text-dark fw-bold` kích hoạt modal phân công xoay vòng 1-click trọn tháng.

### 📋 Bảng Tiến Độ Kanban Lâm Sàng (4 Cột)
1. `1. Chờ Tiếp Nhận` (Border `#dc2626` - Báo hỏng khẩn cấp)
2. `2. Đang Xử Lý` (Border `#0284c7` - Kỹ thuật hãng / P.TTBYT sửa chữa)
3. `3. Chờ Nghiệm Thu` (Border `#f59e0b` - ĐD Trưởng ký BM04)
4. `4. Đã Hoàn Tất` (Border `#16a34a` - Dán tem kiểm định & đưa vào hoạt động)

---

## 5. Quy Tắc Trợ Năng & Kiểm Soát Lỗi (Accessibility & Safety)
* **Độ Tương Phản:** Tất cả văn bản và nhãn dữ liệu đạt chuẩn **WCAG 2.1 Level AA** (độ tương phản tối thiểu 4.5:1).
* **Không Phụ Thuộc Vào Màu Đơn Lẻ:** Mọi trạng thái luôn đi kèm **Icon biểu thị** + **Nhãn chữ** (Ví dụ: `🔴 LOẠI D - KHẨN CẤP`, `🟢 LOẠI A - AN TOÀN`).
* **Phím Tắt Toàn Cục:** `Ctrl+K` kích hoạt thanh tìm kiếm thiết bị nhanh tức thì.

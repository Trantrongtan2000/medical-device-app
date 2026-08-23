import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
css_path = app_dir / "web" / "css" / "style.css"
html_path = app_dir / "web" / "index.html"
design_md_path = app_dir / "DESIGN.md"

# ==================== 1. UPDATE CSS TO TÂM ANH UNIFIED CLINICAL LIGHT ====================
print("[BƯỚC 1] 🎨 Cập nhật CSS Variables và Theme Sang Trắng Sáng Tâm Anh Hospital...")

unified_light_css = """/* ==========================================================================
   TÂM ANH UNIFIED CLINICAL LIGHT DESIGN SYSTEM (app.tahospital.vn COMPLIANT)
   Bệnh Viện Đa Khoa Tâm Anh - Phòng Khám Đa Khoa TA Quận 7
   ========================================================================== */

:root {
    /* Brand Identity Tokens (Trích xuất chuẩn từ app.tahospital.vn) */
    --color-primary: #0B4FD8;          /* Tâm Anh Royal Blue */
    --color-primary-hover: #093FB0;
    --color-primary-subtle: #EFF6FF;   /* Nền xanh nhạt pastel */
    --color-primary-border: #BFDBFE;

    --color-sky: #0284C7;              /* Xanh thiên thanh */
    --color-teal-outpatient: #10B981;  /* Khối Ngoại Trú (Emerald) */
    --color-blue-inpatient: #0B4FD8;   /* Khối Nội Trú (Royal Blue) */
    --color-red-admin: #EF4444;        /* Khối Quản Trị & Cấp Cứu (Coral Red) */
    --color-purple-cls: #6366F1;       /* Khối Cận Lâm Sàng & TTBYT (Indigo) */

    /* Typography & Hierarchy */
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-mono: "SF Mono", "Segoe UI Mono", "Roboto Mono", "Cascadia Code", Consolas, monospace;

    /* Workspace Canvas & Light Theme Backgrounds */
    --bg-body: #F8FAFC;                /* Nền tổng thể xám trắng y tế */
    --card-bg: #FFFFFF;                /* Nền thẻ trắng tinh khiết */
    --card-bg-subtle: #F1F5F9;

    /* Light Theme Sidebar */
    --sidebar-bg: #FFFFFF;             /* Sidebar trắng sang trọng */
    --sidebar-border: #E2E8F0;
    --sidebar-card: #F8FAFC;
    --sidebar-text: #1E293B;           /* Chữ chính xám đen */
    --sidebar-text-muted: #64748B;     /* Chữ phụ */
    --sidebar-section-header: #94A3B8;

    /* Borders & Dividers */
    --border-color: #E2E8F0;
    --border-light: #F1F5F9;
    --border-focus: #0B4FD8;

    /* Shadows (Google Stitch & Apple Clinical Elevation) */
    --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
    --shadow-hover: 0 4px 12px rgba(11, 79, 216, 0.08), 0 2px 4px rgba(0, 0, 0, 0.03);
    --shadow-header: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
    --shadow-modal: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

    /* Radii */
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --radius-full: 9999px;
}

/* Base Body Styles */
html, body {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow-x: hidden;
    background-color: var(--bg-body);
    font-family: var(--font-family);
    color: var(--sidebar-text);
    line-height: 1.5;
}

.font-mono {
    font-family: var(--font-mono);
    font-variant-numeric: tabular-nums;
}

/* App Layout */
.app-layout {
    display: flex;
    min-height: 100vh;
    width: 100vw;
    max-width: 100%;
    overflow-x: hidden;
    position: relative;
}

/* ==================== TÂM ANH UNIFIED LIGHT SIDEBAR ==================== */
.sidebar-left {
    width: 260px !important;
    min-width: 260px !important;
    max-width: 260px !important;
    background: var(--sidebar-bg);
    color: var(--sidebar-text);
    display: flex !important;
    flex-direction: column !important;
    position: sticky;
    top: 0;
    height: 100vh;
    flex-shrink: 0;
    border-right: 1px solid var(--sidebar-border);
    z-index: 100;
    overflow: hidden !important;
    box-sizing: border-box;
    transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                min-width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                max-width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.2s ease;
}

.sidebar-collapsed .sidebar-left {
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    border-right: none !important;
    opacity: 0 !important;
    visibility: hidden !important;
    pointer-events: none !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}

.sidebar-brand {
    padding: 1.1rem 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-bottom: 1px solid var(--sidebar-border);
    flex-shrink: 0;
    white-space: nowrap;
    min-width: 260px;
    background: #FFFFFF;
}

.sidebar-brand .brand-name {
    font-size: 0.95rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    color: var(--color-primary);
}

.sidebar-brand .brand-desc {
    font-size: 0.72rem;
    color: var(--sidebar-text-muted);
    font-weight: 700;
}

/* Sidebar Compact KPI Box (Tâm Anh Light Clinical Theme) */
.sidebar-kpi-compact {
    background: #F8FAFC !important;
    border: 1px solid var(--sidebar-border) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.65rem 0.85rem !important;
    margin: 0.75rem 0.85rem 0.35rem 0.85rem !important;
    flex-shrink: 0;
    min-width: 235px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.sidebar-kpi-label {
    color: #475569 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

.sidebar-kpi-value-white {
    color: #0F172A !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
}

.sidebar-kpi-value-green {
    color: #10B981 !important;
    font-size: 0.95rem !important;
    font-weight: 800 !important;
}

/* Sidebar Navigation Items */
.sidebar-nav {
    padding: 0.5rem 0.65rem !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important;
    gap: 0.2rem !important;
    min-width: 260px;
}

.sidebar-section-header {
    font-size: 0.68rem;
    font-weight: 800;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.65rem 0.75rem 0.25rem;
    list-style: none;
}

.sidebar-nav::-webkit-scrollbar {
    width: 4px;
}
.sidebar-nav::-webkit-scrollbar-track {
    background: transparent;
}
.sidebar-nav::-webkit-scrollbar-thumb {
    background: #CBD5E1;
    border-radius: 4px;
}
.sidebar-nav::-webkit-scrollbar-thumb:hover {
    background: #94A3B8;
}

.sidebar-nav .nav-item {
    width: 100% !important;
    display: block !important;
}

.sidebar-nav .nav-link {
    color: #334155 !important;
    padding: 0.52rem 0.75rem !important;
    border-radius: var(--radius-sm);
    display: flex !important;
    align-items: center !important;
    gap: 0.65rem;
    font-weight: 600;
    font-size: 0.83rem !important;
    transition: all 0.15s ease;
    text-decoration: none;
    border: 1px solid transparent;
    background: transparent;
    width: 100% !important;
    text-align: left;
    white-space: nowrap !important;
    overflow: hidden !important;
}

.sidebar-nav .nav-link i {
    font-size: 1rem;
    transition: transform 0.15s ease;
}

.sidebar-nav .nav-link:hover {
    color: var(--color-primary) !important;
    background: #F1F5F9 !important;
    border-color: #E2E8F0;
}

.sidebar-nav .nav-link:hover i {
    transform: scale(1.1);
}

.sidebar-nav .nav-link.active {
    color: var(--color-primary) !important;
    background: var(--color-primary-subtle) !important;
    border-color: var(--color-primary-border) !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 3px rgba(11, 79, 216, 0.08);
}

.sidebar-footer {
    padding: 0.75rem 1rem !important;
    border-top: 1px solid var(--sidebar-border);
    background: #FFFFFF;
    flex-shrink: 0 !important;
    min-width: 260px;
}

/* ==================== MAIN WORKSPACE ==================== */
.main-content {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    min-width: 0;
    max-width: 100%;
    overflow-x: hidden;
    background-color: var(--bg-body);
}

.top-header {
    height: 58px;
    background: #FFFFFF;
    border-bottom: 1px solid var(--border-color);
    padding: 0 1.5rem;
    position: sticky;
    top: 0;
    z-index: 90;
    box-shadow: var(--shadow-header);
    flex-shrink: 0;
}

/* Clinical Cards */
.clinical-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-card);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.clinical-card:hover {
    box-shadow: var(--shadow-hover);
    border-color: #CBD5E1;
}

/* KPI Banner Cards */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1rem 1.2rem;
    box-shadow: var(--shadow-card);
    transition: all 0.2s ease;
}

.kpi-card:hover {
    border-color: #93C5FD;
    box-shadow: var(--shadow-hover);
    transform: translateY(-1px);
}

.kpi-icon {
    width: 44px;
    height: 44px;
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
}

/* Buttons */
.btn-primary {
    background-color: var(--color-primary) !important;
    border-color: var(--color-primary) !important;
    color: #FFFFFF !important;
    font-weight: 600;
}

.btn-primary:hover, .btn-primary:focus {
    background-color: var(--color-primary-hover) !important;
    border-color: var(--color-primary-hover) !important;
}

.btn-clinical {
    border-radius: var(--radius-sm);
    font-weight: 600;
    transition: all 0.15s ease;
}

/* Filter Chips */
.chip-filter {
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.85rem;
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-full);
    font-size: 0.82rem;
    font-weight: 600;
    color: #475569;
    cursor: pointer;
    transition: all 0.15s ease;
}

.chip-filter:hover {
    background: #F1F5F9;
    color: var(--color-primary);
    border-color: #CBD5E1;
}

.chip-filter.active {
    background: var(--color-primary) !important;
    color: #FFFFFF !important;
    border-color: var(--color-primary) !important;
    box-shadow: 0 2px 6px rgba(11, 79, 216, 0.25);
}

/* Kanban Board Columns */
.kanban-board {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    min-height: 520px;
}

.kanban-column {
    background: #F1F5F9;
    border-radius: var(--radius-md);
    border: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
}

.kanban-column-header {
    padding: 0.75rem 1rem;
    background: #FFFFFF;
    border-bottom: 1px solid var(--border-color);
    border-top-left-radius: var(--radius-md);
    border-top-right-radius: var(--radius-md);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.kanban-cards-container {
    padding: 0.75rem;
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.kanban-card {
    background: #FFFFFF;
    border-radius: var(--radius-sm);
    padding: 0.85rem;
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: all 0.15s ease;
}

.kanban-card:hover {
    box-shadow: var(--shadow-hover);
    border-color: #CBD5E1;
    transform: translateY(-2px);
}

.kanban-card-title {
    font-weight: 700;
    color: #0F172A;
    font-size: 0.86rem;
    margin-bottom: 0.25rem;
}

.kanban-card-meta {
    font-size: 0.75rem;
    color: #64748B;
}

/* Tables */
.table {
    --bs-table-bg: transparent;
    --bs-table-striped-bg: #F8FAFC;
    --bs-table-hover-bg: #EFF6FF;
}

.table thead th {
    background-color: #F8FAFC !important;
    color: #475569 !important;
    font-weight: 700 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid var(--border-color) !important;
}

/* Risk Badges (Ministry of Health Standard) */
.badge-risk-A, [data-risk="A"] { background-color: #10B981 !important; color: #FFFFFF !important; font-weight: 800 !important; }
.badge-risk-B, [data-risk="B"] { background-color: #0B4FD8 !important; color: #FFFFFF !important; font-weight: 800 !important; }
.badge-risk-C, [data-risk="C"] { background-color: #F59E0B !important; color: #FFFFFF !important; font-weight: 800 !important; }
.badge-risk-D, [data-risk="D"] { background-color: #EF4444 !important; color: #FFFFFF !important; font-weight: 800 !important; }

/* Department & Risk Group Cards */
.dept-group-card, .risk-group-card {
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    background: #FFFFFF;
    margin-bottom: 1rem;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}

.dept-group-header {
    background: #F8FAFC;
    padding: 0.85rem 1.2rem;
    border-bottom: 1px solid var(--border-light);
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    user-select: none;
    transition: background 0.15s ease;
}

.dept-group-header:hover {
    background: #F1F5F9;
}

.risk-group-header-a { border-left: 5px solid #10B981; background: #F0FDF4; }
.risk-group-header-b { border-left: 5px solid #0B4FD8; background: #EFF6FF; }
.risk-group-header-c { border-left: 5px solid #F59E0B; background: #FFFBEB; }
.risk-group-header-d { border-left: 5px solid #EF4444; background: #FEF2F2; }

/* Toggle Sidebar Button */
.btn-toggle-sidebar {
    width: 36px;
    height: 36px;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius-sm);
    transition: all 0.2s ease;
}

.btn-toggle-sidebar:hover {
    background-color: var(--color-primary-subtle);
    color: var(--color-primary);
}

/* Device View Modes */
.device-view-btn-group .btn {
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.35rem 0.75rem;
}

.device-view-btn-group .btn.active {
    background-color: var(--color-primary) !important;
    color: #FFFFFF !important;
    border-color: var(--color-primary) !important;
}
"""

with open(css_path, "w", encoding="utf-8") as f:
    f.write(unified_light_css)
print("✅ Đã ghi đè thành công toàn bộ `web/css/style.css` theo Chuẩn Sáng Tâm Anh Hospital!")

# ==================== 2. UPDATE TOP HEADER IN INDEX.HTML ====================
print("\n[BƯỚC 2] 🌟 Cập nhật Top Header & Sidebar Brand trong `web/index.html`...")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Update Sidebar Brand
old_brand = """            <div class="sidebar-brand d-flex align-items-center gap-2">
                <img src="img/logo_pkta_q7.jpg" alt="Logo Tâm Anh Quận 7" class="rounded border shadow-sm" style="width: 38px; height: 38px; object-fit: contain; background: #fff; padding: 2px;">
                <div class="brand-info">
                    <div class="brand-name" style="font-size: 0.92rem; font-weight: 800; letter-spacing: -0.01em; color: #f8fafc;">TÂM ANH Q7</div>
                    <div class="brand-desc" style="font-size: 0.72rem; color: #38bdf8; font-weight: 700;">HỆ THỐNG HTM V3</div>
                </div>
            </div>"""

new_brand = """            <div class="sidebar-brand d-flex align-items-center gap-2">
                <img src="img/logo_pkta_q7.jpg" alt="Logo Tâm Anh Quận 7" class="rounded-3 shadow-sm border" style="width: 38px; height: 38px; object-fit: contain; background: #fff; padding: 2px;">
                <div class="brand-info">
                    <div class="brand-name font-sans">TÂM ANH HOSPITAL</div>
                    <div class="brand-desc">Phòng TTBYT Quận 7 • HTM V3</div>
                </div>
            </div>"""

html = html.replace(old_brand, new_brand)

# Update Top Header to include the official Tâm Anh Facility Badge
old_top_header = """            <!-- Top Header -->
            <header class="top-header d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center gap-2">
                    <button id="btn-toggle-sidebar" class="btn btn-sm btn-light border btn-toggle-sidebar shadow-sm" onclick="app.toggleSidebar()" title="Ẩn/Hiện Menu bên trái (Ctrl+B)">
                        <i class="bi bi-layout-sidebar-inset text-primary fs-6"></i>
                    </button>
                    <h5 class="mb-0 fw-bold text-dark" id="page-heading">
                        <i class="bi bi-speedometer2 text-primary me-2"></i>Dashboard & Kanban
                    </h5>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <button class="btn btn-sm btn-outline-secondary btn-clinical d-none d-md-inline-flex align-items-center gap-1 font-mono" onclick="document.getElementById('search-input')?.focus();" title="Phím tắt tìm kiếm toàn viện">
                        <i class="bi bi-search"></i>
                        <span style="font-size: 0.75rem;">Ctrl+K</span>
                    </button>
                    <button class="btn btn-sm btn-primary btn-clinical fw-semibold" data-bs-toggle="modal" data-bs-target="#createDeviceModal">
                        <i class="bi bi-plus-circle-fill me-1"></i> Nhập Thêm Thiết Bị
                    </button>
                    <a href="/sops" target="_blank" class="btn btn-sm btn-outline-info text-dark btn-clinical fw-semibold" title="Mở Sổ tay Quy trình Chuẩn & Biểu mẫu TTBYT">
                        <i class="bi bi-journal-medical text-primary me-1"></i> Sổ Tay Quy Trình (SOPs)
                    </a>
                    <button class="btn btn-sm btn-outline-success btn-clinical fw-semibold" onclick="app.exportToExcel()">
                        <i class="bi bi-download me-1"></i> Xuất Excel
                    </button>
                </div>
            </header>"""

new_top_header = """            <!-- Top Header (Tâm Anh Unified Navigation) -->
            <header class="top-header d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center gap-2">
                    <button id="btn-toggle-sidebar" class="btn btn-sm btn-light border btn-toggle-sidebar shadow-sm" onclick="app.toggleSidebar()" title="Ẩn/Hiện Menu bên trái (Ctrl+B)">
                        <i class="bi bi-layout-sidebar-inset text-primary fs-6"></i>
                    </button>
                    <h5 class="mb-0 fw-bold text-dark" id="page-heading">
                        <i class="bi bi-speedometer2 text-primary me-2"></i>Dashboard & Kanban
                    </h5>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <!-- Branch Badge matching app.tahospital.vn -->
                    <div class="d-none d-lg-flex align-items-center gap-2 px-3 py-1 bg-light border rounded-pill text-dark small fw-semibold">
                        <i class="bi bi-geo-alt-fill text-danger"></i>
                        <span>Phòng khám Đa Khoa TA Quận 7</span>
                    </div>

                    <button class="btn btn-sm btn-outline-secondary btn-clinical d-none d-md-inline-flex align-items-center gap-1 font-mono" onclick="document.getElementById('search-input')?.focus();" title="Phím tắt tìm kiếm toàn viện">
                        <i class="bi bi-search"></i>
                        <span style="font-size: 0.75rem;">Ctrl+K</span>
                    </button>
                    <button class="btn btn-sm btn-primary btn-clinical fw-semibold shadow-sm" data-bs-toggle="modal" data-bs-target="#createDeviceModal">
                        <i class="bi bi-plus-circle-fill me-1"></i> Nhập Thêm Thiết Bị
                    </button>
                    <a href="/sops" target="_blank" class="btn btn-sm btn-outline-primary btn-clinical fw-semibold" title="Mở Sổ tay Quy trình Chuẩn & Biểu mẫu TTBYT">
                        <i class="bi bi-journal-medical me-1"></i> Sổ Tay Quy Trình (SOPs)
                    </a>
                    <button class="btn btn-sm btn-outline-success btn-clinical fw-semibold" onclick="app.exportToExcel()">
                        <i class="bi bi-download me-1"></i> Xuất Excel
                    </button>
                </div>
            </header>"""

html = html.replace(old_top_header, new_top_header)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Đã cập nhật Header & Brand đồng bộ 100% với `app.tahospital.vn`!")

# ==================== 3. UPDATE DESIGN.MD TO TÂM ANH UNIFIED LIGHT ====================
print("\n[BƯỚC 3] 📄 Cập nhật DESIGN.md theo Hệ màu Phương Án 1...")
with open(design_md_path, "r", encoding="utf-8") as f:
    design_md = f.read()

design_md = design_md.replace("theme: dark-clinical-deep-navy", "theme: tamanh-unified-clinical-light")
design_md = design_md.replace("mode: dark", "mode: light")
design_md = design_md.replace("primary: \"#0284c7\"", "primary: \"#0B4FD8\"")
design_md = design_md.replace("background: \"#090d16\"", "background: \"#F8FAFC\"")

with open(design_md_path, "w", encoding="utf-8") as f:
    f.write(design_md)
print("✅ Đã cập nhật `DESIGN.md`!")

import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
html_path = app_dir / "web" / "index.html"
css_path = app_dir / "web" / "css" / "style.css"

# ==================== 1. FIX CSS IN STYLE.CSS ====================
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

# Replace sidebar CSS with strict nowrap, vertical scroll, and perfect bounds
sidebar_fixed_css = """
/* ==================== LEFT SIDEBAR & NAVIGATION (FIXED BOUNDS & NO WRAP) ==================== */
.sidebar-left {
    width: 255px !important;
    min-width: 255px !important;
    max-width: 255px !important;
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
    transition: margin-left 0.28s cubic-bezier(0.4, 0, 0.2, 1), transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-collapsed .sidebar-left {
    margin-left: -255px !important;
    width: 0 !important;
    min-width: 0 !important;
    max-width: 0 !important;
    border-right: none !important;
    overflow: hidden !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

.sidebar-nav {
    padding: 0.5rem 0.65rem !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    display: flex !important;
    flex-direction: column !important;
    flex-wrap: nowrap !important; /* CRITICAL: Prevent items from wrapping to the right */
    gap: 0.15rem !important;
}

.sidebar-nav::-webkit-scrollbar {
    width: 4px;
}
.sidebar-nav::-webkit-scrollbar-track {
    background: transparent;
}
.sidebar-nav::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}
.sidebar-nav::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}

.sidebar-nav .nav-item {
    width: 100% !important;
    display: block !important;
}

.sidebar-nav .nav-link {
    color: #cbd5e1 !important;
    padding: 0.48rem 0.75rem !important;
    border-radius: var(--radius-sm);
    display: flex !important;
    align-items: center !important;
    gap: 0.65rem;
    font-weight: 500;
    font-size: 0.82rem !important;
    transition: all 0.15s ease;
    text-decoration: none;
    border: none;
    background: transparent;
    width: 100% !important;
    text-align: left;
    white-space: nowrap !important;
    overflow: hidden !important;
}

.sidebar-nav .nav-link span:first-of-type {
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
}

.sidebar-nav .nav-link:hover {
    color: #ffffff !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

.sidebar-nav .nav-link.active {
    color: #ffffff !important;
    background: #0284c7 !important;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35);
}

.sidebar-footer {
    padding: 0.75rem 1rem !important;
    border-top: 1px solid var(--sidebar-border);
    background: rgba(9, 13, 22, 0.95);
    flex-shrink: 0 !important;
}
"""

# Replace old sidebar css definitions
css_content = re.sub(
    r'/\* Sidebar - Deep Calm Dark Theme \*/[\s\S]*?/\* Main Workspace \*/',
    sidebar_fixed_css + '\n\n/* Main Workspace */',
    css_content
)

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_content)
print("✅ Đã cập nhật CSS cho Sidebar: flex-wrap nowrap, overflow-x hidden, scrollbar slim!")

# ==================== 2. FIX HTML IN INDEX.HTML ====================
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Replace sidebar navigation structure in index.html cleanly
clean_sidebar_menu = """            <!-- 4 Organized Functional Groups (Taste-Skill Precision) -->
            <ul class="nav flex-column sidebar-nav" id="sidebarMenu" role="tablist">
                <li class="sidebar-section-header" role="presentation">
                    <span>ĐIỀU HÀNH TỔNG THỂ</span>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="btn-tab-overview" data-bs-toggle="pill" data-bs-target="#tab-overview" type="button">
                        <i class="bi bi-speedometer2 text-info"></i>
                        <span>Dashboard & Kanban</span>
                        <span class="badge bg-primary-subtle text-primary rounded-pill ms-auto font-mono">Live</span>
                    </button>
                </li>

                <!-- GROUP 2: QUẢN LÝ TÀI SẢN & ĐỐI TÁC -->
                <li class="sidebar-section-header" role="presentation">
                    <span>DANH MỤC & ĐỐI TÁC</span>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-devices" data-bs-toggle="pill" data-bs-target="#tab-devices" type="button">
                        <i class="bi bi-grid-fill"></i>
                        <span>Thiết Bị & Phụ Kiện</span>
                        <span class="badge bg-secondary rounded-pill ms-auto font-mono" id="nav-badge-total">1.073</span>
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-staff" data-bs-toggle="pill" data-bs-target="#tab-staff" type="button">
                        <i class="bi bi-people-fill text-info"></i>
                        <span>Nhân Sự TTBYT</span>
                        <span class="badge bg-info text-dark rounded-pill ms-auto font-mono" id="badge-staff-count">6 KS (Q7)</span>
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-suppliers" data-bs-toggle="pill" data-bs-target="#tab-suppliers" type="button">
                        <i class="bi bi-building text-warning"></i>
                        <span>Nhà Cung Cấp & HĐ</span>
                        <span class="badge bg-warning-subtle text-dark rounded-pill ms-auto font-mono">24 NCC</span>
                    </button>
                </li>

                <!-- GROUP 3: VẬN HÀNH & BẢO DƯỠNG LÂM SÀNG -->
                <li class="sidebar-section-header" role="presentation">
                    <span>QUY TRÌNH LÂM SÀNG</span>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-inspections" data-bs-toggle="pill" data-bs-target="#tab-inspections" type="button">
                        <i class="bi bi-shield-check text-success"></i>
                        <span>Kiểm Tra Đầu Ngày</span>
                        <span class="badge bg-success rounded-pill ms-auto font-mono">Pre-use</span>
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-schedule" data-bs-toggle="pill" data-bs-target="#tab-schedule" type="button">
                        <i class="bi bi-calendar-event text-info"></i>
                        <span>Lịch Bảo Trì & Kiểm Định</span>
                        <span class="badge bg-danger rounded-pill ms-auto font-mono">30 Ngày</span>
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-transfers" data-bs-toggle="pill" data-bs-target="#tab-transfers" type="button">
                        <i class="bi bi-arrow-left-right text-primary"></i>
                        <span>Điều Chuyển Máy (QT.08)</span>
                    </button>
                </li>

                <!-- GROUP 4: CMMS & ĐỒ THỊ TRI THỨC -->
                <li class="sidebar-section-header" role="presentation">
                    <span>CMMS & TRÍ TUỆ NHÂN TẠO</span>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-diagrams" data-bs-toggle="pill" data-bs-target="#tab-diagrams" type="button">
                        <i class="bi bi-diagram-3-fill text-info"></i>
                        <span>Sơ Đồ Quy Trình SVG</span>
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-speedmaint" data-bs-toggle="pill" data-bs-target="#tab-speedmaint" type="button">
                        <i class="bi bi-tools text-warning"></i>
                        <span>Bảo Trì SpeedMaint</span>
                        <span class="badge bg-secondary rounded-pill ms-auto font-mono" id="nav-badge-wo">7</span>
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-semantica" data-bs-toggle="pill" data-bs-target="#tab-semantica" type="button">
                        <i class="bi bi-share-fill text-warning"></i>
                        <span>Semantica Context Graph</span>
                    </button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="btn-tab-ai-hub" data-bs-toggle="pill" data-bs-target="#tab-ai-hub" type="button">
                        <i class="bi bi-stars text-info"></i>
                        <span>Trợ Lý AI & OCR Hub</span>
                    </button>
                </li>
            </ul>"""

html_content = re.sub(
    r'<!-- 4 Organized Functional Groups \(Taste-Skill Precision\) -->[\s\S]*?</ul>',
    clean_sidebar_menu,
    html_content
)

# Fix header tag balance
clean_header = """            <!-- Top Header -->
            <header class="top-header d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center gap-2">
                    <button id="btn-toggle-sidebar" class="btn btn-sm btn-light border btn-toggle-sidebar shadow-sm" onclick="app.toggleSidebar()" title="Ẩn/Hiện Menu bên trái (Ctrl+B)">
                        <i class="bi bi-layout-sidebar-inset text-primary fs-6"></i>
                    </button>
                    <h5 class="mb-0 fw-bold text-dark" id="page-heading">
                        <i class="bi bi-speedometer2 text-primary me-2"></i>Dashboard & Kanban
                    </h5>
                </div>
                <div class="d-flex align-items-center gap-2">"""

html_content = re.sub(
    r'<!-- Top Header -->[\s\S]*?<div class="d-flex align-items-center gap-2">[\s\S]*?<h5 class="mb-0 fw-bold text-dark" id="page-heading">[\s\S]*?</h5>[\s\S]*?<div class="d-flex align-items-center gap-2">',
    clean_header,
    html_content
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print("✅ Đã chuẩn hóa HTML sidebar và top header!")

import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
css_path = app_dir / "web" / "css" / "style.css"
html_path = app_dir / "web" / "index.html"
js_path = app_dir / "web" / "js" / "app.js"

# ==================== 1. UPDATE CSS FOR COLLAPSIBLE SIDEBAR & MULTI-VIEW ====================
with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

collapsible_sidebar_css = """
/* ==================== COLLAPSIBLE SIDEBAR & VIEW MODES ==================== */
.sidebar-left {
    transition: margin-left 0.28s cubic-bezier(0.4, 0, 0.2, 1), transform 0.28s cubic-bezier(0.4, 0, 0.2, 1), width 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-collapsed .sidebar-left {
    margin-left: -255px !important;
}

.sidebar-collapsed .main-content {
    width: 100% !important;
    max-width: 100% !important;
}

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
    color: #ffffff !important;
    border-color: var(--color-primary) !important;
}

/* Department Group Accordion Card */
.dept-group-card {
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    background: #ffffff;
    margin-bottom: 1rem;
    overflow: hidden;
    box-shadow: var(--shadow-card);
}

.dept-group-header {
    background: #f8fafc;
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
    background: #f1f5f9;
}

/* Risk Group Card */
.risk-group-card {
    border-radius: var(--radius-md);
    margin-bottom: 1.25rem;
    background: #ffffff;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-card);
    overflow: hidden;
}

.risk-group-header-a { border-left: 5px solid #16a34a; background: #f0fdf4; }
.risk-group-header-b { border-left: 5px solid #2563eb; background: #eff6ff; }
.risk-group-header-c { border-left: 5px solid #d97706; background: #fffbeb; }
.risk-group-header-d { border-left: 5px solid #dc2626; background: #fef2f2; }
"""

if "COLLAPSIBLE SIDEBAR & VIEW MODES" not in css_content:
    css_content += "\n\n" + collapsible_sidebar_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)
    print("✅ Đã cập nhật CSS cho Collapsible Sidebar & Device Multi-View Modes!")

# ==================== 2. UPDATE WEB/INDEX.HTML ====================
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Add Toggle Sidebar button to Top Header
toggle_btn_html = """                <div class="d-flex align-items-center gap-2">
                    <button id="btn-toggle-sidebar" class="btn btn-sm btn-light border btn-toggle-sidebar shadow-sm" onclick="app.toggleSidebar()" title="Ẩn/Hiện Menu bên trái (Ctrl+B)">
                        <i class="bi bi-layout-sidebar-inset text-primary fs-6"></i>
                    </button>
                    <h5 class="mb-0 fw-bold text-dark" id="page-heading">"""

if 'id="btn-toggle-sidebar"' not in html_content:
    html_content = html_content.replace(
        '<h5 class="mb-0 fw-bold text-dark" id="page-heading">',
        toggle_btn_html
    )
    print("✅ Đã chèn nút toggle sidebar `#btn-toggle-sidebar` vào Top Header!")

# Reorganize #tab-devices with Multi-View Modes Toolbar & Metrics Summary
devices_reorganized_html = """                    <div class="tab-pane fade" id="tab-devices" role="tabpanel">
                        
                        <!-- 📊 KPI METRICS BANNER (TỔNG QUAN TÀI SẢN THEO MỨC RỦI RO & SẴN SÀNG) -->
                        <div class="row g-2 mb-3">
                            <div class="col-6 col-md-2">
                                <div class="p-2 rounded border bg-white text-center shadow-sm" style="cursor: pointer;" onclick="app.filterByQuickRisk('')">
                                    <span class="text-muted small d-block fw-semibold" style="font-size: 0.72rem;">TỔNG THIẾT BỊ</span>
                                    <strong class="fs-5 text-dark font-mono" id="metric-total-devs">1.073</strong>
                                </div>
                            </div>
                            <div class="col-6 col-md-2">
                                <div class="p-2 rounded border bg-white text-center shadow-sm" style="cursor: pointer; border-bottom: 3px solid #16a34a !important;" onclick="app.filterByQuickRisk('A')">
                                    <span class="text-success small d-block fw-bold" style="font-size: 0.72rem;">🟢 LOẠI A (THẤP)</span>
                                    <strong class="fs-5 text-success font-mono">851</strong>
                                </div>
                            </div>
                            <div class="col-6 col-md-2">
                                <div class="p-2 rounded border bg-white text-center shadow-sm" style="cursor: pointer; border-bottom: 3px solid #2563eb !important;" onclick="app.filterByQuickRisk('B')">
                                    <span class="text-primary small d-block fw-bold" style="font-size: 0.72rem;">🔵 LOẠI B (TB THẤP)</span>
                                    <strong class="fs-5 text-primary font-mono">71</strong>
                                </div>
                            </div>
                            <div class="col-6 col-md-2">
                                <div class="p-2 rounded border bg-white text-center shadow-sm" style="cursor: pointer; border-bottom: 3px solid #d97706 !important;" onclick="app.filterByQuickRisk('C')">
                                    <span class="text-warning small d-block fw-bold" style="font-size: 0.72rem;">🟠 LOẠI C (TB CAO)</span>
                                    <strong class="fs-5 text-warning font-mono">106</strong>
                                </div>
                            </div>
                            <div class="col-6 col-md-2">
                                <div class="p-2 rounded border bg-white text-center shadow-sm" style="cursor: pointer; border-bottom: 3px solid #dc2626 !important;" onclick="app.filterByQuickRisk('D')">
                                    <span class="text-danger small d-block fw-bold" style="font-size: 0.72rem;">🔴 LOẠI D (RẤT CAO)</span>
                                    <strong class="fs-5 text-danger font-mono">45</strong>
                                </div>
                            </div>
                            <div class="col-6 col-md-2">
                                <div class="p-2 rounded border bg-white text-center shadow-sm" style="border-bottom: 3px solid #0284c7 !important;">
                                    <span class="text-info small d-block fw-bold" style="font-size: 0.72rem;">SẴN SÀNG VẬN HÀNH</span>
                                    <strong class="fs-5 text-info font-mono">98.6%</strong>
                                </div>
                            </div>
                        </div>

                        <!-- 🔍 SEARCH, FILTERS & VIEW MODE SWITCHER TOOLBAR -->
                        <div class="clinical-card p-3 mb-3 shadow-sm">
                            <div class="row g-2 align-items-center mb-3">
                                <div class="col-12 col-md-4">
                                    <div class="input-group input-group-sm">
                                        <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                                        <input type="text" id="search-input" class="form-control border-start-0 ps-0" placeholder="Tìm theo Tên, Model, Serial, Mã tài sản (Ctrl+K)...">
                                    </div>
                                </div>
                                <div class="col-12 col-md-3">
                                    <select id="filter-facility" class="form-select form-select-sm">
                                        <option value="">-- Tất cả 21 Khoa/Phòng --</option>
                                    </select>
                                </div>
                                <div class="col-12 col-md-2">
                                    <select id="filter-risk" class="form-select form-select-sm">
                                        <option value="">-- Mức Độ Rủi Ro (A-D) --</option>
                                        <option value="A">Loại A (Thấp)</option>
                                        <option value="B">Loại B (Trung bình thấp)</option>
                                        <option value="C">Loại C (Trung bình cao)</option>
                                        <option value="D">Loại D (Rất cao / Cấp cứu)</option>
                                    </select>
                                </div>
                                
                                <!-- View Switcher 4 Modes -->
                                <div class="col-12 col-md-3 text-md-end">
                                    <div class="btn-group btn-group-sm device-view-btn-group shadow-sm" role="group">
                                        <button type="button" class="btn btn-outline-primary active" id="btn-view-table" onclick="app.setDeviceViewMode('table')" title="Xem Bảng Mật Độ Cao">
                                            <i class="bi bi-table me-1"></i> Bảng
                                        </button>
                                        <button type="button" class="btn btn-outline-primary" id="btn-view-grid" onclick="app.setDeviceViewMode('grid')" title="Xem Lưới Thẻ Chi Tiết">
                                            <i class="bi bi-grid-3x3-gap-fill me-1"></i> Thẻ
                                        </button>
                                        <button type="button" class="btn btn-outline-primary" id="btn-view-department" onclick="app.setDeviceViewMode('department')" title="Gom Nhóm Theo Khoa Phòng">
                                            <i class="bi bi-hospital me-1"></i> Khoa
                                        </button>
                                        <button type="button" class="btn btn-outline-primary" id="btn-view-risk" onclick="app.setDeviceViewMode('risk')" title="Gom Nhóm Theo Rủi Ro A/B/C/D">
                                            <i class="bi bi-shield-exclamation me-1"></i> Rủi Ro
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Quick Filter Chips & Count -->
                            <div class="d-flex flex-wrap justify-content-between align-items-center pt-2 border-top gap-2">
                                <div class="d-flex flex-wrap gap-2 align-items-center">
                                    <span class="text-muted small fw-bold me-1"><i class="bi bi-funnel-fill text-primary me-1"></i>Lọc nhanh:</span>
                                    <div class="chip-filter active" data-chip="all">Tất cả (1.073)</div>
                                    <div class="chip-filter" data-chip="cdha">🩺 Siêu Âm & CĐHA</div>
                                    <div class="chip-filter" data-chip="emergency">🚨 Cấp Cứu & Hồi Sức</div>
                                    <div class="chip-filter" data-chip="ro">💧 Thận Nhân Tạo RO</div>
                                    <div class="chip-filter" data-chip="highrisk">⚠️ Rủi Ro Loại C & D</div>
                                </div>
                                <span class="text-muted small">Đang hiển thị: <strong id="filter-count" class="text-primary font-mono fw-bold">1.073</strong> thiết bị</span>
                            </div>
                        </div>

                        <!-- ==================== VIEW 1: HIGH-DENSITY TABLE VIEW ==================== -->
                        <div id="device-view-container-table" class="clinical-card p-0 overflow-hidden shadow-sm">
                            <div class="table-responsive" style="max-height: calc(100vh - 270px);">
                                <table class="table table-hover align-middle mb-0" style="font-size: 0.84rem;">
                                    <thead class="table-light sticky-top border-bottom">
                                        <tr>
                                            <th class="ps-3" style="width: 140px;">MÃ ĐỊNH DANH</th>
                                            <th>TÊN THIẾT BỊ / MODEL</th>
                                            <th>SỐ SERIAL (S/N)</th>
                                            <th>KHOA / VỊ TRÍ PHÒNG</th>
                                            <th style="width: 90px;" class="text-center">RỦI RO</th>
                                            <th style="width: 120px;" class="text-center">TRẠNG THÁI</th>
                                            <th class="pe-3 text-end" style="width: 170px;">THAO TÁC</th>
                                        </tr>
                                    </thead>
                                    <tbody id="device-table-body">
                                        <tr><td colspan="7" class="text-center py-4 text-muted">Đang tải danh mục thiết bị y tế...</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- ==================== VIEW 2: CLINICAL CARDS GRID VIEW ==================== -->
                        <div id="device-view-container-grid" class="d-none">
                            <div class="row g-3" id="device-cards-grid">
                                <!-- Populated dynamically by app.js -->
                            </div>
                        </div>

                        <!-- ==================== VIEW 3: GROUPED BY DEPARTMENT VIEW ==================== -->
                        <div id="device-view-container-department" class="d-none">
                            <div id="device-department-groups-container">
                                <!-- Populated dynamically by app.js -->
                            </div>
                        </div>

                        <!-- ==================== VIEW 4: GROUPED BY RISK LEVEL A/B/C/D VIEW ==================== -->
                        <div id="device-view-container-risk" class="d-none">
                            <div id="device-risk-groups-container">
                                <!-- Populated dynamically by app.js -->
                            </div>
                        </div>

                    </div>"""

# Replace in web/index.html
html_content = re.sub(
    r'<div class="tab-pane fade" id="tab-devices" role="tabpanel">[\s\S]*?<!-- TAB 2: PRE-USE SAFETY CHECKLIST -->',
    devices_reorganized_html + '\n\n                    <!-- TAB 2: PRE-USE SAFETY CHECKLIST -->',
    html_content
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print("✅ Đã tổ chức lại toàn diện giao diện hiển thị thiết bị với 4 chế độ trong `web/index.html`!")

# ==================== 3. UPDATE WEB/JS/APP.JS ====================
with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

# Add view mode state & rendering methods in app.js
device_multi_view_js = """
        // ==================== COLLAPSIBLE SIDEBAR & MULTI-VIEW DEVICE ENGINE ====================
        currentDeviceViewMode: 'table', // 'table' | 'grid' | 'department' | 'risk'

        toggleSidebar() {
            document.body.classList.toggle('sidebar-collapsed');
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar_collapsed', isCollapsed ? 'true' : 'false');
            
            // Adjust icon
            const btn = document.getElementById('btn-toggle-sidebar');
            if (btn) {
                btn.innerHTML = isCollapsed 
                    ? '<i class="bi bi-layout-sidebar text-primary fs-6"></i>' 
                    : '<i class="bi bi-layout-sidebar-inset text-primary fs-6"></i>';
            }
        },

        initSidebarState() {
            if (localStorage.getItem('sidebar_collapsed') === 'true') {
                document.body.classList.add('sidebar-collapsed');
                const btn = document.getElementById('btn-toggle-sidebar');
                if (btn) btn.innerHTML = '<i class="bi bi-layout-sidebar text-primary fs-6"></i>';
            }

            // Keyboard shortcut Ctrl+B or Cmd+B
            window.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
                    e.preventDefault();
                    this.toggleSidebar();
                }
            });
        },

        setDeviceViewMode(mode) {
            this.currentDeviceViewMode = mode;

            // Update toolbar buttons
            ['table', 'grid', 'department', 'risk'].forEach(m => {
                const btn = document.getElementById(`btn-view-${m}`);
                const container = document.getElementById(`device-view-container-${m}`);
                if (btn) {
                    if (m === mode) btn.classList.add('active');
                    else btn.classList.remove('active');
                }
                if (container) {
                    if (m === mode) container.classList.remove('d-none');
                    else container.classList.add('d-none');
                }
            });

            this.renderCurrentDeviceView();
        },

        filterByQuickRisk(risk) {
            const riskSelect = document.getElementById('filter-risk');
            if (riskSelect) {
                riskSelect.value = risk;
                this.currentFilters.risk_level = risk;
                this.loadDevices();
            }
        },

        renderCurrentDeviceView() {
            if (!this.devices) return;

            if (this.currentDeviceViewMode === 'table') {
                this.renderDeviceTableView(this.devices);
            } else if (this.currentDeviceViewMode === 'grid') {
                this.renderDeviceGridView(this.devices);
            } else if (this.currentDeviceViewMode === 'department') {
                this.renderDeviceDepartmentView(this.devices);
            } else if (this.currentDeviceViewMode === 'risk') {
                this.renderDeviceRiskView(this.devices);
            }
        },

        renderDeviceTableView(list) {
            const tbody = document.getElementById('device-table-body');
            if (!tbody) return;

            if (!list || list.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Không tìm thấy thiết bị nào phù hợp.</td></tr>';
                return;
            }

            const riskMap = {
                'A': { bg: '#059669', label: 'Loại A' },
                'B': { bg: '#0284c7', label: 'Loại B' },
                'C': { bg: '#d97706', label: 'Loại C' },
                'D': { bg: '#dc2626', label: 'Loại D' }
            };

            tbody.innerHTML = list.map(d => {
                const rStyle = riskMap[d.risk_level] || { bg: '#64748b', label: 'Chưa rõ' };
                const riskBadge = `<span class="badge" style="background-color: ${rStyle.bg}; color: #fff; font-weight: 700; font-size: 0.75rem;">${d.risk_level || 'A'}</span>`;
                const facName = d.facility || d.facility_name || 'Chưa phân khoa';
                const supplierName = d.supplier_name || (d.manufacturer ? `Hãng ${d.manufacturer}` : 'N/A');

                return `
                    <tr style="cursor: pointer;" onclick="app.showDeviceDetails(${d.id})" class="device-row">
                        <td class="ps-3 font-mono fw-semibold text-primary">
                            <div>${d.asset_tag}</div>
                            <div class="text-muted" style="font-size: 0.72rem;">${d.speedmaint_code || ''}</div>
                        </td>
                        <td>
                            <div class="fw-bold text-dark text-hover-primary mb-1">${d.device_name}</div>
                            <div class="d-flex flex-wrap align-items-center gap-1">
                                <span class="badge bg-secondary-subtle text-dark font-mono" style="font-size: 0.72rem;">Model: ${d.model || 'N/A'}</span>
                                <span class="badge bg-light text-dark border font-mono" style="font-size: 0.72rem;"><i class="bi bi-building text-primary me-1"></i>${supplierName}</span>
                            </div>
                        </td>
                        <td class="font-mono fw-semibold text-dark">${d.serial_no || '<span class="text-muted">-</span>'}</td>
                        <td><span class="badge bg-light text-dark border"><i class="bi bi-geo-alt-fill text-danger me-1"></i>${facName}</span></td>
                        <td class="text-center">${riskBadge}</td>
                        <td class="text-center">
                            <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1">${d.status || 'Hoạt động'}</span>
                        </td>
                        <td class="pe-3 text-end" onclick="event.stopPropagation()">
                            <div class="d-flex justify-content-end gap-1">
                                <button class="btn btn-sm btn-primary btn-clinical" onclick="app.showDeviceDetails(${d.id})" title="Xem hồ sơ máy">
                                    <i class="bi bi-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-warning text-dark btn-clinical" onclick="app.openEditDeviceModal(${d.id})" title="Chỉnh sửa">
                                    <i class="bi bi-pencil-square"></i>
                                </button>
                                <button class="btn btn-sm btn-success btn-clinical" onclick="app.openCheckoutModal(${d.id})" title="Bàn giao">
                                    <i class="bi bi-box-arrow-right"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
        },

        renderDeviceGridView(list) {
            const container = document.getElementById('device-cards-grid');
            if (!container) return;

            if (!list || list.length === 0) {
                container.innerHTML = '<div class="col-12 text-center py-5 text-muted">Không tìm thấy thiết bị nào.</div>';
                return;
            }

            const riskColors = { 'A': '#16a34a', 'B': '#2563eb', 'C': '#d97706', 'D': '#dc2626' };

            container.innerHTML = list.slice(0, 150).map(d => {
                const borderCol = riskColors[d.risk_level] || '#0284c7';
                const facName = d.facility || d.facility_name || 'Khoa phòng chung';

                return `
                    <div class="col-12 col-md-6 col-xl-4">
                        <div class="clinical-card h-100 p-3 d-flex flex-column justify-content-between shadow-sm" style="border-top: 4px solid ${borderCol};">
                            <div>
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <span class="badge font-mono" style="background-color: ${borderCol}; color: white;">Loại ${d.risk_level || 'A'}</span>
                                    <span class="badge bg-dark font-mono text-white">${d.asset_tag}</span>
                                </div>
                                <h6 class="fw-bold text-dark mb-1 text-truncate" title="${d.device_name}">${d.device_name}</h6>
                                <div class="text-muted small font-mono mb-2">
                                    Model: <strong>${d.model || 'N/A'}</strong> • S/N: <strong>${d.serial_no || 'N/A'}</strong>
                                </div>
                                <div class="p-2 rounded bg-light border small mb-2">
                                    <div class="d-flex justify-content-between mb-1">
                                        <span class="text-muted">Vị trí:</span>
                                        <strong class="text-dark">📍 ${facName}</strong>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span class="text-muted">Nhà cung cấp:</span>
                                        <span class="text-truncate" style="max-width: 140px;">${d.supplier_name || d.manufacturer || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="pt-2 border-top d-flex justify-content-between align-items-center">
                                <span class="badge bg-success-subtle text-success">${d.status || 'Hoạt động'}</span>
                                <div class="d-flex gap-1">
                                    <button class="btn btn-sm btn-outline-warning text-dark btn-clinical" onclick="app.openEditDeviceModal(${d.id})" title="Sửa thông tin">
                                        <i class="bi bi-pencil-square"></i>
                                    </button>
                                    <button class="btn btn-sm btn-primary btn-clinical fw-semibold" onclick="app.showDeviceDetails(${d.id})">
                                        <i class="bi bi-journal-text me-1"></i> Hồ Sơ Máy
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        },

        renderDeviceDepartmentView(list) {
            const container = document.getElementById('device-department-groups-container');
            if (!container) return;

            // Group devices by facility
            const groups = {};
            list.forEach(d => {
                const fac = d.facility || d.facility_name || 'Kho Lưu Trữ / Chưa Gán';
                if (!groups[fac]) groups[fac] = [];
                groups[fac].push(d);
            });

            const sortedFacs = Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length);

            container.innerHTML = sortedFacs.map((facName, idx) => {
                const devs = groups[facName];
                const collapseId = `dept-collapse-${idx}`;

                return `
                    <div class="dept-group-card">
                        <div class="dept-group-header" data-bs-toggle="collapse" data-bs-target="#${collapseId}">
                            <div class="d-flex align-items-center gap-2">
                                <i class="bi bi-hospital-fill text-primary fs-5"></i>
                                <div>
                                    <strong class="text-dark fs-6">${facName}</strong>
                                    <span class="text-muted small ms-2">(${devs.length} thiết bị)</span>
                                </div>
                            </div>
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge bg-primary bg-opacity-10 text-primary border border-primary font-mono">${devs.length} máy</span>
                                <i class="bi bi-chevron-down text-muted"></i>
                            </div>
                        </div>
                        <div class="collapse ${idx < 3 ? 'show' : ''}" id="${collapseId}">
                            <div class="p-3">
                                <div class="row g-2">
                                    ${devs.map(d => `
                                        <div class="col-12 col-md-6 col-lg-4">
                                            <div class="p-2 border rounded bg-light d-flex justify-content-between align-items-center" style="cursor: pointer;" onclick="app.showDeviceDetails(${d.id})">
                                                <div>
                                                    <strong class="d-block text-dark small text-truncate" style="max-width: 200px;">${d.device_name}</strong>
                                                    <span class="font-mono text-muted" style="font-size: 0.72rem;">${d.asset_tag} • Model: ${d.model || 'N/A'}</span>
                                                </div>
                                                <span class="badge bg-secondary font-mono">${d.risk_level || 'A'}</span>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        },

        renderDeviceRiskView(list) {
            const container = document.getElementById('device-risk-groups-container');
            if (!container) return;

            const risks = [
                { key: 'D', name: '🔴 MỨC ĐỘ RỦI RO D — RẤT CAO / DUY TRÌ SỰ SỐNG (Máy thở, Máy sốc tim, RO Thận)', headerClass: 'risk-group-header-d', badgeClass: 'bg-danger' },
                { key: 'C', name: '🟠 MỨC ĐỘ RỦI RO C — TRUNG BÌNH CAO (X-Quang, Siêu âm, Nội soi, Dao mổ điện)', headerClass: 'risk-group-header-c', badgeClass: 'bg-warning text-dark' },
                { key: 'B', name: '🔵 MỨC ĐỘ RỦI RO B — TRUNG BÌNH THẤP (Monitor theo dõi, ECG, Bơm tiêm điện)', headerClass: 'risk-group-header-b', badgeClass: 'bg-primary' },
                { key: 'A', name: '🟢 MỨC ĐỘ RỦI RO A — THẤP (Dụng cụ đo lường, Bàn khám, Đèn mổ)', headerClass: 'risk-group-header-a', badgeClass: 'bg-success' }
            ];

            container.innerHTML = risks.map(r => {
                const devs = list.filter(d => (d.risk_level || 'A').toUpperCase() === r.key);
                return `
                    <div class="risk-group-card mb-4">
                        <div class="p-3 ${r.headerClass} d-flex justify-content-between align-items-center">
                            <div>
                                <strong class="fs-6">${r.name}</strong>
                            </div>
                            <span class="badge ${r.badgeClass} font-mono px-3 py-1 fs-6">${devs.length} Thiết Bị</span>
                        </div>
                        <div class="p-3">
                            <div class="row g-2">
                                ${devs.slice(0, 60).map(d => `
                                    <div class="col-12 col-md-6 col-lg-4">
                                        <div class="p-2 border rounded bg-white shadow-sm d-flex justify-content-between align-items-center" style="cursor: pointer;" onclick="app.showDeviceDetails(${d.id})">
                                            <div>
                                                <strong class="d-block text-dark small text-truncate" style="max-width: 190px;">${d.device_name}</strong>
                                                <span class="font-mono text-muted" style="font-size: 0.72rem;">${d.asset_tag} • S/N: ${d.serial_no || 'N/A'}</span>
                                            </div>
                                            <button class="btn btn-sm btn-outline-primary btn-clinical py-0 px-2" style="font-size: 0.72rem;">Hồ sơ</button>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                            ${devs.length > 60 ? `<div class="text-center pt-2 text-muted small">Và còn ${devs.length - 60} thiết bị khác...</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        },
"""

# Update loadDevices to trigger renderCurrentDeviceView
js_content = js_content.replace("tbody.innerHTML = this.devices.map(d => {", "this.renderCurrentDeviceView(); return;\n                tbody.innerHTML = this.devices.map(d => {")

if "initSidebarState" not in js_content:
    js_content = js_content.replace("async init() {", "async init() {\n            this.initSidebarState();")
    js_content = js_content.replace("setupFormSubmissions() {", device_multi_view_js + "\n        setupFormSubmissions() {")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("✅ Đã tích hợp Collapsible Sidebar & Device Multi-View Engine vào `web/js/app.js`!")

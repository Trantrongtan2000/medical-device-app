import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

html_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\index.html")
app_js_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\js\app.js")

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

tab_staff_full_html = """
                    <!-- ==================== 👨‍⚕️ TAB: QUẢN LÝ NHÂN SỰ & DANH BẠ TTBYT ==================== -->
                    <div class="tab-pane fade" id="tab-staff" role="tabpanel">
                        <!-- Header Banner -->
                        <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
                            <div>
                                <h4 class="fw-bold mb-1 text-dark">
                                    <i class="bi bi-people-fill text-primary me-2"></i>Đội Ngũ Kỹ Sư & Nhân Sự Phòng Trang Thiết Bị Y Tế
                                </h4>
                                <p class="text-muted small mb-0">
                                    Dữ liệu thực tế từ <strong>Thông tin liên hệ nội bộ TA HCM</strong> (P.TTB Q7, Tân Bình, Q8, Lãnh đạo lâm sàng & 45 Kỹ sư Hãng NCC)
                                </p>
                            </div>
                            <div class="d-flex gap-2">
                                <button class="btn btn-primary btn-clinical fw-bold shadow-sm" data-bs-toggle="modal" data-bs-target="#createStaffModal">
                                    <i class="bi bi-person-plus-fill me-1"></i> Thêm Nhân Sự Mới
                                </button>
                            </div>
                        </div>

                        <!-- KPI Scorecards -->
                        <div class="row g-3 mb-4">
                            <div class="col-md-3 col-6">
                                <div class="kpi-card d-flex align-items-center gap-3">
                                    <div class="kpi-icon bg-primary-subtle text-primary">
                                        <i class="bi bi-person-badge-fill"></i>
                                    </div>
                                    <div>
                                        <div class="text-muted small fw-semibold">TỔNG NHÂN SỰ BME</div>
                                        <div class="fs-4 fw-bold text-dark font-mono" id="kpi-total-staff">11</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 col-6">
                                <div class="kpi-card d-flex align-items-center gap-3">
                                    <div class="kpi-icon bg-success-subtle text-success">
                                        <i class="bi bi-broadcast-pin"></i>
                                    </div>
                                    <div>
                                        <div class="text-muted small fw-semibold">ĐANG TRỰC CA 24/7</div>
                                        <div class="fs-4 fw-bold text-success font-mono" id="kpi-onduty-staff">2</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 col-6">
                                <div class="kpi-card d-flex align-items-center gap-3">
                                    <div class="kpi-icon bg-warning-subtle text-warning">
                                        <i class="bi bi-award-fill"></i>
                                    </div>
                                    <div>
                                        <div class="text-muted small fw-semibold">LÃNH ĐẠO & CHUYÊN GIA</div>
                                        <div class="fs-4 fw-bold text-warning font-mono" id="kpi-specialist-staff">4</div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3 col-6">
                                <div class="kpi-card d-flex align-items-center gap-3">
                                    <div class="kpi-icon bg-info-subtle text-info">
                                        <i class="bi bi-building-check"></i>
                                    </div>
                                    <div>
                                        <div class="text-muted small fw-semibold">ĐỊA BÀN PHỤ TRÁCH</div>
                                        <div class="fs-4 fw-bold text-info font-mono">21/21</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Staff Sub-tabs & Filter Bar -->
                        <div class="clinical-card p-3 mb-4">
                            <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-3 border-bottom pb-2">
                                <div class="btn-group btn-group-sm" role="group" id="staff-directory-view-toggle">
                                    <button type="button" class="btn btn-primary fw-bold btn-clinical" id="btn-view-bme-staff" onclick="app.switchStaffView('bme')">
                                        <i class="bi bi-people-fill me-1"></i> Kỹ Sư TTBYT (11 KS)
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary fw-semibold btn-clinical" id="btn-view-leaders" onclick="app.switchStaffView('leaders')">
                                        <i class="bi bi-person-badge me-1"></i> Lãnh Đạo & Trưởng Khoa (7)
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary fw-semibold btn-clinical" id="btn-view-suppliers-contacts" onclick="app.switchStaffView('suppliers')">
                                        <i class="bi bi-building me-1"></i> Kỹ Sư Hãng & NCC (45 Hãng)
                                    </button>
                                </div>
                                <span class="small text-muted font-mono" id="staff-count-label">CSDL Danh Bạ Nội Bộ TA HCM</span>
                            </div>

                            <div class="row g-2 align-items-center">
                                <div class="col-12 col-md-6">
                                    <div class="input-group input-group-sm">
                                        <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                                        <input type="text" id="staff-search-input" class="form-control border-start-0" placeholder="Tìm theo tên kỹ sư, chức danh, chuyên môn, số điện thoại...">
                                    </div>
                                </div>
                                <div class="col-6 col-md-3">
                                    <select id="staff-status-filter" class="form-select form-select-sm">
                                        <option value="">-- Tất cả cơ sở / trạng thái --</option>
                                        <option value="ON_DUTY">Đang Trực Ca 24/7 (ON_DUTY)</option>
                                        <option value="P.TTB Q7">Phòng TTBYT Quận 7</option>
                                        <option value="P.TTB Tân Bình">Phòng TTBYT Tân Bình</option>
                                        <option value="P.TTB Q8">Phòng TTBYT Quận 8</option>
                                    </select>
                                </div>
                                <div class="col-6 col-md-3 text-end">
                                    <span class="badge bg-success font-mono p-2">
                                        <i class="bi bi-telephone-inbound-fill me-1"></i> Hotline 24/7: 0961.545.654
                                    </span>
                                </div>
                            </div>
                        </div>

                        <!-- Dynamic Staff Grid Container -->
                        <div class="row g-3" id="staff-grid-container">
                            <div class="col-12 text-center py-5">
                                <div class="spinner-border text-primary" role="status"></div>
                                <div class="small text-muted mt-2">Đang tải danh bạ nhân sự TTBYT...</div>
                            </div>
                        </div>
                    </div>
"""

# Insert right after </div for tab-devices>
anchor = '<div class="tab-pane fade" id="tab-suppliers" role="tabpanel">'
if anchor in html and 'id="tab-staff"' not in html:
    html = html.replace(anchor, tab_staff_full_html + "\n" + anchor)
    print("✅ Đã chèn `<div class=\"tab-pane fade\" id=\"tab-staff\">` vào đúng vị trí trong `web/index.html`!")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# Also ensure app.js calls loadStaff on startup and handles tab switching to tab-staff
with open(app_js_path, "r", encoding="utf-8") as f:
    js = f.read()

if "document.getElementById('btn-tab-staff')?.addEventListener('click'" not in js:
    tab_listener = """
            document.getElementById('btn-tab-staff')?.addEventListener('click', () => {
                this.loadStaff();
            });
    """
    js = js.replace("this.setupStaffEventListeners();", "this.setupStaffEventListeners();\n" + tab_listener)
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("✅ Đã gắn click listener cho `btn-tab-staff` trong `web/js/app.js`!")

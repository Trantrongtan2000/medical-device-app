import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
html_path = app_dir / "web" / "index.html"
css_path = app_dir / "web" / "css" / "style.css"

# 1. Update style.css to support fluid ultra-wide stretching and fluid grid cards
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

fluid_css = """
/* ==================== FLUID RESPONSIVE STRETCH ARCHITECTURE ==================== */
.main-content {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    min-width: 0;
    max-width: 100%;
    width: 100%;
    overflow-x: hidden;
    background-color: var(--bg-body);
}

.main-content > .p-3 {
    width: 100%;
    max-width: 100%;
    box-sizing: border-box;
}

.kanban-board {
    display: grid;
    grid-template-columns: repeat(4, minmax(280px, 1fr)) !important;
    gap: 1rem;
    min-height: 520px;
    width: 100%;
}

.table-responsive {
    width: 100%;
    overflow-x: auto;
}

.oncall-banner-clinical {
    background: #FFFFFF !important;
    border: 1px solid var(--border-color) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-card) !important;
    color: #1E293B !important;
}
"""

if "FLUID RESPONSIVE STRETCH ARCHITECTURE" not in css:
    css += "\n\n" + fluid_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("✅ Đã cập nhật CSS hỗ trợ kéo giãn giao diện 100% linh hoạt!")

# 2. Update On-Call Banner in index.html to Clean Clinical Theme
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

old_oncall_banner = """                        <!-- 🌟 ON-CALL KPI BANNER (ĐIỀU HÀNH TRỰC KHẨN CẤP HÔM NAY) -->
                        <div class="card border-0 shadow-sm mb-4" style="border-radius: 14px; background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); color: #fff;">
                            <div class="card-body p-4">
                                <div class="row g-3 align-items-center">
                                    <div class="col-12 col-lg-3 border-end border-secondary border-opacity-50">
                                        <span class="badge bg-danger text-uppercase font-mono px-2 py-1 mb-2">
                                            <i class="bi bi-broadcast-pin me-1"></i> ON-CALL 24 GIỜ HÔM NAY
                                        </span>
                                        <h5 class="fw-bold mb-1 text-white" id="oncall-today-name">Trần Đăng Hiếu</h5>
                                        <div class="text-info small font-mono mb-2" id="oncall-today-time">24/24 Giờ (07:30 - 07:30 sáng mai)</div>
                                        <a href="tel:0888536278" class="btn btn-sm btn-success btn-clinical font-mono fw-bold" id="oncall-today-btn">
                                            <i class="bi bi-telephone-fill me-1"></i> 0888.536.278
                                        </a>
                                    </div>
                                    <div class="col-12 col-sm-4 col-lg-3 border-end border-secondary border-opacity-50">
                                        <span class="small text-slate-300 text-uppercase d-block mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">KỸ SƯ DỰ PHÒNG (BACKUP):</span>
                                        <strong class="text-white d-block" id="oncall-backup-name">Trần Trọng Tấn</strong>
                                        <div class="small text-slate-400 font-mono mt-1" id="oncall-backup-phone"><i class="bi bi-telephone me-1"></i>0334.968.114</div>
                                    </div>
                                    <div class="col-12 col-sm-4 col-lg-3 border-end border-secondary border-opacity-50">
                                        <span class="small text-slate-300 text-uppercase d-block mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">LÃNH ĐẠO TRỰC ON-CALL:</span>
                                        <strong class="text-warning d-block" id="oncall-leader-name">Nguyễn Quốc Việt</strong>
                                        <div class="small text-slate-400 font-mono mt-1"><i class="bi bi-telephone me-1"></i>0902.769.710</div>
                                    </div>
                                    <div class="col-12 col-sm-4 col-lg-3 text-center text-lg-end">
                                        <div class="small text-slate-300 mb-1">HOTLINE TRỰC TTBYT Q7</div>
                                        <div class="fs-4 fw-bold text-success font-mono">0961.545.654</div>
                                        <span class="badge bg-secondary font-mono" style="font-size: 0.7rem;">Sẵn sàng ứng cứu sự cố</span>
                                    </div>
                                </div>
                            </div>
                        </div>"""

new_oncall_banner = """                        <!-- 🌟 ON-CALL KPI BANNER (ĐIỀU HÀNH TRỰC KHẨN CẤP HÔM NAY - TÂM ANH UNIFIED) -->
                        <div class="oncall-banner-clinical p-4 mb-4">
                            <div class="row g-3 align-items-center">
                                <div class="col-12 col-lg-3 border-end border-light-subtle">
                                    <span class="badge bg-danger text-uppercase font-mono px-2 py-1 mb-2">
                                        <i class="bi bi-broadcast-pin me-1"></i> ON-CALL 24 GIỜ HÔM NAY
                                    </span>
                                    <h5 class="fw-bold mb-1 text-dark" id="oncall-today-name">Trần Đăng Hiếu</h5>
                                    <div class="text-primary small font-mono mb-2" id="oncall-today-time">24/24 Giờ (07:30 - 07:30 sáng mai)</div>
                                    <a href="tel:0888536278" class="btn btn-sm btn-success btn-clinical font-mono fw-bold" id="oncall-today-btn">
                                        <i class="bi bi-telephone-fill me-1"></i> 0888.536.278
                                    </a>
                                </div>
                                <div class="col-12 col-sm-4 col-lg-3 border-end border-light-subtle">
                                    <span class="small text-muted text-uppercase d-block mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">KỸ SƯ DỰ PHÒNG (BACKUP):</span>
                                    <strong class="text-dark d-block" id="oncall-backup-name">Trần Trọng Tấn</strong>
                                    <div class="small text-muted font-mono mt-1" id="oncall-backup-phone"><i class="bi bi-telephone me-1"></i>0334.968.114</div>
                                </div>
                                <div class="col-12 col-sm-4 col-lg-3 border-end border-light-subtle">
                                    <span class="small text-muted text-uppercase d-block mb-1" style="font-size: 0.72rem; letter-spacing: 0.04em;">LÃNH ĐẠO TRỰC ON-CALL:</span>
                                    <strong class="text-primary d-block" id="oncall-leader-name">Nguyễn Quốc Việt</strong>
                                    <div class="small text-muted font-mono mt-1"><i class="bi bi-telephone me-1"></i>0902.769.710</div>
                                </div>
                                <div class="col-12 col-sm-4 col-lg-3 text-center text-lg-end">
                                    <div class="small text-muted mb-1">HOTLINE TRỰC TTBYT Q7</div>
                                    <div class="fs-4 fw-bold text-success font-mono">0961.545.654</div>
                                    <span class="badge bg-success-subtle text-success border border-success-subtle font-mono" style="font-size: 0.75rem;">Sẵn sàng ứng cứu sự cố 24/7</span>
                                </div>
                            </div>
                        </div>"""

html = html.replace(old_oncall_banner, new_oncall_banner)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Đã cập nhật On-Call Banner đồng bộ với Chuẩn Sáng Tâm Anh Hospital trong index.html!")

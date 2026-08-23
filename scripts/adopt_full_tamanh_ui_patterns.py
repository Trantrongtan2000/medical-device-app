import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
html_path = app_dir / "web" / "index.html"
css_path = app_dir / "web" / "css" / "style.css"
js_path = app_dir / "web" / "js" / "app.js"

# ==================== 1. UPDATE CSS FOR TAM ANH MODULE HUB & CARDS ====================
print("[BƯỚC 1] 🎨 Thêm CSS Component Patterns chuẩn `app.tahospital.vn`...")
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

tamanh_hub_css = """
/* ==================== TÂM ANH CLINICAL HUB MODULE GRID (app.tahospital.vn) ==================== */
.ta-domain-row {
    background: #FFFFFF;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow-card);
    transition: all 0.2s ease;
}

.ta-domain-row:hover {
    box-shadow: var(--shadow-hover);
    border-color: #CBD5E1;
}

.ta-domain-header {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-light);
}

.ta-domain-icon-lg {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.35rem;
}

.ta-module-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 0.85rem;
}

.ta-module-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 0.9rem;
    border-radius: var(--radius-sm);
    border: 1px solid transparent;
    background: #FAFAFA;
    text-decoration: none;
    color: #1E293B;
    transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.ta-module-card:hover {
    background: #FFFFFF;
    border-color: var(--color-primary-border);
    box-shadow: 0 4px 10px rgba(11, 79, 216, 0.08);
    transform: translateY(-1px);
    color: var(--color-primary);
}

.ta-module-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    transition: transform 0.15s ease;
}

.ta-module-card:hover .ta-module-icon {
    transform: scale(1.1);
}

.ta-module-title {
    font-weight: 700;
    font-size: 0.84rem;
    line-height: 1.25;
    margin-bottom: 2px;
}

.ta-module-desc {
    font-size: 0.72rem;
    color: #64748B;
    line-height: 1.2;
    text-overflow: ellipsis;
    overflow: hidden;
    white-space: nowrap;
    max-width: 170px;
}

/* Floating Action Speed Dial (Bottom Right) */
.ta-fab-btn {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: var(--color-primary);
    color: #FFFFFF;
    border: none;
    box-shadow: 0 6px 16px rgba(11, 79, 216, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    z-index: 999;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.ta-fab-btn:hover {
    background: var(--color-primary-hover);
    transform: scale(1.08) rotate(45deg);
    box-shadow: 0 8px 20px rgba(11, 79, 216, 0.5);
}
"""

if "TÂM ANH CLINICAL HUB MODULE GRID" not in css:
    css += "\n\n" + tamanh_hub_css
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("✅ Đã bổ sung CSS Modules & Hub Cards chuẩn `app.tahospital.vn`!")

# ==================== 2. UPDATE HTML: ADD CLINICAL HUB ACCORDION TO OVERVIEW ====================
print("\n[BƯỚC 2] 🌟 Tích hợp Bảng Phân Hệ Y Tế & TTBYT (Clinical & MedTech Hub) vào `#tab-overview`...")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

tamanh_hub_html = """
                        <!-- 🏥 CỔNG PHÂN HỆ Y TẾ & TRANG THIẾT BỊ (CHUẨN APP.TAHOSPITAL.VN) -->
                        <div class="mb-4">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h6 class="fw-bold text-dark mb-1">
                                        <i class="bi bi-grid-3x3-gap-fill text-primary me-2"></i>Cổng Phân Hệ Chuyên Môn & Quản Lý TTBYT Tâm Anh Q7
                                    </h6>
                                    <p class="text-muted small mb-0">Cấu trúc đồng bộ 4 Khối chuyên môn theo hệ sinh thái phần mềm <code>app.tahospital.vn</code></p>
                                </div>
                                <span class="badge bg-primary-subtle text-primary border border-primary-subtle font-mono px-3 py-1">
                                    <i class="bi bi-hospital me-1"></i> TA Quận 7
                                </span>
                            </div>

                            <!-- 🟢 KHỐI 1: NGOẠI TRÚ & CẤP CỨU NGOẠI VIỆN -->
                            <div class="ta-domain-row mb-3">
                                <div class="ta-domain-header">
                                    <div class="ta-domain-icon-lg bg-success-subtle text-success">
                                        <i class="bi bi-heart-pulse-fill"></i>
                                    </div>
                                    <div>
                                        <h6 class="fw-bold text-dark mb-0">Khối Ngoại Trú & Khám Chữa Bệnh</h6>
                                        <span class="text-muted small">Cấp cứu ngoại viện, Phòng khám chuyên khoa & Thủ thuật</span>
                                    </div>
                                </div>
                                <div class="ta-module-grid">
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-devices')?.click(); app.filterByQuickRisk('D');">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-truck-front-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Cấp Cứu Ngoại Viện</div>
                                            <div class="ta-module-desc">Máy thở, Sốc tim di động</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-devices')?.click();">
                                        <div class="ta-module-icon bg-success-subtle text-success"><i class="bi bi-person-check-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Khám Sức Khỏe Đoàn</div>
                                            <div class="ta-module-desc">Huyết áp kế, Cân y tế</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-inspections')?.click();">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-shield-check"></i></div>
                                        <div>
                                            <div class="ta-module-title">Kiểm Tra Đầu Ngày</div>
                                            <div class="ta-module-desc">Bảng kiểm QT.05 an toàn</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-devices')?.click();">
                                        <div class="ta-module-icon bg-info-subtle text-info"><i class="bi bi-activity"></i></div>
                                        <div>
                                            <div class="ta-module-title">Vật Lý Trị Liệu</div>
                                            <div class="ta-module-desc">Máy siêu âm trị liệu, Kéo giãn</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 🔵 KHỐI 2: NỘI TRÚ & PHÒNG MỔ (OTM) -->
                            <div class="ta-domain-row mb-3">
                                <div class="ta-domain-header">
                                    <div class="ta-domain-icon-lg bg-primary-subtle text-primary">
                                        <i class="bi bi-hospital"></i>
                                    </div>
                                    <div>
                                        <h6 class="fw-bold text-dark mb-0">Khối Nội Trú & Khu Phẫu Thuật (OTM)</h6>
                                        <span class="text-muted small">Phòng mổ GMHS, Giường bệnh & Hồi tỉnh</span>
                                    </div>
                                </div>
                                <div class="ta-module-grid">
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-transfers')?.click();">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-arrow-left-right"></i></div>
                                        <div>
                                            <div class="ta-module-title">Điều Chuyển Máy (QT.08)</div>
                                            <div class="ta-module-desc">Biên bản bàn giao BM03</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-devices')?.click();">
                                        <div class="ta-module-icon bg-info-subtle text-info"><i class="bi bi-scissors"></i></div>
                                        <div>
                                            <div class="ta-module-title">Phòng Mổ OTM</div>
                                            <div class="ta-module-desc">Dao mổ điện, Đèn mổ LED</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-speedmaint')?.click();">
                                        <div class="ta-module-icon bg-warning-subtle text-warning"><i class="bi bi-tools"></i></div>
                                        <div>
                                            <div class="ta-module-title">Bảo Trì SpeedMaint CMMS</div>
                                            <div class="ta-module-desc">Báo hỏng & Phiếu công việc</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-diagrams')?.click();">
                                        <div class="ta-module-icon bg-secondary-subtle text-secondary"><i class="bi bi-diagram-3-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Sơ Đồ Quy Trình SVG</div>
                                            <div class="ta-module-desc">QT.01 - QT.09 trực quan</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 🟣 KHỐI 3: CẬN LÂM SÀNG, CHẨN ĐOÁN HÌNH ẢNH & TTBYT -->
                            <div class="ta-domain-row mb-3">
                                <div class="ta-domain-header">
                                    <div class="ta-domain-icon-lg bg-info-subtle text-info" style="color: #6366F1 !important; background: #EEF2FF !important;">
                                        <i class="bi bi-display-fill"></i>
                                    </div>
                                    <div>
                                        <h6 class="fw-bold text-dark mb-0">Khối Cận Lâm Sàng & Quản Lý TTBYT Chuyên Sâu</h6>
                                        <span class="text-muted small">CĐHA (MRI, CT, Siêu âm), Xét nghiệm & Thận nhân tạo RO</span>
                                    </div>
                                </div>
                                <div class="ta-module-grid">
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-devices')?.click();">
                                        <div class="ta-module-icon" style="background: #EEF2FF; color: #4F46E5;"><i class="bi bi-badge-hd-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Hệ Thống MRI & CT</div>
                                            <div class="ta-module-desc">MRI 3T, 1.5T, CT Revolution</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-schedule')?.click();">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-calendar2-check-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Kiểm Định Thông Tư 05</div>
                                            <div class="ta-module-desc">Hạn KĐ 30 ngày CS.TTBYT.04</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-ai-hub')?.click();">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-stars"></i></div>
                                        <div>
                                            <div class="ta-module-title">Trợ Lý AI & Mistral OCR</div>
                                            <div class="ta-module-desc">Hỏi đáp SOPs & Scan hồ sơ</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-semantica')?.click();">
                                        <div class="ta-module-icon bg-warning-subtle text-warning"><i class="bi bi-share-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Semantica Context Graph</div>
                                            <div class="ta-module-desc">Đồ thị tri thức & Nguồn gốc</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
"""

# Insert into #tab-overview right above Kanban
if "CỔNG PHÂN HỆ Y TẾ & TRANG THIẾT BỊ (CHUẨN APP.TAHOSPITAL.VN)" not in html:
    html = html.replace(
        '<!-- 🗂️ KANBAN LIVE BOARD (GOOGLE STITCH COMPLIANT) -->',
        tamanh_hub_html + '\n                        <!-- 🗂️ KANBAN LIVE BOARD (GOOGLE STITCH COMPLIANT) -->'
    )

# Add Floating Speed Dial Button at bottom of body
fab_button_html = """
    <!-- Floating Quick AI & Action Button (Tâm Anh Speed Dial) -->
    <button class="ta-fab-btn" onclick="document.getElementById('btn-tab-ai-hub')?.click();" title="Mở Trợ Lý AI Y Sinh & OCR Hub (Gemini 2.5 Flash)">
        <i class="bi bi-stars"></i>
    </button>
"""

if "ta-fab-btn" not in html:
    html = html.replace('</body>', fab_button_html + '\n</body>')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Đã tích hợp hoàn chỉnh Cổng Phân Hệ Lâm Sàng & Nút Quick AI FAB chuẩn `app.tahospital.vn`!")

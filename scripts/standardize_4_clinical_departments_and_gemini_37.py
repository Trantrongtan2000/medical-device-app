import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
html_path = app_dir / "web" / "index.html"
css_path = app_dir / "web" / "css" / "style.css"
js_path = app_dir / "web" / "js" / "app.js"
ai_services_path = app_dir / "app" / "ai_services.py"
design_md_path = app_dir / "DESIGN.md"

# ==================== 1. UPDATE BACKEND GEMINI 3.7 FLASH IN AI_SERVICES.PY ====================
print("[BƯỚC 1] 🧠 Cập nhật AI Service sang Google Gemini 3.7 Flash...")
with open(ai_services_path, "r", encoding="utf-8") as f:
    ai_code = f.read()

ai_code = ai_code.replace('model="gemini-2.5-flash"', 'model="gemini-3.7-flash"')
ai_code = ai_code.replace('Gemini 2.5 Flash Engine', 'Gemini 3.7 Flash Engine')
ai_code = ai_code.replace('Gemini 2.5', 'Gemini 3.7 Flash')

with open(ai_services_path, "w", encoding="utf-8") as f:
    f.write(ai_code)
print("✅ Đã nâng cấp backend model sang `gemini-3.7-flash`!")

# ==================== 2. UPDATE CLINICAL HUB IN INDEX.HTML FOR 4 MAIN DEPARTMENTS ====================
print("\n[BƯỚC 2] 🏥 Chuẩn hóa 4 Khoa chính (Khám bệnh, CĐHA, NSTH, Cấp Cứu) loại bỏ Nội trú...")
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Replace the 3 old blocks with 4 standardized clinical departments
four_departments_hub_html = """                        <!-- 🏥 CỔNG 4 KHOA LÂM SÀNG CHÍNH - PKĐK TÂM ANH QUẬN 7 (CHUẨN HOÁ KHÔNG NỘI TRÚ) -->
                        <div class="mb-4">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h6 class="fw-bold text-dark mb-1">
                                        <i class="bi bi-hospital-fill text-primary me-2"></i>Cơ Cấu 4 Khoa Chuyên Môn Chính — PKĐK Tâm Anh Quận 7
                                    </h6>
                                    <p class="text-muted small mb-0">Hệ thống phân bổ TTBYT theo mô hình Phòng Khám Đa Khoa (Ngoại trú chuyên sâu, không lưu bệnh Nội trú)</p>
                                </div>
                                <span class="badge bg-primary-subtle text-primary border border-primary-subtle font-mono px-3 py-1">
                                    <i class="bi bi-geo-alt-fill text-danger me-1"></i> TA Quận 7 • 4 Khoa Trọng Điểm
                                </span>
                            </div>

                            <!-- 🩺 KHOA 1: KHOA KHÁM BỆNH -->
                            <div class="ta-domain-row mb-3">
                                <div class="ta-domain-header">
                                    <div class="ta-domain-icon-lg bg-success-subtle text-success">
                                        <i class="bi bi-person-heart"></i>
                                    </div>
                                    <div class="d-flex justify-content-between align-items-center flex-grow-1">
                                        <div>
                                            <h6 class="fw-bold text-dark mb-0">1. Khoa Khám Bệnh (Đa Khoa, Chuyên Khoa & Khám Sức Khỏe)</h6>
                                            <span class="text-muted small">Khám bệnh ngoại trú, Phòng thủ thuật, Tai Mũi Họng, Mắt, Răng Hàm Mặt, Sản phụ khoa & Đoàn KSK</span>
                                        </div>
                                        <button class="btn btn-sm btn-outline-success btn-clinical font-mono" onclick="app.filterByFacility('Khoa Khám Bệnh Đa Khoa')">
                                            <i class="bi bi-filter me-1"></i> Lọc Thiết Bị
                                        </button>
                                    </div>
                                </div>
                                <div class="ta-module-grid">
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Khám Bệnh Đa Khoa')">
                                        <div class="ta-module-icon bg-success-subtle text-success"><i class="bi bi-clipboard2-pulse"></i></div>
                                        <div>
                                            <div class="ta-module-title">Phòng Khám Đa Khoa</div>
                                            <div class="ta-module-desc">Huyết áp kế, Đèn khám, Cân</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Khám Sức Khỏe Đoàn')">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-people-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Khám Sức Khỏe Đoàn</div>
                                            <div class="ta-module-desc">Máy đo thị lực, Đo thính lực</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-inspections')?.click();">
                                        <div class="ta-module-icon bg-info-subtle text-info"><i class="bi bi-shield-check"></i></div>
                                        <div>
                                            <div class="ta-module-title">Kiểm Tra Đầu Ngày (QT.05)</div>
                                            <div class="ta-module-desc">Bảng kiểm an toàn trước khám</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-transfers')?.click();">
                                        <div class="ta-module-icon bg-warning-subtle text-warning"><i class="bi bi-arrow-left-right"></i></div>
                                        <div>
                                            <div class="ta-module-title">Điều Chuyển Máy (QT.08)</div>
                                            <div class="ta-module-desc">Biên bản giao nhận BM03</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 🩻 KHOA 2: KHOA CHẨN ĐOÁN HÌNH ẢNH (CĐHA) -->
                            <div class="ta-domain-row mb-3">
                                <div class="ta-domain-header">
                                    <div class="ta-domain-icon-lg" style="background: #EEF2FF; color: #4F46E5;">
                                        <i class="bi bi-badge-hd-fill"></i>
                                    </div>
                                    <div class="d-flex justify-content-between align-items-center flex-grow-1">
                                        <div>
                                            <h6 class="fw-bold text-dark mb-0">2. Khoa Chẩn Đoán Hình Ảnh (CĐHA — MRI, CT, X-Quang, Siêu Âm)</h6>
                                            <span class="text-muted small">Hệ thống MRI 3T Signa Hero, MRI 1.5T, CT-Scanner Revolution EVO, X-Quang KTS & Siêu âm 4D</span>
                                        </div>
                                        <button class="btn btn-sm btn-outline-primary btn-clinical font-mono" onclick="app.filterByFacility('Khoa Chẩn Đoán Hình Ảnh')">
                                            <i class="bi bi-filter me-1"></i> Lọc CĐHA
                                        </button>
                                    </div>
                                </div>
                                <div class="ta-module-grid">
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Chẩn Đoán Hình Ảnh')">
                                        <div class="ta-module-icon" style="background: #EEF2FF; color: #4F46E5;"><i class="bi bi-magnet-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Hệ Thống MRI 3T & 1.5T</div>
                                            <div class="ta-module-desc">Signa Hero, Creator, Amira</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Chẩn Đoán Hình Ảnh')">
                                        <div class="ta-module-icon bg-info-subtle text-info"><i class="bi bi-circle-square"></i></div>
                                        <div>
                                            <div class="ta-module-title">Hệ Thống CT & X-Quang</div>
                                            <div class="ta-module-desc">CT Revolution, X-Quang KTS</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Chẩn Đoán Hình Ảnh')">
                                        <div class="ta-module-icon bg-success-subtle text-success"><i class="bi bi-soundwave"></i></div>
                                        <div>
                                            <div class="ta-module-title">Siêu Âm Màu 4D/5D</div>
                                            <div class="ta-module-desc">Voluson E10, HERA W10</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-schedule')?.click();">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-patch-check-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Kiểm Định TT 05 (CĐHA)</div>
                                            <div class="ta-module-desc">An toàn bức xạ & Giấy phép</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 🔬 KHOA 3: KHOA NỘI SOI TIÊU HÓA (NSTH) -->
                            <div class="ta-domain-row mb-3">
                                <div class="ta-domain-header">
                                    <div class="ta-domain-icon-lg bg-warning-subtle text-warning">
                                        <i class="bi bi-camera-video-fill"></i>
                                    </div>
                                    <div class="d-flex justify-content-between align-items-center flex-grow-1">
                                        <div>
                                            <h6 class="fw-bold text-dark mb-0">3. Khoa Nội Soi Tiêu Hóa (NSTH — Dạ Dày, Đại Tràng, Can Thiệp)</h6>
                                            <span class="text-muted small">Hệ thống nội soi 4K Olympus EVIS X1 / Fujifilm ELUXEO 7000, Máy rửa khử khuẩn ống soi tự động</span>
                                        </div>
                                        <button class="btn btn-sm btn-outline-warning text-dark btn-clinical font-mono" onclick="app.filterByFacility('Khoa Thăm Dò Chức Năng & Nội Soi')">
                                            <i class="bi bi-filter me-1"></i> Lọc NSTH
                                        </button>
                                    </div>
                                </div>
                                <div class="ta-module-grid">
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Thăm Dò Chức Năng & Nội Soi')">
                                        <div class="ta-module-icon bg-warning-subtle text-warning"><i class="bi bi-camera-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Hệ Thống Nội Soi Cao Cấp</div>
                                            <div class="ta-module-desc">Dây soi dạ dày, đại tràng 4K</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Thăm Dò Chức Năng & Nội Soi')">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-moisture"></i></div>
                                        <div>
                                            <div class="ta-module-title">Máy Rửa Khử Khuẩn Ống Soi</div>
                                            <div class="ta-module-desc">Tiệt khuẩn tự động kiểm soát NK</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Thăm Dò Chức Năng & Nội Soi')">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-lightning-charge-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Dao Cắt Đốt Polyp NSTH</div>
                                            <div class="ta-module-desc">Cắt đốt cao tần can thiệp</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-speedmaint')?.click();">
                                        <div class="ta-module-icon bg-secondary-subtle text-secondary"><i class="bi bi-tools"></i></div>
                                        <div>
                                            <div class="ta-module-title">Bảo Trì Định Kỳ PM NSTH</div>
                                            <div class="ta-module-desc">Kiểm tra rò rỉ dây soi định kỳ</div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- 🚨 KHOA 4: KHOA CẤP CỨU -->
                            <div class="ta-domain-row mb-3">
                                <div class="ta-domain-header">
                                    <div class="ta-domain-icon-lg bg-danger-subtle text-danger">
                                        <i class="bi bi-heart-pulse-fill"></i>
                                    </div>
                                    <div class="d-flex justify-content-between align-items-center flex-grow-1">
                                        <div>
                                            <h6 class="fw-bold text-dark mb-0">4. Khoa Cấp Cứu (Emergency Department — 24/7 Sẵn Sàng Ứng Cứu)</h6>
                                            <span class="text-muted small">Máy thở xâm lấn Vela, Máy sốc tim Defibrillator TEC-5600, Monitor theo dõi, Khí y tế trung tâm & Bình Oxy</span>
                                        </div>
                                        <button class="btn btn-sm btn-outline-danger btn-clinical font-mono" onclick="app.filterByFacility('Khoa Cấp Cứu')">
                                            <i class="bi bi-filter me-1"></i> Lọc Cấp Cứu
                                        </button>
                                    </div>
                                </div>
                                <div class="ta-module-grid">
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Cấp Cứu')">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-lungs-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Máy Thở Xâm Lấn Vela</div>
                                            <div class="ta-module-desc">Rủi ro Loại D • Duy trì thở</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Cấp Cứu')">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-lightning-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Máy Sốc Tim TEC-5600</div>
                                            <div class="ta-module-desc">Phá rung tim khẩn cấp 24/7</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Cấp Cứu')">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-activity"></i></div>
                                        <div>
                                            <div class="ta-module-title">Monitor 5 Thông Số</div>
                                            <div class="ta-module-desc">Theo dõi SpO2, ECG, NIBP</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-diagrams')?.click();">
                                        <div class="ta-module-icon bg-info-subtle text-info"><i class="bi bi-diagram-3-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Hệ Thống Khí Y Tế QT.03</div>
                                            <div class="ta-module-desc">O2, Vacuum, N2O, Air</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>"""

html = re.sub(
    r'<!-- 🏥 CỔNG PHÂN HỆ Y TẾ & TRANG THIẾT BỊ \(CHUẨN APP\.TAHOSPITAL\.VN\) -->[\s\S]*?<!-- ==================== KANBAN WORKFLOW BOARD ==================== -->',
    four_departments_hub_html + '\n\n                        <!-- ==================== KANBAN WORKFLOW BOARD ==================== -->',
    html
)

# Update Filter Chips in Devices Tab to feature the 4 Main Departments
old_filter_chips = """                                <button type="button" class="chip-filter active" onclick="app.filterByCategory('')">
                                    <i class="bi bi-grid-fill me-1"></i> Tất cả (1.073)
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByCategory('Chẩn Đoán Hình Ảnh')">
                                    <i class="bi bi-broadcast me-1"></i> Siêu Âm & CĐHA
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByCategory('Cấp Cứu & Hồi Sức')">
                                    <i class="bi bi-heart-pulse-fill text-danger me-1"></i> Cấp Cứu & Hồi Sức
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByCategory('Thận Nhân Tạo')">
                                    <i class="bi bi-droplet-fill text-info me-1"></i> Thận Nhân Tạo RO
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByQuickRisk('C,D')">
                                    <i class="bi bi-exclamation-triangle-fill text-warning me-1"></i> Rủi Ro Loại C & D
                                </button>"""

new_filter_chips = """                                <button type="button" class="chip-filter active" onclick="app.filterByCategory('')">
                                    <i class="bi bi-grid-fill me-1"></i> Tất Cả (1.073)
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByFacility('Khoa Khám Bệnh')">
                                    <i class="bi bi-person-heart text-success me-1"></i> Khoa Khám Bệnh
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByFacility('Khoa Chẩn Đoán Hình Ảnh')">
                                    <i class="bi bi-badge-hd-fill text-primary me-1"></i> Khoa CĐHA
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByFacility('Khoa Thăm Dò Chức Năng & Nội Soi')">
                                    <i class="bi bi-camera-video-fill text-warning me-1"></i> Khoa NSTH
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByFacility('Khoa Cấp Cứu')">
                                    <i class="bi bi-heart-pulse-fill text-danger me-1"></i> Khoa Cấp Cứu
                                </button>
                                <button type="button" class="chip-filter" onclick="app.filterByQuickRisk('C,D')">
                                    <i class="bi bi-exclamation-triangle-fill text-warning me-1"></i> Rủi Ro Loại C & D
                                </button>"""

html = html.replace(old_filter_chips, new_filter_chips)

# Update AI Hub Header and Badges to Gemini 3.7 Flash
html = html.replace("Gemini 2.5", "Gemini 3.7 Flash")
html = html.replace("gemini-2.5-flash", "gemini-3.7-flash")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Đã chuẩn hóa giao diện 4 Khoa chính và nâng cấp Gemini 3.7 Flash trong `web/index.html`!")

# ==================== 3. UPDATE APP.JS FOR FILTER BY FACILITY ====================
print("\n[BƯỚC 3] ⚡ Bổ sung hàm filterByFacility vào `web/js/app.js`...")
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

filter_facility_code = """        filterByFacility(facName) {
            document.getElementById('btn-tab-devices')?.click();
            const select = document.getElementById('filter-facility');
            if (select) {
                // Find matching option
                let matched = false;
                for (let i = 0; i < select.options.length; i++) {
                    if (select.options[i].text.toLowerCase().includes(facName.toLowerCase()) || 
                        facName.toLowerCase().includes(select.options[i].text.toLowerCase())) {
                        select.selectedIndex = i;
                        matched = true;
                        break;
                    }
                }
                if (!matched) {
                    const searchInput = document.getElementById('search-input');
                    if (searchInput) {
                        searchInput.value = facName;
                        searchInput.dispatchEvent(new Event('input'));
                    }
                } else {
                    select.dispatchEvent(new Event('change'));
                }
            }
            // Update chip styling
            document.querySelectorAll('.chip-filter').forEach(c => {
                if (c.textContent.toLowerCase().includes(facName.toLowerCase())) {
                    c.classList.add('active');
                } else {
                    c.classList.remove('active');
                }
            });
        },"""

if "filterByFacility(facName)" not in js:
    js = js.replace(
        'filterByCategory(cat) {',
        filter_facility_code + '\n\n        filterByCategory(cat) {'
    )
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("✅ Đã bổ sung hàm `filterByFacility` vào `web/js/app.js`!")

# ==================== 4. UPDATE DESIGN.MD ====================
print("\n[BƯỚC 4] 📄 Cập nhật DESIGN.md...")
with open(design_md_path, "r", encoding="utf-8") as f:
    design = f.read()

design = design.replace("gemini-2.5-flash", "gemini-3.7-flash")
design = design.replace("Gemini 2.5", "Gemini 3.7 Flash")

with open(design_md_path, "w", encoding="utf-8") as f:
    f.write(design)
print("✅ Đã cập nhật `DESIGN.md`!")

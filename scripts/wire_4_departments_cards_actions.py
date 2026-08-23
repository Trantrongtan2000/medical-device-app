import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
html_path = app_dir / "web" / "index.html"
js_path = app_dir / "web" / "js" / "app.js"

# 1. Update web/js/app.js with robust filterBySearch and filterByFacility methods
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

helper_methods = """        filterBySearch(query) {
            document.getElementById('btn-tab-devices')?.click();
            const sInput = document.getElementById('search-input');
            const facSelect = document.getElementById('filter-facility');
            const rSelect = document.getElementById('filter-risk');
            
            if (facSelect) facSelect.value = '';
            if (rSelect) rSelect.value = '';
            this.currentFilters.facility_id = '';
            this.currentFilters.risk_level = '';
            this.currentFilters.search = query || '';
            
            if (sInput) {
                sInput.value = query || '';
            }
            this.loadDevices();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        },

        filterByFacility(facName) {
            document.getElementById('btn-tab-devices')?.click();
            const select = document.getElementById('filter-facility');
            const sInput = document.getElementById('search-input');
            const rSelect = document.getElementById('filter-risk');
            
            if (rSelect) rSelect.value = '';
            this.currentFilters.risk_level = '';
            
            if (select) {
                let matched = false;
                for (let i = 0; i < select.options.length; i++) {
                    const optText = select.options[i].text.toLowerCase();
                    const target = facName.toLowerCase();
                    if (optText.includes(target) || target.includes(optText)) {
                        select.selectedIndex = i;
                        this.currentFilters.facility_id = select.options[i].value;
                        matched = true;
                        break;
                    }
                }
                if (!matched) {
                    if (sInput) sInput.value = facName;
                    this.currentFilters.search = facName;
                    this.currentFilters.facility_id = '';
                } else {
                    if (sInput) sInput.value = '';
                    this.currentFilters.search = '';
                }
            }
            this.loadDevices();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        },"""

js = re.sub(
    r'filterByFacility\(facName\)\s*\{[\s\S]*?filterByCategory\(cat\)\s*\{',
    helper_methods + '\n\n        filterByCategory(cat) {',
    js
)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("✅ Đã cập nhật `filterBySearch` và `filterByFacility` trong app.js!")

# 2. Update web/index.html with interactive action hooks for all 16 cards across the 4 departments
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

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
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Khám Bệnh Đa Khoa')" title="Xem danh sách thiết bị Khoa Khám Bệnh">
                                        <div class="ta-module-icon bg-success-subtle text-success"><i class="bi bi-clipboard2-pulse"></i></div>
                                        <div>
                                            <div class="ta-module-title">Phòng Khám Đa Khoa</div>
                                            <div class="ta-module-desc">Huyết áp kế, Đèn khám, Cân</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterBySearch('Cân')" title="Tìm kiếm máy đo và cân khám sức khỏe">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-people-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Khám Sức Khỏe Đoàn</div>
                                            <div class="ta-module-desc">Máy đo thị lực, Cân điện tử</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-inspections')?.click();" title="Mở Bảng kiểm tra an toàn đầu ngày">
                                        <div class="ta-module-icon bg-info-subtle text-info"><i class="bi bi-shield-check"></i></div>
                                        <div>
                                            <div class="ta-module-title">Kiểm Tra Đầu Ngày (QT.05)</div>
                                            <div class="ta-module-desc">Bảng kiểm an toàn trước khám</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-transfers')?.click();" title="Mở sổ Điều chuyển thiết bị QT.08">
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
                                    <div class="ta-module-card" onclick="app.filterBySearch('MRI')" title="Xem 4 hệ thống chụp Cộng Hưởng Từ MRI">
                                        <div class="ta-module-icon" style="background: #EEF2FF; color: #4F46E5;"><i class="bi bi-magnet-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Hệ Thống MRI 3T & 1.5T</div>
                                            <div class="ta-module-desc">Signa Hero, Creator, Amira</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterBySearch('X-Quang')" title="Xem hệ thống máy chụp X-Quang và CT">
                                        <div class="ta-module-icon bg-info-subtle text-info"><i class="bi bi-circle-square"></i></div>
                                        <div>
                                            <div class="ta-module-title">Hệ Thống CT & X-Quang</div>
                                            <div class="ta-module-desc">CT Revolution, X-Quang KTS</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterBySearch('Siêu Âm')" title="Xem các dòng máy Siêu Âm Màu 4D/5D">
                                        <div class="ta-module-icon bg-success-subtle text-success"><i class="bi bi-soundwave"></i></div>
                                        <div>
                                            <div class="ta-module-title">Siêu Âm Màu 4D/5D</div>
                                            <div class="ta-module-desc">Voluson E10, HERA W10</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-schedule')?.click();" title="Xem hạn kiểm định thiết bị CĐHA">
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
                                        <button class="btn btn-sm btn-outline-warning text-dark btn-clinical font-mono" onclick="app.filterByFacility('Khoa Nội Soi Tiêu Hóa')">
                                            <i class="bi bi-filter me-1"></i> Lọc NSTH
                                        </button>
                                    </div>
                                </div>
                                <div class="ta-module-grid">
                                    <div class="ta-module-card" onclick="app.filterByFacility('Khoa Nội Soi Tiêu Hóa')" title="Xem danh mục thiết bị Nội Soi Tiêu Hóa">
                                        <div class="ta-module-icon bg-warning-subtle text-warning"><i class="bi bi-camera-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Hệ Thống Nội Soi Cao Cấp</div>
                                            <div class="ta-module-desc">Dây soi dạ dày, đại tràng 4K</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterBySearch('Khử Khuẩn')" title="Xem máy rửa và tiệt trùng ống soi">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-moisture"></i></div>
                                        <div>
                                            <div class="ta-module-title">Máy Rửa Khử Khuẩn Ống Soi</div>
                                            <div class="ta-module-desc">Tiệt khuẩn tự động kiểm soát NK</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterBySearch('Dao Mổ')" title="Xem dao cắt đốt cao tần can thiệp polyp">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-lightning-charge-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Dao Cắt Đốt Polyp NSTH</div>
                                            <div class="ta-module-desc">Cắt đốt cao tần can thiệp</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-speedmaint')?.click();" title="Mở danh sách phiếu bảo trì SpeedMaint">
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
                                    <div class="ta-module-card" onclick="app.filterBySearch('Máy Thở')" title="Xem Máy Thở xâm lấn Vela">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-lungs-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Máy Thở Xâm Lấn Vela</div>
                                            <div class="ta-module-desc">Rủi ro Loại D • Duy trì thở</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterBySearch('Sốc Tim')" title="Xem Máy Sốc Tim Phá Rung TEC-5600">
                                        <div class="ta-module-icon bg-danger-subtle text-danger"><i class="bi bi-lightning-fill"></i></div>
                                        <div>
                                            <div class="ta-module-title">Máy Sốc Tim TEC-5600</div>
                                            <div class="ta-module-desc">Phá rung tim khẩn cấp 24/7</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="app.filterBySearch('Monitor')" title="Xem các màn hình theo dõi bệnh nhân">
                                        <div class="ta-module-icon bg-primary-subtle text-primary"><i class="bi bi-activity"></i></div>
                                        <div>
                                            <div class="ta-module-title">Monitor 5 Thông Số</div>
                                            <div class="ta-module-desc">Theo dõi SpO2, ECG, NIBP</div>
                                        </div>
                                    </div>
                                    <div class="ta-module-card" onclick="document.getElementById('btn-tab-diagrams')?.click();" title="Xem sơ đồ vận hành khí y tế QT.03">
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
    r'<!-- 🏥 CỔNG 4 KHOA LÂM SÀNG CHÍNH - PKĐK TÂM ANH QUẬN 7 \(CHUẨN HOÁ KHÔNG NỘI TRÚ\) -->[\s\S]*?<!-- ==================== KANBAN WORKFLOW BOARD ==================== -->',
    four_departments_hub_html + '\n\n                        <!-- ==================== KANBAN WORKFLOW BOARD ==================== -->',
    html
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Đã cập nhật toàn bộ action hooks cho 16 thẻ của 4 Khoa chính trong index.html!")

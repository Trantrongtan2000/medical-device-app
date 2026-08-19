import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
html_path = app_dir / "web" / "index.html"
js_path = app_dir / "web" / "js" / "app.js"

# 1. Update HTML chips
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

old_chips_html = """                                    <div class="chip-filter active" data-chip="all">Tất cả (1.073)</div>
                                    <div class="chip-filter" data-chip="cdha">🩺 Siêu Âm & CĐHA</div>
                                    <div class="chip-filter" data-chip="emergency">🚨 Cấp Cứu & Hồi Sức</div>
                                    <div class="chip-filter" data-chip="ro">💧 Thận Nhân Tạo RO</div>
                                    <div class="chip-filter" data-chip="highrisk">⚠️ Rủi Ro Loại C & D</div>"""

new_chips_html = """                                    <div class="chip-filter active" data-chip="all"><i class="bi bi-grid-fill me-1"></i>Tất cả (1.073)</div>
                                    <div class="chip-filter" data-chip="khambenh"><i class="bi bi-person-heart text-success me-1"></i>Khoa Khám Bệnh</div>
                                    <div class="chip-filter" data-chip="cdha"><i class="bi bi-badge-hd-fill text-primary me-1"></i>Khoa CĐHA</div>
                                    <div class="chip-filter" data-chip="nsth"><i class="bi bi-camera-video-fill text-warning me-1"></i>Khoa NSTH</div>
                                    <div class="chip-filter" data-chip="emergency"><i class="bi bi-heart-pulse-fill text-danger me-1"></i>Khoa Cấp Cứu</div>
                                    <div class="chip-filter" data-chip="highrisk"><i class="bi bi-exclamation-triangle-fill text-danger me-1"></i>Rủi Ro Loại C & D</div>"""

html = html.replace(old_chips_html, new_chips_html)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Đã cập nhật 4 Filter Chips cho 4 Khoa chính trong index.html!")

# 2. Update JS chip handler
with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

new_chip_js = """            // Quick Filter Chips for 4 Clinical Departments
            const chips = document.querySelectorAll('.chip-filter');
            chips.forEach(chip => {
                chip.addEventListener('click', () => {
                    chips.forEach(c => c.classList.remove('active'));
                    chip.classList.add('active');

                    const filterType = chip.getAttribute('data-chip');
                    const facSelect = document.getElementById('filter-facility');
                    const rSelect = document.getElementById('filter-risk');
                    const sInput = document.getElementById('search-input');

                    if (filterType === 'all') {
                        this.currentFilters.search = '';
                        this.currentFilters.risk_level = '';
                        this.currentFilters.facility = '';
                        if (facSelect) facSelect.value = '';
                    } else if (filterType === 'khambenh') {
                        this.currentFilters.search = 'Khám Bệnh';
                        this.currentFilters.risk_level = '';
                    } else if (filterType === 'cdha') {
                        this.currentFilters.search = 'Chẩn Đoán Hình Ảnh';
                        this.currentFilters.risk_level = '';
                    } else if (filterType === 'nsth') {
                        this.currentFilters.search = 'Nội Soi';
                        this.currentFilters.risk_level = '';
                    } else if (filterType === 'emergency') {
                        this.currentFilters.search = 'Cấp Cứu';
                        this.currentFilters.risk_level = '';
                    } else if (filterType === 'highrisk') {
                        this.currentFilters.search = '';
                        this.currentFilters.risk_level = 'C';
                    }
                    if (sInput) sInput.value = this.currentFilters.search;
                    if (rSelect) rSelect.value = this.currentFilters.risk_level;
                    this.loadDevices();
                });
            });"""

js = re.sub(
    r'// Quick Filter Chips\s*const chips = document\.querySelectorAll\(\'\.chip-filter\'\);[\s\S]*?this\.loadDevices\(\);\s*\}\);\s*\}\);',
    new_chip_js,
    js
)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)
print("✅ Đã cập nhật JavaScript xử lý lọc 4 Khoa chính trong app.js!")

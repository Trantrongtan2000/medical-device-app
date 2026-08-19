import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
routes_path = app_dir / "app" / "routes.py"
html_path = app_dir / "web" / "index.html"
app_js_path = app_dir / "web" / "js" / "app.js"

# ==================== 1. UPDATE APP/ROUTES.PY ====================
with open(routes_path, "r", encoding="utf-8") as f:
    routes_code = f.read()

# Replace oncall endpoints in routes_code
old_oncall_section = """@router.get("/api/oncall/schedule")
async def get_oncall_schedule(db = Depends(get_db)):
    \"\"\"Danh sách Lịch On-call TTBYT theo tuần (Thứ Hai -> Chủ Nhật)\"\"\"
    rows = db.execute("SELECT * FROM oncall_schedule ORDER BY id ASC").fetchall()
    return [dict(r) for r in rows]"""

new_oncall_section = """@router.get("/api/oncall/schedule")
async def get_oncall_schedule(
    month: Optional[int] = Query(8, description="Tháng cần xem lịch"),
    year: Optional[int] = Query(2026, description="Năm cần xem lịch"),
    db = Depends(get_db)
):
    \"\"\"Danh sách Lịch On-call TTBYT 24 giờ xếp theo tháng để sắp xếp trước\"\"\"
    query = "SELECT * FROM oncall_schedule WHERE month = ? AND year = ? ORDER BY day_num ASC"
    rows = db.execute(query, (month, year)).fetchall()
    if not rows:
        # Fallback to all if specific month not generated
        rows = db.execute("SELECT * FROM oncall_schedule ORDER BY year ASC, month ASC, day_num ASC LIMIT 31").fetchall()
    return [dict(r) for r in rows]"""

if old_oncall_section in routes_code:
    routes_code = routes_code.replace(old_oncall_section, new_oncall_section)

# Update today endpoint
old_today_endpoint = """@router.get("/api/oncall/today")
async def get_today_oncall(db = Depends(get_db)):
    \"\"\"Kỹ sư và Lãnh đạo On-call trực chính hôm nay\"\"\"
    row = db.execute("SELECT * FROM oncall_schedule WHERE status = 'TODAY' LIMIT 1").fetchone()
    if not row:
        row = db.execute("SELECT * FROM oncall_schedule ORDER BY id ASC LIMIT 1").fetchone()
    return dict(row) if row else {}"""

new_today_endpoint = """@router.get("/api/oncall/today")
async def get_today_oncall(db = Depends(get_db)):
    \"\"\"Kỹ sư và Lãnh đạo On-call 24 giờ trực chính hôm nay\"\"\"
    row = db.execute("SELECT * FROM oncall_schedule WHERE status = 'TODAY' LIMIT 1").fetchone()
    if not row:
        row = db.execute("SELECT * FROM oncall_schedule WHERE day_num = 19 AND month = 8 AND year = 2026 LIMIT 1").fetchone()
    if not row:
        row = db.execute("SELECT * FROM oncall_schedule ORDER BY id ASC LIMIT 1").fetchone()
    return dict(row) if row else {}"""

if old_today_endpoint in routes_code:
    routes_code = routes_code.replace(old_today_endpoint, new_today_endpoint)

with open(routes_path, "w", encoding="utf-8") as f:
    f.write(routes_code)
print("✅ Đã cập nhật On-call monthly backend API trong `app/routes.py`!")

# ==================== 2. UPDATE WEB/INDEX.HTML ====================
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Update tab button in sub-tabs toggle
html = html.replace(
    '<i class="bi bi-calendar-check-fill me-1"></i> Lịch On-Call 7 Ngày',
    '<i class="bi bi-calendar-month-fill me-1"></i> Lịch Xếp On-Call Tháng (24/24h)'
)

html = html.replace(
    'Bảng Lịch On-Call Tuần',
    'Lịch Xếp On-Call Theo Tháng (24h)'
)

# Update Banner Wording
html = html.replace(
    'ON-CALL HÔM NAY',
    'ON-CALL 24 GIỜ HÔM NAY'
)

html = html.replace(
    '16:30 - 07:30 sáng mai',
    '24/24 Giờ (07:30 - 07:30 sáng mai)'
)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Đã cập nhật giao diện Banner & Menu Lịch On-call 24 giờ trong `web/index.html`!")

# ==================== 3. UPDATE WEB/JS/APP.JS ====================
with open(app_js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

new_oncall_methods = """
        currentOncallMonth: 8,
        currentOncallYear: 2026,
        oncallScheduleList: [],

        async loadOncallData(month = null, year = null) {
            if (month) this.currentOncallMonth = month;
            if (year) this.currentOncallYear = year;

            try {
                // 1. Load Today Oncall
                const resToday = await fetch('/api/oncall/today');
                if (resToday.ok) {
                    const today = await resToday.json();
                    if (today.primary_engineer) {
                        const elName = document.getElementById('oncall-today-name');
                        const elBtn = document.getElementById('oncall-today-btn');
                        const elBackup = document.getElementById('oncall-backup-name');
                        const elBackupPhone = document.getElementById('oncall-backup-phone');

                        if (elName) elName.textContent = today.primary_engineer;
                        if (elBtn) {
                            elBtn.href = `tel:${today.primary_phone}`;
                            elBtn.innerHTML = `<i class="bi bi-telephone-fill me-1"></i> ${today.primary_phone}`;
                        }
                        if (elBackup) elBackup.textContent = today.backup_engineer;
                        if (elBackupPhone) elBackupPhone.innerHTML = `<i class="bi bi-telephone me-1"></i>${today.backup_phone}`;
                    }
                }

                // 2. Load Monthly Schedule
                const resSched = await fetch(`/api/oncall/schedule?month=${this.currentOncallMonth}&year=${this.currentOncallYear}`);
                if (resSched.ok) {
                    this.oncallScheduleList = await resSched.json();
                }
            } catch (err) {
                console.error('Error loading oncall data:', err);
            }
        },

        async changeOncallMonth(month, year) {
            this.currentOncallMonth = parseInt(month, 10);
            this.currentOncallYear = parseInt(year, 10);
            await this.loadOncallData(this.currentOncallMonth, this.currentOncallYear);
            this.renderOncallSchedule();
        },

        renderOncallSchedule() {
            const container = document.getElementById('staff-grid-container');
            const countLabel = document.getElementById('staff-count-label');
            if (countLabel) countLabel.textContent = `Lịch Xếp On-Call 24 Giờ Tháng ${this.currentOncallMonth}/${this.currentOncallYear} (${this.oncallScheduleList.length} Ngày)`;
            if (!container) return;

            const completedCount = this.oncallScheduleList.filter(s => s.status === 'COMPLETED').length;
            const scheduledCount = this.oncallScheduleList.filter(s => s.status === 'SCHEDULED' || s.status === 'TODAY').length;

            container.innerHTML = `
                <!-- Month Selector & Controls -->
                <div class="col-12 mb-2">
                    <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 p-3 bg-light rounded border shadow-sm">
                        <div class="d-flex align-items-center gap-2">
                            <span class="fw-bold text-dark"><i class="bi bi-calendar3 me-1 text-primary"></i>Chọn Tháng Xếp Lịch:</span>
                            <select class="form-select form-select-sm font-mono fw-bold" style="width: auto;" onchange="app.changeOncallMonth(this.value.split('-')[0], this.value.split('-')[1])">
                                <option value="8-2026" ${this.currentOncallMonth === 8 ? 'selected' : ''}>Tháng 08/2026 (Hiện tại - 31 ngày)</option>
                                <option value="9-2026" ${this.currentOncallMonth === 9 ? 'selected' : ''}>Tháng 09/2026 (Kế hoạch - 30 ngày)</option>
                                <option value="10-2026" ${this.currentOncallMonth === 10 ? 'selected' : ''}>Tháng 10/2026 (Kế hoạch - 31 ngày)</option>
                            </select>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <span class="badge bg-secondary font-mono"><i class="bi bi-check2-circle me-1"></i>Đã xong: ${completedCount} ca</span>
                            <span class="badge bg-primary font-mono"><i class="bi bi-clock-history me-1"></i>Sắp tới: ${scheduledCount} ca</span>
                            <span class="badge bg-success font-mono"><i class="bi bi-shield-check me-1"></i>Bảo đảm 24/24h</span>
                        </div>
                    </div>
                </div>

                <!-- Monthly Schedule Table -->
                <div class="col-12">
                    <div class="clinical-card p-0 overflow-hidden shadow-sm">
                        <div class="table-responsive" style="max-height: 600px; overflow-y: auto;">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light sticky-top shadow-sm" style="z-index: 10;">
                                    <tr>
                                        <th class="ps-3" style="width: 130px;">NGÀY / THỨ</th>
                                        <th>KỸ SƯ ON-CALL CHÍNH (24H)</th>
                                        <th>KỸ SƯ DỰ PHÒNG (BACKUP)</th>
                                        <th>LÃNH ĐẠO TRỰC</th>
                                        <th>KHUNG GIỜ</th>
                                        <th>TRẠNG THÁI</th>
                                        <th>GHI CHÚ</th>
                                        <th class="text-end pe-3">THAO TÁC</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${this.oncallScheduleList.map(s => {
                                        const isToday = s.status === 'TODAY';
                                        const isWeekend = s.day_name === 'Thứ Bảy' || s.day_name === 'Chủ Nhật';
                                        let rowClass = '';
                                        if (isToday) rowClass = 'table-warning bg-opacity-50 fw-semibold';
                                        else if (isWeekend) rowClass = 'table-light bg-opacity-75';

                                        let statusBadge = '<span class="badge bg-light text-dark border">Kế hoạch</span>';
                                        if (isToday) statusBadge = '<span class="badge bg-danger pulse-emergency"><i class="bi bi-broadcast-pin me-1"></i>ĐANG TRỰC HÔM NAY</span>';
                                        else if (s.status === 'COMPLETED') statusBadge = '<span class="badge bg-secondary">Đã xong</span>';

                                        return `
                                            <tr class="${rowClass}">
                                                <td class="ps-3">
                                                    <strong class="${isWeekend ? 'text-danger' : 'text-dark'}">${s.date_str}</strong>
                                                    <div class="small ${isWeekend ? 'text-danger fw-bold' : 'text-muted'}">${s.day_name}</div>
                                                </td>
                                                <td>
                                                    <div class="d-flex align-items-center gap-2">
                                                        <div class="rounded-circle text-white d-flex align-items-center justify-content-center fw-bold shadow-sm" 
                                                             style="width: 32px; height: 32px; font-size: 0.85rem; background: ${isToday ? '#dc2626' : '#0284c7'};">
                                                            ${s.primary_engineer.charAt(0)}
                                                        </div>
                                                        <div>
                                                            <strong class="text-dark d-block">${s.primary_engineer}</strong>
                                                            <a href="tel:${s.primary_phone}" class="small font-mono text-primary">${s.primary_phone}</a>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>
                                                    <strong class="text-dark d-block">${s.backup_engineer}</strong>
                                                    <a href="tel:${s.backup_phone}" class="small font-mono text-muted">${s.backup_phone}</a>
                                                </td>
                                                <td>
                                                    <span class="text-dark small">${s.leader_oncall}</span>
                                                </td>
                                                <td>
                                                    <span class="badge bg-light text-dark border font-mono">24/24 Giờ</span>
                                                </td>
                                                <td>${statusBadge}</td>
                                                <td class="small text-muted" style="max-width: 200px;">
                                                    ${s.notes || '-'}
                                                </td>
                                                <td class="text-end pe-3">
                                                    <button class="btn btn-sm btn-outline-primary btn-clinical fw-semibold" onclick="app.openEditOncallModal(${s.id})">
                                                        <i class="bi bi-pencil-square me-1"></i> Đổi Ca
                                                    </button>
                                                </td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        },
"""

# Replace old oncall methods in app.js
if "currentOncallMonth: 8," not in js_code:
    js_code = js_code.replace("oncallScheduleList: [],", new_oncall_methods)
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print("✅ Đã tích hợp Monthly On-call Planner Engine vào `web/js/app.js`!")

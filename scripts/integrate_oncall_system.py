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

oncall_endpoints = """
# ==================== ON-CALL SCHEDULE MANAGEMENT ====================

class OncallScheduleUpdate(BaseModel):
    primary_engineer: Optional[str] = None
    primary_phone: Optional[str] = None
    backup_engineer: Optional[str] = None
    backup_phone: Optional[str] = None
    leader_oncall: Optional[str] = None
    time_window: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

@router.get("/api/oncall/schedule")
async def get_oncall_schedule(db = Depends(get_db)):
    \"\"\"Danh sách Lịch On-call TTBYT theo tuần (Thứ Hai -> Chủ Nhật)\"\"\"
    rows = db.execute("SELECT * FROM oncall_schedule ORDER BY id ASC").fetchall()
    return [dict(r) for r in rows]

@router.get("/api/oncall/today")
async def get_today_oncall(db = Depends(get_db)):
    \"\"\"Kỹ sư và Lãnh đạo On-call trực chính hôm nay\"\"\"
    row = db.execute("SELECT * FROM oncall_schedule WHERE status = 'TODAY' LIMIT 1").fetchone()
    if not row:
        row = db.execute("SELECT * FROM oncall_schedule ORDER BY id ASC LIMIT 1").fetchone()
    return dict(row) if row else {}

@router.put("/api/oncall/schedule/{sched_id}")
async def update_oncall_schedule(sched_id: int, req: OncallScheduleUpdate, db = Depends(get_db)):
    \"\"\"Chỉnh sửa phân công ca trực On-call TTBYT\"\"\"
    row = db.execute("SELECT * FROM oncall_schedule WHERE id = ?", (sched_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy lịch on-call")
    fields = []
    params = []
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None:
            fields.append(f"{k} = ?")
            params.append(v)
    if fields:
        params.append(sched_id)
        db.execute(f"UPDATE oncall_schedule SET {', '.join(fields)} WHERE id = ?", params)
        db.commit()
    return {"status": "success", "message": f"Đã cập nhật lịch On-call cho {row['day_name']} thành công!"}
"""

if "get_oncall_schedule" not in routes_code:
    routes_code += "\n\n" + oncall_endpoints
    with open(routes_path, "w", encoding="utf-8") as f:
        f.write(routes_code)
    print("✅ Đã chèn On-call API endpoints vào `app/routes.py`!")

# ==================== 2. UPDATE WEB/INDEX.HTML ====================
with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Update sidebar badge
html = html.replace('id="badge-staff-count">6 KS</span>', 'id="badge-staff-count">6 KS (Q7)</span>')
html = html.replace('id="badge-staff-count">11 KS</span>', 'id="badge-staff-count">6 KS (Q7)</span>')

# Replace the entire #tab-staff content with the new Q7 Staff & On-call schedule layout
old_tab_staff_start = '<div class="tab-pane fade" id="tab-staff" role="tabpanel">'
old_tab_staff_end = '<div class="tab-pane fade" id="tab-suppliers" role="tabpanel">'

new_tab_staff_content = """                    <!-- ==================== 👨‍⚕️ TAB: NHÂN SỰ & LỊCH ON-CALL TTBYT QUẬN 7 ==================== -->
                    <div class="tab-pane fade" id="tab-staff" role="tabpanel">
                        <!-- Header Banner -->
                        <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-4">
                            <div>
                                <h4 class="fw-bold mb-1 text-dark">
                                    <i class="bi bi-people-fill text-primary me-2"></i>Nhân Sự & Lịch On-Call Phòng Trang Thiết Bị Y Tế Quận 7
                                </h4>
                                <p class="text-muted small mb-0">
                                    Đội ngũ <strong>6 nhân sự chính thức Phòng TTBYT Quận 7</strong> & Lịch phân công On-call xử lý sự cố khẩn cấp 24/7
                                </p>
                            </div>
                            <div class="d-flex gap-2">
                                <button class="btn btn-outline-primary btn-clinical fw-semibold" onclick="app.switchStaffView('oncall')">
                                    <i class="bi bi-calendar-week-fill me-1"></i> Bảng Lịch On-Call Tuần
                                </button>
                                <button class="btn btn-primary btn-clinical fw-bold shadow-sm" data-bs-toggle="modal" data-bs-target="#createStaffModal">
                                    <i class="bi bi-person-plus-fill me-1"></i> Thêm Nhân Sự
                                </button>
                            </div>
                        </div>

                        <!-- 🌟 ON-CALL KPI BANNER (ĐIỀU HÀNH TRỰC KHẨN CẤP HÔM NAY) -->
                        <div class="card border-0 shadow-sm mb-4" style="border-radius: 14px; background: linear-gradient(135deg, #090d16 0%, #1e293b 100%); color: #fff;">
                            <div class="card-body p-4">
                                <div class="row g-3 align-items-center">
                                    <div class="col-12 col-lg-3 border-end border-secondary border-opacity-50">
                                        <span class="badge bg-danger text-uppercase font-mono px-2 py-1 mb-2">
                                            <i class="bi bi-broadcast-pin me-1"></i> ON-CALL HÔM NAY
                                        </span>
                                        <h5 class="fw-bold mb-1 text-white" id="oncall-today-name">Trần Đăng Hiếu</h5>
                                        <div class="text-info small font-mono mb-2" id="oncall-today-time">16:30 - 07:30 sáng mai</div>
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
                        </div>

                        <!-- Sub-tabs Toggle: 1. Nhân Sự Q7 (6) | 2. Lịch On-Call | 3. Lãnh Đạo Khoa (7) | 4. Hãng NCC (45) -->
                        <div class="clinical-card p-3 mb-4">
                            <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 mb-3 border-bottom pb-2">
                                <div class="btn-group btn-group-sm" role="group" id="staff-directory-view-toggle">
                                    <button type="button" class="btn btn-primary fw-bold btn-clinical" id="btn-view-bme-staff" onclick="app.switchStaffView('bme')">
                                        <i class="bi bi-people-fill me-1"></i> Nhân Sự TTBYT Q7 (6 Người)
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary fw-semibold btn-clinical" id="btn-view-oncall" onclick="app.switchStaffView('oncall')">
                                        <i class="bi bi-calendar-check-fill me-1"></i> Lịch On-Call 7 Ngày
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary fw-semibold btn-clinical" id="btn-view-leaders" onclick="app.switchStaffView('leaders')">
                                        <i class="bi bi-person-badge me-1"></i> Lãnh Đạo & Trưởng Khoa (7)
                                    </button>
                                    <button type="button" class="btn btn-outline-secondary fw-semibold btn-clinical" id="btn-view-suppliers-contacts" onclick="app.switchStaffView('suppliers')">
                                        <i class="bi bi-building me-1"></i> Kỹ Sư Hãng & NCC (45)
                                    </button>
                                </div>
                                <span class="small text-muted font-mono" id="staff-count-label">Phòng Trang Thiết Bị Y Tế Quận 7</span>
                            </div>

                            <div class="row g-2 align-items-center">
                                <div class="col-12 col-md-6">
                                    <div class="input-group input-group-sm">
                                        <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                                        <input type="text" id="staff-search-input" class="form-control border-start-0" placeholder="Tìm theo tên kỹ sư, chuyên môn, số điện thoại...">
                                    </div>
                                </div>
                                <div class="col-6 col-md-3">
                                    <select id="staff-status-filter" class="form-select form-select-sm">
                                        <option value="">-- Tất cả 6 nhân sự Q7 --</option>
                                        <option value="ONCALL_TODAY">On-call Hôm Nay</option>
                                        <option value="AVAILABLE">Sẵn Sàng Hỗ Trợ</option>
                                    </select>
                                </div>
                                <div class="col-6 col-md-3 text-end">
                                    <span class="badge bg-success font-mono p-2">
                                        <i class="bi bi-check-circle-fill me-1"></i> Đội Ngũ Q7 Sẵn Sàng 100%
                                    </span>
                                </div>
                            </div>
                        </div>

                        <!-- Dynamic Staff / On-call Grid Container -->
                        <div class="row g-3" id="staff-grid-container">
                            <div class="col-12 text-center py-5">
                                <div class="spinner-border text-primary" role="status"></div>
                                <div class="small text-muted mt-2">Đang tải dữ liệu nhân sự & lịch on-call...</div>
                            </div>
                        </div>
                    </div>
"""

# Replace tab-staff pane
if old_tab_staff_start in html:
    idx_start = html.find(old_tab_staff_start)
    idx_end = html.find(old_tab_staff_end)
    if idx_start != -1 and idx_end != -1:
        html = html[:idx_start] + new_tab_staff_content + "\n                    " + html[idx_end:]
        print("✅ Đã thay thế thành công Tab Nhân Sự & Lịch On-call Quận 7 trong `web/index.html`!")

# Add Modal Edit Oncall Schedule
edit_oncall_modal_html = """
    <!-- ==================== MODAL: ĐIỀU CHỈNH PHÂN CÔNG LỊCH ON-CALL ==================== -->
    <div class="modal fade" id="editOncallModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-primary text-white px-4 py-3 border-0">
                    <h5 class="modal-title fw-bold"><i class="bi bi-calendar-event me-2"></i>Điều Chỉnh Phân Công Lịch On-Call</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <form id="editOncallForm">
                        <input type="hidden" id="oncall-edit-id">
                        <div class="p-2 mb-3 bg-light rounded border">
                            <span class="small text-muted d-block">Ca trực ngày:</span>
                            <strong class="text-dark" id="oncall-edit-day">Thứ Ba (19/08/2026)</strong>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">KỸ SƯ ON-CALL CHÍNH (*)</label>
                            <select id="oncall-edit-primary" class="form-select form-select-sm" required>
                                <option value="Nguyễn Quốc Việt">Nguyễn Quốc Việt (0902.769.710)</option>
                                <option value="Nguyễn Tấn Lợi">Nguyễn Tấn Lợi (0779.798.786)</option>
                                <option value="Trần Đăng Hiếu">Trần Đăng Hiếu (0888.536.278)</option>
                                <option value="Lê Minh Thiện">Lê Minh Thiện (0378.716.561)</option>
                                <option value="Trần Thị Ngọc Châu">Trần Thị Ngọc Châu (0335.802.380)</option>
                                <option value="Trần Trọng Tấn">Trần Trọng Tấn (0334.968.114)</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">KỸ SƯ ON-CALL DỰ PHÒNG (BACKUP) (*)</label>
                            <select id="oncall-edit-backup" class="form-select form-select-sm" required>
                                <option value="Trần Trọng Tấn">Trần Trọng Tấn (0334.968.114)</option>
                                <option value="Trần Đăng Hiếu">Trần Đăng Hiếu (0888.536.278)</option>
                                <option value="Nguyễn Tấn Lợi">Nguyễn Tấn Lợi (0779.798.786)</option>
                                <option value="Lê Minh Thiện">Lê Minh Thiện (0378.716.561)</option>
                                <option value="Trần Thị Ngọc Châu">Trần Thị Ngọc Châu (0335.802.380)</option>
                                <option value="Nguyễn Quốc Việt">Nguyễn Quốc Việt (0902.769.710)</option>
                            </select>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">KHUNG GIỜ ON-CALL</label>
                            <input type="text" id="oncall-edit-time" class="form-control form-control-sm font-mono" value="16:30 - 07:30 sáng hôm sau">
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">GHI CHÚ CA TRỰC</label>
                            <textarea id="oncall-edit-notes" class="form-control form-control-sm" rows="2" placeholder="Ghi chú sự cố cần lưu ý, phân công khoa phòng..."></textarea>
                        </div>
                        <div class="d-flex justify-content-end gap-2 pt-3 border-top">
                            <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Hủy</button>
                            <button type="submit" class="btn btn-primary btn-clinical fw-bold shadow-sm">
                                <i class="bi bi-check-lg me-1"></i> Cập Nhật Lịch On-Call
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
"""

if 'id="editOncallModal"' not in html:
    html = html.replace('</body>', edit_oncall_modal_html + '\n</body>')
    print("✅ Đã chèn `#editOncallModal` vào `web/index.html`!")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

# ==================== 3. UPDATE WEB/JS/APP.JS ====================
with open(app_js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

oncall_frontend_methods = """
        oncallScheduleList: [],

        async loadOncallData() {
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

                // 2. Load Weekly Schedule
                const resSched = await fetch('/api/oncall/schedule');
                if (resSched.ok) {
                    this.oncallScheduleList = await resSched.json();
                }
            } catch (err) {
                console.error('Error loading oncall data:', err);
            }
        },

        renderOncallSchedule() {
            const container = document.getElementById('staff-grid-container');
            const countLabel = document.getElementById('staff-count-label');
            if (countLabel) countLabel.textContent = `Bảng Lịch On-Call 7 Ngày Trong Tuần`;
            if (!container) return;

            container.innerHTML = `
                <div class="col-12">
                    <div class="clinical-card p-0 overflow-hidden shadow-sm">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th class="ps-3">THỨ / NGÀY</th>
                                        <th>KỸ SƯ ON-CALL CHÍNH</th>
                                        <th>KỸ SƯ DỰ PHÒNG (BACKUP)</th>
                                        <th>LÃNH ĐẠO TRỰC</th>
                                        <th>KHUNG GIỜ</th>
                                        <th>TRẠNG THÁI</th>
                                        <th class="text-end pe-3">THAO TÁC</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${this.oncallScheduleList.map(s => {
                                        const isToday = s.status === 'TODAY';
                                        const rowClass = isToday ? 'table-warning bg-opacity-25' : '';
                                        const statusBadge = isToday 
                                            ? '<span class="badge bg-danger"><i class="bi bi-broadcast-pin me-1"></i>ĐANG TRỰC HÔM NAY</span>'
                                            : (s.status === 'COMPLETED' ? '<span class="badge bg-secondary">Đã xong</span>' : '<span class="badge bg-light text-dark border">Theo kế hoạch</span>');

                                        return `
                                            <tr class="${rowClass}">
                                                <td class="ps-3">
                                                    <strong class="text-dark">${s.day_name}</strong>
                                                    <div class="small font-mono text-muted">${s.date_str}</div>
                                                </td>
                                                <td>
                                                    <div class="d-flex align-items-center gap-2">
                                                        <div class="rounded-circle text-white d-flex align-items-center justify-content-center fw-bold" style="width: 32px; height: 32px; font-size: 0.85rem; background: #0284c7;">
                                                            ${s.primary_engineer.charAt(0)}
                                                        </div>
                                                        <div>
                                                            <strong class="text-dark">${s.primary_engineer}</strong>
                                                            <a href="tel:${s.primary_phone}" class="small font-mono text-primary d-block">${s.primary_phone}</a>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>
                                                    <strong class="text-dark">${s.backup_engineer}</strong>
                                                    <a href="tel:${s.backup_phone}" class="small font-mono text-muted d-block">${s.backup_phone}</a>
                                                </td>
                                                <td>
                                                    <span class="text-dark small">${s.leader_oncall}</span>
                                                </td>
                                                <td>
                                                    <span class="badge bg-light text-dark border font-mono">${s.time_window}</span>
                                                </td>
                                                <td>${statusBadge}</td>
                                                <td class="text-end pe-3">
                                                    <button class="btn btn-sm btn-outline-primary btn-clinical" onclick="app.openEditOncallModal(${s.id})">
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

        openEditOncallModal(id) {
            const sched = this.oncallScheduleList.find(s => s.id === id);
            if (!sched) return;

            document.getElementById('oncall-edit-id').value = sched.id;
            document.getElementById('oncall-edit-day').textContent = `${sched.day_name} (${sched.date_str})`;
            document.getElementById('oncall-edit-primary').value = sched.primary_engineer;
            document.getElementById('oncall-edit-backup').value = sched.backup_engineer;
            document.getElementById('oncall-edit-time').value = sched.time_window || '16:30 - 07:30 sáng hôm sau';
            document.getElementById('oncall-edit-notes').value = sched.notes || '';

            const modal = new bootstrap.Modal(document.getElementById('editOncallModal'));
            modal.show();
        },

        setupOncallEditForm() {
            const form = document.getElementById('editOncallForm');
            form?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const id = document.getElementById('oncall-edit-id').value;
                const primary = document.getElementById('oncall-edit-primary').value;
                const backup = document.getElementById('oncall-edit-backup').value;

                // Map phone numbers
                const phoneMap = {
                    "Nguyễn Quốc Việt": "0902769710",
                    "Nguyễn Tấn Lợi": "0779798786",
                    "Trần Đăng Hiếu": "0888536278",
                    "Lê Minh Thiện": "0378716561",
                    "Trần Thị Ngọc Châu": "0335802380",
                    "Trần Trọng Tấn": "0334968114"
                };

                const payload = {
                    primary_engineer: primary,
                    primary_phone: phoneMap[primary] || "",
                    backup_engineer: backup,
                    backup_phone: phoneMap[backup] || "",
                    time_window: document.getElementById('oncall-edit-time').value.trim(),
                    notes: document.getElementById('oncall-edit-notes').value.trim()
                };

                try {
                    const res = await fetch(`/api/oncall/schedule/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi cập nhật lịch On-call');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('editOncallModal'))?.hide();
                    await this.loadOncallData();
                    this.renderOncallSchedule();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });
        },
"""

# Update switchStaffView to support 'oncall'
js_code = js_code.replace(
    "if (viewType === 'bme') {",
    "if (viewType === 'oncall') {\n                this.renderOncallSchedule();\n            } else if (viewType === 'bme') {"
)

js_code = js_code.replace(
    "const btnSuppliers = document.getElementById('btn-view-suppliers-contacts');",
    "const btnSuppliers = document.getElementById('btn-view-suppliers-contacts');\n            const btnOncall = document.getElementById('btn-view-oncall');"
)

js_code = js_code.replace(
    "[btnBme, btnLeaders, btnSuppliers].forEach(btn => {",
    "[btnBme, btnOncall, btnLeaders, btnSuppliers].forEach(btn => {"
)

js_code = js_code.replace(
    "if (viewType === 'suppliers' && btnSuppliers) btnSuppliers.className = 'btn btn-primary fw-bold btn-clinical';",
    "if (viewType === 'suppliers' && btnSuppliers) btnSuppliers.className = 'btn btn-primary fw-bold btn-clinical';\n            if (viewType === 'oncall' && btnOncall) btnOncall.className = 'btn btn-primary fw-bold btn-clinical';"
)

if "loadOncallData()" not in js_code:
    js_code = js_code.replace("this.loadStaff();", "this.loadStaff();\n            this.loadOncallData();")
    js_code = js_code.replace("this.setupDirectoryEditForms();", "this.setupDirectoryEditForms();\n            this.setupOncallEditForm();")
    js_code = js_code.replace("setupFormSubmissions() {", oncall_frontend_methods + "\n        setupFormSubmissions() {")
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print("✅ Đã gắn On-call engine vào `web/js/app.js`!")

# ==================== 4. UPDATE TESTS/TEST_API.PY ====================
with open(app_dir / "tests" / "test_api.py", "r", encoding="utf-8") as f:
    test_code = f.read()

oncall_test = """
def test_oncall_schedule_endpoints():
    # 1. Test GET /api/oncall/schedule
    res = client.get("/api/oncall/schedule")
    assert res.status_code == 200
    sched = res.json()
    assert isinstance(sched, list)
    assert len(sched) == 7
    assert any(s["primary_engineer"] == "Trần Đăng Hiếu" for s in sched)

    # 2. Test GET /api/oncall/today
    res_today = client.get("/api/oncall/today")
    assert res_today.status_code == 200
    today = res_today.json()
    assert "primary_engineer" in today
"""

if "test_oncall_schedule_endpoints" not in test_code:
    test_code += "\n\n" + oncall_test
    with open(app_dir / "tests" / "test_api.py", "w", encoding="utf-8") as f:
        f.write(test_code)
    print("✅ Đã bổ sung On-call automated tests vào `tests/test_api.py`!")

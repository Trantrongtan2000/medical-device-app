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

quick_assign_api = """
class QuickAssignWeeklyRequest(BaseModel):
    month: int
    year: int
    assign_mode: str = "AUTO_MONTH" # "AUTO_MONTH", "SPECIFIC_WEEK", "CUSTOM_RANGE"
    start_engineer: str = "Trần Trọng Tấn" # "Trần Trọng Tấn", "Lê Minh Thiện", "Trần Đăng Hiếu"
    start_day: Optional[int] = None
    end_day: Optional[int] = None
    target_engineer: Optional[str] = None
    backup_engineer: Optional[str] = None

@router.post("/api/oncall/quick-assign-weekly")
async def quick_assign_weekly_oncall(req: QuickAssignWeeklyRequest, db = Depends(get_db)):
    \"\"\"Chỉnh nhanh phân công lịch On-call 1 tuần cho 3 nhân sự chính: Tấn, Thiện, Hiếu\"\"\"
    engineers_map = {
        "Trần Trọng Tấn": "0334968114",
        "Lê Minh Thiện": "0378716561",
        "Trần Đăng Hiếu": "0888536278",
        "Nguyễn Tấn Lợi": "0779798786",
        "Nguyễn Quốc Việt": "0902769710",
        "Trần Thị Ngọc Châu": "0335802380"
    }
    
    order = ["Trần Trọng Tấn", "Lê Minh Thiện", "Trần Đăng Hiếu"]
    
    if req.assign_mode == "AUTO_MONTH":
        # Start rotating 3 engineers week-by-week
        rows = db.execute("SELECT id, day_num, day_name, date_str FROM oncall_schedule WHERE month = ? AND year = ? ORDER BY day_num ASC", (req.month, req.year)).fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="Chưa có dữ liệu tháng này")
        
        # Start index
        start_idx = 0
        if req.start_engineer in order:
            start_idx = order.index(req.start_engineer)
            
        cur_idx = start_idx
        for r in rows:
            d_id = r["id"]
            d_name = r["day_name"]
            
            # Switch engineer every Monday
            if d_name == "Thứ Hai" and r["day_num"] > 1:
                cur_idx = (cur_idx + 1) % len(order)
                
            prim = order[cur_idx]
            back = order[(cur_idx + 1) % len(order)]
            
            db.execute(\"\"\"
                UPDATE oncall_schedule
                SET primary_engineer = ?, primary_phone = ?, backup_engineer = ?, backup_phone = ?, notes = ?
                WHERE id = ?
            \"\"\", (prim, engineers_map.get(prim, ""), back, engineers_map.get(back, ""), f"Phân công nhanh tuần (On-call 24h {prim})", d_id))
            
        db.commit()
        return {"status": "success", "message": f"Đã tự động xếp lịch On-call 24h trọn Tháng {req.month}/{req.year} xoay vòng theo 3 kỹ sư: Tấn -> Thiện -> Hiếu!"}

    elif req.assign_mode == "CUSTOM_RANGE":
        if not req.start_day or not req.end_day or not req.target_engineer:
            raise HTTPException(status_code=400, detail="Thiếu thông tin khoảng ngày hoặc kỹ sư")
            
        prim = req.target_engineer
        back = req.backup_engineer or order[(order.index(prim) + 1) % len(order)] if prim in order else "Trần Đăng Hiếu"
        
        db.execute(\"\"\"
            UPDATE oncall_schedule
            SET primary_engineer = ?, primary_phone = ?, backup_engineer = ?, backup_phone = ?, notes = ?
            WHERE month = ? AND year = ? AND day_num >= ? AND day_num <= ?
        \"\"\", (prim, engineers_map.get(prim, ""), back, engineers_map.get(back, ""), f"Chỉnh nhanh trọn tuần cho {prim}", req.month, req.year, req.start_day, req.end_day))
        
        db.commit()
        return {"status": "success", "message": f"Đã gán trọn ca (Ngày {req.start_day:02d} -> {req.end_day:02d}/{req.month:02d}) cho KS. {prim} thành công!"}

    return {"status": "success", "message": "Thao tác thành công"}
"""

if "quick_assign_weekly_oncall" not in routes_code:
    routes_code += "\n\n" + quick_assign_api
    with open(routes_path, "w", encoding="utf-8") as f:
        f.write(routes_code)
    print("✅ Đã chèn `POST /api/oncall/quick-assign-weekly` vào `app/routes.py`!")

# ==================== 2. UPDATE WEB/INDEX.HTML ====================
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

# Add Quick Assign Button to the Top Bar
quick_btn = """<button class="btn btn-warning text-dark btn-clinical fw-bold shadow-sm" onclick="app.openQuickAssignModal()">
                                    <i class="bi bi-lightning-charge-fill me-1"></i> Chỉnh Nhanh Tuần (Tấn - Thiện - Hiếu)
                                </button>
                                <button class="btn btn-outline-primary btn-clinical fw-semibold" onclick="app.switchStaffView('oncall')">"""

if 'onclick="app.openQuickAssignModal()"' not in html_code:
    html_code = html_code.replace(
        '<button class="btn btn-outline-primary btn-clinical fw-semibold" onclick="app.switchStaffView(\'oncall\')">',
        quick_btn
    )
    print("✅ Đã thêm nút bấm 'Chỉnh Nhanh Tuần' vào thanh công cụ `web/index.html`!")

# Add Modal Quick Assign
quick_assign_modal_html = """
    <!-- ==================== MODAL: CHỈNH NHANH LỊCH ON-CALL THEO TUẦN (3 NHÂN SỰ TẤN / THIỆN / HIẾU) ==================== -->
    <div class="modal fade" id="quickAssignWeeklyOncallModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-warning text-dark px-4 py-3 border-0">
                    <h5 class="modal-title fw-bold"><i class="bi bi-lightning-charge-fill me-2"></i>Chỉnh Nhanh Phân Công On-Call Theo Tuần</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <div class="alert alert-warning d-flex align-items-center gap-2 mb-3 py-2 small">
                        <i class="bi bi-info-circle-fill fs-5"></i>
                        <div><strong>Quy tắc On-call Q7:</strong> 3 nhân sự chính (<strong>Tấn, Thiện, Hiếu</strong>) sẽ luân phiên trực On-call 24/24h <strong>trọn 1 tuần</strong> (Thứ 2 đến CN).</div>
                    </div>

                    <form id="quickAssignWeeklyForm">
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">CHỌN PHƯƠNG THỨC XẾP NHANH</label>
                            <select id="quick-assign-mode" class="form-select form-select-sm" onchange="app.toggleQuickAssignMode(this.value)">
                                <option value="AUTO_MONTH">1 Click: Tự động xếp xoay vòng 3 KS trọn cả tháng (Tấn -> Thiện -> Hiếu)</option>
                                <option value="CUSTOM_RANGE">Gán 1 tuần / khoảng ngày cụ thể cho 1 Kỹ sư</option>
                            </select>
                        </div>

                        <div id="quick-auto-month-options">
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-dark">KỸ SƯ TRỰC TUẦN ĐẦU TIÊN CỦA THÁNG (*)</label>
                                <select id="quick-start-engineer" class="form-select form-select-sm font-mono fw-bold">
                                    <option value="Trần Trọng Tấn">KS. Trần Trọng Tấn (Tuần 1: Tấn -> Tuần 2: Thiện -> Tuần 3: Hiếu)</option>
                                    <option value="Lê Minh Thiện">KS. Lê Minh Thiện (Tuần 1: Thiện -> Tuần 2: Hiếu -> Tuần 3: Tấn)</option>
                                    <option value="Trần Đăng Hiếu">KS. Trần Đăng Hiếu (Tuần 1: Hiếu -> Tuần 2: Tấn -> Tuần 3: Thiện)</option>
                                </select>
                            </div>
                        </div>

                        <div id="quick-custom-range-options" class="d-none">
                            <div class="row g-2 mb-3">
                                <div class="col-6">
                                    <label class="form-label small fw-bold text-dark">TỪ NGÀY</label>
                                    <input type="number" id="quick-start-day" class="form-control form-control-sm" min="1" max="31" value="1">
                                </div>
                                <div class="col-6">
                                    <label class="form-label small fw-bold text-dark">ĐẾN NGÀY</label>
                                    <input type="number" id="quick-end-day" class="form-control form-control-sm" min="1" max="31" value="7">
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-dark">KỸ SƯ ON-CALL CHÍNH (24H)</label>
                                <select id="quick-target-engineer" class="form-select form-select-sm font-mono fw-bold">
                                    <option value="Trần Trọng Tấn">KS. Trần Trọng Tấn (0334.968.114)</option>
                                    <option value="Lê Minh Thiện">KS. Lê Minh Thiện (0378.716.561)</option>
                                    <option value="Trần Đăng Hiếu">KS. Trần Đăng Hiếu (0888.536.278)</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold text-dark">KỸ SƯ DỰ PHÒNG (BACKUP)</label>
                                <select id="quick-backup-engineer" class="form-select form-select-sm font-mono">
                                    <option value="Trần Đăng Hiếu">KS. Trần Đăng Hiếu (0888.536.278)</option>
                                    <option value="Trần Trọng Tấn">KS. Trần Trọng Tấn (0334.968.114)</option>
                                    <option value="Lê Minh Thiện">KS. Lê Minh Thiện (0378.716.561)</option>
                                </select>
                            </div>
                        </div>

                        <div class="d-flex justify-content-end gap-2 pt-3 border-top">
                            <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Hủy</button>
                            <button type="submit" class="btn btn-warning text-dark btn-clinical fw-bold shadow-sm">
                                <i class="bi bi-lightning-charge-fill me-1"></i> Áp Dụng Xếp Lịch Nhanh
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
"""

if 'id="quickAssignWeeklyOncallModal"' not in html_code:
    html_code = html_code.replace('</body>', quick_assign_modal_html + '\n</body>')
    print("✅ Đã chèn `#quickAssignWeeklyOncallModal` vào `web/index.html`!")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_code)

# ==================== 3. UPDATE WEB/JS/APP.JS ====================
with open(app_js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

quick_assign_js = """
        openQuickAssignModal() {
            const modal = new bootstrap.Modal(document.getElementById('quickAssignWeeklyOncallModal'));
            modal.show();
        },

        toggleQuickAssignMode(mode) {
            const autoOpt = document.getElementById('quick-auto-month-options');
            const customOpt = document.getElementById('quick-custom-range-options');
            if (mode === 'AUTO_MONTH') {
                autoOpt?.classList.remove('d-none');
                customOpt?.classList.add('d-none');
            } else {
                autoOpt?.classList.add('d-none');
                customOpt?.classList.remove('d-none');
            }
        },

        setupQuickAssignForm() {
            const form = document.getElementById('quickAssignWeeklyForm');
            form?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const mode = document.getElementById('quick-assign-mode').value;
                const payload = {
                    month: this.currentOncallMonth || 8,
                    year: this.currentOncallYear || 2026,
                    assign_mode: mode,
                    start_engineer: document.getElementById('quick-start-engineer').value,
                    start_day: parseInt(document.getElementById('quick-start-day').value || 1, 10),
                    end_day: parseInt(document.getElementById('quick-end-day').value || 7, 10),
                    target_engineer: document.getElementById('quick-target-engineer').value,
                    backup_engineer: document.getElementById('quick-backup-engineer').value
                };

                try {
                    const res = await fetch('/api/oncall/quick-assign-weekly', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi xếp lịch nhanh');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('quickAssignWeeklyOncallModal'))?.hide();
                    await this.loadOncallData(this.currentOncallMonth, this.currentOncallYear);
                    this.renderOncallSchedule();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });
        },
"""

if "setupQuickAssignForm" not in js_code:
    js_code = js_code.replace("this.setupOncallEditForm();", "this.setupOncallEditForm();\n            this.setupQuickAssignForm();")
    js_code = js_code.replace("setupFormSubmissions() {", quick_assign_js + "\n        setupFormSubmissions() {")
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print("✅ Đã tích hợp Quick-Assign Weekly Engine vào `web/js/app.js`!")

# ==================== 4. UPDATE TEST_API.PY ====================
test_path = app_dir / "tests" / "test_api.py"
with open(test_path, "r", encoding="utf-8") as f:
    t_code = f.read()

quick_test = """
def test_quick_assign_weekly_endpoint():
    payload = {
        "month": 8,
        "year": 2026,
        "assign_mode": "AUTO_MONTH",
        "start_engineer": "Trần Trọng Tấn"
    }
    res = client.post("/api/oncall/quick-assign-weekly", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
"""

if "test_quick_assign_weekly_endpoint" not in t_code:
    t_code += "\n\n" + quick_test
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(t_code)
    print("✅ Đã bổ sung bài test `test_quick_assign_weekly_endpoint` vào `tests/test_api.py`!")

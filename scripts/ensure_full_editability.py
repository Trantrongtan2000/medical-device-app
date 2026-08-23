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

# Expand BMEStaffUpdate model
routes_code = routes_code.replace(
"""class BMEStaffUpdate(BaseModel):
    full_name: Optional[str] = None
    title: Optional[str] = None
    role_level: Optional[str] = None
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    assigned_departments: Optional[str] = None
    certificates: Optional[str] = None
    duty_shift: Optional[str] = None
    status: Optional[str] = None
    avatar_color: Optional[str] = None""",
"""class BMEStaffUpdate(BaseModel):
    staff_code: Optional[str] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    role_level: Optional[str] = None
    department_unit: Optional[str] = None
    specialty: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    assigned_departments: Optional[str] = None
    certificates: Optional[str] = None
    duty_shift: Optional[str] = None
    status: Optional[str] = None
    avatar_color: Optional[str] = None"""
)

# Add Leader and Supplier update endpoints
extra_put_endpoints = """
class HospitalLeaderUpdate(BaseModel):
    group_name: Optional[str] = None
    full_name: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None

@router.put("/api/directory/leaders/{leader_id}")
async def update_hospital_leader(leader_id: int, req: HospitalLeaderUpdate, db = Depends(get_db)):
    \"\"\"Chỉnh sửa thông tin lãnh đạo / trưởng khoa lâm sàng\"\"\"
    row = db.execute("SELECT * FROM hospital_directory WHERE id = ?", (leader_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy lãnh đạo")
    fields = []
    params = []
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None:
            fields.append(f"{k} = ?")
            params.append(v)
    if fields:
        params.append(leader_id)
        db.execute(f"UPDATE hospital_directory SET {', '.join(fields)} WHERE id = ?", params)
        db.commit()
    return {"status": "success", "message": "Đã cập nhật thông tin lãnh đạo thành công!"}

class SupplierContactUpdate(BaseModel):
    supplier_name: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    service_scope: Optional[str] = None

@router.put("/api/directory/suppliers/{sup_id}")
async def update_supplier_contact(sup_id: int, req: SupplierContactUpdate, db = Depends(get_db)):
    \"\"\"Chỉnh sửa thông tin đối tác / đại diện hãng kỹ thuật\"\"\"
    row = db.execute("SELECT * FROM supplier_contacts WHERE id = ?", (sup_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà cung cấp")
    fields = []
    params = []
    for k, v in req.dict(exclude_unset=True).items():
        if v is not None:
            fields.append(f"{k} = ?")
            params.append(v)
    if fields:
        params.append(sup_id)
        db.execute(f"UPDATE supplier_contacts SET {', '.join(fields)} WHERE id = ?", params)
        db.commit()
    return {"status": "success", "message": "Đã cập nhật thông tin đối tác NCC thành công!"}
"""

if "update_hospital_leader" not in routes_code:
    routes_code += "\n\n" + extra_put_endpoints
    with open(routes_path, "w", encoding="utf-8") as f:
        f.write(routes_code)
    print("✅ Đã chèn các endpoint cập nhật dữ liệu vào `app/routes.py`!")

# ==================== 2. UPDATE WEB/INDEX.HTML ====================
with open(html_path, "r", encoding="utf-8") as f:
    html_code = f.read()

# Add Edit Leader and Edit Supplier Modals
edit_modals_html = """
    <!-- ==================== MODAL: CHỈNH SỬA THÔNG TIN LÃNH ĐẠO / TRƯỞNG KHOA ==================== -->
    <div class="modal fade" id="editLeaderModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-danger text-white px-4 py-3 border-0">
                    <h5 class="modal-title fw-bold"><i class="bi bi-person-badge me-2"></i>Chỉnh Sửa Thông Tin Lãnh Đạo / Trưởng Khoa</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <form id="editLeaderForm">
                        <input type="hidden" id="leader-edit-id">
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">HỌ VÀ TÊN (*)</label>
                            <input type="text" id="leader-edit-name" class="form-control form-control-sm" required>
                        </div>
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">ĐƠN VỊ / NHÓM</label>
                                <input type="text" id="leader-edit-group" class="form-control form-control-sm" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">CHỨC VỤ (*)</label>
                                <input type="text" id="leader-edit-title" class="form-control form-control-sm" required>
                            </div>
                        </div>
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">SỐ ĐIỆN THOẠI (*)</label>
                                <input type="text" id="leader-edit-phone" class="form-control form-control-sm font-mono" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">EMAIL</label>
                                <input type="email" id="leader-edit-email" class="form-control form-control-sm">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">GHI CHÚ / PHẠM VI CHUYÊN MÔN</label>
                            <textarea id="leader-edit-notes" class="form-control form-control-sm" rows="2"></textarea>
                        </div>
                        <div class="d-flex justify-content-end gap-2 pt-3 border-top">
                            <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Hủy</button>
                            <button type="submit" class="btn btn-danger btn-clinical fw-bold shadow-sm">
                                <i class="bi bi-save me-1"></i> Cập Nhật Thông Tin
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- ==================== MODAL: CHỈNH SỬA THÔNG TIN ĐỐI TÁC / KỸ SƯ HÃNG ==================== -->
    <div class="modal fade" id="editSupplierContactModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-warning text-dark px-4 py-3 border-0">
                    <h5 class="modal-title fw-bold"><i class="bi bi-building me-2"></i>Chỉnh Sửa Thông Tin Kỹ Sư Hãng & NCC</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <form id="editSupplierContactForm">
                        <input type="hidden" id="sup-contact-edit-id">
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">TÊN NHÀ CUNG CẤP / HÃNG (*)</label>
                            <input type="text" id="sup-contact-edit-name" class="form-control form-control-sm" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">ĐẠI DIỆN LIÊN HỆ / KỸ SƯ HÃNG</label>
                            <input type="text" id="sup-contact-edit-person" class="form-control form-control-sm" placeholder="VD: Anh Thịnh - Kỹ sư Siemens">
                        </div>
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">SỐ ĐIỆN THOẠI HOTLINE (*)</label>
                                <input type="text" id="sup-contact-edit-phone" class="form-control form-control-sm font-mono" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">EMAIL LIÊN HỆ</label>
                                <input type="email" id="sup-contact-edit-email" class="form-control form-control-sm">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">PHẠM VI DỊCH VỤ & BẢO TRÌ</label>
                            <input type="text" id="sup-contact-edit-scope" class="form-control form-control-sm" value="Bảo trì, sửa chữa & cung cấp vật tư chính hãng">
                        </div>
                        <div class="d-flex justify-content-end gap-2 pt-3 border-top">
                            <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Hủy</button>
                            <button type="submit" class="btn btn-warning text-dark btn-clinical fw-bold shadow-sm">
                                <i class="bi bi-save me-1"></i> Cập Nhật Thông Tin
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
"""

if 'id="editLeaderModal"' not in html_code:
    html_code = html_code.replace('</body>', edit_modals_html + '\n</body>')
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_code)
    print("✅ Đã chèn Modals `#editLeaderModal` và `#editSupplierContactModal` vào `web/index.html`!")

# ==================== 3. UPDATE WEB/JS/APP.JS ====================
with open(app_js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Make sure all edit modals have open and submit functions
edit_support_js = """
        openEditLeaderModal(id) {
            const l = this.leadersList.find(item => item.id === id);
            if (!l) return;

            document.getElementById('leader-edit-id').value = l.id;
            document.getElementById('leader-edit-name').value = l.full_name;
            document.getElementById('leader-edit-group').value = l.group_name || '';
            document.getElementById('leader-edit-title').value = l.title || '';
            document.getElementById('leader-edit-phone').value = l.phone || '';
            document.getElementById('leader-edit-email').value = l.email || '';
            document.getElementById('leader-edit-notes').value = l.notes || '';

            const modal = new bootstrap.Modal(document.getElementById('editLeaderModal'));
            modal.show();
        },

        openEditSupplierContactModal(id) {
            const s = this.supplierContactsList.find(item => item.id === id);
            if (!s) return;

            document.getElementById('sup-contact-edit-id').value = s.id;
            document.getElementById('sup-contact-edit-name').value = s.supplier_name;
            document.getElementById('sup-contact-edit-person').value = s.contact_person || '';
            document.getElementById('sup-contact-edit-phone').value = s.phone || '';
            document.getElementById('sup-contact-edit-email').value = s.email || '';
            document.getElementById('sup-contact-edit-scope').value = s.service_scope || '';

            const modal = new bootstrap.Modal(document.getElementById('editSupplierContactModal'));
            modal.show();
        },

        setupDirectoryEditForms() {
            // Edit Leader Form
            const leaderForm = document.getElementById('editLeaderForm');
            leaderForm?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const id = document.getElementById('leader-edit-id').value;
                const payload = {
                    full_name: document.getElementById('leader-edit-name').value.trim(),
                    group_name: document.getElementById('leader-edit-group').value.trim(),
                    title: document.getElementById('leader-edit-title').value.trim(),
                    phone: document.getElementById('leader-edit-phone').value.trim(),
                    email: document.getElementById('leader-edit-email').value.trim(),
                    notes: document.getElementById('leader-edit-notes').value.trim()
                };

                try {
                    const res = await fetch(`/api/directory/leaders/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi cập nhật');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('editLeaderModal'))?.hide();
                    this.leadersList = [];
                    this.loadAndRenderLeaders();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });

            // Edit Supplier Contact Form
            const supForm = document.getElementById('editSupplierContactForm');
            supForm?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const id = document.getElementById('sup-contact-edit-id').value;
                const payload = {
                    supplier_name: document.getElementById('sup-contact-edit-name').value.trim(),
                    contact_person: document.getElementById('sup-contact-edit-person').value.trim(),
                    phone: document.getElementById('sup-contact-edit-phone').value.trim(),
                    email: document.getElementById('sup-contact-edit-email').value.trim(),
                    service_scope: document.getElementById('sup-contact-edit-scope').value.trim()
                };

                try {
                    const res = await fetch(`/api/directory/suppliers/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi cập nhật');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('editSupplierContactModal'))?.hide();
                    this.supplierContactsList = [];
                    this.loadAndRenderSupplierContacts();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });
        },
"""

# Update Leader and Supplier rendering to include Edit buttons
js_code = js_code.replace(
    '<a href="mailto:${l.email || \'\'}" class="btn btn-sm btn-light border btn-clinical text-dark">',
    '<button type="button" class="btn btn-sm btn-light border btn-clinical text-dark" onclick="app.openEditLeaderModal(${l.id})"><i class="bi bi-pencil-square me-1"></i>Sửa</button>\n                                <a href="mailto:${l.email || \'\'}" class="btn btn-sm btn-light border btn-clinical text-dark">'
)

js_code = js_code.replace(
    '<span class="badge bg-light text-muted border font-mono">${s.email ? s.email : \'Hotline Kỹ Thuật\'}</span>',
    '<button type="button" class="btn btn-sm btn-light border btn-clinical text-dark" onclick="app.openEditSupplierContactModal(${s.id})"><i class="bi bi-pencil-square me-1"></i>Sửa</button>'
)

if "setupDirectoryEditForms" not in js_code:
    js_code = js_code.replace("this.setupStaffEventListeners();", "this.setupStaffEventListeners();\n            this.setupDirectoryEditForms();")
    js_code = js_code.replace("setupFormSubmissions() {", edit_support_js + "\n        setupFormSubmissions() {")
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print("✅ Đã tích hợp tính năng chỉnh sửa toàn diện vào `web/js/app.js`!")

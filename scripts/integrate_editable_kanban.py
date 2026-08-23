import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
html_path = app_dir / "web" / "index.html"
js_path = app_dir / "web" / "js" / "app.js"

# ==================== 1. ADD EDIT KANBAN MODAL TO INDEX.HTML ====================
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

edit_kanban_modal_html = """
    <!-- ==================== MODAL: CHỈNH SỬA THÔNG TIN TÁC VỤ KANBAN ==================== -->
    <div class="modal fade" id="editKanbanTaskModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-dark text-white px-4 py-3 border-0">
                    <h5 class="modal-title fw-bold"><i class="bi bi-pencil-square text-warning me-2"></i>Chỉnh Sửa Tác Vụ & Thẻ Kanban</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <form id="editKanbanTaskForm" onsubmit="event.preventDefault(); app.submitEditKanbanTask();">
                        <input type="hidden" id="edit-kanban-id">
                        
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">TIÊU ĐỀ TÁC VỤ / TÊN THIẾT BỊ (*)</label>
                            <input type="text" id="edit-kanban-title" class="form-control form-control-sm fw-bold" required>
                        </div>

                        <div class="row g-2 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">THẺ CÔNG TÁC / QUY TRÌNH</label>
                                <input type="text" id="edit-kanban-type" class="form-control form-control-sm font-mono" placeholder="VD: Báo hỏng, PM Định kỳ, QT.08, BM04..." required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">MỨC ĐỘ ƯU TIÊN</label>
                                <select id="edit-kanban-priority" class="form-select form-select-sm">
                                    <option value="Khẩn cấp">🔴 Khẩn cấp (Ưu tiên số 1)</option>
                                    <option value="Cao">🟠 Cao (Trong 24-48h)</option>
                                    <option value="Bình thường">🔵 Bình thường</option>
                                    <option value="Thấp">⚪ Thấp</option>
                                </select>
                            </div>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">VỊ TRÍ / SERIAL / THÔNG TIN BỔ SUNG</label>
                            <input type="text" id="edit-kanban-meta" class="form-control form-control-sm" placeholder="VD: Khoa Cấp Cứu • S/N: VEL8829">
                        </div>

                        <div class="row g-2 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">NGƯỜI PHỤ TRÁCH / KỸ SƯ</label>
                                <input type="text" id="edit-kanban-assignee" class="form-control form-control-sm" placeholder="VD: KS. Trần Trọng Tấn" list="kanban-staff-suggestions">
                                <datalist id="kanban-staff-suggestions">
                                    <option value="KS. Trần Trọng Tấn">
                                    <option value="KS. Lê Minh Thiện">
                                    <option value="KS. Trần Đăng Hiếu">
                                    <option value="KS. Nguyễn Quốc Việt">
                                    <option value="KS. Nguyễn Tấn Lợi">
                                    <option value="CN. Trần Thị Ngọc Châu">
                                    <option value="BS. Nguyễn Tuấn">
                                    <option value="ĐD. Trưởng trực">
                                    <option value="Hãng GE Healthcare">
                                    <option value="P.TTBYT">
                                </datalist>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">GIAI ĐOẠN / CỘT TIẾN ĐỘ</label>
                                <select id="edit-kanban-col" class="form-select form-select-sm">
                                    <option value="todo">1. Chờ Tiếp Nhận (To Do)</option>
                                    <option value="inprog">2. Đang Xử Lý (In Progress)</option>
                                    <option value="review">3. Chờ Nghiệm Thu (Review)</option>
                                    <option value="done">4. Đã Hoàn Tất (Done)</option>
                                </select>
                            </div>
                        </div>

                        <div class="mb-4">
                            <label class="form-label small fw-bold text-dark">HẠN CHÓT / TIẾN ĐỘ THỰC HIỆN</label>
                            <input type="text" id="edit-kanban-deadline" class="form-control form-control-sm" placeholder="VD: Hạn: Hôm nay, Tiến độ 60%, Chờ ký BM04...">
                        </div>

                        <div class="d-flex justify-content-between align-items-center pt-2 border-top">
                            <button type="button" class="btn btn-sm btn-outline-danger btn-clinical" onclick="app.deleteCurrentEditingKanbanTask()">
                                <i class="bi bi-trash me-1"></i> Xóa Tác Vụ
                            </button>
                            <div class="d-flex gap-2">
                                <button type="button" class="btn btn-sm btn-secondary btn-clinical" data-bs-dismiss="modal">Hủy</button>
                                <button type="submit" class="btn btn-sm btn-primary btn-clinical fw-bold shadow-sm">
                                    <i class="bi bi-check-circle-fill me-1"></i> Lưu Thay Đổi
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
"""

if 'id="editKanbanTaskModal"' not in html_content:
    html_content = html_content.replace('</body>', edit_kanban_modal_html + '\n</body>')
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ Đã chèn `#editKanbanTaskModal` vào `web/index.html`!")

# ==================== 2. UPDATE KANBAN EDIT METHODS IN JS ====================
with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

# Replace renderKanban card creation to include edit trigger
old_card_render_start = """                cardEl.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <span class="badge ${pBadgeClass} font-mono" style="font-size: 0.7rem;">${this.escapeHtml(task.priority)}</span>
                        <div class="d-flex align-items-center gap-1">
                            <span class="text-muted font-mono" style="font-size: 0.7rem;">${this.escapeHtml(task.type)}</span>
                            <button class="btn btn-sm btn-link p-0 text-muted kanban-card-actions" onclick="event.stopPropagation(); app.deleteKanbanTask('${task.id}')" title="Xóa thẻ">
                                <i class="bi bi-x"></i>
                            </button>
                        </div>
                    </div>"""

new_card_render_start = """                cardEl.style.cursor = 'pointer';
                cardEl.title = 'Nhấp để chỉnh sửa thông tin thẻ này';
                cardEl.addEventListener('click', (e) => {
                    if (e.target.closest('.kanban-card-actions')) return;
                    app.openEditKanbanModal(task.id);
                });

                cardEl.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <span class="badge ${pBadgeClass} font-mono" style="font-size: 0.7rem;" onclick="event.stopPropagation(); app.openEditKanbanModal('${task.id}')" title="Nhấp để đổi ưu tiên">${this.escapeHtml(task.priority)}</span>
                        <div class="d-flex align-items-center gap-1">
                            <span class="badge bg-light text-dark border font-mono" style="font-size: 0.68rem;" onclick="event.stopPropagation(); app.openEditKanbanModal('${task.id}')" title="Nhấp để đổi loại thẻ">${this.escapeHtml(task.type)}</span>
                            <button class="btn btn-sm btn-link p-0 text-primary kanban-card-actions" onclick="event.stopPropagation(); app.openEditKanbanModal('${task.id}')" title="Chỉnh sửa thông tin">
                                <i class="bi bi-pencil-square"></i>
                            </button>
                            <button class="btn btn-sm btn-link p-0 text-danger kanban-card-actions" onclick="event.stopPropagation(); app.deleteKanbanTask('${task.id}')" title="Xóa thẻ">
                                <i class="bi bi-x fs-6"></i>
                            </button>
                        </div>
                    </div>"""

if "openEditKanbanModal" not in js_content:
    if old_card_render_start in js_content:
        js_content = js_content.replace(old_card_render_start, new_card_render_start)
    else:
        # Regex replacement if whitespace differs
        js_content = re.sub(
            r'cardEl\.innerHTML\s*=\s*`\s*<div class="d-flex justify-content-between align-items-start mb-1">[\s\S]*?<div class="d-flex align-items-center gap-1">[\s\S]*?<button class="btn btn-sm btn-link p-0 text-muted kanban-card-actions" onclick="event\.stopPropagation\(\); app\.deleteKanbanTask[\s\S]*?</div>\s*</div>',
            new_card_render_start,
            js_content
        )

# Add openEditKanbanModal, submitEditKanbanTask, deleteCurrentEditingKanbanTask methods
kanban_edit_methods = """
        openEditKanbanModal(taskId) {
            const task = this.kanbanTasks.find(t => t.id === taskId);
            if (!task) return;

            document.getElementById('edit-kanban-id').value = task.id;
            document.getElementById('edit-kanban-title').value = task.title || '';
            document.getElementById('edit-kanban-type').value = task.type || 'Báo hỏng';
            document.getElementById('edit-kanban-priority').value = task.priority || 'Bình thường';
            document.getElementById('edit-kanban-meta').value = task.meta || '';
            document.getElementById('edit-kanban-assignee').value = task.assignee || '';
            document.getElementById('edit-kanban-col').value = task.col || 'todo';
            document.getElementById('edit-kanban-deadline').value = task.deadline || '';

            const modal = new bootstrap.Modal(document.getElementById('editKanbanTaskModal'));
            modal.show();
        },

        submitEditKanbanTask() {
            const taskId = document.getElementById('edit-kanban-id').value;
            const task = this.kanbanTasks.find(t => t.id === taskId);
            if (!task) return;

            task.title = document.getElementById('edit-kanban-title').value.trim() || 'Tác vụ';
            task.type = document.getElementById('edit-kanban-type').value.trim() || 'Công tác';
            task.priority = document.getElementById('edit-kanban-priority').value;
            task.meta = document.getElementById('edit-kanban-meta').value.trim();
            task.assignee = document.getElementById('edit-kanban-assignee').value.trim() || 'P.TTBYT';
            task.col = document.getElementById('edit-kanban-col').value;
            task.deadline = document.getElementById('edit-kanban-deadline').value.trim();

            this.saveKanbanState();
            this.renderKanban();

            bootstrap.Modal.getInstance(document.getElementById('editKanbanTaskModal'))?.hide();
        },

        deleteCurrentEditingKanbanTask() {
            const taskId = document.getElementById('edit-kanban-id').value;
            if (!taskId) return;
            if (confirm('Bạn có chắc chắn muốn xóa tác vụ Kanban này?')) {
                this.deleteKanbanTask(taskId);
                bootstrap.Modal.getInstance(document.getElementById('editKanbanTaskModal'))?.hide();
            }
        },
"""

if "submitEditKanbanTask" not in js_content:
    js_content = js_content.replace("setupKanbanForm() {", kanban_edit_methods + "\n        setupKanbanForm() {")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("✅ Đã bổ sung các hàm xử lý chỉnh sửa Kanban vào `web/js/app.js`!")

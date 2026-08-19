import re
import sys
import sqlite3
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")

# 1. Create system_feedback table in SQLite
db_path = app_dir / "database" / "devices.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS system_feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        sender_name TEXT,
        sender_dept TEXT,
        priority TEXT DEFAULT 'NORMAL',
        content TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        resolution_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")
conn.commit()
conn.close()
print("✅ [1] Đã khởi tạo bảng `system_feedback` trong SQLite database!")

# 2. Add Feedback Endpoints to app/routes.py
routes_path = app_dir / "app" / "routes.py"
with open(routes_path, "r", encoding="utf-8") as f:
    routes_content = f.read()

feedback_routes_code = """
# ==================== SYSTEM FEEDBACK & IMPROVEMENTS ====================

class FeedbackCreate(BaseModel):
    category: str
    sender_name: Optional[str] = "Cán bộ y tế / Kỹ sư"
    sender_dept: Optional[str] = "Phòng TTBYT / Lâm sàng"
    priority: Optional[str] = "NORMAL"
    content: str

class FeedbackStatusUpdate(BaseModel):
    status: str
    resolution_notes: Optional[str] = None

@router.get("/api/feedback")
async def list_feedback(db = Depends(get_db)):
    \"\"\"Danh sách các phiếu góp ý, đề xuất chỉnh sửa hoàn thiện hệ thống\"\"\"
    rows = db.execute("SELECT * FROM system_feedback ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]

@router.post("/api/feedback")
async def create_feedback(req: FeedbackCreate, db = Depends(get_db)):
    \"\"\"Gửi góp ý hoặc báo lỗi / đề xuất hoàn thiện mới\"\"\"
    if not req.content or not req.content.strip():
        raise HTTPException(status_code=400, detail="Nội dung góp ý không được để trống")
    
    cur = db.execute(\"\"\"
        INSERT INTO system_feedback (category, sender_name, sender_dept, priority, content, status)
        VALUES (?, ?, ?, ?, ?, 'PENDING')
    \"\"\", (req.category, req.sender_name, req.sender_dept, req.priority, req.content.strip()))
    db.commit()
    return {"status": "success", "id": cur.lastrowid, "message": "Cảm ơn bạn! Đã ghi nhận góp ý chỉnh sửa thành công!"}

@router.put("/api/feedback/{feedback_id}/status")
async def update_feedback_status(feedback_id: int, req: FeedbackStatusUpdate, db = Depends(get_db)):
    \"\"\"Cập nhật trạng thái xử lý góp ý\"\"\"
    row = db.execute("SELECT * FROM system_feedback WHERE id = ?", (feedback_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi góp ý")
    
    db.execute(\"\"\"
        UPDATE system_feedback
        SET status = ?, resolution_notes = ?
        WHERE id = ?
    \"\"\", (req.status, req.resolution_notes, feedback_id))
    db.commit()
    return {"status": "success", "message": "Đã cập nhật trạng thái xử lý góp ý thành công!"}

@router.delete("/api/feedback/{feedback_id}")
async def delete_feedback(feedback_id: int, db = Depends(get_db)):
    \"\"\"Xóa bản ghi góp ý\"\"\"
    db.execute("DELETE FROM system_feedback WHERE id = ?", (feedback_id,))
    db.commit()
    return {"status": "success", "message": "Đã xóa bản ghi góp ý!"}
"""

if "/api/feedback" not in routes_content:
    routes_content += "\n\n" + feedback_routes_code
    with open(routes_path, "w", encoding="utf-8") as f:
        f.write(routes_content)
    print("✅ [2] Đã bổ sung toàn bộ Feedback RESTful APIs vào `app/routes.py`!")

# 3. Add Feedback button & Modal to web/index.html
index_path = app_dir / "web" / "index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Add button in top-header
top_header_button_html = """                    <button class="btn btn-sm btn-warning text-dark btn-clinical fw-bold shadow-sm d-flex align-items-center gap-1" onclick="app.openFeedbackModal()" title="Gửi góp ý, báo lỗi hoặc đề xuất chỉnh sửa hoàn thiện hệ thống">
                        <i class="bi bi-chat-square-dots-fill text-danger"></i>
                        <span>Góp Ý Chỉnh Sửa</span>
                    </button>"""

if "Góp Ý Chỉnh Sửa" not in html_content:
    html_content = html_content.replace(
        '<button id="btn-export-csv" class="btn btn-sm btn-outline-secondary btn-clinical" title="Xuất file Excel CSV">',
        top_header_button_html + '\n                    <button id="btn-export-csv" class="btn btn-sm btn-outline-secondary btn-clinical" title="Xuất file Excel CSV">'
    )

# Floating button styling and element
floating_btn_html = """
    <!-- Floating Feedback Trigger Button on Bottom-Right -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 1040; margin-bottom: 75px;">
        <button class="btn btn-warning text-dark fw-bold rounded-pill shadow-lg d-flex align-items-center gap-2 px-3 py-2 border border-2 border-white" onclick="app.openFeedbackModal()" style="transition: transform 0.2s; font-size: 0.85rem;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
            <i class="bi bi-chat-right-text-fill text-danger fs-6"></i>
            <span>Góp Ý Chỉnh Sửa</span>
            <span class="badge bg-danger rounded-pill font-mono" id="floating-feedback-badge">New</span>
        </button>
    </div>

    <!-- ==================== MODAL: GÓP Ý & ĐỀ XUẤT CHỈNH SỬA ==================== -->
    <div class="modal fade" id="feedbackModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header text-white px-4 py-3 border-0" style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-2 rounded bg-warning text-dark fs-5">
                            <i class="bi bi-chat-square-quote-fill"></i>
                        </div>
                        <div>
                            <h5 class="modal-title fw-bold text-white mb-0">Hộp Thư Góp Ý & Đề Xuất Chỉnh Sửa Hệ Thống</h5>
                            <span class="small text-white text-opacity-75">Thu thập ý kiến đóng góp để hoàn thiện dữ liệu thiết bị, hợp đồng, quy trình SOPs và giao diện</span>
                        </div>
                    </div>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4 bg-light">
                    <!-- Nav Tabs for Submit vs History -->
                    <ul class="nav nav-pills nav-fill bg-white p-1 rounded-3 border mb-3 shadow-sm" role="tablist">
                        <li class="nav-item">
                            <button class="nav-link active fw-bold py-2" id="pill-tab-new-feedback" data-bs-toggle="pill" data-bs-target="#tab-new-feedback" type="button">
                                <i class="bi bi-pencil-square me-2 text-primary"></i>Gửi Góp Ý / Báo Lỗi Mới
                            </button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link fw-bold py-2 text-dark" id="pill-tab-feedback-list" data-bs-toggle="pill" data-bs-target="#tab-feedback-list" type="button" onclick="app.loadFeedbackHistory()">
                                <i class="bi bi-clock-history me-2 text-warning"></i>Lịch Sử Góp Ý Đã Gửi
                                <span class="badge bg-secondary ms-2 font-mono" id="feedback-history-count">0</span>
                            </button>
                        </li>
                    </ul>

                    <div class="tab-content">
                        <!-- TAB 1: FORM GỬI GÓP Ý -->
                        <div class="tab-pane fade show active" id="tab-new-feedback" role="tabpanel">
                            <div class="bg-white p-3 rounded-3 border shadow-sm">
                                <form id="feedbackForm" onsubmit="event.preventDefault(); app.submitFeedbackForm();">
                                    <div class="row g-3 mb-3">
                                        <div class="col-md-6">
                                            <label class="form-label small fw-bold text-dark">PHÂN LOẠI NỘI DUNG GÓP Ý (*)</label>
                                            <select id="fb-category" class="form-select form-select-sm" required>
                                                <option value="Đính chính dữ liệu thiết bị" selected>🩺 Đính chính dữ liệu thiết bị (Tên, Model, S/N, Khoa)</option>
                                                <option value="Bổ sung hợp đồng & nhà thầu">📑 Bổ sung / Chỉnh sửa Hợp đồng & Nhà cung cấp</option>
                                                <option value="Quy trình lâm sàng SOPs">📖 Quy trình vận hành & Sổ tay SOPs (QT.01 - QT.09)</option>
                                                <option value="Giao diện UI/UX & Tính năng">🎨 Giao diện UI/UX & Tính năng tiện ích</option>
                                                <option value="Trợ lý AI & Mistral OCR">🤖 Trợ lý AI (Gemini 3.7) & Bóc tách OCR</option>
                                                <option value="Khác">💡 Đề xuất cải tiến khác</option>
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label small fw-bold text-dark">MỨC ĐỘ ƯU TIÊN</label>
                                            <select id="fb-priority" class="form-select form-select-sm">
                                                <option value="NORMAL" selected>🟢 Bình thường (Cải tiến dần)</option>
                                                <option value="IMPORTANT">🟡 Quan trọng (Cần chỉnh sửa sớm)</option>
                                                <option value="URGENT">🔴 Khẩn cấp (Sai sót dữ liệu ảnh hưởng vận hành)</option>
                                            </select>
                                        </div>
                                    </div>

                                    <div class="row g-3 mb-3">
                                        <div class="col-md-6">
                                            <label class="form-label small fw-bold text-dark">HỌ TÊN NGƯỜI GÓP Ý (TÙY CHỌN)</label>
                                            <input type="text" id="fb-sender-name" class="form-control form-control-sm" placeholder="VD: KS. Trần Trọng Tấn / BS. Khoa CĐHA">
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label small fw-bold text-dark">KHOA PHÒNG / ĐƠN VỊ</label>
                                            <input type="text" id="fb-sender-dept" class="form-control form-control-sm" placeholder="VD: Phòng Trang Thiết Bị Y Tế">
                                        </div>
                                    </div>

                                    <div class="mb-3">
                                        <label class="form-label small fw-bold text-dark">NỘI DUNG CHI TIẾT GÓP Ý / ĐỀ XUẤT CHỈNH SỬA (*)</label>
                                        <textarea id="fb-content" class="form-control form-control-sm" rows="4" placeholder="Mô tả cụ thể thông tin cần cập nhật, ví dụ: 'Máy siêu âm Voluson E10 phòng 102 cần cập nhật thêm phụ kiện đầu dò tim mạch' hoặc 'Chỉnh sửa lại số điện thoại hotline nhà thầu GE'..." required></textarea>
                                    </div>

                                    <div class="d-flex justify-content-between align-items-center pt-3 border-top">
                                        <span class="small text-muted"><i class="bi bi-shield-check text-success me-1"></i>Thông tin được lưu trữ bảo mật và phục vụ trực tiếp công tác hoàn thiện hệ thống.</span>
                                        <div class="d-flex gap-2">
                                            <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Đóng</button>
                                            <button type="submit" class="btn btn-warning text-dark btn-clinical fw-bold shadow-sm">
                                                <i class="bi bi-send-fill me-1 text-danger"></i> Gửi Góp Ý Ngay
                                            </button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>

                        <!-- TAB 2: LỊCH SỬ GÓP Ý -->
                        <div class="tab-pane fade" id="tab-feedback-list" role="tabpanel">
                            <div class="bg-white p-3 rounded-3 border shadow-sm" style="max-height: 400px; overflow-y: auto;">
                                <div class="table-responsive">
                                    <table class="table table-hover align-middle mb-0" style="font-size: 0.84rem;">
                                        <thead class="table-light sticky-top">
                                            <tr>
                                                <th style="width: 45px;">#</th>
                                                <th>PHÂN LOẠI</th>
                                                <th>NỘI DUNG ĐỀ XUẤT</th>
                                                <th>NGƯỜI GỬI</th>
                                                <th>THỜI GIAN</th>
                                                <th>TRẠNG THÁI</th>
                                                <th class="text-end" style="width: 80px;">XÓA</th>
                                            </tr>
                                        </thead>
                                        <tbody id="feedback-history-tbody">
                                            <tr>
                                                <td colspan="7" class="text-center py-4 text-muted">Chưa có góp ý nào.</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
"""

if "feedbackModal" not in html_content:
    html_content = html_content.replace("</body>", floating_btn_html + "\n</body>")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ [3] Đã tích hợp Nút Góp Ý & Modal Góp Ý Chỉnh Sửa vào `web/index.html`!")

# 4. Add JS methods to web/js/app.js
js_path = app_dir / "web" / "js" / "app.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

feedback_js_code = """
        // ==================== SYSTEM FEEDBACK CONTROLLER ====================
        openFeedbackModal() {
            document.getElementById('feedbackForm')?.reset();
            const modal = new bootstrap.Modal(document.getElementById('feedbackModal'));
            modal.show();
            this.loadFeedbackHistory();
        },

        async submitFeedbackForm() {
            const payload = {
                category: document.getElementById('fb-category')?.value || 'Khác',
                sender_name: document.getElementById('fb-sender-name')?.value.trim() || 'Cán bộ y tế / Kỹ sư',
                sender_dept: document.getElementById('fb-sender-dept')?.value.trim() || 'Phòng TTBYT',
                priority: document.getElementById('fb-priority')?.value || 'NORMAL',
                content: document.getElementById('fb-content')?.value.trim()
            };

            if (!payload.content) {
                alert('Vui lòng nhập nội dung góp ý!');
                return;
            }

            try {
                const res = await fetch('/api/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok) {
                    alert('✅ ' + data.message);
                    document.getElementById('feedbackForm')?.reset();
                    // Switch to history tab to see the newly submitted feedback
                    document.getElementById('pill-tab-feedback-list')?.click();
                    this.loadFeedbackHistory();
                } else {
                    alert('❌ Lỗi: ' + (data.detail || 'Không thể gửi góp ý'));
                }
            } catch (err) {
                alert('❌ Lỗi kết nối: ' + err.message);
            }
        },

        async loadFeedbackHistory() {
            try {
                const res = await fetch('/api/feedback');
                const list = await res.json();
                
                const badge = document.getElementById('feedback-history-count');
                const floatingBadge = document.getElementById('floating-feedback-badge');
                if (badge) badge.textContent = list.length;
                if (floatingBadge) floatingBadge.textContent = list.length > 0 ? list.length : 'New';

                const tbody = document.getElementById('feedback-history-tbody');
                if (!tbody) return;

                if (list.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">Chưa có góp ý nào được ghi nhận. Bạn có thể là người đầu tiên đóng góp ý kiến!</td></tr>`;
                    return;
                }

                let html = '';
                list.forEach((fb, idx) => {
                    const timeStr = fb.created_at ? new Date(fb.created_at).toLocaleString('vi-VN') : 'Vừa xong';
                    let statusBadge = '<span class="badge bg-warning text-dark"><i class="bi bi-hourglass-split me-1"></i>Đang chờ tiếp nhận</span>';
                    if (fb.status === 'IN_PROGRESS') {
                        statusBadge = '<span class="badge bg-info text-dark"><i class="bi bi-gear-fill me-1"></i>Đang hoàn thiện</span>';
                    } else if (fb.status === 'RESOLVED' || fb.status === 'COMPLETED') {
                        statusBadge = '<span class="badge bg-success"><i class="bi bi-check-circle-fill me-1"></i>Đã cập nhật xong</span>';
                    }

                    let priorityBadge = '';
                    if (fb.priority === 'URGENT') {
                        priorityBadge = '<span class="badge bg-danger ms-1">Khẩn cấp</span>';
                    } else if (fb.priority === 'IMPORTANT') {
                        priorityBadge = '<span class="badge bg-warning text-dark ms-1">Quan trọng</span>';
                    }

                    html += `
                        <tr>
                            <td class="fw-bold text-muted">${idx + 1}</td>
                            <td>
                                <strong class="text-dark d-block">${fb.category}</strong>
                                ${priorityBadge}
                            </td>
                            <td>
                                <div class="text-dark" style="max-width: 320px; word-break: break-word;">${fb.content}</div>
                            </td>
                            <td>
                                <strong class="text-dark d-block">${fb.sender_name}</strong>
                                <small class="text-muted">${fb.sender_dept}</small>
                            </td>
                            <td class="font-mono text-muted small">${timeStr}</td>
                            <td>${statusBadge}</td>
                            <td class="text-end">
                                <button class="btn btn-sm btn-outline-danger" onclick="app.deleteFeedbackItem(${fb.id})" title="Xóa góp ý này">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                });
                tbody.innerHTML = html;
            } catch (err) {
                console.error('Lỗi tải lịch sử góp ý:', err);
            }
        },

        async deleteFeedbackItem(feedbackId) {
            if (!confirm('Bạn có chắc chắn muốn xóa mục góp ý này?')) return;
            try {
                const res = await fetch(`/api/feedback/${feedbackId}`, { method: 'DELETE' });
                const data = await res.json();
                alert('✅ ' + data.message);
                this.loadFeedbackHistory();
            } catch (err) {
                alert('Lỗi xóa góp ý: ' + err.message);
            }
        },
"""

if "openFeedbackModal" not in js_content:
    # insert before init() in app.js
    pattern = r'(\s+activateTab\(targetId)'
    replacement = feedback_js_code + r'\n\1'
    js_content = re.sub(pattern, replacement, js_content, count=1)
    
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("✅ [4] Đã tích hợp Controller Góp Ý Chỉnh Sửa vào `web/js/app.js`!")

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
index_path = app_dir / "web" / "index.html"
js_path = app_dir / "web" / "js" / "app.js"

# 1. Update web/index.html with the comprehensive Key Management Modal
with open(index_path, "r", encoding="utf-8") as f:
    html_content = f.read()

new_key_modal_html = """    <!-- ==================== MODAL: QUẢN LÝ & CHỈNH SỬA KHÓA API KEYS POOL ==================== -->
    <div class="modal fade" id="keyConfigModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 16px; overflow: hidden;">
                <!-- Header with Gradient & Service Tabs -->
                <div class="modal-header text-white px-4 py-3 border-0" style="background: linear-gradient(135deg, #002d62 0%, #0284c7 100%);">
                    <div class="d-flex align-items-center gap-2">
                        <div class="p-2 rounded bg-white bg-opacity-20 fs-4">
                            <i class="bi bi-key-fill text-warning"></i>
                        </div>
                        <div>
                            <h5 class="modal-title fw-bold mb-0">Quản Lý Cơ Chế Xoay Khóa API Key Pool</h5>
                            <span class="small text-white text-opacity-75">Thêm, Sửa, Bật/Tắt, Kiểm tra kết nối Live & Đặt khóa ưu tiên cho AI Engine</span>
                        </div>
                    </div>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>

                <div class="modal-body p-4 bg-light">
                    <!-- Service Selector Navigation Pills -->
                    <ul class="nav nav-pills nav-fill mb-3 bg-white p-1 rounded-3 border shadow-sm" id="key-service-tabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active fw-bold py-2" id="pill-gemini-keys" onclick="app.switchKeyServiceTab('gemini')" type="button">
                                <i class="bi bi-stars text-primary me-2"></i>Google Gemini 3.7 Flash Pool
                                <span class="badge bg-primary ms-2" id="gemini-modal-badge">...</span>
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link fw-bold py-2 text-dark" id="pill-mistral-keys" onclick="app.switchKeyServiceTab('mistral')" type="button">
                                <i class="bi bi-file-earmark-text-fill text-warning me-2"></i>Mistral AI OCR Engine
                                <span class="badge bg-warning text-dark ms-2" id="mistral-modal-badge">...</span>
                            </button>
                        </li>
                    </ul>

                    <!-- Summary Stats Bar -->
                    <div class="row g-2 mb-3">
                        <div class="col-6 col-md-3">
                            <div class="bg-white p-2 rounded border text-center">
                                <span class="small text-muted d-block" style="font-size: 0.72rem; font-weight: 700;">TỔNG SỐ KEY</span>
                                <strong class="fs-5 text-dark" id="stat-total-keys">0</strong>
                            </div>
                        </div>
                        <div class="col-6 col-md-3">
                            <div class="bg-white p-2 rounded border text-center border-success">
                                <span class="small text-success d-block" style="font-size: 0.72rem; font-weight: 700;">ĐANG HOẠT ĐỘNG</span>
                                <strong class="fs-5 text-success" id="stat-active-keys">0</strong>
                            </div>
                        </div>
                        <div class="col-6 col-md-3">
                            <div class="bg-white p-2 rounded border text-center">
                                <span class="small text-muted d-block" style="font-size: 0.72rem; font-weight: 700;">TẠM DỪNG / INACTIVE</span>
                                <strong class="fs-5 text-secondary" id="stat-inactive-keys">0</strong>
                            </div>
                        </div>
                        <div class="col-6 col-md-3">
                            <div class="bg-white p-2 rounded border text-center border-warning">
                                <span class="small text-warning d-block" style="font-size: 0.72rem; font-weight: 700;">RATE-LIMIT / COOLDOWN</span>
                                <strong class="fs-5 text-warning" id="stat-ratelimit-keys">0</strong>
                            </div>
                        </div>
                    </div>

                    <!-- Interactive Keys List Container -->
                    <div class="clinical-card p-3 bg-white mb-3 shadow-sm">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="fw-bold mb-0 text-dark">
                                <i class="bi bi-shield-lock-fill text-primary me-2"></i>Danh Sách Khóa Trong Pool Hiện Tại
                            </h6>
                            <button class="btn btn-sm btn-outline-primary btn-clinical" onclick="app.loadAndRenderKeys(app.currentKeyService)">
                                <i class="bi bi-arrow-clockwise me-1"></i>Làm mới
                            </button>
                        </div>
                        
                        <div id="keys-table-container" class="table-responsive" style="max-height: 280px; overflow-y: auto;">
                            <!-- Dynamic Table Rendered via JS -->
                            <div class="text-center py-4 text-muted">
                                <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                                Đang tải danh sách API Keys...
                            </div>
                        </div>
                    </div>

                    <!-- Add New Key Form Accordion/Card -->
                    <div class="clinical-card p-3 bg-white shadow-sm">
                        <h6 class="fw-bold mb-2 text-dark">
                            <i class="bi bi-plus-circle-fill text-success me-2"></i>Thêm Khóa API Mới Vào Pool
                        </h6>
                        <form id="addKeyForm" onsubmit="event.preventDefault(); app.submitNewAPIKey();">
                            <div class="row g-2 mb-2">
                                <div class="col-12">
                                    <textarea id="key-input-textarea" class="form-control form-control-sm font-mono" rows="2" placeholder="Dán API Key mới tại đây (hỗ trợ nhập nhiều key phân cách bằng dấu phẩy hoặc xuống dòng)..." required></textarea>
                                </div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="small text-muted">
                                    <i class="bi bi-info-circle me-1"></i>Hệ thống tự động kiểm tra cú pháp và lưu trữ an toàn vào SQLite.
                                </span>
                                <button type="submit" class="btn btn-sm btn-success btn-clinical fw-bold px-3">
                                    <i class="bi bi-plus-lg me-1"></i> Thêm Khóa Mới
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                <div class="modal-footer bg-light px-4 py-2 border-top">
                    <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Đóng</button>
                </div>
            </div>
        </div>
    </div>

    <!-- ==================== SUB-MODAL: CHỈNH SỬA CHI TIẾT 1 API KEY ==================== -->
    <div class="modal fade" id="editSingleKeyModal" tabindex="-1" aria-hidden="true" style="z-index: 1060;">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-dark text-white px-4 py-3 border-0">
                    <h5 class="modal-title fw-bold"><i class="bi bi-pencil-square text-warning me-2"></i>Chỉnh Sửa API Key</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <form id="editSingleKeyForm" onsubmit="event.preventDefault(); app.submitEditSingleKey();">
                        <input type="hidden" id="edit-key-service">
                        <input type="hidden" id="edit-key-old-value">

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">DỊCH VỤ AI LIÊN KẾT</label>
                            <input type="text" id="edit-key-service-display" class="form-control form-control-sm" readonly disabled>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">GIÁ TRỊ API KEY (*)</label>
                            <input type="text" id="edit-key-new-value" class="form-control form-control-sm font-mono" required>
                        </div>

                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">TRẠNG THÁI HOẠT ĐỘNG</label>
                            <select id="edit-key-status" class="form-select form-select-sm">
                                <option value="ACTIVE">🟢 Đang Kích Hoạt (ACTIVE - Sẵn sàng xoay key)</option>
                                <option value="INACTIVE">⚪ Tạm Dừng Sử Dụng (INACTIVE)</option>
                                <option value="RATE_LIMITED">🟠 Tạm Khóa Cooldown (RATE_LIMITED)</option>
                            </select>
                        </div>

                        <div class="d-flex justify-content-between align-items-center pt-3 border-top">
                            <button type="button" class="btn btn-outline-info btn-sm btn-clinical" id="btn-test-modal-key" onclick="app.testModalKeyLive()">
                                <i class="bi bi-lightning-charge me-1"></i> Kiểm Tra Kết Nối Live
                            </button>
                            <div class="d-flex gap-2">
                                <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Hủy</button>
                                <button type="submit" class="btn btn-primary btn-clinical fw-bold shadow-sm">
                                    <i class="bi bi-check-lg me-1"></i> Lưu Cập Nhật
                                </button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
"""

# Replace old key modal
pattern = r'<!-- ==================== MODAL: QUẢN LÝ KHÓA API KEYS POOL ==================== -->.*?<!-- ==================== MODAL: CHỈNH SỬA THÔNG TIN TÁC VỤ KANBAN ==================== -->'
replacement = new_key_modal_html + "\n\n    <!-- ==================== MODAL: CHỈNH SỬA THÔNG TIN TÁC VỤ KANBAN ==================== -->"

if "keyConfigModal" in html_content:
    html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ [2] Đã cập nhật `web/index.html` với Giao Diện Quản Lý & Chỉnh Sửa Key Chuyên Nghiệp!")

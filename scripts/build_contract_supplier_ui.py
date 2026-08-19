import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
index_path = app_dir / "web" / "index.html"
js_path = app_dir / "web" / "js" / "app.js"

# 1. Update web/index.html
with open(index_path, "r", encoding="utf-8") as f:
    html_content = f.read()

new_tab_suppliers_html = """                    <!-- ==================== TAB: NHÀ CUNG CẤP & HỢP ĐỒNG (DYNAMIC & FULL CRUD) ==================== -->
                    <div class="tab-pane fade" id="tab-suppliers" role="tabpanel">
                        <!-- Header Banner -->
                        <div class="clinical-card p-3 mb-3" style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0369a1 100%); color: white;">
                            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                                <div class="d-flex align-items-center gap-3">
                                    <div class="p-2 rounded bg-white bg-opacity-20 fs-3">
                                        <i class="bi bi-building"></i>
                                    </div>
                                    <div>
                                        <h5 class="fw-bold mb-0 text-white">Quản Lý Danh Mục Hợp Đồng Mua Sắm & Danh Bạ Nhà Cung Cấp TTBYT</h5>
                                        <span class="small text-white text-opacity-75">Quản lý hồ sơ thầu, ủy quyền bảo hành hãng & thông tin kỹ sư thường trực 24/7</span>
                                    </div>
                                </div>
                                <div class="d-flex gap-2">
                                    <button class="btn btn-sm btn-light text-primary fw-bold btn-clinical shadow-sm" onclick="app.openCreateContractModal()">
                                        <i class="bi bi-file-earmark-plus me-1"></i> Thêm Hợp Đồng Mới
                                    </button>
                                    <button class="btn btn-sm btn-success text-white fw-bold btn-clinical shadow-sm" onclick="app.openCreateSupplierModal()">
                                        <i class="bi bi-person-plus-fill me-1"></i> Thêm Nhà Cung Cấp
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Sub-Navigation Navigation Pills -->
                        <div class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3">
                            <ul class="nav nav-pills bg-white p-1 rounded-3 border shadow-sm" id="supplier-contract-tabs" role="tablist">
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link active fw-bold py-2" id="pill-tab-contracts" onclick="app.switchSupplierSubTab('contracts')" type="button">
                                        <i class="bi bi-file-earmark-text text-primary me-2"></i>Hợp Đồng & Gói Thầu Mua Sắm
                                        <span class="badge bg-primary ms-2" id="contracts-count-badge">24 HĐ</span>
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link fw-bold py-2 text-dark" id="pill-tab-suppliers-list" onclick="app.switchSupplierSubTab('suppliers')" type="button">
                                        <i class="bi bi-people-fill text-warning me-2"></i>Danh Bạ Nhà Cung Cấp & Kỹ Sư Hãng
                                        <span class="badge bg-warning text-dark ms-2" id="suppliers-count-badge">45 NCC</span>
                                    </button>
                                </li>
                            </ul>

                            <!-- Search Bar -->
                            <div class="d-flex gap-2" style="min-width: 320px;">
                                <div class="input-group input-group-sm">
                                    <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
                                    <input type="text" id="contract-supplier-search-input" class="form-control border-start-0" placeholder="Tìm theo số HĐ, tên nhà thầu, thiết bị, hotline..." oninput="app.filterContractsSuppliers()">
                                </div>
                            </div>
                        </div>

                        <!-- SECTION 1: CONTRACTS VIEW -->
                        <div id="contracts-view-container" class="clinical-card p-3 mb-4 shadow-sm bg-white">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h6 class="fw-bold text-dark mb-0"><i class="bi bi-journal-check text-primary me-2"></i>Danh Sách Hợp Đồng Mua Sắm & Bàn Giao Thiết Bị</h6>
                                    <span class="small text-muted">Bấm vào số thiết bị để xem danh sách máy thuộc từng gói thầu</span>
                                </div>
                                <span class="badge bg-primary-subtle text-primary font-mono" id="contracts-summary-label">Đang tải dữ liệu...</span>
                            </div>

                            <div class="table-responsive">
                                <table class="table table-hover align-middle mb-0" style="font-size: 0.84rem;">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 50px;">#</th>
                                            <th>SỐ HỢP ĐỒNG</th>
                                            <th>TÊN GÓI THẦU / HỢP ĐỒNG</th>
                                            <th>NHÀ CUNG CẤP / ĐẠI DIỆN HÃNG</th>
                                            <th>NGÀY BÀN GIAO</th>
                                            <th>SỐ THIẾT BỊ</th>
                                            <th>TRẠNG THÁI</th>
                                            <th class="text-end" style="width: 140px;">THAO TÁC</th>
                                        </tr>
                                    </thead>
                                    <tbody id="contracts-table-body">
                                        <tr>
                                            <td colspan="8" class="text-center py-4 text-muted">
                                                <div class="spinner-border spinner-border-sm text-primary me-2"></div>
                                                Đang tải danh sách hợp đồng...
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- SECTION 2: SUPPLIERS VIEW (Hidden by default) -->
                        <div id="suppliers-view-container" class="clinical-card p-3 mb-4 shadow-sm bg-white d-none">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h6 class="fw-bold text-dark mb-0"><i class="bi bi-telephone-inbound text-warning me-2"></i>Danh Bạ Kỹ Sư & Hotline Bảo Hành Nhà Cung Cấp (45 Hãng)</h6>
                                    <span class="small text-muted">Liên hệ trực tiếp khi xảy ra sự cố thiết bị cần hỗ trợ kỹ thuật khẩn cấp</span>
                                </div>
                                <span class="badge bg-warning-subtle text-dark font-mono" id="suppliers-summary-label">45 Nhà Cung Cấp</span>
                            </div>

                            <div class="table-responsive">
                                <table class="table table-hover align-middle mb-0" style="font-size: 0.84rem;">
                                    <thead class="table-light">
                                        <tr>
                                            <th style="width: 50px;">#</th>
                                            <th>NHÀ THẦU / ĐỐI TÁC CUNG CẤP</th>
                                            <th>KỸ SƯ HÃNG / ĐẠI DIỆN</th>
                                            <th>HOTLINE LIÊN HỆ</th>
                                            <th>EMAIL KỸ THUẬT</th>
                                            <th>PHẠM VI THIẾT BỊ PHỤ TRÁCH</th>
                                            <th class="text-end" style="width: 140px;">THAO TÁC</th>
                                        </tr>
                                    </thead>
                                    <tbody id="suppliers-table-body">
                                        <tr>
                                            <td colspan="7" class="text-center py-4 text-muted">
                                                <div class="spinner-border spinner-border-sm text-warning me-2"></div>
                                                Đang tải danh bạ nhà cung cấp...
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>"""

# Replace static tab-suppliers
old_tab_suppliers_pattern = r'<div class="tab-pane fade" id="tab-suppliers" role="tabpanel">.*?</div>\s*<!-- ==================== TAB: LỊCH BẢO TRÌ & KIỂM ĐỊNH ==================== -->'
replacement_html = new_tab_suppliers_html + "\n\n                    <!-- ==================== TAB: LỊCH BẢO TRÌ & KIỂM ĐỊNH ==================== -->"

html_content = re.sub(old_tab_suppliers_pattern, replacement_html, html_content, flags=re.DOTALL)

# Add Modals at end of body if not exist
contract_modals_html = """
    <!-- ==================== MODAL: THÊM / CHỈNH SỬA HỢP ĐỒNG ==================== -->
    <div class="modal fade" id="contractModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-primary text-white px-4 py-3 border-0">
                    <h5 class="modal-title fw-bold" id="contract-modal-title"><i class="bi bi-file-earmark-text me-2"></i>Thêm Hợp Đồng Mua Sắm Mới</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <form id="contractForm" onsubmit="event.preventDefault(); app.submitContractForm();">
                        <input type="hidden" id="contract-form-id">
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">SỐ HỢP ĐỒNG (*)</label>
                                <input type="text" id="contract-form-no" class="form-control form-control-sm font-mono fw-bold" placeholder="VD: HĐ 20.2024HĐ/TAQ7-ANVIET" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">NGÀY BÀN GIAO / KÝ KẾT</label>
                                <input type="date" id="contract-form-date" class="form-control form-control-sm font-mono">
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">TÊN GÓI THẦU / HỢP ĐỒNG MUA SẮM (*)</label>
                            <input type="text" id="contract-form-name" class="form-control form-control-sm" placeholder="VD: Hợp đồng Cung Cấp Hệ Thống Siêu Âm Màu Chuyên Sản Samsung Medison..." required>
                        </div>
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">NHÀ CUNG CẤP / ĐỐI TÁC</label>
                                <input type="text" id="contract-form-supplier" class="form-control form-control-sm" placeholder="VD: Công Ty TNHH Thiết Bị Y Tế An Việt" list="supplier-names-list">
                                <datalist id="supplier-names-list"></datalist>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label small fw-bold text-dark">BẢO HÀNH (THÁNG)</label>
                                <input type="number" id="contract-form-warranty" class="form-control form-control-sm" value="24">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label small fw-bold text-dark">TRẠNG THÁI</label>
                                <select id="contract-form-status" class="form-select form-select-sm">
                                    <option value="ACTIVE" selected>Đang Hiệu Lực</option>
                                    <option value="EXPIRED">Hết Hạn Bảo Hành</option>
                                    <option value="CLOSED">Đã Thanh Lý</option>
                                </select>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">GHI CHÚ / DANH MỤC THIẾT BỊ CUNG CẤP</label>
                            <textarea id="contract-form-notes" class="form-control form-control-sm" rows="2" placeholder="Ghi chú chi tiết về hợp đồng, điều khoản bảo trì..."></textarea>
                        </div>
                        <div class="d-flex justify-content-end gap-2 pt-3 border-top">
                            <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Hủy</button>
                            <button type="submit" class="btn btn-primary btn-clinical fw-bold shadow-sm">
                                <i class="bi bi-check-lg me-1"></i> Lưu Hợp Đồng
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- ==================== MODAL: THÊM / CHỈNH SỬA NHÀ CUNG CẤP ==================== -->
    <div class="modal fade" id="supplierModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-warning text-dark px-4 py-3 border-0">
                    <h5 class="modal-title fw-bold" id="supplier-modal-title"><i class="bi bi-building me-2"></i>Thêm Nhà Cung Cấp Mới</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <form id="supplierForm" onsubmit="event.preventDefault(); app.submitSupplierForm();">
                        <input type="hidden" id="supplier-form-id">
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">TÊN NHÀ THẦU / NHÀ CUNG CẤP (*)</label>
                            <input type="text" id="supplier-form-name" class="form-control form-control-sm fw-bold" placeholder="VD: Công Ty TNHH GE Healthcare Việt Nam" required>
                        </div>
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">KỸ SƯ HÃNG / ĐẠI DIỆN</label>
                                <input type="text" id="supplier-form-person" class="form-control form-control-sm" placeholder="VD: Anh Thịnh - Kỹ sư">
                            </div>
                            <div class="col-md-6">
                                <label class="form-label small fw-bold text-dark">HOTLINE LIÊN HỆ (*)</label>
                                <input type="text" id="supplier-form-phone" class="form-control form-control-sm font-mono" placeholder="VD: 028.3822.XXXX" required>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">EMAIL HỖ TRỢ KỸ THUẬT</label>
                            <input type="email" id="supplier-form-email" class="form-control form-control-sm font-mono" placeholder="VD: service@gehealthcare.vn">
                        </div>
                        <div class="mb-3">
                            <label class="form-label small fw-bold text-dark">PHẠM VI THIẾT BỊ CUNG CẤP / BẢO HÀNH</label>
                            <textarea id="supplier-form-scope" class="form-control form-control-sm" rows="2" placeholder="VD: Hệ thống Siêu Âm Voluson E10, Máy Chụp Cắt Lớp Vi Tính CT-Scanner..."></textarea>
                        </div>
                        <div class="d-flex justify-content-end gap-2 pt-3 border-top">
                            <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Hủy</button>
                            <button type="submit" class="btn btn-warning btn-clinical fw-bold shadow-sm">
                                <i class="bi bi-check-lg me-1"></i> Lưu Nhà Cung Cấp
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- ==================== MODAL: XEM DANH SÁCH THIẾT BỊ THEO HỢP ĐỒNG / NHÀ CUNG CẤP ==================== -->
    <div class="modal fade" id="viewLinkedDevicesModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <div class="modal-header bg-dark text-white px-4 py-3 border-0">
                    <div>
                        <h5 class="modal-title fw-bold" id="linked-devices-modal-title">Danh Sách Thiết Bị Thuộc Gói Thầu</h5>
                        <span class="small text-white text-opacity-75" id="linked-devices-modal-subtitle">...</span>
                    </div>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <div class="table-responsive" style="max-height: 400px; overflow-y: auto;">
                        <table class="table table-hover align-middle mb-0" style="font-size: 0.84rem;">
                            <thead class="table-light sticky-top">
                                <tr>
                                    <th style="width: 50px;">#</th>
                                    <th>MÃ TÀI SẢN</th>
                                    <th>TÊN THIẾT BỊ</th>
                                    <th>MODEL</th>
                                    <th>SỐ SERIAL</th>
                                    <th>KHOA PHÒNG</th>
                                    <th>TRẠNG THÁI</th>
                                </tr>
                            </thead>
                            <tbody id="linked-devices-table-body">
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="modal-footer bg-light px-4 py-2 border-top">
                    <button type="button" class="btn btn-secondary btn-clinical" data-bs-dismiss="modal">Đóng</button>
                </div>
            </div>
        </div>
    </div>
"""

if "contractModal" not in html_content:
    html_content = html_content.replace("</body>", contract_modals_html + "\n</body>")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ Đã cập nhật `web/index.html` với Giao diện Hợp đồng & Nhà cung cấp đầy đủ!")


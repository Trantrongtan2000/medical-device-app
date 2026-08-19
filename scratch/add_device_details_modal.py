import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

html_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\index.html")
app_js_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\js\app.js")

# 1. Update HTML with Device Details Modal
device_modal_html = """
    <!-- ==================== MODAL: BẢNG THÔNG TIN CHI TIẾT THIẾT BỊ (DEVICE PASSPORT) ==================== -->
    <div class="modal fade" id="deviceDetailsModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
            <div class="modal-content border-0 shadow-lg" style="border-radius: 14px; overflow: hidden;">
                <!-- Header -->
                <div class="modal-header bg-dark text-white px-4 py-3 border-0">
                    <div class="d-flex align-items-center gap-3">
                        <div class="p-2 rounded-3 bg-primary text-white fs-4">
                            <i class="bi bi-hospital"></i>
                        </div>
                        <div>
                            <div class="d-flex align-items-center gap-2 mb-1">
                                <h5 class="modal-title fw-bold text-white mb-0" id="modal-dev-name">Tên Thiết Bị</h5>
                                <span class="badge" id="modal-dev-risk">Loại C</span>
                                <span class="badge bg-success-subtle text-success" id="modal-dev-status">Hoạt động</span>
                            </div>
                            <div class="text-secondary small font-mono">
                                Asset Tag: <strong class="text-info" id="modal-dev-tag">BVQ7-TTB-00001</strong> | 
                                SpeedMaint: <strong class="text-light" id="modal-dev-sm">BM/BVQ7/00001</strong> | 
                                Serial: <strong class="text-warning" id="modal-dev-sn">S/N</strong>
                            </div>
                        </div>
                    </div>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>

                <!-- Nav Tabs Inside Modal -->
                <div class="bg-light border-bottom px-4 pt-2">
                    <ul class="nav nav-tabs border-0" id="deviceModalTabs" role="tablist">
                        <li class="nav-item">
                            <button class="nav-link active fw-bold small text-dark" data-bs-toggle="tab" data-bs-target="#tab-modal-general">
                                <i class="bi bi-info-circle-fill text-primary me-1"></i> 1. Thông Tin Chung
                            </button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link fw-bold small text-dark" data-bs-toggle="tab" data-bs-target="#tab-modal-accessories">
                                <i class="bi bi-diagram-2 text-info me-1"></i> 2. Cấu Kiện & Phụ Kiện (<span id="modal-acc-count">0</span>)
                            </button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link fw-bold small text-dark" data-bs-toggle="tab" data-bs-target="#tab-modal-calibration">
                                <i class="bi bi-patch-check-fill text-success me-1"></i> 3. Kiểm Định & Hiệu Chuẩn
                            </button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link fw-bold small text-dark" data-bs-toggle="tab" data-bs-target="#tab-modal-maintenance">
                                <i class="bi bi-clock-history text-secondary me-1"></i> 4. Sổ Lý Lịch & Bảo Trì (BM05)
                            </button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link fw-bold small text-dark" data-bs-toggle="tab" data-bs-target="#tab-modal-provenance">
                                <i class="bi bi-share-fill text-warning me-1"></i> 5. Truy Vết Semantica W3C
                            </button>
                        </li>
                    </ul>
                </div>

                <!-- Modal Body Content -->
                <div class="modal-body p-4">
                    <div class="tab-content" id="deviceModalTabContent">
                        
                        <!-- TAB 1: THÔNG TIN CHUNG -->
                        <div class="tab-pane fade show active" id="tab-modal-general">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <div class="p-3 bg-light rounded border h-100">
                                        <h6 class="fw-bold text-primary mb-3"><i class="bi bi-geo-alt-fill me-2"></i>Vị Trí Phân Bổ Lâm Sàng</h6>
                                        <table class="table table-sm table-borderless mb-0 small">
                                            <tr>
                                                <td class="text-muted" style="width: 140px;">Khoa / Phòng:</td>
                                                <td><strong class="text-dark fs-6" id="modal-dev-facility">-</strong></td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Nhóm Danh Mục:</td>
                                                <td id="modal-dev-category">-</td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Ngày Lắp Đặt:</td>
                                                <td class="font-mono" id="modal-dev-install-date">-</td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Trạng Thái Vận Hành:</td>
                                                <td><span class="badge bg-success-subtle text-success border border-success" id="modal-dev-status-tag">IN_SERVICE</span></td>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="p-3 bg-light rounded border h-100">
                                        <h6 class="fw-bold text-primary mb-3"><i class="bi bi-cpu-fill me-2"></i>Thông Số Kỹ Thuật Gốc</h6>
                                        <table class="table table-sm table-borderless mb-0 small">
                                            <tr>
                                                <td class="text-muted" style="width: 140px;">Model:</td>
                                                <td><strong class="font-mono text-dark" id="modal-dev-model">-</strong></td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Hãng Sản Xuất:</td>
                                                <td class="fw-semibold text-dark" id="modal-dev-mfg">-</td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Nước Sản Xuất:</td>
                                                <td id="modal-dev-country">-</td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Năm Sản Xuất:</td>
                                                <td class="font-mono" id="modal-dev-year">-</td>
                                            </tr>
                                            <tr>
                                                <td class="text-muted">Phân Loại Rủi Ro:</td>
                                                <td><span class="badge badge-risk-C" id="modal-dev-risk-tag">C</span></td>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                                <div class="col-12">
                                    <div class="p-3 bg-light rounded border">
                                        <h6 class="fw-bold text-primary mb-2"><i class="bi bi-card-text me-2"></i>Ghi Chú & Đặc Điểm Cấu Hình</h6>
                                        <div class="small text-muted" id="modal-dev-notes">Không có ghi chú bổ sung.</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- TAB 2: CẤU KIỆN & PHỤ KIỆN -->
                        <div class="tab-pane fade" id="tab-modal-accessories">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h6 class="fw-bold text-dark mb-0">Cây Cấu Kiện / Đầu Dò / Phụ Kiện Đi Kèm (Parent-Child)</h6>
                                <span class="badge bg-primary font-mono" id="modal-acc-badge">0 phụ kiện</span>
                            </div>
                            <div class="table-responsive border rounded">
                                <table class="table table-hover align-middle mb-0" style="font-size: 0.84rem;">
                                    <thead class="table-light">
                                        <tr>
                                            <th>LOẠI PHỤ KIỆN</th>
                                            <th>TÊN CẤU KIỆN / MODEL</th>
                                            <th>SỐ SERIAL (S/N)</th>
                                            <th>TRẠNG THÁI</th>
                                            <th>GHI CHÚ / PHÒNG</th>
                                        </tr>
                                    </thead>
                                    <tbody id="modal-accessories-table-body">
                                        <tr><td colspan="5" class="text-center py-4 text-muted">Không có phụ kiện rời đi kèm.</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- TAB 3: KIỂM ĐỊNH & HIỆU CHUẨN -->
                        <div class="tab-pane fade" id="tab-modal-calibration">
                            <h6 class="fw-bold text-dark mb-3">Hồ Sơ Giấy Chứng Nhận Kiểm Định & Hiệu Chuẩn (Thông tư 05/2022/TT-BYT)</h6>
                            <div class="table-responsive border rounded">
                                <table class="table table-hover align-middle mb-0" style="font-size: 0.84rem;">
                                    <thead class="table-light">
                                        <tr>
                                            <th>SỐ GCN KIỂM ĐỊNH</th>
                                            <th>NGÀY THỰC HIỆN</th>
                                            <th>HẠN KIỂM ĐỊNH KẾ TIẾP</th>
                                            <th>SỐ TEM KIỂM ĐỊNH</th>
                                            <th>ĐƠN VỊ KIỂM ĐỊNH</th>
                                            <th class="text-center">KẾT LUẬN</th>
                                        </tr>
                                    </thead>
                                    <tbody id="modal-calibration-table-body">
                                        <tr><td colspan="6" class="text-center py-4 text-muted">Chưa có bản ghi kiểm định trong hệ thống.</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- TAB 4: SỔ LÝ LỊCH & BẢO TRÌ -->
                        <div class="tab-pane fade" id="tab-modal-maintenance">
                            <h6 class="fw-bold text-dark mb-3">Sổ Lý Lịch Máy Điện Tử & Nhật Ký Công Tác (BM05_TA5.TTBYT.QT.04)</h6>
                            <div class="table-responsive border rounded">
                                <table class="table table-hover align-middle mb-0" style="font-size: 0.84rem;">
                                    <thead class="table-light">
                                        <tr>
                                            <th>NGÀY THỰC HIỆN</th>
                                            <th>LOẠI CÔNG TÁC</th>
                                            <th>NGƯỜI THỰC HIỆN</th>
                                            <th>NỘI DUNG CHI TIẾT</th>
                                        </tr>
                                    </thead>
                                    <tbody id="modal-maintenance-table-body">
                                        <tr><td colspan="4" class="text-center py-4 text-muted">Chưa có nhật ký bảo dưỡng nào.</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!-- TAB 5: TRUY VẾT SEMANTICA -->
                        <div class="tab-pane fade" id="tab-modal-provenance">
                            <h6 class="fw-bold text-dark mb-2">Chuỗi Giải Trình Ngữ Nghĩa Semantica Context Graph (W3C PROV-O)</h6>
                            <p class="text-muted small mb-3">Liên kết xác thực từ Hợp đồng mua sắm, Nhà thầu, Khoa phòng đến Giấy kiểm định scan gốc.</p>
                            <div id="modal-provenance-content" class="p-3 bg-light border rounded font-mono small">
                                Đang tải chuỗi giải trình...
                            </div>
                        </div>

                    </div>
                </div>

                <!-- Footer Actions -->
                <div class="modal-footer bg-light px-4 py-3 border-top d-flex justify-content-between">
                    <div class="d-flex gap-2">
                        <button type="button" class="btn btn-outline-primary btn-clinical" id="modal-btn-transfer">
                            <i class="bi bi-arrow-left-right me-1"></i> Lập Phiếu Điều Chuyển (QT.08)
                        </button>
                        <button type="button" class="btn btn-outline-secondary btn-clinical" id="modal-btn-wo">
                            <i class="bi bi-tools me-1"></i> Tạo Phiếu Bảo Trì (SpeedMaint)
                        </button>
                    </div>
                    <button type="button" class="btn btn-secondary btn-clinical px-4" data-bs-dismiss="modal">Đóng</button>
                </div>
            </div>
        </div>
    </div>
"""

with open(html_path, "r", encoding="utf-8") as f:
    html_text = f.read()

# Replace or insert modal before </main> or </body>
if "id=\"deviceDetailsModal\"" not in html_text:
    html_text = html_text.replace("<!-- MODAL: DEVICE ACCESSORIES DRAWER -->", device_modal_html + "\n    <!-- MODAL: DEVICE ACCESSORIES DRAWER -->")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_text)
    print("✅ Đã chèn modal `#deviceDetailsModal` vào `web/index.html`!")
else:
    print("ℹ️ Modal `#deviceDetailsModal` đã tồn tại trong `web/index.html`.")

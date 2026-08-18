/**
 * Medical Device Management System (BV Quận 7)
 * Frontend Application Logic - Taste-Skill Elevated UI
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('🏥 Hệ thống Quản lý Trang thiết bị Y tế BV Quận 7 đã khởi chạy');

    const app = {
        devices: [],
        facilities: [],
        categories: [],
        currentFilters: {
            search: '',
            facility_id: '',
            category_id: '',
            alert_status: '',
            status: '',
            limit: 200,
            offset: 0
        },
        searchTimeout: null,

        async init() {
            this.setupEventListeners();
            await this.loadInitialData();
            await this.loadDevices();
        },

        setupEventListeners() {
            // Search input với debounce
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    clearTimeout(this.searchTimeout);
                    this.searchTimeout = setTimeout(() => {
                        this.currentFilters.search = e.target.value;
                        this.loadDevices();
                    }, 300);
                });
            }

            // Filter dropdowns
            const facilityFilter = document.getElementById('filter-facility');
            if (facilityFilter) {
                facilityFilter.addEventListener('change', (e) => {
                    this.currentFilters.facility_id = e.target.value;
                    this.loadDevices();
                });
            }

            const categoryFilter = document.getElementById('filter-category');
            if (categoryFilter) {
                categoryFilter.addEventListener('change', (e) => {
                    this.currentFilters.category_id = e.target.value;
                    this.loadDevices();
                });
            }

            const statusFilter = document.getElementById('filter-alert-status');
            if (statusFilter) {
                statusFilter.addEventListener('change', (e) => {
                    this.currentFilters.alert_status = e.target.value;
                    this.loadDevices();
                });
            }

            // Reset filters
            const resetBtn = document.getElementById('btn-reset-filters');
            if (resetBtn) {
                resetBtn.addEventListener('click', () => {
                    if (searchInput) searchInput.value = '';
                    if (facilityFilter) facilityFilter.value = '';
                    if (categoryFilter) categoryFilter.value = '';
                    if (statusFilter) statusFilter.value = '';
                    this.currentFilters = {
                        search: '',
                        facility_id: '',
                        category_id: '',
                        alert_status: '',
                        status: '',
                        limit: 200,
                        offset: 0
                    };
                    this.loadDevices();
                });
            }

            // Refresh button
            const refreshBtn = document.getElementById('btn-refresh');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', () => {
                    this.loadInitialData();
                    this.loadDevices();
                });
            }
        },

        async loadInitialData() {
            try {
                // Thống kê KPI
                const summary = await apiClient.getSummary();
                this.renderSummary(summary);

                // Danh mục khoa phòng
                this.facilities = await apiClient.getFacilities();
                this.renderFacilityOptions(this.facilities);

                // Danh mục loại thiết bị
                this.categories = await apiClient.getCategories();
                this.renderCategoryOptions(this.categories);
            } catch (err) {
                console.error('Lỗi nạp dữ liệu khởi tạo:', err);
            }
        },

        async loadDevices() {
            try {
                this.showLoading();
                const devices = await apiClient.getDevices(this.currentFilters);
                this.devices = devices;
                this.renderDevicesTable(devices);
            } catch (err) {
                console.error('Lỗi khi tải danh sách thiết bị:', err);
                this.showTableError('Không thể tải danh sách thiết bị từ máy chủ.');
            }
        },

        showLoading() {
            const tbody = document.getElementById('devices-body');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center py-5">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Đang tải...</span>
                            </div>
                            <p class="mt-2 text-muted fw-semibold">Đang truy vấn cơ sở dữ liệu thiết bị...</p>
                        </td>
                    </tr>
                `;
            }
        },

        showTableError(msg) {
            const tbody = document.getElementById('devices-body');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center py-4 text-danger">
                            <i class="bi bi-exclamation-triangle-fill fs-3"></i>
                            <p class="mt-2 fw-semibold">${msg}</p>
                        </td>
                    </tr>
                `;
            }
        },

        renderSummary(summary) {
            const elTotal = document.getElementById('kpi-total');
            const elOk = document.getElementById('kpi-ok');
            const elWarning = document.getElementById('kpi-warning');
            const elOverdue = document.getElementById('kpi-overdue');

            if (elTotal) elTotal.textContent = Number(summary.total_devices || 0).toLocaleString('vi-VN');
            if (elOk) elOk.textContent = Number(summary.ok_count || 0).toLocaleString('vi-VN');
            if (elWarning) elWarning.textContent = Number(summary.warning_count || 0).toLocaleString('vi-VN');
            if (elOverdue) elOverdue.textContent = Number(summary.overdue_count || 0).toLocaleString('vi-VN');
        },

        renderFacilityOptions(facilities) {
            const select = document.getElementById('filter-facility');
            if (!select) return;
            select.innerHTML = '<option value="">-- Tất cả Khoa / Phòng ban --</option>' +
                facilities.map(f => `<option value="${f.id}">${f.name} (${f.device_count || 0})</option>`).join('');
        },

        renderCategoryOptions(categories) {
            const select = document.getElementById('filter-category');
            if (!select) return;
            select.innerHTML = '<option value="">-- Tất cả Phân loại --</option>' +
                categories.map(c => `<option value="${c.id}">${c.name} (${c.device_count || 0})</option>`).join('');
        },

        renderDevicesTable(devices) {
            const tbody = document.getElementById('devices-body');
            const countLabel = document.getElementById('table-count');
            if (countLabel) {
                countLabel.textContent = `Hiển thị ${devices.length} thiết bị`;
            }

            if (!tbody) return;

            if (!devices || devices.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center py-5 text-muted">
                            <i class="bi bi-inbox fs-2"></i>
                            <p class="mt-2">Không tìm thấy thiết bị nào phù hợp với bộ lọc.</p>
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = devices.map(d => {
                const alertStatus = d.alert_status || 'NO_DATA';
                let badgeHtml = '';

                if (alertStatus === 'OVERDUE') {
                    badgeHtml = `<span class="badge-status-pill status-overdue"><i class="bi bi-x-circle-fill"></i> Quá hạn KĐ</span>`;
                } else if (alertStatus === 'WARNING') {
                    badgeHtml = `<span class="badge-status-pill status-warning"><i class="bi bi-exclamation-triangle-fill"></i> Cảnh báo 30N</span>`;
                } else if (alertStatus === 'OK') {
                    badgeHtml = `<span class="badge-status-pill status-ok"><i class="bi bi-check-circle-fill"></i> Đạt chuẩn</span>`;
                } else {
                    badgeHtml = `<span class="badge-status-pill status-nodata"><i class="bi bi-dash-circle"></i> Chưa KĐ</span>`;
                }

                const riskClass = `risk-tag risk-tag-${(d.risk_level || 'a').toLowerCase()}`;
                const pdfBtn = d.source_pdf ? `
                    <a href="${apiClient.getPdfUrl(d.source_pdf)}" target="_blank" class="btn btn-sm btn-clinical-pdf btn-clinical" title="Xem PDF gốc">
                        <i class="bi bi-file-earmark-pdf"></i> PDF
                    </a>
                ` : '';

                return `
                    <tr>
                        <td><span class="fw-bold text-primary font-mono">${d.serial_no || '-'}</span></td>
                        <td>
                            <div class="fw-bold">${d.device_name || 'Thiết bị y tế'}</div>
                            <small class="text-muted">${d.manufacturer || '-'} ${d.country_of_manufacturer ? `• ${d.country_of_manufacturer}` : ''}</small>
                        </td>
                        <td><span class="badge bg-light text-dark border font-mono">${d.model || '-'}</span></td>
                        <td><span class="${riskClass}">Mức ${d.risk_level || 'A'}</span></td>
                        <td><i class="bi bi-hospital text-muted me-1"></i>${d.facility || 'Chưa phân bổ'}</td>
                        <td class="font-mono text-muted">${apiClient.formatDate(d.calibration_date)}</td>
                        <td class="font-mono"><strong class="${alertStatus === 'OVERDUE' ? 'text-danger' : alertStatus === 'WARNING' ? 'text-warning' : ''}">${apiClient.formatDate(d.recalibration_date)}</strong></td>
                        <td>${badgeHtml}</td>
                        <td class="text-end">
                            <button class="btn btn-sm btn-clinical-primary btn-clinical me-1" onclick="app.viewDetails(${d.id})" title="Xem lý lịch máy">
                                <i class="bi bi-eye"></i>
                            </button>
                            ${pdfBtn}
                        </td>
                    </tr>
                `;
            }).join('');
        },

        async viewDetails(deviceId) {
            try {
                const device = await apiClient.getDevice(deviceId);
                const modalTitle = document.getElementById('device-modal-title');
                const modalBody = document.getElementById('device-modal-body');

                if (modalTitle) {
                    modalTitle.innerHTML = `<i class="bi bi-heart-pulse-fill text-primary me-2"></i>Hồ Sơ Thiết Bị: ${device.device_name}`;
                }

                if (modalBody) {
                    const certsHtml = (device.certificates && device.certificates.length > 0)
                        ? device.certificates.map(c => `
                            <div class="list-group-item border-0 mb-2 p-3 bg-light rounded-3">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h6 class="mb-1 text-primary fw-bold"><i class="bi bi-award me-1"></i>Số GCN: ${c.certificate_no || 'N/A'}</h6>
                                    <span class="badge-status-pill ${c.result_status === 'OK' ? 'status-ok' : 'status-overdue'}">${c.result_status || 'OK'}</span>
                                </div>
                                <div class="row text-muted small mt-2 g-2">
                                    <div class="col-6">Ngày KĐ: <strong class="font-mono text-dark">${apiClient.formatDate(c.calibration_date)}</strong></div>
                                    <div class="col-6">Hạn KĐ kế tiếp: <strong class="font-mono text-dark">${apiClient.formatDate(c.recalibration_date)}</strong></div>
                                    <div class="col-6">Số tem: <strong class="font-mono text-dark">${c.stamp_no || '-'}</strong></div>
                                    <div class="col-6">Đơn vị KĐ: <strong class="text-dark">${c.calibrated_by || '-'}</strong></div>
                                </div>
                                ${c.source_pdf ? `
                                    <div class="mt-2 pt-2 border-top">
                                        <a href="${apiClient.getPdfUrl(c.source_pdf)}" target="_blank" class="btn btn-sm btn-clinical-pdf btn-clinical">
                                            <i class="bi bi-file-earmark-pdf me-1"></i> Xem tệp chứng chỉ PDF gốc
                                        </a>
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')
                        : '<p class="text-muted p-3 bg-light rounded-3">Chưa có lịch sử chứng chỉ kiểm định.</p>';

                    const qrData = encodeURIComponent(`TB:${device.device_name}|SN:${device.serial_no}|MD:${device.model}|KHOA:${device.facility || ''}`);
                    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${qrData}`;

                    modalBody.innerHTML = `
                        <div class="row g-3">
                            <div class="col-md-8">
                                <div class="device-spec-grid">
                                    <div class="spec-item">
                                        <div class="spec-label">Tên thiết bị</div>
                                        <div class="spec-value text-primary">${device.device_name}</div>
                                    </div>
                                    <div class="spec-item">
                                        <div class="spec-label">Số Serial (S/N)</div>
                                        <div class="spec-value font-mono">${device.serial_no}</div>
                                    </div>
                                    <div class="spec-item">
                                        <div class="spec-label">Model / Ký hiệu</div>
                                        <div class="spec-value font-mono">${device.model}</div>
                                    </div>
                                    <div class="spec-item">
                                        <div class="spec-label">Khoa / Phòng ban</div>
                                        <div class="spec-value">${device.facility || 'Chưa phân bổ'}</div>
                                    </div>
                                    <div class="spec-item">
                                        <div class="spec-label">Hãng sản xuất</div>
                                        <div class="spec-value">${device.manufacturer || '-'}</div>
                                    </div>
                                    <div class="spec-item">
                                        <div class="spec-label">Nước sản xuất</div>
                                        <div class="spec-value">${device.country_of_manufacturer || '-'}</div>
                                    </div>
                                    <div class="spec-item">
                                        <div class="spec-label">Phân loại rủi ro</div>
                                        <div class="spec-value"><span class="risk-tag risk-tag-${(device.risk_level || 'a').toLowerCase()}">Mức ${device.risk_level || 'A'} (Nghị định 98)</span></div>
                                    </div>
                                    <div class="spec-item">
                                        <div class="spec-label">Trạng thái vận hành</div>
                                        <div class="spec-value"><span class="badge-status-pill status-ok">${device.status || 'Đang sử dụng'}</span></div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 text-center">
                                <div class="p-3 bg-light rounded-3 border">
                                    <img src="${qrUrl}" alt="QR Code" class="img-fluid rounded mb-2 shadow-sm" style="width: 130px; height: 130px;">
                                    <div class="small fw-bold">NHÃN MÃ QR CODE</div>
                                    <small class="text-muted d-block">Quét camera xem hồ sơ</small>
                                </div>
                            </div>
                        </div>

                        <hr class="my-4">
                        <h6 class="fw-bold mb-3 d-flex align-items-center gap-2">
                            <i class="bi bi-journal-check text-success"></i>
                            <span>Lịch Sử Kiểm Định & Hiệu Chuẩn</span>
                        </h6>
                        <div class="list-group border-0">
                            ${certsHtml}
                        </div>
                    `;
                }

                const modal = new bootstrap.Modal(document.getElementById('device-detail-modal'));
                modal.show();
            } catch (err) {
                console.error('Lỗi xem chi tiết:', err);
                alert('Không thể tải chi tiết thiết bị.');
            }
        }
    };

    window.app = app;
    app.init();
});
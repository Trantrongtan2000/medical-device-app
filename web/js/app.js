/**
 * Medical Device Management System (BV Quận 7)
 * Smart Management Frontend Application Logic
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('🏥 Hệ thống Quản lý Trang thiết bị Y tế Thông minh đã sẵn sàng');

    const app = {
        devices: [],
        selectedDeviceIds: new Set(),
        facilities: [],
        categories: [],
        schedules: [],
        workOrders: [],
        currentFilters: {
            search: '',
            facility_id: '',
            category_id: '',
            alert_status: '',
            risk_level: '',
            status: '',
            limit: 300,
            offset: 0
        },
        searchTimeout: null,

        async init() {
            this.setupEventListeners();
            await this.loadInitialData();
            await this.loadDevices();
            await this.loadSchedules();
            await this.loadWorkOrders();
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
                    }, 250);
                });
            }

            // Quick Filter Chips
            const chips = document.querySelectorAll('.chip-btn');
            chips.forEach(chip => {
                chip.addEventListener('click', (e) => {
                    chips.forEach(c => c.classList.remove('active'));
                    chip.classList.add('active');

                    const filterType = chip.getAttribute('data-filter');
                    const searchKw = chip.getAttribute('data-search');
                    const riskKw = chip.getAttribute('data-risk');

                    if (filterType === 'all') {
                        this.currentFilters.alert_status = '';
                        this.currentFilters.search = '';
                        this.currentFilters.risk_level = '';
                    } else if (filterType) {
                        this.currentFilters.alert_status = filterType;
                        this.currentFilters.search = '';
                        this.currentFilters.risk_level = '';
                    } else if (searchKw) {
                        this.currentFilters.search = searchKw;
                        this.currentFilters.alert_status = '';
                        this.currentFilters.risk_level = '';
                    } else if (riskKw) {
                        this.currentFilters.risk_level = riskKw;
                        this.currentFilters.alert_status = '';
                        this.currentFilters.search = '';
                    }

                    if (searchInput) searchInput.value = this.currentFilters.search;
                    this.loadDevices();
                });
            });

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
                    chips.forEach(c => c.classList.remove('active'));
                    document.querySelector('[data-filter="all"]')?.classList.add('active');

                    this.currentFilters = {
                        search: '',
                        facility_id: '',
                        category_id: '',
                        alert_status: '',
                        risk_level: '',
                        status: '',
                        limit: 300,
                        offset: 0
                    };
                    this.loadDevices();
                });
            }

            // CSV Export button
            const exportBtn = document.getElementById('btn-export-csv');
            if (exportBtn) {
                exportBtn.addEventListener('click', () => {
                    const exportUrl = apiClient.getCsvExportUrl(this.currentFilters);
                    window.open(exportUrl, '_blank');
                });
            }

            // Check All Devices checkbox
            const checkAll = document.getElementById('check-all-devices');
            if (checkAll) {
                checkAll.addEventListener('change', (e) => {
                    const isChecked = e.target.checked;
                    this.devices.forEach(d => {
                        if (isChecked) this.selectedDeviceIds.add(d.id);
                        else this.selectedDeviceIds.delete(d.id);
                    });
                    this.updateCheckboxUI();
                    this.renderQrStudio();
                });
            }

            // Select all for QR Button
            const selectAllQrBtn = document.getElementById('btn-select-all-qr');
            if (selectAllQrBtn) {
                selectAllQrBtn.addEventListener('click', () => {
                    this.devices.forEach(d => this.selectedDeviceIds.add(d.id));
                    this.updateCheckboxUI();
                    this.renderQrStudio();
                    // Switch to QR Tab
                    const qrTabTrigger = document.getElementById('tab-qr-btn');
                    if (qrTabTrigger) {
                        const tab = new bootstrap.Tab(qrTabTrigger);
                        tab.show();
                    }
                });
            }

            // Incident form submit
            const incidentForm = document.getElementById('incident-form');
            if (incidentForm) {
                incidentForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const deviceId = document.getElementById('incident-device-select').value;
                    const priority = document.getElementById('incident-priority').value;
                    const issueType = document.getElementById('incident-type').value;
                    const reporter = document.getElementById('incident-reporter').value;
                    const desc = document.getElementById('incident-desc').value;

                    try {
                        await apiClient.createWorkOrder({
                            device_id: parseInt(deviceId),
                            reported_by: reporter,
                            priority: priority,
                            issue_type: issueType,
                            description: desc
                        });

                        alert('✅ Đã ghi nhận phiếu báo hỏng thành công!');
                        incidentForm.reset();
                        const modalEl = document.getElementById('incidentModal');
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        if (modal) modal.hide();

                        await this.loadInitialData();
                        await this.loadDevices();
                        await this.loadWorkOrders();
                    } catch (err) {
                        alert('Lỗi tạo phiếu: ' + err.message);
                    }
                });
            }
        },

        async loadInitialData() {
            try {
                const summary = await apiClient.getSummary();
                this.renderSummary(summary);

                this.facilities = await apiClient.getFacilities();
                this.renderFacilityOptions(this.facilities);
                this.renderAnalyticsFacilities(this.facilities);

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
                this.populateIncidentDeviceOptions(devices);
                this.renderQrStudio();
            } catch (err) {
                console.error('Lỗi khi tải danh sách thiết bị:', err);
                this.showTableError('Không thể tải danh sách thiết bị từ máy chủ.');
            }
        },

        async loadSchedules() {
            try {
                const schedules = await apiClient.getSchedules();
                this.schedules = schedules;
                this.renderSchedules(schedules);
            } catch (err) {
                console.error('Lỗi nạp lịch trình:', err);
            }
        },

        async loadWorkOrders() {
            try {
                const orders = await apiClient.getWorkOrders();
                this.workOrders = orders;
                this.renderWorkOrders(orders);
            } catch (err) {
                console.error('Lỗi nạp work orders:', err);
            }
        },

        showLoading() {
            const tbody = document.getElementById('devices-body');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="10" class="text-center py-5">
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
                        <td colspan="10" class="text-center py-4 text-danger">
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

        populateIncidentDeviceOptions(devices) {
            const select = document.getElementById('incident-device-select');
            if (!select) return;
            select.innerHTML = '<option value="">-- Chọn thiết bị cần báo hỏng --</option>' +
                devices.map(d => `<option value="${d.id}">${d.device_name} (SN: ${d.serial_no}) - ${d.facility || 'Toàn viện'}</option>`).join('');
        },

        toggleDeviceSelection(id) {
            if (this.selectedDeviceIds.has(id)) {
                this.selectedDeviceIds.delete(id);
            } else {
                this.selectedDeviceIds.add(id);
            }
            this.updateCheckboxUI();
            this.renderQrStudio();
        },

        updateCheckboxUI() {
            document.querySelectorAll('.device-checkbox').forEach(cb => {
                const id = parseInt(cb.getAttribute('data-id'));
                cb.checked = this.selectedDeviceIds.has(id);
            });
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
                        <td colspan="10" class="text-center py-5 text-muted">
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
                        <i class="bi bi-file-earmark-pdf"></i>
                    </a>
                ` : '';

                const isChecked = this.selectedDeviceIds.has(d.id) ? 'checked' : '';

                return `
                    <tr>
                        <td>
                            <input type="checkbox" class="device-checkbox" data-id="${d.id}" ${isChecked} onchange="app.toggleDeviceSelection(${d.id})">
                        </td>
                        <td><span class="fw-bold text-primary font-mono">${d.serial_no || '-'}</span></td>
                        <td>
                            <div class="fw-bold text-dark">${d.device_name || 'Thiết bị y tế'}</div>
                            <small class="text-muted">${d.manufacturer || '-'} ${d.country_of_manufacturer ? `• ${d.country_of_manufacturer}` : ''}</small>
                        </td>
                        <td><span class="badge bg-light text-dark border font-mono">${d.model || '-'}</span></td>
                        <td><span class="${riskClass}">Mức ${d.risk_level || 'A'}</span></td>
                        <td><i class="bi bi-hospital text-muted me-1"></i>${d.facility || 'Chưa phân bổ'}</td>
                        <td class="font-mono text-muted">${apiClient.formatDate(d.calibration_date)}</td>
                        <td class="font-mono"><strong class="${alertStatus === 'OVERDUE' ? 'text-danger' : alertStatus === 'WARNING' ? 'text-warning' : ''}">${apiClient.formatDate(d.recalibration_date)}</strong></td>
                        <td>${badgeHtml}</td>
                        <td class="text-end">
                            <button class="btn btn-sm btn-clinical-primary btn-clinical me-1" onclick="app.viewDetails(${d.id})" title="Xem hồ sơ chi tiết">
                                <i class="bi bi-eye"></i>
                            </button>
                            ${pdfBtn}
                        </td>
                    </tr>
                `;
            }).join('');
        },

        renderSchedules(schedules) {
            const tbody = document.getElementById('schedules-body');
            const alertList = document.getElementById('schedule-alerts-list');
            const countLabel = document.getElementById('schedule-count');

            if (countLabel) countLabel.textContent = `${schedules.length} Lịch trình`;

            if (tbody) {
                if (schedules.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">Không có lịch kiểm định.</td></tr>';
                } else {
                    tbody.innerHTML = schedules.map(s => `
                        <tr>
                            <td class="font-mono fw-bold text-primary">${apiClient.formatDate(s.due_date)}</td>
                            <td><div class="fw-bold">${s.device_name}</div><small class="text-muted">Model: ${s.model}</small></td>
                            <td><span class="font-mono badge bg-light text-dark border">${s.serial_no}</span></td>
                            <td>${s.facility || 'Toàn viện'}</td>
                            <td class="font-mono text-muted">${s.certificate_no || '-'}</td>
                            <td>
                                <span class="badge-status-pill ${s.alert_status === 'OVERDUE' ? 'status-overdue' : s.alert_status === 'WARNING' ? 'status-warning' : 'status-ok'}">
                                    ${s.alert_status || 'OK'}
                                </span>
                            </td>
                        </tr>
                    `).join('');
                }
            }

            if (alertList) {
                const upcoming = schedules.slice(0, 8);
                alertList.innerHTML = upcoming.map(u => `
                    <div class="list-group-item px-0 py-2 border-bottom">
                        <div class="d-flex justify-content-between align-items-center">
                            <strong class="text-dark small">${u.device_name}</strong>
                            <span class="font-mono small text-danger">${apiClient.formatDate(u.due_date)}</span>
                        </div>
                        <small class="text-muted d-block font-mono">SN: ${u.serial_no} • ${u.facility || ''}</small>
                    </div>
                `).join('');
            }
        },

        renderWorkOrders(orders) {
            const tbody = document.getElementById('workorders-body');
            if (!tbody) return;

            if (orders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">Chưa có phiếu báo hỏng nào.</td></tr>';
                return;
            }

            tbody.innerHTML = orders.map(o => `
                <tr>
                    <td class="font-mono fw-bold">WO-#${o.id}</td>
                    <td class="font-mono text-muted">${apiClient.formatDate(o.maintenance_date)}</td>
                    <td><div class="fw-bold">${o.device_name}</div><small class="font-mono text-muted">SN: ${o.serial_no}</small></td>
                    <td>${o.facility || 'Toàn viện'}</td>
                    <td><span class="badge bg-light text-dark border">${o.maintenance_type || 'REPAIR'}</span></td>
                    <td>${o.performed_by || '-'}</td>
                    <td class="small">${o.description || '-'}</td>
                    <td><span class="badge-status-pill status-ok">Đang xử lý</span></td>
                </tr>
            `).join('');
        },

        renderQrStudio() {
            const grid = document.getElementById('qr-labels-grid');
            if (!grid) return;

            const selectedList = this.devices.filter(d => this.selectedDeviceIds.has(d.id));
            const listToRender = selectedList.length > 0 ? selectedList : this.devices.slice(0, 12);

            grid.innerHTML = listToRender.map(d => {
                const qrData = encodeURIComponent(`BVQ7|TB:${d.device_name}|SN:${d.serial_no}|MD:${d.model}|KHOA:${d.facility || ''}`);
                const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=110x110&data=${qrData}`;

                return `
                    <div class="col-md-4 col-sm-6">
                        <div class="qr-label-card">
                            <img src="${qrUrl}" alt="QR" style="width: 85px; height: 85px;" class="rounded border">
                            <div class="qr-label-info">
                                <div class="qr-hospital">BV QUẬN 7 • TP.HCM</div>
                                <div class="qr-dev-name">${d.device_name}</div>
                                <div class="qr-serial">S/N: ${d.serial_no}</div>
                                <div class="text-muted" style="font-size: 0.72rem;">Model: ${d.model} • ${d.facility || 'Toàn viện'}</div>
                                <div class="text-muted" style="font-size: 0.68rem;">Hạn KĐ: ${apiClient.formatDate(d.recalibration_date)}</div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        },

        renderAnalyticsFacilities(facilities) {
            const list = document.getElementById('analytics-facilities-list');
            if (!list) return;

            list.innerHTML = facilities.map(f => `
                <div class="list-group-item px-0 py-2 border-bottom d-flex justify-content-between align-items-center">
                    <div>
                        <span class="fw-bold text-dark">${f.name}</span>
                        <small class="text-muted d-block">Mã khoa: ${f.code || '-'}</small>
                    </div>
                    <span class="badge bg-primary rounded-pill font-mono">${f.device_count || 0} máy</span>
                </div>
            `).join('');
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
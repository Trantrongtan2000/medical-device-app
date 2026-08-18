/**
 * Medical Device Management System (BV Quận 7)
 * Minimalist, High-Clarity Clinical Frontend Logic
 * Triết lý: "Less, but better" - Tối giản, tập trung vào thông tin cốt lõi
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('🏥 Hệ thống Quản lý Thiết bị Y tế BV Quận 7 (Giao diện Tinh Gọn) đã sẵn sàng');

    const app = {
        devices: [],
        selectedDeviceIds: new Set(),
        facilities: [],
        categories: [],
        schedules: [],
        workOrders: [],
        audits: [],
        currentFilters: {
            search: '',
            facility_id: '',
            alert_status: '',
            limit: 300,
            offset: 0
        },
        searchTimeout: null,

        async init() {
            this.setupEventListeners();
            await this.loadInitialData();
            await this.loadDevices();
            await this.loadAudits();
            await this.loadWorkOrders();
        },

        setupEventListeners() {
            // Sidebar Nav Tab switching
            const navButtons = document.querySelectorAll('.sidebar-nav .nav-link');
            const pageHeading = document.getElementById('page-heading');

            navButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    navButtons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    const targetId = btn.getAttribute('data-bs-target');
                    if (targetId) {
                        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('show', 'active'));
                        document.querySelector(targetId)?.classList.add('show', 'active');
                    }

                    const text = btn.querySelector('span')?.textContent || 'Quản lý TTBYT';
                    const iconClass = btn.querySelector('i')?.className || 'bi bi-grid-fill';
                    if (pageHeading) {
                        pageHeading.innerHTML = `<i class="${iconClass} text-primary me-2"></i>${text}`;
                    }
                });
            });

            // Search input
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

            // Facility Filter
            const facilityFilter = document.getElementById('filter-facility');
            if (facilityFilter) {
                facilityFilter.addEventListener('change', (e) => {
                    this.currentFilters.facility_id = e.target.value;
                    this.loadDevices();
                });
            }

            // Status Filter
            const statusFilter = document.getElementById('filter-alert-status');
            if (statusFilter) {
                statusFilter.addEventListener('change', (e) => {
                    this.currentFilters.alert_status = e.target.value;
                    this.loadDevices();
                });
            }

            // CSV Export
            const exportBtn = document.getElementById('btn-export-csv');
            if (exportBtn) {
                exportBtn.addEventListener('click', () => {
                    window.open(apiClient.getCsvExportUrl(this.currentFilters), '_blank');
                });
            }

            // Check All Devices
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

            // SpeedMaint Work Order Form Submit
            const woForm = document.getElementById('speedmaint-wo-form');
            if (woForm) {
                woForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const deviceId = document.getElementById('wo-device-select').value;
                    const title = document.getElementById('wo-title').value;
                    const workType = document.getElementById('wo-type').value;
                    const assignedTo = document.getElementById('wo-assigned-to').value;
                    const desc = document.getElementById('wo-desc').value;

                    try {
                        await apiClient.createWorkOrder({
                            device_id: parseInt(deviceId),
                            title: title,
                            work_type: workType,
                            start_date: new Date().toISOString().split('T')[0],
                            end_date: new Date().toISOString().split('T')[0],
                            assigned_to: assignedTo,
                            reporter: assignedTo,
                            description: desc
                        });

                        alert('✅ Đã lưu phiếu công việc thành công!');
                        woForm.reset();
                        bootstrap.Modal.getInstance(document.getElementById('speedmaintWorkOrderModal'))?.hide();
                        await this.loadInitialData();
                        await this.loadWorkOrders();
                    } catch (err) {
                        alert('Lỗi: ' + err.message);
                    }
                });
            }

            // Quick Audit Form Submit
            const auditForm = document.getElementById('audit-form');
            if (auditForm) {
                auditForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const deviceId = document.getElementById('audit-device-select').value;
                    const condition = document.getElementById('audit-condition').value;
                    const person = document.getElementById('audit-person').value;

                    try {
                        await apiClient.auditDevice({
                            device_id: parseInt(deviceId),
                            audited_by: person,
                            condition: condition,
                            notes: 'Kiểm kê định kỳ hiện trường'
                        });

                        alert('✅ Đã lưu kết quả kiểm kê!');
                        auditForm.reset();
                        bootstrap.Modal.getInstance(document.getElementById('quickAuditModal'))?.hide();
                        await this.loadInitialData();
                        await this.loadAudits();
                    } catch (err) {
                        alert('Lỗi: ' + err.message);
                    }
                });
            }

            // Transfer Form Submit
            const transferForm = document.getElementById('transfer-form');
            if (transferForm) {
                transferForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const deviceId = document.getElementById('transfer-device-select').value;
                    const toFacilityId = document.getElementById('transfer-target-facility').value;
                    const transferredBy = document.getElementById('transfer-person').value;
                    const reason = document.getElementById('transfer-reason').value;

                    try {
                        const res = await apiClient.transferDevice({
                            device_id: parseInt(deviceId),
                            to_facility_id: parseInt(toFacilityId),
                            transferred_by: transferredBy,
                            reason: reason
                        });

                        alert(res.message || '✅ Bàn giao thiết bị thành công!');
                        transferForm.reset();
                        bootstrap.Modal.getInstance(document.getElementById('transferModal'))?.hide();
                        await this.loadInitialData();
                        await this.loadDevices();
                    } catch (err) {
                        alert('Lỗi: ' + err.message);
                    }
                });
            }

            // Gemini AI Chat Submit
            const aiForm = document.getElementById('ai-chat-form');
            const aiInput = document.getElementById('ai-chat-input');
            const aiMsgBox = document.getElementById('ai-chat-messages');

            if (aiForm) {
                aiForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const text = aiInput.value.trim();
                    if (!text) return;

                    if (aiMsgBox) {
                        aiMsgBox.innerHTML += `
                            <div class="d-flex justify-content-end mb-2">
                                <div class="p-2 bg-primary text-white rounded-3 small" style="max-width: 80%;">
                                    <strong>Bạn:</strong> ${text}
                                </div>
                            </div>
                        `;
                        aiMsgBox.scrollTop = aiMsgBox.scrollHeight;
                    }

                    aiInput.value = '';

                    try {
                        const res = await apiClient.aiChat(text);
                        if (aiMsgBox) {
                            aiMsgBox.innerHTML += `
                                <div class="d-flex mb-2">
                                    <div class="p-2 bg-white border rounded-3 small" style="max-width: 85%; white-space: pre-wrap;">
                                        <strong class="text-primary">Gemini BME:</strong><br>${res.reply}
                                    </div>
                                </div>
                            `;
                            aiMsgBox.scrollTop = aiMsgBox.scrollHeight;
                        }
                    } catch (err) {
                        if (aiMsgBox) {
                            aiMsgBox.innerHTML += `<div class="text-danger small">Lỗi: ${err.message}</div>`;
                        }
                    }
                });
            }

            // Mistral OCR Sample trigger
            const ocrBtn = document.getElementById('btn-run-sample-ocr');
            if (ocrBtn) {
                ocrBtn.addEventListener('click', async () => {
                    const jsonPre = document.getElementById('ocr-json-preview');
                    if (jsonPre) jsonPre.textContent = '⏳ Đang bóc tách chứng chỉ...';

                    try {
                        const ocrRes = await apiClient.processOcr('GCN_Monitor_2026.pdf');
                        if (jsonPre) jsonPre.textContent = JSON.stringify(ocrRes.extracted_fields || {}, null, 2);
                    } catch (err) {
                        if (jsonPre) jsonPre.textContent = 'Lỗi: ' + err.message;
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

                this.categories = await apiClient.getCategories();
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
                this.populateTransferDeviceOptions(devices);
                this.populateAuditDeviceOptions(devices);
                this.renderQrStudio();
            } catch (err) {
                console.error('Lỗi tải danh sách thiết bị:', err);
                this.showTableError('Không thể tải danh sách thiết bị.');
            }
        },

        async loadAudits() {
            try {
                const audits = await apiClient.getAudits();
                this.audits = audits;
                this.renderAudits(audits);
            } catch (err) {
                console.error('Lỗi nạp kiểm kê:', err);
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
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Đang tải dữ liệu thiết bị...</td></tr>`;
            }
        },

        showTableError(msg) {
            const tbody = document.getElementById('devices-body');
            if (tbody) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-3 text-danger">${msg}</td></tr>`;
            }
        },

        renderSummary(summary) {
            const sideTotal = document.getElementById('side-kpi-total');
            const sideAvail = document.getElementById('side-kpi-avail');
            const navBadgeTotal = document.getElementById('nav-badge-total');
            const navBadgeAudits = document.getElementById('nav-badge-audits');

            if (sideTotal) sideTotal.textContent = Number(summary.total_devices || 0).toLocaleString('vi-VN');
            if (sideAvail) sideAvail.textContent = `${summary.availability_rate || 100}%`;
            if (navBadgeTotal) navBadgeTotal.textContent = Number(summary.total_devices || 0).toLocaleString('vi-VN');
            if (navBadgeAudits) navBadgeAudits.textContent = `${summary.audited_count || 0}`;
        },

        renderFacilityOptions(facilities) {
            const select = document.getElementById('filter-facility');
            const transferTargetSelect = document.getElementById('transfer-target-facility');

            const optionsHtml = '<option value="">-- Chọn Khoa / Vị trí --</option>' +
                facilities.map(f => `<option value="${f.id}">${f.name} (${f.device_count || 0})</option>`).join('');

            if (select) select.innerHTML = '<option value="">-- Tất cả Khoa / Vị trí --</option>' +
                facilities.map(f => `<option value="${f.id}">${f.name} (${f.device_count || 0})</option>`).join('');

            if (transferTargetSelect) transferTargetSelect.innerHTML = optionsHtml;
        },

        populateIncidentDeviceOptions(devices) {
            const select = document.getElementById('wo-device-select');
            if (!select) return;
            select.innerHTML = '<option value="">-- Chọn thiết bị --</option>' +
                devices.map(d => `<option value="${d.id}">${d.asset_tag || ''} - ${d.device_name} (SN: ${d.serial_no})</option>`).join('');
        },

        populateTransferDeviceOptions(devices) {
            const select = document.getElementById('transfer-device-select');
            if (!select) return;
            select.innerHTML = '<option value="">-- Chọn thiết bị cần bàn giao --</option>' +
                devices.map(d => `<option value="${d.id}">${d.asset_tag || ''} - ${d.device_name} [${d.facility || 'Chưa rõ'}]</option>`).join('');
        },

        populateAuditDeviceOptions(devices) {
            const select = document.getElementById('audit-device-select');
            if (!select) return;
            select.innerHTML = '<option value="">-- Chọn thiết bị cần kiểm kê --</option>' +
                devices.map(d => `<option value="${d.id}">${d.asset_tag || ''} - ${d.device_name} (SN: ${d.serial_no})</option>`).join('');
        },

        toggleDeviceSelection(id) {
            if (this.selectedDeviceIds.has(id)) this.selectedDeviceIds.delete(id);
            else this.selectedDeviceIds.add(id);
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
            if (!tbody) return;

            if (!devices || devices.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">Không tìm thấy thiết bị phù hợp.</td></tr>`;
                return;
            }

            // Clean 6-Column Minimalist Row
            tbody.innerHTML = devices.map(d => {
                const alertStatus = d.alert_status || 'NO_DATA';
                let badgeHtml = '';

                if (alertStatus === 'OVERDUE') {
                    badgeHtml = `<span class="badge-clean-status status-overdue"><i class="bi bi-x-circle-fill"></i> Quá hạn</span>`;
                } else if (alertStatus === 'WARNING') {
                    badgeHtml = `<span class="badge-clean-status status-warning"><i class="bi bi-exclamation-triangle-fill"></i> Cảnh báo 30N</span>`;
                } else if (alertStatus === 'OK') {
                    badgeHtml = `<span class="badge-clean-status status-ok"><i class="bi bi-check-circle-fill"></i> Đạt chuẩn</span>`;
                } else {
                    badgeHtml = `<span class="badge-clean-status status-nodata"><i class="bi bi-dash"></i> Chưa KĐ</span>`;
                }

                const isChecked = this.selectedDeviceIds.has(d.id) ? 'checked' : '';

                return `
                    <tr>
                        <td>
                            <input type="checkbox" class="device-checkbox" data-id="${d.id}" ${isChecked} onchange="app.toggleDeviceSelection(${d.id})">
                        </td>
                        <td><span class="badge bg-light text-dark border font-mono">${d.asset_tag || `BVQ7-TTB-${d.id}`}</span></td>
                        <td>
                            <div class="fw-bold text-dark">${d.device_name || 'Thiết bị y tế'}</div>
                            <div class="text-muted font-mono" style="font-size: 0.75rem;">Model: ${d.model || '-'} • SN: ${d.serial_no || '-'}</div>
                        </td>
                        <td class="text-secondary">${d.facility || 'Kho lưu trữ'}</td>
                        <td class="font-mono ${alertStatus === 'OVERDUE' ? 'text-danger fw-bold' : ''}">${apiClient.formatDate(d.recalibration_date)}</td>
                        <td>${badgeHtml}</td>
                        <td class="text-end">
                            <button class="btn btn-sm btn-outline-primary btn-clinical" onclick="app.viewDetails(${d.id})">
                                Xem hồ sơ
                            </button>
                        </td>
                    </tr>
                `;
            }).join('');
        },

        renderAudits(audits) {
            const tbody = document.getElementById('audits-table-body');
            if (!tbody) return;

            if (audits.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center py-3 text-muted">Chưa có bản ghi kiểm kê nào.</td></tr>';
                return;
            }

            tbody.innerHTML = audits.map(a => `
                <tr>
                    <td class="font-mono text-muted">${apiClient.formatDate(a.audit_date)}</td>
                    <td><span class="badge bg-light text-dark border font-mono">${a.asset_tag}</span></td>
                    <td class="fw-semibold">${a.device_name}</td>
                    <td>${a.facility || 'Toàn viện'}</td>
                    <td>${a.auditor || '-'}</td>
                    <td><span class="badge-clean-status status-ok"><i class="bi bi-check2"></i> Đã kiểm kê</span></td>
                </tr>
            `).join('');
        },

        renderWorkOrders(orders) {
            const tbody = document.getElementById('workorders-body');
            const countBadge = document.getElementById('nav-badge-wo');
            if (countBadge) countBadge.textContent = `${orders.length}`;
            if (!tbody) return;

            if (orders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center py-3 text-muted">Không có phiếu công việc.</td></tr>';
                return;
            }

            tbody.innerHTML = orders.map(o => `
                <tr>
                    <td><span class="font-mono fw-bold text-primary">#${o.task_code || `260${o.id}`}</span></td>
                    <td><div class="fw-semibold">${o.work_type || 'PM định kỳ'}</div><small class="text-muted">${o.description || '-'}</small></td>
                    <td>${o.device_name || 'Thiết bị y tế'}</td>
                    <td>${o.assigned_to || '-'}</td>
                    <td><span class="badge-clean-status status-ok">Hoàn thành</span></td>
                </tr>
            `).join('');
        },

        renderQrStudio() {
            const grid = document.getElementById('qr-labels-grid');
            if (!grid) return;

            const selectedList = this.devices.filter(d => this.selectedDeviceIds.has(d.id));
            const listToRender = selectedList.length > 0 ? selectedList : this.devices.slice(0, 8);

            grid.innerHTML = listToRender.map(d => {
                const assetTag = d.asset_tag || `BVQ7-TTB-${d.id}`;
                const qrData = encodeURIComponent(`TAG:${assetTag}|TB:${d.device_name}|SN:${d.serial_no}`);
                const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=90x90&data=${qrData}`;

                return `
                    <div class="col-md-4 col-sm-6">
                        <div class="qr-label-card">
                            <img src="${qrUrl}" alt="QR" style="width: 70px; height: 70px;" class="rounded border">
                            <div class="qr-label-info">
                                <div class="qr-hospital">BV QUẬN 7</div>
                                <div class="qr-dev-name">${d.device_name}</div>
                                <div class="qr-serial font-mono">TAG: ${assetTag}</div>
                                <div class="text-muted small">SN: ${d.serial_no}</div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        },

        async viewDetails(deviceId) {
            try {
                const device = await apiClient.getDevice(deviceId);
                const modalTitle = document.getElementById('device-modal-title');
                const modalBody = document.getElementById('device-modal-body');

                if (modalTitle) {
                    modalTitle.innerHTML = `<i class="bi bi-info-circle text-primary me-2"></i>${device.device_name} <span class="badge bg-light text-dark border ms-2 font-mono">${device.asset_tag}</span>`;
                }

                if (modalBody) {
                    const certsHtml = (device.certificates && device.certificates.length > 0)
                        ? device.certificates.map(c => `
                            <div class="p-2 bg-light rounded-2 border mb-2 small">
                                <div class="d-flex justify-content-between">
                                    <strong>Số GCN: ${c.certificate_no || 'N/A'}</strong>
                                    <span class="badge-clean-status status-ok">Đạt chuẩn</span>
                                </div>
                                <div class="text-muted mt-1">Hạn KĐ: <span class="font-mono text-dark fw-bold">${apiClient.formatDate(c.recalibration_date)}</span> • Đơn vị: ${c.calibrated_by || '-'}</div>
                                ${c.source_pdf ? `<div class="mt-1"><a href="${apiClient.getPdfUrl(c.source_pdf)}" target="_blank" class="btn btn-sm btn-outline-danger btn-clinical"><i class="bi bi-file-earmark-pdf me-1"></i>Xem PDF gốc</a></div>` : ''}
                            </div>
                        `).join('')
                        : '<p class="text-muted small">Chưa có lịch sử chứng chỉ kiểm định.</p>';

                    modalBody.innerHTML = `
                        <div class="device-spec-grid mb-3">
                            <div class="spec-item">
                                <div class="spec-label">Mã tài sản</div>
                                <div class="spec-value text-primary font-mono">${device.asset_tag}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-label">Số Serial (S/N)</div>
                                <div class="spec-value font-mono">${device.serial_no}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-label">Model</div>
                                <div class="spec-value font-mono">${device.model}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-label">Khoa / Vị trí</div>
                                <div class="spec-value">${device.facility || 'Kho lưu trữ'}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-label">Hãng sản xuất</div>
                                <div class="spec-value">${device.manufacturer || '-'}</div>
                            </div>
                            <div class="spec-item">
                                <div class="spec-label">Mức rủi ro (NĐ 98)</div>
                                <div class="spec-value font-mono">Mức ${device.risk_level || 'A'}</div>
                            </div>
                        </div>

                        <h6 class="fw-bold small text-muted text-uppercase mb-2">Hồ sơ kiểm định & Chứng từ</h6>
                        ${certsHtml}
                    `;
                }

                bootstrap.Modal.getOrCreateInstance(document.getElementById('device-detail-modal')).show();
            } catch (err) {
                alert('Không thể tải chi tiết thiết bị.');
            }
        }
    };

    window.app = app;
    app.init();
});
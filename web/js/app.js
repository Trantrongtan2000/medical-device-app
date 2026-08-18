/**
 * Medical Device Management System (BV Quận 7)
 * Smart Management Frontend Application Logic
 * Chuẩn hóa theo SpeedMaint Cloud CMMS (Bệnh viện Hoàn Mỹ) & Snipe-IT
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('🏥 Hệ thống Quản lý Trang thiết bị Y tế SpeedMaint CMMS & Snipe-IT đã sẵn sàng');

    const app = {
        devices: [],
        selectedDeviceIds: new Set(),
        facilities: [],
        categories: [],
        schedules: [],
        workOrders: [],
        audits: [],
        accessories: [],
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
            await this.loadAudits();
            await this.loadSchedules();
            await this.loadWorkOrders();
            await this.loadAccessories();
        },

        setupEventListeners() {
            // Sidebar Nav Tab Title updates
            const navButtons = document.querySelectorAll('.sidebar-nav .nav-link');
            const pageHeading = document.getElementById('page-heading');

            navButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    navButtons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    const targetId = btn.getAttribute('data-bs-target');
                    if (targetId) {
                        document.querySelectorAll('.tab-pane').forEach(p => {
                            p.classList.remove('show', 'active');
                        });
                        const targetPane = document.querySelector(targetId);
                        if (targetPane) {
                            targetPane.classList.add('show', 'active');
                        }
                    }

                    const text = btn.querySelector('span')?.textContent || 'Quản lý TTBYT';
                    const iconClass = btn.querySelector('i')?.className || 'bi bi-boxes';
                    if (pageHeading) {
                        pageHeading.innerHTML = `<i class="${iconClass} text-primary me-2"></i>${text}`;
                    }
                });
            });

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
                    const qrTabTrigger = document.getElementById('btn-tab-qr');
                    if (qrTabTrigger) {
                        const tab = new bootstrap.Tab(qrTabTrigger);
                        tab.show();
                    }
                });
            }

            // SpeedMaint Work Order Form Submit (Ảnh 01bc & 605c)
            const woForm = document.getElementById('speedmaint-wo-form');
            if (woForm) {
                woForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const deviceId = document.getElementById('wo-device-select').value;
                    const title = document.getElementById('wo-title').value;
                    const workType = document.getElementById('wo-type').value;
                    const priority = document.getElementById('wo-priority').value;
                    const startDate = document.getElementById('wo-start-date').value;
                    const endDate = document.getElementById('wo-end-date').value;
                    const assignedTo = document.getElementById('wo-assigned-to').value;
                    const coWorkers = document.getElementById('wo-co-workers').value;
                    const supervisor = document.getElementById('wo-supervisor').value;
                    const location = document.getElementById('wo-location').value;
                    const desc = document.getElementById('wo-desc').value;
                    const materials = document.getElementById('wo-materials')?.value;

                    try {
                        await apiClient.createWorkOrder({
                            device_id: parseInt(deviceId),
                            title: title,
                            work_type: workType,
                            start_date: startDate,
                            end_date: endDate,
                            assigned_to: assignedTo,
                            co_workers: coWorkers,
                            supervisor: supervisor,
                            reporter: supervisor || assignedTo,
                            priority: priority,
                            location: location,
                            description: desc,
                            materials: materials
                        });

                        alert('✅ Đã tạo và lưu phiếu công việc SpeedMaint thành công!');
                        woForm.reset();
                        const modalEl = document.getElementById('speedmaintWorkOrderModal');
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

            // Transfer form submit (Snipe-IT Check-out)
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
                        const modalEl = document.getElementById('transferModal');
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        if (modal) modal.hide();

                        await this.loadInitialData();
                        await this.loadDevices();
                        await this.loadWorkOrders();
                    } catch (err) {
                        alert('Lỗi bàn giao: ' + err.message);
                    }
                });
            }

            // Quick Audit Form Submit (Dedicated Audits Module)
            const auditForm = document.getElementById('audit-form');
            if (auditForm) {
                auditForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const deviceId = document.getElementById('audit-device-select').value;
                    const condition = document.getElementById('audit-condition').value;
                    const location = document.getElementById('audit-location').value;
                    const person = document.getElementById('audit-person').value;
                    const notes = document.getElementById('audit-notes').value;

                    try {
                        await apiClient.auditDevice({
                            device_id: parseInt(deviceId),
                            audited_by: person,
                            location_checked: location,
                            condition: condition,
                            notes: notes
                        });

                        alert('✅ Đã lưu kết quả kiểm kê tài sản thành công!');
                        auditForm.reset();
                        const modalEl = document.getElementById('quickAuditModal');
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        if (modal) modal.hide();

                        await this.loadInitialData();
                        await this.loadAudits();
                    } catch (err) {
                        alert('Lỗi kiểm kê: ' + err.message);
                    }
                });
            }

            // Gemini AI Chat Form Submit
            const aiForm = document.getElementById('ai-chat-form');
            const aiInput = document.getElementById('ai-chat-input');
            const aiMsgBox = document.getElementById('ai-chat-messages');

            if (aiForm) {
                aiForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const text = aiInput.value.trim();
                    if (!text) return;

                    // Append user message
                    if (aiMsgBox) {
                        aiMsgBox.innerHTML += `
                            <div class="d-flex gap-2 mb-3 justify-content-end">
                                <div class="p-3 bg-primary text-white rounded-3 shadow-sm" style="max-width: 80%;">
                                    <div class="small fw-bold mb-1">Kỹ sư BME (Bạn)</div>
                                    <div class="small">${text}</div>
                                </div>
                            </div>
                        `;
                        aiMsgBox.scrollTop = aiMsgBox.scrollHeight;
                    }

                    aiInput.value = '';

                    // Show typing indicator
                    const typingId = 'typing-' + Date.now();
                    if (aiMsgBox) {
                        aiMsgBox.innerHTML += `
                            <div class="d-flex gap-2 mb-3" id="${typingId}">
                                <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center flex-shrink-0" style="width:36px; height:36px;">
                                    <i class="bi bi-robot"></i>
                                </div>
                                <div class="p-3 bg-white border rounded-3 shadow-sm text-muted small">
                                    <span class="spinner-border spinner-border-sm me-1"></span> Gemini BME Agent đang suy luận...
                                </div>
                            </div>
                        `;
                        aiMsgBox.scrollTop = aiMsgBox.scrollHeight;
                    }

                    try {
                        const res = await apiClient.aiChat(text);
                        document.getElementById(typingId)?.remove();

                        if (aiMsgBox) {
                            aiMsgBox.innerHTML += `
                                <div class="d-flex gap-2 mb-3">
                                    <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center flex-shrink-0" style="width:36px; height:36px;">
                                        <i class="bi bi-robot"></i>
                                    </div>
                                    <div class="p-3 bg-white border rounded-3 shadow-sm" style="max-width: 85%;">
                                        <div class="fw-bold text-primary small mb-1">Gemini BME Agent</div>
                                        <div class="small" style="white-space: pre-wrap;">${res.reply}</div>
                                    </div>
                                </div>
                            `;
                            aiMsgBox.scrollTop = aiMsgBox.scrollHeight;
                        }
                    } catch (err) {
                        document.getElementById(typingId)?.remove();
                        if (aiMsgBox) {
                            aiMsgBox.innerHTML += `
                                <div class="d-flex gap-2 mb-3">
                                    <div class="p-3 bg-danger text-white rounded-3 small">
                                        Lỗi kết nối Gemini AI: ${err.message}
                                    </div>
                                </div>
                            `;
                        }
                    }
                });
            }

            // Quick Prompt buttons
            document.querySelectorAll('.ai-prompt-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const prompt = btn.getAttribute('data-prompt');
                    if (aiInput && prompt) {
                        aiInput.value = prompt;
                        aiForm?.dispatchEvent(new Event('submit'));
                    }
                });
            });

            // Mistral OCR Sample trigger
            const ocrBtn = document.getElementById('btn-run-sample-ocr');
            if (ocrBtn) {
                ocrBtn.addEventListener('click', async () => {
                    const mdPre = document.getElementById('ocr-markdown-preview');
                    const jsonPre = document.getElementById('ocr-json-preview');

                    if (mdPre) mdPre.textContent = '⏳ Mistral OCR Engine đang bóc tách cấu trúc tài liệu PDF/Scan...';
                    if (jsonPre) jsonPre.textContent = '// Đang trích xuất JSON Schema...';

                    try {
                        const ocrRes = await apiClient.processOcr('GCN_Kiem_Dinh_Monitor_2026.pdf');
                        if (mdPre) mdPre.textContent = ocrRes.markdown || 'Hoàn tất bóc tách.';
                        if (jsonPre) jsonPre.textContent = JSON.stringify(ocrRes.extracted_fields || {}, null, 2);
                    } catch (err) {
                        if (mdPre) mdPre.textContent = 'Lỗi OCR: ' + err.message;
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
                this.populateTransferDeviceOptions(devices);
                this.populateAuditDeviceOptions(devices);
                this.renderQrStudio();
            } catch (err) {
                console.error('Lỗi khi tải danh sách thiết bị:', err);
                this.showTableError('Không thể tải danh sách thiết bị từ máy chủ.');
            }
        },

        async loadAudits() {
            try {
                const audits = await apiClient.getAudits();
                this.audits = audits;
                this.renderAudits(audits);
            } catch (err) {
                console.error('Lỗi nạp danh sách kiểm kê:', err);
            }
        },

        async loadAccessories() {
            try {
                const accessories = await apiClient.getAccessories();
                this.accessories = accessories;
                this.renderAccessories(accessories);
            } catch (err) {
                console.error('Lỗi nạp phụ kiện:', err);
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
                this.renderTransfers(orders);
            } catch (err) {
                console.error('Lỗi nạp work orders:', err);
            }
        },

        showLoading() {
            const tbody = document.getElementById('devices-body');
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="11" class="text-center py-5">
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
                        <td colspan="11" class="text-center py-4 text-danger">
                            <i class="bi bi-exclamation-triangle-fill fs-3"></i>
                            <p class="mt-2 fw-semibold">${msg}</p>
                        </td>
                    </tr>
                `;
            }
        },

        renderSummary(summary) {
            const sideTotal = document.getElementById('side-kpi-total');
            const sideAvail = document.getElementById('side-kpi-avail');
            const sideWarning = document.getElementById('side-kpi-warning');
            const sideOverdue = document.getElementById('side-kpi-overdue');
            const navBadgeTotal = document.getElementById('nav-badge-total');

            if (sideTotal) sideTotal.textContent = Number(summary.total_devices || 0).toLocaleString('vi-VN');
            if (sideAvail) sideAvail.textContent = `${summary.availability_rate || 100}%`;
            if (sideWarning) sideWarning.textContent = Number(summary.warning_count || 0).toLocaleString('vi-VN');
            if (sideOverdue) sideOverdue.textContent = Number(summary.overdue_count || 0).toLocaleString('vi-VN');
            if (navBadgeTotal) navBadgeTotal.textContent = Number(summary.total_devices || 0).toLocaleString('vi-VN');

            // Audit stats
            const auditDone = document.getElementById('audit-stat-done');
            const auditPending = document.getElementById('audit-stat-pending');
            const auditBadge = document.getElementById('nav-badge-audits');

            const auditedCount = summary.audited_count || 0;
            const totalCount = summary.total_devices || 1049;

            if (auditDone) auditDone.textContent = `${auditedCount} máy`;
            if (auditPending) auditPending.textContent = `${totalCount - auditedCount} máy`;
            if (auditBadge) auditBadge.textContent = `${auditedCount}`;
        },

        renderFacilityOptions(facilities) {
            const select = document.getElementById('filter-facility');
            const transferTargetSelect = document.getElementById('transfer-target-facility');
            const woFacSelect = document.getElementById('wo-facility');

            const optionsHtml = '<option value="">-- Chọn Khoa / Vị trí --</option>' +
                facilities.map(f => `<option value="${f.id}">${f.name} (${f.device_count || 0})</option>`).join('');

            if (select) select.innerHTML = '<option value="">-- Tất cả Khoa / Vị trí --</option>' +
                facilities.map(f => `<option value="${f.id}">${f.name} (${f.device_count || 0})</option>`).join('');

            if (transferTargetSelect) transferTargetSelect.innerHTML = optionsHtml;
            if (woFacSelect) woFacSelect.innerHTML = optionsHtml;
        },

        renderCategoryOptions(categories) {
            const select = document.getElementById('filter-category');
            if (!select) return;
            select.innerHTML = '<option value="">-- Tất cả Phân loại --</option>' +
                categories.map(c => `<option value="${c.id}">${c.name} (${c.device_count || 0})</option>`).join('');
        },

        populateIncidentDeviceOptions(devices) {
            const select = document.getElementById('wo-device-select');
            if (!select) return;
            select.innerHTML = '<option value="">-- Chọn thiết bị cần lập phiếu công việc --</option>' +
                devices.map(d => `<option value="${d.id}">${d.speedmaint_code || `BM/BVQ7/${d.id}`} - ${d.device_name} (SN: ${d.serial_no}) [${d.facility || 'Kho'}]</option>`).join('');
        },

        populateTransferDeviceOptions(devices) {
            const select = document.getElementById('transfer-device-select');
            if (!select) return;
            select.innerHTML = '<option value="">-- Chọn thiết bị cần bàn giao --</option>' +
                devices.map(d => `<option value="${d.id}">${d.asset_tag || ''} - ${d.device_name} (SN: ${d.serial_no}) [Đang ở: ${d.facility || 'Chưa rõ'}]</option>`).join('');
        },

        populateAuditDeviceOptions(devices) {
            const select = document.getElementById('audit-device-select');
            if (!select) return;
            select.innerHTML = '<option value="">-- Chọn thiết bị cần kiểm kê --</option>' +
                devices.map(d => `<option value="${d.id}">${d.asset_tag || ''} - ${d.device_name} (SN: ${d.serial_no}) [${d.facility || 'Chưa rõ'}]</option>`).join('');
        },

        openWorkOrderModalForDevice(deviceId, deviceName) {
            const select = document.getElementById('wo-device-select');
            if (select) select.value = deviceId;
            const titleInput = document.getElementById('wo-title');
            if (titleInput) titleInput.value = `PM định kỳ thiết bị: ${deviceName}`;

            const today = new Date().toISOString().split('T')[0];
            const startInput = document.getElementById('wo-start-date');
            const endInput = document.getElementById('wo-end-date');
            if (startInput) startInput.value = today;
            if (endInput) endInput.value = today;

            const modal = new bootstrap.Modal(document.getElementById('speedmaintWorkOrderModal'));
            modal.show();
        },

        openTransferModalForDevice(deviceId) {
            const select = document.getElementById('transfer-device-select');
            if (select) select.value = deviceId;
            const modal = new bootstrap.Modal(document.getElementById('transferModal'));
            modal.show();
        },

        openAuditModalForDevice(deviceId) {
            const select = document.getElementById('audit-device-select');
            if (select) select.value = deviceId;
            const modal = new bootstrap.Modal(document.getElementById('quickAuditModal'));
            modal.show();
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
                        <td colspan="11" class="text-center py-5 text-muted">
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
                    badgeHtml = `<span class="badge-status-pill status-overdue"><i class="bi bi-x-circle-fill"></i> Quá hạn</span>`;
                } else if (alertStatus === 'WARNING') {
                    badgeHtml = `<span class="badge-status-pill status-warning"><i class="bi bi-exclamation-triangle-fill"></i> Cảnh báo 30N</span>`;
                } else if (alertStatus === 'OK') {
                    badgeHtml = `<span class="badge-status-pill status-ok"><i class="bi bi-check-circle-fill"></i> Đạt chuẩn</span>`;
                } else {
                    badgeHtml = `<span class="badge-status-pill status-nodata"><i class="bi bi-dash-circle"></i> Chưa KĐ</span>`;
                }

                const riskClass = `risk-tag risk-tag-${(d.risk_level || 'a').toLowerCase()}`;
                const pdfBtn = d.source_pdf ? `
                    <a href="${apiClient.getPdfUrl(d.source_pdf)}" target="_blank" class="btn btn-sm btn-clinical-pdf btn-clinical" title="Xem PDF chứng từ gốc">
                        <i class="bi bi-file-earmark-pdf"></i>
                    </a>
                ` : '';

                const isChecked = this.selectedDeviceIds.has(d.id) ? 'checked' : '';

                return `
                    <tr>
                        <td>
                            <input type="checkbox" class="device-checkbox" data-id="${d.id}" ${isChecked} onchange="app.toggleDeviceSelection(${d.id})">
                        </td>
                        <td><span class="badge bg-dark text-light border font-mono">${d.asset_tag || `BVQ7-TTB-${d.id}`}</span></td>
                        <td><span class="fw-bold text-primary font-mono">${d.serial_no || '-'}</span></td>
                        <td>
                            <div class="fw-bold text-dark">${d.device_name || 'Thiết bị y tế'}</div>
                            <small class="text-muted font-mono">${d.speedmaint_code || `BM/BVQ7/${d.id}`} • ${d.manufacturer || '-'} ${d.country_of_manufacturer ? `(${d.country_of_manufacturer})` : ''}</small>
                        </td>
                        <td><span class="badge bg-light text-dark border font-mono">${d.model || '-'}</span></td>
                        <td><span class="${riskClass}">Mức ${d.risk_level || 'A'}</span></td>
                        <td><i class="bi bi-geo-alt-fill text-muted me-1"></i>${d.facility || 'Kho lưu trữ'}</td>
                        <td class="font-mono text-muted">${apiClient.formatDate(d.calibration_date)}</td>
                        <td class="font-mono"><strong class="${alertStatus === 'OVERDUE' ? 'text-danger' : alertStatus === 'WARNING' ? 'text-warning' : ''}">${apiClient.formatDate(d.recalibration_date)}</strong></td>
                        <td>${badgeHtml}</td>
                        <td class="text-end">
                            <button class="btn btn-sm btn-clinical-primary btn-clinical me-1" onclick="app.viewDetails(${d.id})" title="Xem hồ sơ lý lịch máy (Dossier)">
                                <i class="bi bi-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-purple btn-clinical me-1" onclick="app.openWorkOrderModalForDevice(${d.id}, '${d.device_name}')" title="Lập phiếu công việc SpeedMaint" style="color:#6d28d9; border-color:#c4b5fd;">
                                <i class="bi bi-tools"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary btn-clinical me-1" onclick="app.openTransferModalForDevice(${d.id})" title="Bàn giao / Check-out">
                                <i class="bi bi-arrow-left-right"></i>
                            </button>
                            ${pdfBtn}
                        </td>
                    </tr>
                `;
            }).join('');
        },

        renderWorkOrders(orders) {
            const tbody = document.getElementById('workorders-body');
            const countBadge = document.getElementById('nav-badge-wo');
            const countLabel = document.getElementById('wo-count-label');

            if (countBadge) countBadge.textContent = `${orders.length}`;
            if (countLabel) countLabel.textContent = `${orders.length} Công việc`;
            if (!tbody) return;

            if (orders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Chưa có phiếu công việc nào. Nhấn "+ Thêm" để tạo phiếu mới.</td></tr>';
                return;
            }

            // Render theo phong cách SpeedMaint (Ảnh 5115f7b33d1abc44e50b.jpg)
            tbody.innerHTML = orders.map(o => `
                <tr>
                    <td><input type="checkbox"></td>
                    <td><span class="font-mono fw-bold text-primary">#${o.task_code || `260${o.id}`}</span></td>
                    <td>
                        <div class="fw-bold text-dark">
                            <span class="text-warning me-1">🏷️</span> ${o.work_type || 'PM định kỳ'} giao cho <strong>${o.assigned_to || 'Kỹ sư Y sinh'}</strong>
                        </div>
                        <small class="text-muted">${o.description || '-'}</small>
                    </td>
                    <td>
                        <span class="badge bg-light text-dark border font-mono small">
                            <i class="bi bi-clock me-1"></i> ${apiClient.formatDate(o.start_date)} - 17:00
                        </span>
                    </td>
                    <td>
                        <div class="font-mono small fw-bold text-primary">${o.speedmaint_device_code || `BM/BVQ7/${o.device_id}`}</div>
                        <div class="small text-dark">${o.device_name || 'Thiết bị y tế'}</div>
                    </td>
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <div class="progress flex-grow-1" style="height: 8px;">
                                <div class="progress-bar bg-success" style="width: 100%;"></div>
                            </div>
                            <span class="badge-status-pill status-ok" style="font-size:0.7rem;">Hoàn thành</span>
                        </div>
                    </td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary btn-clinical" onclick="app.viewDetails(${o.device_id})" title="Xem chi tiết thiết bị">
                            <i class="bi bi-eye"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        },

        renderAudits(audits) {
            const tbody = document.getElementById('audits-table-body');
            if (!tbody) return;

            if (audits.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">Chưa có bản ghi kiểm kê thực tế nào. Hãy lập phiếu kiểm kê mới.</td></tr>';
                return;
            }

            tbody.innerHTML = audits.map(a => `
                <tr>
                    <td class="font-mono fw-bold text-primary">${apiClient.formatDate(a.audit_date)}</td>
                    <td><span class="badge bg-dark font-mono">${a.asset_tag}</span></td>
                    <td><div class="fw-bold">${a.device_name}</div><small class="text-muted">Model: ${a.model}</small></td>
                    <td><span class="font-mono badge bg-light text-dark border">${a.serial_no}</span></td>
                    <td><i class="bi bi-hospital me-1"></i>${a.facility || 'Toàn viện'}</td>
                    <td><strong>${a.auditor || '-'}</strong></td>
                    <td class="small">${a.description || '-'}</td>
                    <td><span class="badge-status-pill status-ok"><i class="bi bi-check-circle-fill"></i> Đã Kiểm Kê</span></td>
                </tr>
            `).join('');
        },

        renderAccessories(accessories) {
            const tbody = document.getElementById('accessories-table-body');
            if (!tbody) return;

            tbody.innerHTML = accessories.map(acc => {
                const percentRem = Math.round(((acc.total_qty - acc.in_use_qty) / acc.total_qty) * 100);

                return `
                    <tr>
                        <td>
                            <div class="fw-bold text-dark">${acc.name}</div>
                            <small class="text-muted font-mono">ID: ACC-#${acc.id}</small>
                        </td>
                        <td><span class="badge bg-light text-dark border">${acc.category}</span></td>
                        <td><span class="font-mono fw-bold">${acc.model_no}</span></td>
                        <td><i class="bi bi-geo-alt me-1"></i>${acc.location}</td>
                        <td class="font-mono fw-bold">${acc.total_qty} cái</td>
                        <td class="font-mono text-primary">${acc.in_use_qty} cái</td>
                        <td>
                            <div class="d-flex align-items-center gap-2">
                                <div class="progress flex-grow-1" style="height: 6px;">
                                    <div class="progress-bar bg-success" style="width: ${percentRem}%;"></div>
                                </div>
                                <span class="small font-mono fw-bold">${percentRem}% tồn</span>
                            </div>
                        </td>
                        <td class="font-mono text-dark fw-bold">${acc.unit_cost}</td>
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

        renderTransfers(orders) {
            const tbody = document.getElementById('transfers-body');
            if (!tbody) return;

            const transfers = orders.filter(o => o.work_type === 'Điều chuyển' || o.description?.includes('Bàn giao') || o.description?.includes('Check-out'));

            if (transfers.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">Chưa có lịch sử bàn giao thiết bị.</td></tr>';
                return;
            }

            tbody.innerHTML = transfers.map(t => `
                <tr>
                    <td class="font-mono fw-bold text-primary">${apiClient.formatDate(t.start_date)}</td>
                    <td><div class="fw-bold">${t.device_name}</div><small class="text-muted">Model: ${t.model}</small></td>
                    <td><span class="font-mono badge bg-light text-dark border">${t.serial_no}</span></td>
                    <td><strong>${t.assigned_to || '-'}</strong></td>
                    <td class="small">${t.description || '-'}</td>
                    <td><span class="badge-status-pill status-ok">Đã bàn giao</span></td>
                </tr>
            `).join('');
        },

        renderQrStudio() {
            const grid = document.getElementById('qr-labels-grid');
            if (!grid) return;

            const selectedList = this.devices.filter(d => this.selectedDeviceIds.has(d.id));
            const listToRender = selectedList.length > 0 ? selectedList : this.devices.slice(0, 12);

            grid.innerHTML = listToRender.map(d => {
                const assetTag = d.asset_tag || `BVQ7-TTB-${d.id}`;
                const speedmaintCode = d.speedmaint_code || `BM/BVQ7/${d.id}`;
                const qrData = encodeURIComponent(`TAG:${assetTag}|CODE:${speedmaintCode}|TB:${d.device_name}|SN:${d.serial_no}|LOC:${d.facility || ''}`);
                const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=110x110&data=${qrData}`;

                return `
                    <div class="col-md-4 col-sm-6">
                        <div class="qr-label-card">
                            <img src="${qrUrl}" alt="QR" style="width: 85px; height: 85px;" class="rounded border">
                            <div class="qr-label-info">
                                <div class="qr-hospital">BV QUẬN 7 • TP.HCM</div>
                                <div class="qr-dev-name">${d.device_name}</div>
                                <div class="qr-serial font-mono">TAG: ${assetTag}</div>
                                <div class="text-muted font-mono" style="font-size: 0.7rem;">Mã: ${speedmaintCode}</div>
                                <div class="text-muted" style="font-size: 0.68rem;">S/N: ${d.serial_no} • Hạn KĐ: ${apiClient.formatDate(d.recalibration_date)}</div>
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
                    modalTitle.innerHTML = `<i class="bi bi-heart-pulse-fill text-primary me-2"></i>Hồ Sơ Lý Lịch Máy: ${device.device_name} <span class="badge bg-dark ms-2 font-mono">${device.asset_tag}</span>`;
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

                    const historyHtml = (device.maintenance_logs && device.maintenance_logs.length > 0)
                        ? device.maintenance_logs.map(l => `
                            <div class="list-group-item border-0 mb-2 p-3 bg-light rounded-3">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="badge ${l.maintenance_type === 'INSPECTION' ? 'bg-success' : 'bg-primary'} text-light">${l.maintenance_type || 'PM định kỳ'}</span>
                                    <span class="font-mono small text-muted">${apiClient.formatDate(l.maintenance_date)}</span>
                                </div>
                                <div class="mt-2 small text-dark">${l.description || '-'}</div>
                                <small class="text-muted d-block mt-1">Người thực hiện: <strong>${l.performed_by || '-'}</strong></small>
                            </div>
                        `).join('')
                        : '<p class="text-muted p-3 bg-light rounded-3">Chưa có nhật ký bảo trì / bàn giao.</p>';

                    const qrData = encodeURIComponent(`TAG:${device.asset_tag}|CODE:${device.speedmaint_code}|TB:${device.device_name}|SN:${device.serial_no}|MD:${device.model}|LOC:${device.facility || ''}`);
                    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${qrData}`;

                    modalBody.innerHTML = `
                        <!-- Nav tabs inside Dossier Modal -->
                        <ul class="nav nav-tabs mb-3" id="dossierTabs" role="tablist">
                            <li class="nav-item">
                                <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-dossier-spec" type="button">
                                    <i class="bi bi-info-circle me-1"></i> Thông Số Kỹ Thuật
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-dossier-certs" type="button">
                                    <i class="bi bi-award me-1"></i> Hồ Sơ Kiểm Định (${device.certificates?.length || 0})
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-dossier-logs" type="button">
                                    <i class="bi bi-clock-history me-1"></i> Lịch Sử Bàn Giao & Audit Trail
                                </button>
                            </li>
                        </ul>

                        <div class="tab-content">
                            <!-- Spec Tab -->
                            <div class="tab-pane fade show active" id="tab-dossier-spec">
                                <div class="row g-3">
                                    <div class="col-md-8">
                                        <div class="device-spec-grid">
                                            <div class="spec-item">
                                                <div class="spec-label">Mã tài sản (Asset Tag)</div>
                                                <div class="spec-value text-primary font-mono fw-bold">${device.asset_tag}</div>
                                            </div>
                                            <div class="spec-item">
                                                <div class="spec-label">Mã SpeedMaint</div>
                                                <div class="spec-value text-dark font-mono fw-bold">${device.speedmaint_code}</div>
                                            </div>
                                            <div class="spec-item">
                                                <div class="spec-label">Số Serial (S/N)</div>
                                                <div class="spec-value font-mono">${device.serial_no}</div>
                                            </div>
                                            <div class="spec-item">
                                                <div class="spec-label">Tên thiết bị y tế</div>
                                                <div class="spec-value text-dark fw-bold">${device.device_name}</div>
                                            </div>
                                            <div class="spec-item">
                                                <div class="spec-label">Model / Ký hiệu</div>
                                                <div class="spec-value font-mono">${device.model}</div>
                                            </div>
                                            <div class="spec-item">
                                                <div class="spec-label">Vị trí / Khoa bàn giao</div>
                                                <div class="spec-value text-dark fw-bold">${device.facility || 'Kho lưu trữ'}</div>
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
                                                <div class="spec-label">Tình trạng kỹ thuật</div>
                                                <div class="spec-value"><span class="badge-status-pill status-ok">${device.status || 'Đang sử dụng'}</span></div>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-4 text-center">
                                        <div class="p-3 bg-light rounded-3 border">
                                            <img src="${qrUrl}" alt="QR Code" class="img-fluid rounded mb-2 shadow-sm" style="width: 130px; height: 130px;">
                                            <div class="small fw-bold font-mono">${device.asset_tag}</div>
                                            <small class="text-muted d-block">Quét camera xem hồ sơ</small>
                                            <div class="d-flex flex-column gap-2 mt-2">
                                                <button class="btn btn-sm btn-outline-primary btn-clinical w-100" onclick="app.openWorkOrderModalForDevice(${device.id}, '${device.device_name}')">
                                                    <i class="bi bi-tools me-1"></i> Tạo phiếu WO SpeedMaint
                                                </button>
                                                <button class="btn btn-sm btn-outline-secondary btn-clinical w-100" onclick="app.openTransferModalForDevice(${device.id})">
                                                    <i class="bi bi-arrow-left-right me-1"></i> Bàn giao máy
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Certs Tab -->
                            <div class="tab-pane fade" id="tab-dossier-certs">
                                <div class="list-group border-0">
                                    ${certsHtml}
                                </div>
                            </div>

                            <!-- Logs Tab -->
                            <div class="tab-pane fade" id="tab-dossier-logs">
                                <div class="list-group border-0">
                                    ${historyHtml}
                                </div>
                            </div>
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
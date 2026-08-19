/**
 * 🏥 Medical Device Management System (BV Quận 7 / PKĐK Tâm Anh Q7)
 * ✨ UI/UX Pro Max Application Client Logic
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 UI/UX Pro Max Clinical Client Logic initialized.');

    const app = {
        devices: [],
        facilities: [],
        categories: [],
        inspections: [],
        transfers: [],
        ecarts: [],
        workOrders: [],
        currentFilters: {
            search: '',
            facility_id: '',
            risk_level: '',
            limit: 300,
            offset: 0
        },

        async init() {
            this.setupNavigation();
            this.setupFormSubmissions();
            await this.loadInitialData();
            await this.loadDevices();
            await this.loadInspections();
            await this.loadTransfers();
            await this.loadECarts();
            await this.loadWorkOrders();
            await this.loadSemanticaStats();

            // Render default diagram
            if (window.DiagramEngine) {
                DiagramEngine.render('diagram-container', 'qt04');
            }
        },

        setupNavigation() {
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

            // Search filter
            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    this.currentFilters.search = e.target.value;
                    this.loadDevices();
                });
            }

            // Facility filter
            const facFilter = document.getElementById('filter-facility');
            if (facFilter) {
                facFilter.addEventListener('change', (e) => {
                    this.currentFilters.facility_id = e.target.value;
                    this.loadDevices();
                });
            }

            // Risk filter
            const riskFilter = document.getElementById('filter-risk');
            if (riskFilter) {
                riskFilter.addEventListener('change', (e) => {
                    this.currentFilters.risk_level = e.target.value;
                    this.loadDevices();
                });
            }
        },

        async loadInitialData() {
            try {
                const [facRes, catRes] = await Promise.all([
                    fetch('/api/facilities'),
                    fetch('/api/categories')
                ]);
                this.facilities = await facRes.json();
                this.categories = await catRes.json();

                // Populate filter dropdowns
                const filterFac = document.getElementById('filter-facility');
                const trFromFac = document.getElementById('tr-from-facility');
                const trToFac = document.getElementById('tr-to-facility');

                if (filterFac) {
                    filterFac.innerHTML = '<option value="">-- Tất cả 21 Khoa/Phòng --</option>' +
                        this.facilities.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
                }
                if (trFromFac) {
                    trFromFac.innerHTML = this.facilities.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
                }
                if (trToFac) {
                    trToFac.innerHTML = this.facilities.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
                }
            } catch (err) {
                console.error('Error loading initial data:', err);
            }
        },

        async loadDevices() {
            try {
                let url = `/api/devices?limit=${this.currentFilters.limit}&offset=${this.currentFilters.offset}`;
                if (this.currentFilters.search) url += `&search=${encodeURIComponent(this.currentFilters.search)}`;
                if (this.currentFilters.facility_id) url += `&facility_id=${this.currentFilters.facility_id}`;
                if (this.currentFilters.risk_level) url += `&risk_level=${this.currentFilters.risk_level}`;

                const res = await fetch(url);
                this.devices = await res.json();

                const tbody = document.getElementById('device-table-body');
                const filterCount = document.getElementById('filter-count');
                if (filterCount) filterCount.textContent = this.devices.length;

                if (!this.devices || this.devices.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Không tìm thấy thiết bị nào phù hợp.</td></tr>';
                    return;
                }

                // Populate device select dropdowns
                const insDeviceSelect = document.getElementById('ins-device-id');
                const trDeviceSelect = document.getElementById('tr-device-id');
                const woDeviceSelect = document.getElementById('wo-device-id');

                const devOptions = this.devices.slice(0, 100).map(d => `<option value="${d.id}">[${d.asset_tag}] ${d.device_name} (SN: ${d.serial_no || 'N/A'})</option>`).join('');
                if (insDeviceSelect) insDeviceSelect.innerHTML = devOptions;
                if (trDeviceSelect) trDeviceSelect.innerHTML = devOptions;
                if (woDeviceSelect) woDeviceSelect.innerHTML = devOptions;

                tbody.innerHTML = this.devices.map(d => {
                    const riskBadge = d.risk_level ? `<span class="badge badge-risk-${d.risk_level}">${d.risk_level}</span>` : '<span class="text-muted">-</span>';
                    const hasAccessories = d.device_name.includes('siêu âm') || d.device_name.includes('Voluson') || d.device_name.includes('BTL') || d.device_name.includes('nội khí quản');

                    return `
                        <tr>
                            <td class="ps-3 font-mono fw-semibold text-primary">
                                <div>${d.asset_tag}</div>
                                <div class="text-muted" style="font-size: 0.72rem;">${d.speedmaint_code || ''}</div>
                            </td>
                            <td>
                                <div class="fw-bold text-dark">${d.device_name}</div>
                                <div class="text-muted small">${d.model || ''} • ${d.manufacturer || ''}</div>
                            </td>
                            <td class="font-mono">${d.serial_no || '<span class="text-muted">-</span>'}</td>
                            <td>${d.facility_name || '<span class="text-muted">Chưa phân khoa</span>'}</td>
                            <td class="text-center">${riskBadge}</td>
                            <td class="text-center">
                                <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1">${d.status || 'Hoạt động'}</span>
                            </td>
                            <td class="pe-3 text-end">
                                <button class="btn btn-sm btn-outline-primary btn-clinical" onclick="app.viewAccessories(${d.id}, '${d.device_name.replace(/'/g, "\\'")}')" title="Xem phụ kiện & cấu kiện">
                                    <i class="bi bi-diagram-2"></i> Phụ kiện
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } catch (err) {
                console.error('Error loading devices:', err);
            }
        },

        async viewAccessories(deviceId, deviceName) {
            try {
                const title = document.getElementById('accessoriesModalTitle');
                if (title) title.innerHTML = `<i class="bi bi-diagram-2 text-primary me-2"></i>Cấu Kiện & Phụ Kiện: <strong>${deviceName}</strong>`;

                const res = await fetch(`/api/devices/${deviceId}/accessories`);
                const accessories = await res.json();

                const tbody = document.getElementById('accessories-table-body');
                if (!accessories || accessories.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Thiết bị này không có cấu kiện rời hoặc sử dụng phụ kiện liền khối.</td></tr>';
                } else {
                    tbody.innerHTML = accessories.map(a => `
                        <tr>
                            <td><span class="badge bg-info text-dark font-mono">${a.accessory_type}</span></td>
                            <td class="fw-bold text-dark">${a.name} <span class="text-muted small font-mono">(${a.model || ''})</span></td>
                            <td class="font-mono fw-semibold text-primary">${a.serial_no || '-'}</td>
                            <td><span class="badge bg-success-subtle text-success">${a.status}</span></td>
                            <td class="text-muted small">${a.notes || '-'}</td>
                        </tr>
                    `).join('');
                }

                const modal = new bootstrap.Modal(document.getElementById('accessoriesModal'));
                modal.show();
            } catch (err) {
                console.error('Error loading accessories:', err);
            }
        },

        async loadInspections() {
            try {
                const res = await fetch('/api/inspections?limit=30');
                this.inspections = await res.json();
                const tbody = document.getElementById('inspections-table-body');
                if (!this.inspections || this.inspections.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Chưa có nhật ký kiểm tra đầu ngày nào.</td></tr>';
                    return;
                }

                tbody.innerHTML = this.inspections.map(ins => `
                    <tr>
                        <td class="font-mono small text-muted">${ins.inspection_time ? ins.inspection_time.substring(0, 16) : '-'}</td>
                        <td>
                            <strong class="text-dark">${ins.device_name}</strong>
                            <div class="text-muted small font-mono">${ins.asset_tag} (SN: ${ins.serial_no || '-'})</div>
                        </td>
                        <td>
                            <div class="fw-semibold text-dark">${ins.inspector_name}</div>
                            <div class="text-muted small">${ins.department}</div>
                        </td>
                        <td class="text-center">
                            <span class="badge ${ins.overall_status === 'PASSED' ? 'bg-success' : 'bg-warning'} px-2 py-1">${ins.overall_status}</span>
                        </td>
                        <td class="text-muted small">${ins.notes || '4/4 tiêu chí đạt chuẩn an toàn'}</td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Error loading inspections:', err);
            }
        },

        async loadTransfers() {
            try {
                const res = await fetch('/api/transfers?limit=30');
                this.transfers = await res.json();
                const tbody = document.getElementById('transfers-table-body');
                if (!this.transfers || this.transfers.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Chưa có biên bản điều chuyển thiết bị nào.</td></tr>';
                    return;
                }

                tbody.innerHTML = this.transfers.map(tr => `
                    <tr>
                        <td class="font-mono small fw-semibold text-primary">${tr.transfer_date}</td>
                        <td>
                            <strong class="text-dark">${tr.device_name}</strong>
                            <div class="text-muted small font-mono">${tr.asset_tag}</div>
                        </td>
                        <td>
                            <div class="small fw-semibold text-dark">${tr.from_facility_name || 'Kho TTB'} → <span class="text-primary">${tr.to_facility_name}</span></div>
                        </td>
                        <td>
                            <div class="small text-muted">Giao: <strong>${tr.giver_name}</strong></div>
                            <div class="small text-muted">Nhận: <strong>${tr.receiver_name}</strong></div>
                        </td>
                        <td class="text-muted small">${tr.transfer_reason || '-'}</td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Error loading transfers:', err);
            }
        },

        async loadECarts() {
            try {
                const res = await fetch('/api/ecarts');
                this.ecarts = await res.json();
                const grid = document.getElementById('ecarts-grid');
                if (!grid) return;

                grid.innerHTML = this.ecarts.map(ec => `
                    <div class="col-md-3">
                        <div class="clinical-card p-3 h-100 border-start border-4 border-danger">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge bg-danger font-mono">${ec.cart_code}</span>
                                <span class="badge bg-success-subtle text-success">${ec.status}</span>
                            </div>
                            <h6 class="fw-bold text-dark mb-1">${ec.department_name}</h6>
                            <div class="text-muted small mb-2"><i class="bi bi-geo-alt-fill text-danger me-1"></i>${ec.location_floor} ${ec.zone ? '- Khu ' + ec.zone : ''} ${ec.room_no ? '(Phòng ' + ec.room_no + ')' : ''}</div>
                            <div class="p-2 bg-light rounded small mb-2">
                                <div class="d-flex justify-content-between">
                                    <span class="text-muted">Máy Nhánh (Ext):</span>
                                    <strong class="font-mono text-danger">${ec.phone_ext || 'Trực tiếp'}</strong>
                                </div>
                            </div>
                            <div class="text-muted" style="font-size: 0.76rem;">
                                • Máy sốc tim phá rung<br>
                                • Máy hút dịch & Bình oxy<br>
                                • Bộ đặt NKQ & Hộp thuốc ACLS
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error('Error loading ECarts:', err);
            }
        },

        async loadWorkOrders() {
            try {
                const res = await fetch('/api/work-orders');
                this.workOrders = await res.json();
                const tbody = document.getElementById('workorders-table-body');
                const badgeWo = document.getElementById('nav-badge-wo');
                if (badgeWo) badgeWo.textContent = this.workOrders.length;

                if (!this.workOrders || this.workOrders.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Không có phiếu bảo trì / sửa chữa nào đang mở.</td></tr>';
                    return;
                }

                tbody.innerHTML = this.workOrders.map(wo => `
                    <tr>
                        <td class="font-mono fw-bold text-primary">#WO-${wo.id}</td>
                        <td class="fw-bold text-dark">${wo.title}</td>
                        <td>${wo.device_name || 'Hệ thống'} <span class="text-muted small font-mono">(${wo.asset_tag || ''})</span></td>
                        <td class="text-center"><span class="badge ${wo.priority === 'URGENT' ? 'bg-danger' : wo.priority === 'HIGH' ? 'bg-warning text-dark' : 'bg-secondary'}">${wo.priority}</span></td>
                        <td class="text-center"><span class="badge ${wo.status === 'COMPLETED' ? 'bg-success' : 'bg-primary'}">${wo.status}</span></td>
                        <td>${wo.assigned_to || 'P.TTBYT'}</td>
                        <td class="text-end">
                            <span class="text-muted small font-mono">${wo.created_at ? wo.created_at.substring(0, 10) : ''}</span>
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Error loading work orders:', err);
            }
        },

        async loadSemanticaStats() {
            try {
                const res = await fetch('/api/semantica/stats');
                const stats = await res.json();
                const box = document.getElementById('semantica-stats-box');
                if (box) {
                    box.innerHTML = `
                        <div class="mb-2"><strong>Động cơ:</strong> ${stats.engine}</div>
                        <div class="mb-1 text-primary"><strong>Tổng Thực Thể (Nodes):</strong> ${stats.total_nodes}</div>
                        <div class="mb-2 text-success"><strong>Tổng Mối Quan Hệ (Edges):</strong> ${stats.total_edges}</div>
                        <div class="small text-muted mb-2">Tiêu chuẩn: <strong>${stats.provenance_standard}</strong></div>
                        <hr class="my-2">
                        <div class="small">
                            • Thiết bị (Devices): <strong>${stats.node_distribution.Device || 0}</strong><br>
                            • Khoa phòng (Facilities): <strong>${stats.node_distribution.Facility || 0}</strong><br>
                            • Phụ kiện (Accessories): <strong>${stats.node_distribution.Accessory || 0}</strong><br>
                            • Xe E-Cart: <strong>${stats.node_distribution.EmergencyCart || 0}</strong><br>
                            • Hợp đồng & Nhà thầu: <strong>${(stats.node_distribution.Contract || 0) + (stats.node_distribution.Supplier || 0)}</strong>
                        </div>
                    `;
                }
            } catch (err) {
                console.error('Error loading Semantica stats:', err);
            }
        },

        async explainDeviceProvenance() {
            const devId = document.getElementById('semantica-search-id')?.value;
            const resBox = document.getElementById('semantica-provenance-result');
            if (!devId || !resBox) return;

            resBox.innerHTML = '<span class="text-muted small">Đang truy vấn chuỗi giải trình Semantica...</span>';
            try {
                const res = await fetch(`/api/semantica/explain/${devId}`);
                const data = await res.json();
                if (data.error) {
                    resBox.innerHTML = `<span class="text-danger small">${data.error}</span>`;
                    return;
                }

                resBox.innerHTML = `
                    <div class="mb-2"><strong class="text-primary">${data.device_name}</strong> (Model: ${data.model})</div>
                    <div class="font-mono small text-muted mb-3">Asset Tag: ${data.asset_tag} | Serial: ${data.serial_no}</div>
                    <h6 class="fw-bold small text-dark mb-2">Chuỗi Giải Trình W3C PROV-O (Không Ảo Tưởng):</h6>
                    <ul class="list-unstyled mb-0" style="font-size: 0.82rem;">
                        ${data.causal_provenance_chain.map(p => `
                            <li class="p-2 mb-1 bg-white border rounded">
                                <span class="badge bg-primary me-2">${p.step}</span>
                                <strong>${p.relation}</strong>: ${p.target}
                                <div class="text-muted" style="font-size: 0.74rem;">${p.evidence}</div>
                            </li>
                        `).join('')}
                    </ul>
                `;
            } catch (err) {
                resBox.innerHTML = `<span class="text-danger small">Lỗi khi truy vết: ${err.message}</span>`;
            }
        },

        setupFormSubmissions() {
            // Pre-use inspection submit
            const insForm = document.getElementById('preUseChecklistForm');
            if (insForm) {
                insForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const payload = {
                        device_id: parseInt(document.getElementById('ins-device-id').value),
                        inspector_name: document.getElementById('ins-inspector').value,
                        department: document.getElementById('ins-department').value,
                        power_ok: document.getElementById('ins-power').checked,
                        physical_ok: document.getElementById('ins-physical').checked,
                        gas_pressure_ok: document.getElementById('ins-gas').checked,
                        selftest_ok: document.getElementById('ins-selftest').checked,
                        notes: document.getElementById('ins-notes').value
                    };

                    const res = await fetch('/api/inspections', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (res.ok) {
                        alert('✅ Đã lưu Bảng kiểm tra an toàn đầu ngày thành công!');
                        insForm.reset();
                        this.loadInspections();
                    }
                });
            }

            // Transfer submit
            const trForm = document.getElementById('deviceTransferForm');
            if (trForm) {
                trForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const payload = {
                        device_id: parseInt(document.getElementById('tr-device-id').value),
                        from_facility_id: parseInt(document.getElementById('tr-from-facility').value),
                        to_facility_id: parseInt(document.getElementById('tr-to-facility').value),
                        giver_name: document.getElementById('tr-giver').value,
                        receiver_name: document.getElementById('tr-receiver').value,
                        transfer_reason: document.getElementById('tr-reason').value,
                        transfer_date: document.getElementById('tr-date').value
                    };

                    const res = await fetch('/api/transfers', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (res.ok) {
                        alert('✅ Đã thực hiện điều chuyển thiết bị thành công theo Quy trình QT.08!');
                        trForm.reset();
                        this.loadTransfers();
                        this.loadDevices();
                    }
                });
            }

            // Work Order submit
            const woForm = document.getElementById('createWorkOrderForm');
            if (woForm) {
                woForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const payload = {
                        device_id: parseInt(document.getElementById('wo-device-id').value),
                        title: document.getElementById('wo-title').value,
                        description: document.getElementById('wo-desc').value,
                        priority: document.getElementById('wo-priority').value,
                        assigned_to: document.getElementById('wo-assignee').value,
                        status: 'PENDING'
                    };

                    const res = await fetch('/api/work-orders', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    if (res.ok) {
                        alert('✅ Đã phát hành Phiếu công việc SpeedMaint thành công!');
                        bootstrap.Modal.getInstance(document.getElementById('speedmaintWorkOrderModal'))?.hide();
                        woForm.reset();
                        this.loadWorkOrders();
                    }
                });
            }
        }
    };

    window.app = app;
    app.init();
});
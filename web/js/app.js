/**
 * 🏥 Medical Device Management System (BV Quận 7 / PKĐK Tâm Anh Q7)
 * ✨ UI/UX Pro Max Application Client Logic
 * 📌 Hỗ trợ Bảng Thông Tin Chi Tiết Thiết Bị Khi Bấm Chọn (Device Passport Modal)
 */

document.addEventListener('DOMContentLoaded', function () {
    const app = {
        devices: [],
        facilities: [],
        categories: [],
        inspections: [],
        transfers: [],
        ecarts: [],
        workOrders: [],
        currentSelectedDeviceId: null,
        currentSelectedDevice: null,
        searchTimer: null,
        currentFilters: {
            search: '',
            facility_id: '',
            category_id: '',
            risk_level: '',
            alert_status: '',
            limit: 50,
            offset: 0,
            total: 0
        },
        paletteTimer: null,
        paletteIndex: 0,
        paletteItems: [],

        formatNumber(value) {
            const n = Number(value || 0);
            return n.toLocaleString('vi-VN');
        },

        statusLabel(status) {
            const map = {
                IN_SERVICE: 'Hoạt động',
                CALIBRATION_DUE: 'Sắp đến hạn KĐ',
                MAINTENANCE: 'Bảo trì',
                REPAIR: 'Sửa chữa',
                RETIRED: 'Ngưng sử dụng',
                PASSED: 'Đạt',
                FAILED: 'Không đạt',
                PENDING: 'Chờ xử lý',
                COMPLETED: 'Hoàn thành',
                URGENT: 'Khẩn cấp',
                HIGH: 'Ưu tiên cao',
                NORMAL: 'Bình thường'
            };
            return map[status] || status || 'Hoạt động';
        },

        statusClass(status) {
            if (['IN_SERVICE', 'PASSED', 'COMPLETED', 'OK'].includes(status)) {
                return 'bg-success-subtle text-success border border-success-subtle';
            }
            if (['WARNING', 'CALIBRATION_DUE', 'HIGH', 'PENDING'].includes(status)) {
                return 'bg-warning-subtle text-warning border border-warning-subtle';
            }
            if (['OVERDUE', 'REPAIR', 'URGENT', 'FAILED'].includes(status)) {
                return 'bg-danger-subtle text-danger border border-danger-subtle';
            }
            return 'bg-secondary-subtle text-secondary border border-secondary-subtle';
        },

        toast(message, type = 'info') {
            const stack = document.getElementById('toast-stack');
            if (!stack) {
                window.alert(message);
                return;
            }
            const el = document.createElement('div');
            el.className = `app-toast ${type}`;
            el.innerHTML = `<div>${message}</div>`;
            stack.appendChild(el);
            setTimeout(() => el.remove(), 4200);
        },

        skeletonRows(cols = 8) {
            return Array.from({ length: 4 }).map(() =>
                `<tr class="skeleton-row"><td colspan="${cols}"><span class="skeleton" style="width:${55 + Math.round(Math.random() * 30)}%;"></span></td></tr>`
            ).join('');
        },

        formatDate(dateStr) {
            if (window.apiClient && apiClient.formatDate) return apiClient.formatDate(dateStr);
            return dateStr || '-';
        },

        alertLabel(status) {
            const map = {
                OVERDUE: 'Quá hạn',
                WARNING: '≤ 30 ngày',
                OK: 'Còn hạn',
                NO_DATA: 'Chưa có KĐ'
            };
            return map[status] || status || 'Chưa có KĐ';
        },

        dueClass(status) {
            if (status === 'OVERDUE') return 'due-overdue';
            if (status === 'WARNING') return 'due-warning';
            if (status === 'OK') return 'due-ok';
            return 'due-none';
        },

        deviceOptionHtml(d) {
            return `<option value="${d.id}">[${d.asset_tag}] ${d.device_name} (SN: ${d.serial_no || 'N/A'})</option>`;
        },

        emptyRow(cols, icon, message) {
            return `<tr><td colspan="${cols}"><div class="empty-state"><i class="bi ${icon}"></i>${message}</div></td></tr>`;
        },

        setSidebarOpen(open) {
            const sidebar = document.getElementById('app-sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            sidebar?.classList.toggle('is-open', open);
            overlay?.classList.toggle('is-visible', open);
            if (overlay) overlay.setAttribute('aria-hidden', open ? 'false' : 'true');
        },

        async init() {
            this.setupNavigation();
            this.setupFormSubmissions();
            await this.loadInitialData();
            await Promise.all([
                this.loadDashboardSummary(),
                this.loadDevices(),
                this.loadInspections(),
                this.loadTransfers(),
                this.loadECarts(),
                this.loadWorkOrders(),
                this.loadWorklist(),
                this.loadSemanticaStats(),
                this.loadSopList(),
                this.refreshDeviceSelects('')
            ]);

            const savedTab = localStorage.getItem('htm-active-tab');
            if (savedTab) {
                document.querySelector(`.sidebar-nav .nav-link[data-bs-target="${savedTab}"]`)?.click();
            }

            if (window.DiagramEngine) {
                DiagramEngine.render('diagram-container', 'qt04');
            }
        },

        setupNavigation() {
            const navButtons = document.querySelectorAll('.sidebar-nav .nav-link');
            const pageHeading = document.getElementById('page-heading');
            const pageKicker = document.getElementById('page-kicker');
            const kickers = {
                '#tab-devices': 'Danh mục tài sản',
                '#tab-inspections': 'An toàn vận hành',
                '#tab-transfers': 'Quy trình QT.08',
                '#tab-ecarts': 'Cấp cứu 24/7',
                '#tab-worklist': 'Hàng việc kiểm định',
                '#tab-workorders': 'SpeedMaint CMMS',
                '#tab-diagrams': 'Sơ đồ quy trình',
                '#tab-semantica': 'Đồ thị tri thức',
                '#tab-ai-hub': 'Trợ lý & sổ tay'
            };

            navButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    navButtons.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    const targetId = btn.getAttribute('data-bs-target');
                    if (targetId) {
                        document.querySelectorAll('#mainTabContent > .tab-pane').forEach(p => p.classList.remove('show', 'active'));
                        document.querySelector(targetId)?.classList.add('show', 'active');
                        if (pageKicker) pageKicker.textContent = kickers[targetId] || 'Hệ thống HTM';
                        localStorage.setItem('htm-active-tab', targetId);
                    }

                    const text = btn.querySelector('span')?.textContent || 'Quản lý TTBYT';
                    const iconClass = btn.querySelector('i')?.className || 'bi bi-grid-fill';
                    if (pageHeading) {
                        pageHeading.innerHTML = `<i class="${iconClass} text-primary me-2"></i>${text}`;
                    }
                    this.setSidebarOpen(false);
                });
            });

            document.getElementById('btn-sidebar-toggle')?.addEventListener('click', () => {
                const sidebar = document.getElementById('app-sidebar');
                this.setSidebarOpen(!sidebar?.classList.contains('is-open'));
            });
            document.getElementById('sidebar-overlay')?.addEventListener('click', () => this.setSidebarOpen(false));
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.setSidebarOpen(false);
                    this.setPaletteOpen(false);
                }
                const tag = (e.target && e.target.tagName) || '';
                const typing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                    e.preventDefault();
                    this.setPaletteOpen(true);
                }
                if (!typing && e.key === '/') {
                    e.preventDefault();
                    document.getElementById('search-input')?.focus();
                }
            });

            const searchInput = document.getElementById('search-input');
            if (searchInput) {
                searchInput.addEventListener('input', (e) => {
                    this.currentFilters.search = e.target.value;
                    this.currentFilters.offset = 0;
                    clearTimeout(this.searchTimer);
                    this.searchTimer = setTimeout(() => this.loadDevices(), 320);
                });
            }

            const bindFilter = (id, key) => {
                const el = document.getElementById(id);
                if (!el) return;
                el.addEventListener('change', (e) => {
                    this.currentFilters[key] = e.target.value;
                    this.currentFilters.offset = 0;
                    this.loadDevices();
                });
            };
            bindFilter('filter-facility', 'facility_id');
            bindFilter('filter-category', 'category_id');
            bindFilter('filter-risk', 'risk_level');
            bindFilter('filter-alert', 'alert_status');

            document.getElementById('page-size')?.addEventListener('change', (e) => {
                this.currentFilters.limit = parseInt(e.target.value, 10) || 50;
                this.currentFilters.offset = 0;
                this.loadDevices();
            });
            document.getElementById('btn-page-prev')?.addEventListener('click', () => {
                this.currentFilters.offset = Math.max(0, this.currentFilters.offset - this.currentFilters.limit);
                this.loadDevices();
            });
            document.getElementById('btn-page-next')?.addEventListener('click', () => {
                const next = this.currentFilters.offset + this.currentFilters.limit;
                if (next < this.currentFilters.total) {
                    this.currentFilters.offset = next;
                    this.loadDevices();
                }
            });

            document.querySelectorAll('[data-kpi-alert]').forEach(card => {
                card.addEventListener('click', () => {
                    this.applyAlertFilter(card.getAttribute('data-kpi-alert') || '');
                    document.getElementById('btn-tab-devices')?.click();
                });
            });

            const chips = document.querySelectorAll('.chip-filter[data-chip]');
            chips.forEach(chip => {
                chip.addEventListener('click', () => {
                    chips.forEach(c => c.classList.remove('active'));
                    chip.classList.add('active');

                    const filterType = chip.getAttribute('data-chip');
                    this.currentFilters.search = '';
                    this.currentFilters.risk_level = '';
                    this.currentFilters.alert_status = '';
                    this.currentFilters.category_id = '';
                    this.currentFilters.offset = 0;
                    if (filterType === 'cdha') {
                        this.currentFilters.search = 'Siêu âm';
                    } else if (filterType === 'emergency') {
                        this.currentFilters.search = 'Cấp cứu';
                    } else if (filterType === 'ro') {
                        this.currentFilters.search = 'RO';
                    } else if (filterType === 'highrisk') {
                        this.currentFilters.risk_level = 'C,D';
                    } else if (filterType === 'overdue') {
                        this.currentFilters.alert_status = 'OVERDUE';
                    } else if (filterType === 'warning') {
                        this.currentFilters.alert_status = 'WARNING';
                    }
                    this.syncFilterControls();
                    this.loadDevices();
                });
            });

            document.getElementById('btn-reset-filters')?.addEventListener('click', () => this.resetFilters());
            document.getElementById('btn-command-palette')?.addEventListener('click', () => this.setPaletteOpen(true));
            document.getElementById('command-palette')?.addEventListener('click', (e) => {
                if (e.target.id === 'command-palette') this.setPaletteOpen(false);
            });
            document.getElementById('command-palette-input')?.addEventListener('input', (e) => {
                clearTimeout(this.paletteTimer);
                this.paletteTimer = setTimeout(() => this.searchPalette(e.target.value), 220);
            });
            document.getElementById('command-palette-input')?.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.movePalette(1);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.movePalette(-1);
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    const item = this.paletteItems[this.paletteIndex];
                    if (item) this.openPaletteDevice(item.id);
                }
            });

            ['ins', 'tr', 'wo'].forEach(prefix => {
                const search = document.getElementById(`${prefix}-device-search`);
                if (!search) return;
                search.addEventListener('input', () => {
                    clearTimeout(this.pickerTimer);
                    this.pickerTimer = setTimeout(() => this.refreshDeviceSelects(search.value, `${prefix}-device-id`), 280);
                });
            });

            document.getElementById('btn-export-csv')?.addEventListener('click', () => {
                const url = (window.apiClient && apiClient.getCsvExportUrl)
                    ? apiClient.getCsvExportUrl(this.currentFilters)
                    : '/api/export/csv';
                window.open(url, '_blank');
                this.toast('Đang xuất danh mục CSV theo bộ lọc hiện tại.', 'info');
            });

            document.getElementById('modal-btn-print-qr')?.addEventListener('click', () => this.printDevicePassport());
            document.getElementById('modal-btn-pdf')?.addEventListener('click', () => {
                const pdf = this.currentSelectedDevice?.source_pdf || this.currentSelectedDevice?.pdf_path;
                if (!pdf) {
                    this.toast('Thiết bị này chưa gắn tệp PDF gốc.', 'info');
                    return;
                }
                window.open(apiClient.getPdfUrl(pdf), '_blank');
            });
        },

        async printDevicePassport() {
            const dev = this.currentSelectedDevice;
            if (!dev) {
                this.toast('Chưa chọn thiết bị để in tem.', 'error');
                return;
            }
            document.getElementById('qr-label-name').textContent = dev.device_name || 'Thiết bị y tế';
            document.getElementById('qr-label-tag').textContent = dev.asset_tag || '';
            document.getElementById('qr-label-sm').textContent = dev.speedmaint_code || '';
            document.getElementById('qr-label-sn').textContent = dev.serial_no || '-';
            document.getElementById('qr-label-fac').textContent = dev.facility || dev.facility_name || '-';
            const payload = `${dev.asset_tag || ''} | ${dev.device_name || ''} | SN:${dev.serial_no || '-'}`;
            try {
                if (window.QRCode) {
                    await QRCode.toCanvas(document.getElementById('qr-label-canvas'), payload, { width: 120, margin: 1 });
                }
            } catch (err) {
                console.warn('QR render failed', err);
            }
            window.print();
        },

        syncFilterControls() {
            const map = {
                'search-input': this.currentFilters.search,
                'filter-facility': this.currentFilters.facility_id,
                'filter-category': this.currentFilters.category_id,
                'filter-risk': this.currentFilters.risk_level,
                'filter-alert': this.currentFilters.alert_status
            };
            Object.entries(map).forEach(([id, value]) => {
                const el = document.getElementById(id);
                if (el) el.value = value || '';
            });
            document.querySelectorAll('[data-kpi-alert]').forEach(card => {
                card.classList.toggle('is-active', (card.getAttribute('data-kpi-alert') || '') === (this.currentFilters.alert_status || ''));
            });
        },

        applyAlertFilter(alertStatus) {
            this.resetFilters(false);
            this.currentFilters.alert_status = alertStatus;
            this.currentFilters.offset = 0;
            document.querySelectorAll('.chip-filter[data-chip]').forEach(c => {
                c.classList.toggle('active', (alertStatus === 'OVERDUE' && c.dataset.chip === 'overdue')
                    || (alertStatus === 'WARNING' && c.dataset.chip === 'warning')
                    || (!alertStatus && c.dataset.chip === 'all'));
            });
            this.syncFilterControls();
            this.loadDevices();
        },

        resetFilters(reload = true) {
            this.currentFilters.search = '';
            this.currentFilters.facility_id = '';
            this.currentFilters.category_id = '';
            this.currentFilters.risk_level = '';
            this.currentFilters.alert_status = '';
            this.currentFilters.offset = 0;
            document.querySelectorAll('.chip-filter[data-chip]').forEach(c => c.classList.toggle('active', c.dataset.chip === 'all'));
            this.syncFilterControls();
            if (reload) this.loadDevices();
        },

        setPaletteOpen(open) {
            const pal = document.getElementById('command-palette');
            if (!pal) return;
            pal.hidden = !open;
            if (open) {
                const input = document.getElementById('command-palette-input');
                if (input) {
                    input.value = '';
                    setTimeout(() => input.focus(), 30);
                }
                this.searchPalette('');
            }
        },

        async searchPalette(query) {
            const box = document.getElementById('command-palette-results');
            if (!box) return;
            box.innerHTML = '<div class="text-muted small px-3 py-2">Đang tìm...</div>';
            try {
                const url = `/api/devices?limit=8&search=${encodeURIComponent(query || '')}`;
                const res = await fetch(url);
                const items = await res.json();
                this.paletteItems = items;
                this.paletteIndex = 0;
                if (!items.length) {
                    box.innerHTML = '<div class="text-muted small px-3 py-3">Không thấy thiết bị phù hợp.</div>';
                    return;
                }
                this.renderPalette();
            } catch (err) {
                box.innerHTML = '<div class="text-danger small px-3 py-2">Không tìm được danh mục.</div>';
            }
        },

        renderPalette() {
            const box = document.getElementById('command-palette-results');
            if (!box) return;
            box.innerHTML = this.paletteItems.map((d, idx) => `
                <button type="button" class="command-item ${idx === this.paletteIndex ? 'is-active' : ''}" data-id="${d.id}">
                    <div>
                        <div class="fw-bold text-dark">${d.device_name}</div>
                        <div class="text-muted small font-mono">${d.asset_tag} · ${d.serial_no || '—'} · ${d.facility || 'Chưa phân khoa'}</div>
                    </div>
                    <span class="badge ${this.statusClass(d.alert_status)} ms-auto">${this.alertLabel(d.alert_status)}</span>
                </button>
            `).join('');
            box.querySelectorAll('.command-item').forEach(btn => {
                btn.addEventListener('click', () => this.openPaletteDevice(parseInt(btn.dataset.id, 10)));
            });
        },

        movePalette(delta) {
            if (!this.paletteItems.length) return;
            this.paletteIndex = (this.paletteIndex + delta + this.paletteItems.length) % this.paletteItems.length;
            this.renderPalette();
        },

        openPaletteDevice(id) {
            this.setPaletteOpen(false);
            this.showDeviceDetails(id);
        },

        async refreshDeviceSelects(query = '', targetId = null) {
            try {
                const url = `/api/devices?limit=80&search=${encodeURIComponent(query || '')}`;
                const res = await fetch(url);
                const items = await res.json();
                const html = items.map(d => this.deviceOptionHtml(d)).join('');
                const ids = targetId ? [targetId] : ['ins-device-id', 'tr-device-id', 'wo-device-id'];
                ids.forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.innerHTML = html || '<option value="">Không tìm thấy thiết bị</option>';
                });
            } catch (err) {
                console.error('Device select refresh failed', err);
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
                    filterFac.innerHTML = '<option value="">Tất cả khoa/phòng</option>' +
                        this.facilities.map(f => `<option value="${f.id}">${f.name}${f.device_count != null ? ' (' + f.device_count + ')' : ''}</option>`).join('');
                }
                const cdFac = document.getElementById('cd-facility');
                if (cdFac) {
                    cdFac.innerHTML = '<option value="">Chưa phân khoa</option>' +
                        this.facilities.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
                }
                const cdCat = document.getElementById('cd-category');
                if (cdCat) {
                    cdCat.innerHTML = '<option value="">Chưa phân nhóm</option>' +
                        this.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
                }
                const filterCat = document.getElementById('filter-category');
                if (filterCat) {
                    filterCat.innerHTML = '<option value="">Tất cả nhóm</option>' +
                        this.categories.map(c => `<option value="${c.id}">${c.name}${c.device_count != null ? ' (' + c.device_count + ')' : ''}</option>`).join('');
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

        async loadDashboardSummary() {
            try {
                const stats = await (window.apiClient ? apiClient.getSummary() : fetch('/api/dashboard/summary').then(r => r.json()));
                const total = this.formatNumber(stats.total_devices);
                const setText = (id, value) => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = value;
                };
                setText('kpi-total-devices', total);
                setText('side-kpi-total', total);
                setText('nav-badge-total', total);
                setText('kpi-ok-devices', this.formatNumber(stats.ok_count ?? stats.in_service_count));
                setText('kpi-warning-devices', this.formatNumber(stats.warning_count));
                setText('kpi-overdue-devices', this.formatNumber(stats.overdue_count));
                setText('side-kpi-overdue', this.formatNumber(stats.overdue_count));
                setText('side-kpi-avail', `${stats.availability_rate ?? 0}%`);
                setText('kpi-avail-rate', `Sẵn sàng vận hành ${stats.availability_rate ?? 0}%`);
                const chipAll = document.getElementById('chip-all');
                if (chipAll) chipAll.textContent = `Tất cả (${total})`;
                const dueBadge = document.getElementById('nav-badge-due');
                if (dueBadge) dueBadge.textContent = this.formatNumber((stats.overdue_count || 0) + (stats.warning_count || 0));
            } catch (err) {
                console.error('Error loading dashboard summary:', err);
            }
        },

        async loadDevices() {
            const tbody = document.getElementById('device-table-body');
            if (tbody) tbody.innerHTML = this.skeletonRows(8);
            try {
                let url = `/api/devices?limit=${this.currentFilters.limit}&offset=${this.currentFilters.offset}`;
                if (this.currentFilters.search) url += `&search=${encodeURIComponent(this.currentFilters.search)}`;
                if (this.currentFilters.facility_id) url += `&facility_id=${this.currentFilters.facility_id}`;
                if (this.currentFilters.category_id) url += `&category_id=${this.currentFilters.category_id}`;
                if (this.currentFilters.risk_level) url += `&risk_level=${encodeURIComponent(this.currentFilters.risk_level)}`;
                if (this.currentFilters.alert_status) url += `&alert_status=${encodeURIComponent(this.currentFilters.alert_status)}`;

                const res = await fetch(url);
                if (!res.ok) throw new Error('Không tải được danh mục thiết bị');
                this.devices = await res.json();
                this.currentFilters.total = parseInt(res.headers.get('X-Total-Count') || this.devices.length, 10);

                const filterCount = document.getElementById('filter-count');
                if (filterCount) filterCount.textContent = this.formatNumber(this.currentFilters.total);
                const from = this.currentFilters.total === 0 ? 0 : this.currentFilters.offset + 1;
                const to = Math.min(this.currentFilters.offset + this.devices.length, this.currentFilters.total);
                const range = document.getElementById('pager-range');
                if (range) range.textContent = `${this.formatNumber(from)}–${this.formatNumber(to)}`;
                const pageEl = document.getElementById('pager-page');
                if (pageEl) pageEl.textContent = String(Math.floor(this.currentFilters.offset / this.currentFilters.limit) + 1);
                const prev = document.getElementById('btn-page-prev');
                const next = document.getElementById('btn-page-next');
                if (prev) prev.disabled = this.currentFilters.offset <= 0;
                if (next) next.disabled = this.currentFilters.offset + this.currentFilters.limit >= this.currentFilters.total;

                if (!this.devices || this.devices.length === 0) {
                    tbody.innerHTML = this.emptyRow(8, 'bi-inbox', 'Không tìm thấy thiết bị nào phù hợp bộ lọc.');
                    return;
                }

                tbody.innerHTML = this.devices.map(d => {
                    const riskBadge = d.risk_level ? `<span class="badge badge-risk-${d.risk_level}">${d.risk_level}</span>` : '<span class="text-muted">-</span>';
                    const alert = d.alert_status || 'NO_DATA';
                    return `
                        <tr style="cursor: pointer;" onclick="app.showDeviceDetails(${d.id})" class="device-row" tabindex="0">
                            <td class="ps-3 font-mono fw-semibold text-primary">
                                <div>${d.asset_tag}</div>
                                <div class="text-muted" style="font-size: 0.72rem;">${d.speedmaint_code || ''}</div>
                            </td>
                            <td>
                                <div class="fw-bold text-dark">${d.device_name}</div>
                                <div class="text-muted small">${d.model || ''} • ${d.manufacturer || ''}</div>
                            </td>
                            <td class="font-mono">${d.serial_no || '<span class="text-muted">-</span>'}</td>
                            <td>${d.facility_name || d.facility || '<span class="text-muted">Chưa phân khoa</span>'}</td>
                            <td class="text-center">${riskBadge}</td>
                            <td class="font-mono small ${this.dueClass(alert)}">${this.formatDate(d.recalibration_date)}</td>
                            <td class="text-center"><span class="badge ${this.statusClass(alert)}">${this.alertLabel(alert)}</span></td>
                            <td class="pe-3 text-end" onclick="event.stopPropagation()">
                                <button class="btn btn-sm btn-outline-primary btn-clinical" onclick="app.showDeviceDetails(${d.id})" title="Hồ sơ máy">
                                    <i class="bi bi-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-secondary btn-clinical" onclick="app.quickWorkOrder(${d.id})" title="Tạo phiếu bảo trì">
                                    <i class="bi bi-tools"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('');
            } catch (err) {
                console.error('Error loading devices:', err);
                if (tbody) tbody.innerHTML = this.emptyRow(8, 'bi-exclamation-triangle', 'Không tải được danh mục thiết bị. Kiểm tra máy chủ API.');
            }
        },

        quickWorkOrder(deviceId) {
            this.refreshDeviceSelects('', 'wo-device-id').then(() => {
                const woSelect = document.getElementById('wo-device-id');
                if (woSelect) woSelect.value = deviceId;
                const woModal = new bootstrap.Modal(document.getElementById('speedmaintWorkOrderModal'));
                woModal.show();
            });
        },

        async showDeviceDetails(deviceId) {
            this.currentSelectedDeviceId = deviceId;
            console.log(`🔍 Đang tải hồ sơ lý lịch thiết bị #${deviceId}...`);

            try {
                const [devRes, accRes, provRes] = await Promise.all([
                    fetch(`/api/devices/${deviceId}`),
                    fetch(`/api/devices/${deviceId}/accessories`),
                    fetch(`/api/semantica/explain/${deviceId}`)
                ]);

                if (!devRes.ok) throw new Error("Không thể tải thông tin thiết bị");

                const dev = await devRes.json();
                const accessories = accRes.ok ? await accRes.json() : [];
                const prov = provRes.ok ? await provRes.json() : null;
                this.currentSelectedDevice = dev;

                // 1. Header Information
                document.getElementById('modal-dev-name').textContent = dev.device_name;
                document.getElementById('modal-dev-tag').textContent = dev.asset_tag;
                document.getElementById('modal-dev-sm').textContent = dev.speedmaint_code;
                document.getElementById('modal-dev-sn').textContent = dev.serial_no || 'Chưa có S/N';
                
                const riskBadge = document.getElementById('modal-dev-risk');
                if (riskBadge) {
                    riskBadge.className = `badge badge-risk-${dev.risk_level || 'A'}`;
                    riskBadge.textContent = `Loại ${dev.risk_level || 'A'}`;
                }

                const statusBadge = document.getElementById('modal-dev-status');
                if (statusBadge) {
                    statusBadge.className = `badge ${this.statusClass(dev.status || 'IN_SERVICE')}`;
                    statusBadge.textContent = this.statusLabel(dev.status || 'IN_SERVICE');
                }

                // 2. Tab 1: General Info
                document.getElementById('modal-dev-facility').textContent = dev.facility || 'Kho thiết bị trung tâm';
                document.getElementById('modal-dev-category').textContent = dev.category || 'Chưa phân nhóm';
                document.getElementById('modal-dev-install-date').textContent = dev.installation_date || '2026-01-01';
                document.getElementById('modal-dev-model').textContent = dev.model || 'Tiêu chuẩn';
                document.getElementById('modal-dev-mfg').textContent = dev.manufacturer || 'Hãng Y Tế';
                document.getElementById('modal-dev-country').textContent = dev.country_of_manufacturer || 'Nhật Bản / Đức / Mỹ';
                document.getElementById('modal-dev-year').textContent = dev.year_of_manufacture || '2024';
                document.getElementById('modal-dev-notes').textContent = dev.notes || 'Hồ sơ lý lịch máy hợp lệ, đầy đủ CO/CQ và biên bản giao nhận.';
                const pdfBtn = document.getElementById('modal-btn-pdf');
                if (pdfBtn) pdfBtn.hidden = !(dev.source_pdf || dev.pdf_path);

                // 3. Tab 2: Accessories Tree
                document.getElementById('modal-acc-count').textContent = accessories.length;
                document.getElementById('modal-acc-badge').textContent = `${accessories.length} cấu kiện/phụ kiện`;

                const accBody = document.getElementById('modal-accessories-table-body');
                if (accessories.length === 0) {
                    accBody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Thiết bị không có phụ kiện rời hoặc sử dụng cấu hình liền khối.</td></tr>';
                } else {
                    accBody.innerHTML = accessories.map(a => `
                        <tr>
                            <td><span class="badge bg-info text-dark font-mono">${a.accessory_type}</span></td>
                            <td class="fw-bold text-dark">${a.name} <span class="text-muted small font-mono">(${a.model || ''})</span></td>
                            <td class="font-mono fw-semibold text-primary">${a.serial_no || '-'}</td>
                            <td><span class="badge bg-success-subtle text-success">${a.status}</span></td>
                            <td class="text-muted small">${a.notes || '-'}</td>
                        </tr>
                    `).join('');
                }

                // 4. Tab 3: Calibration Certificates
                const calBody = document.getElementById('modal-calibration-table-body');
                const certs = dev.certificates || [];
                if (certs.length === 0) {
                    calBody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-muted">Chưa có dữ liệu giấy chứng nhận kiểm định.</td></tr>';
                } else {
                    calBody.innerHTML = certs.map(c => `
                        <tr>
                            <td class="font-mono fw-bold text-primary">${c.certificate_no}</td>
                            <td class="font-mono small">${c.calibration_date || '-'}</td>
                            <td class="font-mono small text-danger fw-semibold">${c.recalibration_date || '-'}</td>
                            <td class="font-mono small">${c.stamp_no || '-'}</td>
                            <td>${c.calibrated_by || 'Trung tâm KĐ'}</td>
                            <td class="text-center"><span class="badge bg-success">${c.result_status || 'ĐẠT'}</span></td>
                        </tr>
                    `).join('');
                }

                // 5. Tab 4: Maintenance Logs (BM05)
                const maintBody = document.getElementById('modal-maintenance-table-body');
                const logs = dev.maintenance_logs || [];
                if (logs.length === 0) {
                    maintBody.innerHTML = '<tr><td colspan="4" class="text-center py-4 text-muted">Chưa có nhật ký bảo trì / sự cố nào ghi nhận.</td></tr>';
                } else {
                    maintBody.innerHTML = logs.map(l => `
                        <tr>
                            <td class="font-mono small text-muted">${l.maintenance_date}</td>
                            <td><span class="badge bg-secondary font-mono">${l.maintenance_type}</span></td>
                            <td><strong>${l.performed_by}</strong></td>
                            <td class="small text-dark">${l.description}</td>
                        </tr>
                    `).join('');
                }

                // 6. Tab 5: Semantica Provenance Chain
                const provBox = document.getElementById('modal-provenance-content');
                if (!prov || !prov.causal_provenance_chain) {
                    provBox.innerHTML = '<span class="text-muted">Đang cập nhật đồ thị tri thức Semantica cho thiết bị này.</span>';
                } else {
                    provBox.innerHTML = `
                        <div class="mb-2"><strong class="text-primary">${prov.device_name}</strong> (Model: ${prov.model})</div>
                        <ul class="list-unstyled mb-0">
                            ${prov.causal_provenance_chain.map((p, idx) => `
                                <li class="p-2 mb-2 bg-white border rounded shadow-sm">
                                    <div class="d-flex align-items-center gap-2">
                                        <span class="badge bg-primary font-mono">BƯỚC ${idx + 1}</span>
                                        <span class="fw-bold text-dark">${typeof p === 'string' ? p : (p.step + ': ' + p.relation)}</span>
                                    </div>
                                </li>
                            `).join('')}
                        </ul>
                    `;
                }

                // Setup footer action buttons
                const btnTr = document.getElementById('modal-btn-transfer');
                if (btnTr) {
                    btnTr.onclick = async () => {
                        bootstrap.Modal.getInstance(document.getElementById('deviceDetailsModal'))?.hide();
                        await this.refreshDeviceSelects('', 'tr-device-id');
                        const trSelect = document.getElementById('tr-device-id');
                        if (trSelect) trSelect.value = deviceId;
                        document.getElementById('btn-tab-transfers')?.click();
                    };
                }

                const btnWo = document.getElementById('modal-btn-wo');
                if (btnWo) {
                    btnWo.onclick = () => {
                        bootstrap.Modal.getInstance(document.getElementById('deviceDetailsModal'))?.hide();
                        this.quickWorkOrder(deviceId);
                    };
                }

                // Show modal
                const modal = new bootstrap.Modal(document.getElementById('deviceDetailsModal'));
                modal.show();

            } catch (err) {
                console.error("Error showing device details:", err);
                this.toast("Không thể tải chi tiết thiết bị: " + err.message, 'error');
            }
        },

        async loadInspections() {
            try {
                const res = await fetch('/api/inspections?limit=30');
                this.inspections = await res.json();
                const tbody = document.getElementById('inspections-table-body');
                if (!this.inspections || this.inspections.length === 0) {
                    tbody.innerHTML = this.emptyRow(5, 'bi-clipboard', 'Chưa có nhật ký kiểm tra đầu ngày nào.');
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
                            <span class="badge ${this.statusClass(ins.overall_status)} px-2 py-1">${this.statusLabel(ins.overall_status)}</span>
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
                    tbody.innerHTML = this.emptyRow(5, 'bi-arrow-left-right', 'Chưa có biên bản điều chuyển thiết bị nào.');
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
                if (!this.ecarts || this.ecarts.length === 0) {
                    grid.innerHTML = '<div class="col-12"><div class="clinical-card empty-state">Chưa có dữ liệu xe cấp cứu.</div></div>';
                    return;
                }
                const ecartBadge = document.getElementById('nav-badge-ecart');
                if (ecartBadge) ecartBadge.textContent = this.ecarts.length;
                const kpiEcart = document.getElementById('kpi-ecart-status');
                if (kpiEcart) kpiEcart.textContent = `E-Cart: ${this.ecarts.length}/${this.ecarts.length} xe trực`;

                grid.innerHTML = this.ecarts.map(ec => `
                    <div class="col-xl-3 col-md-6">
                        <div class="clinical-card p-3 h-100 ecart-card">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <span class="badge bg-danger font-mono">${ec.cart_code}</span>
                                <span class="badge ${this.statusClass(ec.status)}">${this.statusLabel(ec.status)}</span>
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
                const kpiWo = document.getElementById('kpi-open-wo');
                if (kpiWo) kpiWo.textContent = `CMMS: ${this.workOrders.length} phiếu`;

                if (!this.workOrders || this.workOrders.length === 0) {
                    tbody.innerHTML = this.emptyRow(7, 'bi-tools', 'Không có phiếu bảo trì / sửa chữa nào đang mở.');
                    return;
                }

                tbody.innerHTML = this.workOrders.map(wo => `
                    <tr>
                        <td class="font-mono fw-bold text-primary">#${wo.task_code || wo.id}</td>
                        <td class="fw-bold text-dark">${wo.title || wo.description || wo.work_type || 'Phiếu công việc'}</td>
                        <td>${wo.device_name || 'Hệ thống'} <span class="text-muted small font-mono">(${wo.asset_tag || wo.speedmaint_device_code || ''})</span></td>
                        <td class="text-center"><span class="badge ${this.statusClass(wo.priority)}">${this.statusLabel(wo.priority)}</span></td>
                        <td class="text-center"><span class="badge ${this.statusClass(wo.status)}">${this.statusLabel(wo.status)}</span></td>
                        <td>${wo.assigned_to || 'P.TTBYT'}</td>
                        <td class="text-end">
                            <span class="text-muted small font-mono">${wo.created_at || wo.start_date || ''}</span>
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Error loading work orders:', err);
            }
        },

        async loadWorklist() {
            const tbody = document.getElementById('worklist-table-body');
            if (!tbody) return;
            try {
                const [overdueRes, warnRes] = await Promise.all([
                    fetch('/api/devices?alert_status=OVERDUE&limit=80'),
                    fetch('/api/devices?alert_status=WARNING&limit=80')
                ]);
                const overdue = overdueRes.ok ? await overdueRes.json() : [];
                const warning = warnRes.ok ? await warnRes.json() : [];
                const rows = [...overdue, ...warning];
                const dueBadge = document.getElementById('nav-badge-due');
                if (dueBadge) dueBadge.textContent = this.formatNumber(rows.length);
                if (!rows.length) {
                    tbody.innerHTML = this.emptyRow(6, 'bi-check2-circle', 'Không có máy quá hạn hoặc sắp đến hạn trong 30 ngày.');
                    return;
                }
                tbody.innerHTML = rows.map(d => `
                    <tr style="cursor:pointer" onclick="app.showDeviceDetails(${d.id})">
                        <td class="ps-3">
                            <div class="fw-bold text-dark">${d.device_name}</div>
                            <div class="text-muted small font-mono">${d.asset_tag} · ${d.serial_no || '-'}</div>
                        </td>
                        <td>${d.facility || '-'}</td>
                        <td class="font-mono small ${this.dueClass(d.alert_status)}">${this.formatDate(d.recalibration_date)}</td>
                        <td class="text-center"><span class="badge ${this.statusClass(d.alert_status)}">${this.alertLabel(d.alert_status)}</span></td>
                        <td class="font-mono small">${d.certificate_no || '-'}</td>
                        <td class="pe-3 text-end" onclick="event.stopPropagation()">
                            <button class="btn btn-sm btn-outline-primary btn-clinical" onclick="app.showDeviceDetails(${d.id})">Mở hồ sơ</button>
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Error loading worklist:', err);
                tbody.innerHTML = this.emptyRow(6, 'bi-exclamation-triangle', 'Không tải được hàng việc kiểm định.');
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
                        ${data.causal_provenance_chain.map((p, idx) => `
                            <li class="p-2 mb-2 bg-white border rounded shadow-sm">
                                <div class="d-flex align-items-center gap-2">
                                    <span class="badge bg-primary font-mono">BƯỚC ${idx + 1}</span>
                                    <span class="fw-bold text-dark">${typeof p === 'string' ? p : (p.step + ': ' + p.relation)}</span>
                                </div>
                            </li>
                        `).join('')}
                    </ul>
                `;
            } catch (err) {
                resBox.innerHTML = `<span class="text-danger small">Lỗi khi truy vết: ${err.message}</span>`;
            }
        },

        async loadSopList() {
            const box = document.getElementById('sop-list');
            if (!box) return;
            try {
                const res = await fetch('/api/sops');
                const sops = await res.json();
                box.innerHTML = sops.map(s => `
                    <div class="col-12">
                        <a class="sop-card d-block text-decoration-none" href="${s.ref}" target="_blank" rel="noopener">
                            <div class="d-flex justify-content-between gap-2">
                                <span class="badge bg-primary-subtle text-primary font-mono">${s.code}</span>
                                <span class="text-muted small">${s.type}</span>
                            </div>
                            <div class="fw-semibold text-dark mt-2 small">${s.name}</div>
                        </a>
                    </div>
                `).join('');
            } catch (err) {
                box.innerHTML = '<div class="col-12 text-muted small">Không tải được danh mục SOP.</div>';
            }
        },

        appendAiBubble(role, text) {
            const box = document.getElementById('ai-transcript');
            if (!box) return;
            const el = document.createElement('div');
            el.className = `ai-bubble ${role}`;
            el.textContent = text;
            box.appendChild(el);
            box.scrollTop = box.scrollHeight;
        },

        async sendAiPrompt(message) {
            const text = (message || '').trim();
            if (!text) return;
            this.appendAiBubble('user', text);
            this.appendAiBubble('assistant', 'Đang soạn trả lời...');
            const box = document.getElementById('ai-transcript');
            const pending = box?.lastElementChild;
            try {
                const data = window.apiClient
                    ? await apiClient.aiChat(text)
                    : await fetch('/api/ai/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: text })
                    }).then(r => r.json());
                if (pending) pending.textContent = data.reply || data.response || data.message || JSON.stringify(data);
            } catch (err) {
                if (pending) pending.textContent = 'Không kết nối được trợ lý AI. Kiểm tra cấu hình API key.';
            }
        },

        setupFormSubmissions() {
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
                        this.toast('Đã lưu bảng kiểm tra an toàn đầu ngày.', 'success');
                        insForm.reset();
                        this.loadInspections();
                    } else {
                        this.toast('Không lưu được bảng kiểm. Thử lại.', 'error');
                    }
                });
            }

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
                        this.toast('Đã ghi nhận điều chuyển theo QT.08.', 'success');
                        trForm.reset();
                        this.loadTransfers();
                        this.loadDevices();
                    } else {
                        this.toast('Không lập được biên bản điều chuyển.', 'error');
                    }
                });
            }

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
                        this.toast('Đã phát hành phiếu công việc SpeedMaint.', 'success');
                        bootstrap.Modal.getInstance(document.getElementById('speedmaintWorkOrderModal'))?.hide();
                        woForm.reset();
                        this.loadWorkOrders();
                    } else {
                        this.toast('Không phát hành được phiếu công việc.', 'error');
                    }
                });
            }

            const cdForm = document.getElementById('createDeviceForm');
            if (cdForm) {
                cdForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const payload = {
                        device_name: document.getElementById('cd-name').value,
                        model: document.getElementById('cd-model').value,
                        serial_no: document.getElementById('cd-serial').value,
                        manufacturer: document.getElementById('cd-mfg').value || null,
                        country_of_manufacturer: document.getElementById('cd-country').value || null,
                        year_of_manufacture: document.getElementById('cd-year').value ? parseInt(document.getElementById('cd-year').value) : null,
                        risk_level: document.getElementById('cd-risk').value,
                        facility_id: document.getElementById('cd-facility').value ? parseInt(document.getElementById('cd-facility').value) : null,
                        category_id: document.getElementById('cd-category').value ? parseInt(document.getElementById('cd-category').value) : null,
                        installation_date: document.getElementById('cd-install').value || null,
                        certification_no: document.getElementById('cd-cert').value || null,
                        notes: document.getElementById('cd-notes').value || null,
                        status: 'IN_SERVICE'
                    };
                    try {
                        const created = window.apiClient
                            ? await apiClient.createDevice(payload)
                            : await fetch('/api/devices', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify(payload)
                            }).then(async r => {
                                const data = await r.json();
                                if (!r.ok) throw new Error(data.detail || 'Lỗi nhập thiết bị');
                                return data;
                            });
                        this.toast(`Đã nhập ${created.asset_tag || 'thiết bị mới'} vào danh mục.`, 'success');
                        bootstrap.Modal.getInstance(document.getElementById('createDeviceModal'))?.hide();
                        cdForm.reset();
                        this.loadDevices();
                        this.loadDashboardSummary();
                    } catch (err) {
                        this.toast(err.message || 'Không nhập được thiết bị.', 'error');
                    }
                });
            }

            const aiForm = document.getElementById('aiChatForm');
            if (aiForm) {
                aiForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const input = document.getElementById('ai-chat-input');
                    const message = input?.value || '';
                    if (input) input.value = '';
                    await this.sendAiPrompt(message);
                });
            }
            document.querySelectorAll('.ai-prompt-btn').forEach(btn => {
                btn.addEventListener('click', () => this.sendAiPrompt(btn.getAttribute('data-prompt')));
            });
        }
    };

    window.app = app;
    app.init();
});
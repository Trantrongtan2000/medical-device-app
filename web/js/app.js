/**
 * 🏥 Medical Device Management System (BV Quận 7 / PKĐK Tâm Anh Q7)
 * ✨ UI/UX Pro Max Application Client Logic
 * 📌 Hỗ trợ Bảng Thông Tin Chi Tiết Thiết Bị Khi Bấm Chọn (Device Passport Modal)
 */

document.addEventListener('DOMContentLoaded', function () {
    console.log('🚀 UI/UX Pro Max Clinical Client Logic initialized.');

    const app = {
        devices: [],
        facilities: [],
        categories: [],
        inspections: [],
        transfers: [],
        workOrders: [],
        currentSelectedDeviceId: null,
        currentFilters: {
            search: '',
            facility_id: '',
            risk_level: '',
            limit: 300,
            offset: 0
        },

        async init() {
            this.initSidebarState();
            this.initKanban();
            this.initOverviewCharts();
            this.setupNavigation();
            this.setupFormSubmissions();
            await this.loadInitialData();
            await this.loadDevices();
            await this.loadInspections();
            await this.loadTransfers();
            await this.loadWorkOrders();
            this.loadStaff();
            this.loadOncallData();
            await this.loadSemanticaStats();
            await this.loadActivityFeed();

            // Render default diagram
            if (window.DiagramEngine) {
                DiagramEngine.render('diagram-container', 'qt04');
            }
        },

        
        
        // ==================== KANBAN BOARD INTERACTIVE ENGINE ====================
        kanbanTasks: [
            {
                id: 'kb-1',
                col: 'todo',
                priority: 'Khẩn cấp',
                type: 'Báo hỏng',
                title: 'Máy thở xâm lấn Vela',
                meta: 'Khoa Cấp Cứu • S/N: VEL8829',
                assignee: 'BS. Nguyễn Tuấn',
                deadline: 'Hạn: Hôm nay'
            },
            {
                id: 'kb-2',
                col: 'todo',
                priority: 'Cao',
                type: 'Kiểm định',
                title: 'Máy Chụp X-Quang Kỹ Thuật Số',
                meta: 'Khoa CĐHA • S/N: XR2024-91',
                assignee: 'Viện Trang Thiết Bị',
                deadline: '15 ngày tới'
            },
            {
                id: 'kb-3',
                col: 'todo',
                priority: 'Bình thường',
                type: 'QT.08',
                title: 'Điều chuyển Monitor Bionet',
                meta: 'Khoa Cấp Cứu → Khoa Khám Bệnh',
                assignee: 'ĐD. Trưởng Khoa',
                deadline: 'Chờ ký BM03'
            },
            {
                id: 'kb-4',
                col: 'inprog',
                priority: 'Bình thường',
                type: 'PM Định kỳ',
                title: 'Hệ Thống Lọc Nước RO Thận #01',
                meta: 'Khu Thận Nhân Tạo • QT.01',
                assignee: 'KS. Trần Văn Hùng',
                deadline: 'Tiến độ 60%'
            },
            {
                id: 'kb-5',
                col: 'inprog',
                priority: 'Cao',
                type: 'Sửa chữa',
                title: 'Máy Siêu Âm Voluson E10',
                meta: 'Khoa CĐHA • Thay cáp đầu dò',
                assignee: 'Hãng GE Healthcare',
                deadline: 'Đang test'
            },
            {
                id: 'kb-6',
                col: 'review',
                priority: 'Bình thường',
                type: 'BM04',
                title: 'Máy Sốc Tim Defibrillator TEC-5600',
                meta: 'Khoa Cấp Cứu • Nihon Kohden',
                assignee: 'ĐD. Trưởng trực',
                deadline: 'Chờ ký BM04'
            },
            {
                id: 'kb-7',
                col: 'review',
                priority: 'Cao',
                type: 'TT 05',
                title: 'Máy Đo Điện Tim 6 Cần ECG',
                meta: 'Phòng Khám Nội • GCN #2026-881',
                assignee: 'TT Kiểm Định 3',
                deadline: 'Dán tem ĐẠT'
            },
            {
                id: 'kb-8',
                col: 'done',
                priority: 'Bình thường',
                type: 'Hoàn tất',
                title: 'Máy Siêu Âm 4D HERA W10',
                meta: 'Cty An Việt • Bàn giao 5 đầu dò',
                assignee: 'Khoa CĐHA',
                deadline: 'Đã nghiệm thu'
            },
            {
                id: 'kb-9',
                col: 'done',
                priority: 'Bình thường',
                type: 'Hoàn tất',
                title: 'Bảo dưỡng Khí Y Tế Trung Tâm',
                meta: 'Áp suất Oxy & N2O đạt chuẩn QT.03',
                assignee: 'P.TTBYT',
                deadline: 'Sẵn sàng 100%'
            }
        ],

        initKanban() {
            // Load saved state from localStorage if available
            const saved = localStorage.getItem('tamanh_kanban_tasks');
            if (saved) {
                try {
                    this.kanbanTasks = JSON.parse(saved);
                } catch (e) {
                    console.error("Error loading saved kanban:", e);
                }
            }

            this.renderKanban();
            this.setupKanbanDragAndDrop();
            this.setupKanbanForm();
        },

        escapeHtml(value) {
            return String(value ?? '').replace(/[&<>"']/g, ch => ({
                '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
            }[ch]));
        },

        saveKanbanState() {
            localStorage.setItem('tamanh_kanban_tasks', JSON.stringify(this.kanbanTasks));
        },

        renderKanban() {
            const cols = {
                todo: document.getElementById('kanban-col-todo'),
                inprog: document.getElementById('kanban-col-inprog'),
                review: document.getElementById('kanban-col-review'),
                done: document.getElementById('kanban-col-done')
            };

            if (!cols.todo) return;

            // Clear containers
            Object.values(cols).forEach(c => { if (c) c.innerHTML = ''; });

            const counts = { todo: 0, inprog: 0, review: 0, done: 0 };

            this.kanbanTasks.forEach(task => {
                const colKey = task.col || 'todo';
                task.col = colKey;
                const targetCol = cols[colKey] || cols.todo;
                counts[colKey] = (counts[colKey] || 0) + 1;

                let borderClass = 'border-primary';
                let pBadgeClass = 'bg-primary text-white';
                if (task.priority === 'Khẩn cấp') {
                    borderClass = 'border-danger';
                    pBadgeClass = 'bg-danger text-white';
                } else if (task.priority === 'Cao') {
                    borderClass = 'border-warning';
                    pBadgeClass = 'bg-warning text-dark';
                }

                const isDone = task.col === 'done';

                const cardEl = document.createElement('div');
                cardEl.className = `kanban-card border-start border-4 ${borderClass} ${isDone ? 'opacity-75' : ''}`;
                cardEl.draggable = true;
                cardEl.id = task.id;

                cardEl.style.cursor = 'pointer';
                cardEl.title = 'Nhấp để chỉnh sửa thông tin thẻ này';
                cardEl.addEventListener('click', (e) => {
                    if (e.target.closest('.kanban-card-actions')) return;
                    app.openEditKanbanModal(task.id);
                });

                cardEl.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <span class="badge ${pBadgeClass} font-mono" style="font-size: 0.7rem;" onclick="event.stopPropagation(); app.openEditKanbanModal('${task.id}')" title="Nhấp để đổi ưu tiên">${this.escapeHtml(task.priority)}</span>
                        <div class="d-flex align-items-center gap-1">
                            <span class="badge bg-light text-dark border font-mono" style="font-size: 0.68rem;" onclick="event.stopPropagation(); app.openEditKanbanModal('${task.id}')" title="Nhấp để đổi loại thẻ">${this.escapeHtml(task.type)}</span>
                            <button class="btn btn-sm btn-link p-0 text-primary kanban-card-actions" onclick="event.stopPropagation(); app.openEditKanbanModal('${task.id}')" title="Chỉnh sửa thông tin">
                                <i class="bi bi-pencil-square"></i>
                            </button>
                            <button class="btn btn-sm btn-link p-0 text-danger kanban-card-actions" onclick="event.stopPropagation(); app.deleteKanbanTask('${task.id}')" title="Xóa thẻ">
                                <i class="bi bi-x fs-6"></i>
                            </button>
                        </div>
                    </div>
                    <div class="kanban-card-title ${isDone ? 'text-decoration-line-through text-muted' : ''}">${this.escapeHtml(task.title)}</div>
                    <div class="kanban-card-meta mb-1">${this.escapeHtml(task.meta)}</div>
                    <div class="d-flex justify-content-between align-items-center pt-2 border-top mt-2 font-mono" style="font-size: 0.72rem;">
                        <span class="text-muted"><i class="bi bi-person me-1"></i>${this.escapeHtml(task.assignee || 'P.TTBYT')}</span>
                        <span class="${task.priority === 'Khẩn cấp' ? 'text-danger fw-bold' : (isDone ? 'text-success fw-bold' : 'text-primary')}">${this.escapeHtml(task.deadline || '')}</span>
                    </div>
                    <!-- Quick Move Controls -->
                    <div class="d-flex justify-content-end gap-1 mt-2 pt-1 border-top kanban-card-actions">
                        ${task.col !== 'todo' ? `<button class="btn btn-sm btn-light border py-0 px-1 font-mono" style="font-size: 0.68rem;" onclick="event.stopPropagation(); app.moveKanbanTask('${task.id}', -1)">◀ Lùi</button>` : ''}
                        ${task.col !== 'done' ? `<button class="btn btn-sm btn-light border py-0 px-1 font-mono text-primary" style="font-size: 0.68rem;" onclick="event.stopPropagation(); app.moveKanbanTask('${task.id}', 1)">Tiếp ▶</button>` : ''}
                    </div>
                `;

                // Add dragstart & dragend
                cardEl.addEventListener('dragstart', (e) => {
                    cardEl.classList.add('dragging');
                    e.dataTransfer.setData('text/plain', task.id);
                });

                cardEl.addEventListener('dragend', () => {
                    cardEl.classList.remove('dragging');
                });

                targetCol.appendChild(cardEl);
            });

            // Update badge counts
            const elTodo = document.getElementById('kanban-count-todo');
            const elInprog = document.getElementById('kanban-count-inprog');
            const elReview = document.getElementById('kanban-count-review');
            const elDone = document.getElementById('kanban-count-done');

            if (elTodo) elTodo.textContent = counts.todo;
            if (elInprog) elInprog.textContent = counts.inprog;
            if (elReview) elReview.textContent = counts.review;
            if (elDone) elDone.textContent = counts.done;
        },

        setupKanbanDragAndDrop() {
            const columns = document.querySelectorAll('.kanban-column');

            columns.forEach(col => {
                col.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    col.classList.add('drag-over');
                });

                col.addEventListener('dragleave', () => {
                    col.classList.remove('drag-over');
                });

                col.addEventListener('drop', (e) => {
                    e.preventDefault();
                    col.classList.remove('drag-over');

                    const taskId = e.dataTransfer.getData('text/plain');
                    const cardsContainer = col.querySelector('.kanban-cards-container');
                    if (!cardsContainer) return;

                    const colId = cardsContainer.id.replace('kanban-col-', ''); // todo, inprog, review, done
                    
                    const task = this.kanbanTasks.find(t => t.id === taskId);
                    if (task && task.col !== colId) {
                        task.col = colId;
                        this.saveKanbanState();
                        this.renderKanban();
                    }
                });
            });
        },

        moveKanbanTask(taskId, direction) {
            const steps = ['todo', 'inprog', 'review', 'done'];
            const task = this.kanbanTasks.find(t => t.id === taskId);
            if (!task) return;

            const currentIndex = steps.indexOf(task.col);
            const newIndex = currentIndex + direction;
            if (newIndex >= 0 && newIndex < steps.length) {
                task.col = steps[newIndex];
                this.saveKanbanState();
                this.renderKanban();
            }
        },

        deleteKanbanTask(taskId) {
            if (confirm("Bạn có chắc muốn xóa thẻ Kanban này?")) {
                this.kanbanTasks = this.kanbanTasks.filter(t => t.id !== taskId);
                this.saveKanbanState();
                this.renderKanban();
            }
        },

        
        openEditKanbanModal(taskId) {
            const task = this.kanbanTasks.find(t => t.id === taskId);
            if (!task) return;

            document.getElementById('edit-kanban-id').value = task.id;
            document.getElementById('edit-kanban-title').value = task.title || '';
            document.getElementById('edit-kanban-type').value = task.type || 'Báo hỏng';
            document.getElementById('edit-kanban-priority').value = task.priority || 'Bình thường';
            document.getElementById('edit-kanban-meta').value = task.meta || '';
            document.getElementById('edit-kanban-assignee').value = task.assignee || '';
            document.getElementById('edit-kanban-col').value = task.col || 'todo';
            document.getElementById('edit-kanban-deadline').value = task.deadline || '';

            const modal = new bootstrap.Modal(document.getElementById('editKanbanTaskModal'));
            modal.show();
        },

        submitEditKanbanTask() {
            const taskId = document.getElementById('edit-kanban-id').value;
            const task = this.kanbanTasks.find(t => t.id === taskId);
            if (!task) return;

            task.title = document.getElementById('edit-kanban-title').value.trim() || 'Tác vụ';
            task.type = document.getElementById('edit-kanban-type').value.trim() || 'Công tác';
            task.priority = document.getElementById('edit-kanban-priority').value;
            task.meta = document.getElementById('edit-kanban-meta').value.trim();
            task.assignee = document.getElementById('edit-kanban-assignee').value.trim() || 'P.TTBYT';
            task.col = document.getElementById('edit-kanban-col').value;
            task.deadline = document.getElementById('edit-kanban-deadline').value.trim();

            this.saveKanbanState();
            this.renderKanban();

            bootstrap.Modal.getInstance(document.getElementById('editKanbanTaskModal'))?.hide();
        },

        deleteCurrentEditingKanbanTask() {
            const taskId = document.getElementById('edit-kanban-id').value;
            if (!taskId) return;
            if (confirm('Bạn có chắc chắn muốn xóa tác vụ Kanban này?')) {
                this.deleteKanbanTask(taskId);
                bootstrap.Modal.getInstance(document.getElementById('editKanbanTaskModal'))?.hide();
            }
        },

        setupKanbanForm() {
            const form = document.getElementById('createKanbanTaskForm');
            if (!form) return;

            form.addEventListener('submit', (e) => {
                e.preventDefault();

                const newTask = {
                    id: 'kb-' + Date.now(),
                    title: document.getElementById('kanban-input-title').value,
                    type: document.getElementById('kanban-input-type').value,
                    priority: document.getElementById('kanban-input-priority').value,
                    meta: document.getElementById('kanban-input-facility').value || 'Khoa lâm sàng',
                    assignee: document.getElementById('kanban-input-assignee').value || 'P.TTBYT',
                    col: document.getElementById('kanban-input-col').value,
                    deadline: document.getElementById('kanban-input-deadline').value || 'Trong tuần'
                };

                this.kanbanTasks.unshift(newTask);
                this.saveKanbanState();
                this.renderKanban();

                form.reset();
                bootstrap.Modal.getInstance(document.getElementById('createKanbanTaskModal'))?.hide();
            });
        },

        initOverviewCharts() {
            if (!window.Chart) return;

            // 1. Department Distribution Chart
            const deptCtx = document.getElementById('chartDepartmentAssets')?.getContext('2d');
            if (deptCtx) {
                if (this.deptChart) this.deptChart.destroy();

                const topDepts = [
                    { name: 'CĐHA (Siêu âm/MRI/CT)', count: 245 },
                    { name: 'Khám Bệnh', count: 185 },
                    { name: 'Cấp Cứu', count: 142 },
                    { name: 'Xét Nghiệm', count: 120 },
                    { name: 'Gây Mê Hồi Sức', count: 98 },
                    { name: 'Nội Tổng Hợp', count: 85 },
                    { name: 'Phụ Sản', count: 72 },
                    { name: 'Nhi Khoa', count: 68 },
                    { name: 'Khác (13 Khoa)', count: 58 }
                ];

                this.deptChart = new Chart(deptCtx, {
                    type: 'bar',
                    data: {
                        labels: topDepts.map(d => d.name),
                        datasets: [{
                            label: 'Số lượng thiết bị',
                            data: topDepts.map(d => d.count),
                            backgroundColor: '#0284c7',
                            borderRadius: 4,
                            barThickness: 18
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: {
                                grid: { display: false },
                                ticks: { font: { family: 'Plus Jakarta Sans', size: 10 } }
                            },
                            y: {
                                beginAtZero: true,
                                grid: { color: '#f1f5f9' },
                                ticks: { font: { family: 'JetBrains Mono', size: 10 } }
                            }
                        }
                    }
                });
            }

            // 2. Risk Breakdown Donut Chart
            const riskCtx = document.getElementById('chartRiskBreakdown')?.getContext('2d');
            if (riskCtx) {
                if (this.riskChart) this.riskChart.destroy();

                this.riskChart = new Chart(riskCtx, {
                    type: 'doughnut',
                    data: {
                        labels: ['Loại A (Rất thấp)', 'Loại B (Thấp)', 'Loại C (Trung bình cao)', 'Loại D (Đặc biệt cao)'],
                        datasets: [{
                            data: [375, 268, 322, 108],
                            backgroundColor: ['#059669', '#0284c7', '#d97706', '#dc2626'],
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '70%',
                        plugins: {
                            legend: { display: false }
                        }
                    }
                });
            }
        },

        
        // ==================== SNIPE-IT CHECKOUT & CHECKIN METHODS ====================
        openCheckoutModal(deviceId) {
            const dev = this.devices.find(d => d.id === deviceId) || this.currentSelectedDevice;
            if (!dev || Number(dev.id) !== Number(deviceId)) {
                fetch(`/api/devices/${deviceId}`).then(r => r.json()).then(full => {
                    this.currentSelectedDevice = full;
                    this.openCheckoutModal(deviceId);
                }).catch(() => alert('Không tải được hồ sơ thiết bị để checkout.'));
                return;
            }

            document.getElementById('checkout-dev-id').value = dev.id;
            document.getElementById('checkout-dev-name').textContent = dev.device_name;
            document.getElementById('checkout-dev-tag').textContent = dev.asset_tag;
            document.getElementById('checkout-date').value = new Date().toISOString().split('T')[0];

            const facSelect = document.getElementById('checkout-target-facility');
            if (facSelect) {
                facSelect.innerHTML = this.facilities.map(f => `<option value="${f.id}" ${f.id === dev.facility_id ? 'selected' : ''}>${f.name}</option>`).join('');
            }

            const modal = new bootstrap.Modal(document.getElementById('checkoutDeviceModal'));
            modal.show();
        },

        async checkinDevice(deviceId) {
            const dev = this.devices.find(d => d.id === deviceId);
            const devName = dev ? dev.device_name : `Thiết bị #${deviceId}`;

            if (!confirm(`Bạn có chắc muốn thu hồi "${devName}" về Kho dự phòng trung tâm?`)) return;

            try {
                const res = await fetch(`/api/devices/${deviceId}/checkin`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ note: "Thu hồi hoàn trả về kho trung tâm" })
                });
                const result = await res.json();
                if (!res.ok) throw new Error(result.detail || 'Lỗi khi thu hồi thiết bị');

                alert('✅ ' + result.message);
                this.loadDevices();
                this.loadActivityFeed();
            } catch (err) {
                alert('❌ Lỗi thu hồi: ' + err.message);
            }
        },

        setupCheckoutForm() {
            const form = document.getElementById('checkoutDeviceForm');
            if (!form) return;

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const devId = parseInt(document.getElementById('checkout-dev-id').value);
                const payload = {
                    facility_id: parseInt(document.getElementById('checkout-target-facility').value),
                    assigned_to_name: document.getElementById('checkout-assigned-to').value,
                    checkout_date: document.getElementById('checkout-date').value,
                    note: document.getElementById('checkout-note').value
                };

                try {
                    const res = await fetch(`/api/devices/${devId}/checkout`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi khi bàn giao');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('checkoutDeviceModal'))?.hide();
                    this.loadDevices();
                    this.loadActivityFeed();
                } catch (err) {
                    alert('❌ Lỗi bàn giao: ' + err.message);
                }
            });
        },

        setupGlobalShortcuts() {
            window.addEventListener('keydown', (e) => {
                // Ctrl+K or Cmd+K to jump to search
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                    e.preventDefault();
                    const searchInput = document.getElementById('search-input');
                    if (searchInput) {
                        document.getElementById('btn-tab-devices')?.click();
                        searchInput.focus();
                        searchInput.select();
                    }
                }
            });
        },

        async loadActivityFeed() {
            const tbody = document.getElementById('overview-activity-tbody');
            if (!tbody) return;
            try {
                const res = await fetch('/api/dashboard/activity?limit=12');
                if (!res.ok) return;
                const events = await res.json();
                if (!Array.isArray(events) || !events.length) return;
                const badge = (type) => {
                    const t = String(type || '').toLowerCase();
                    if (t.includes('inspect')) return 'bg-primary';
                    if (t.includes('checkin')) return 'bg-warning text-dark';
                    if (t.includes('checkout') || t.includes('handover')) return 'bg-success';
                    if (t.includes('repair')) return 'bg-danger';
                    return 'bg-secondary';
                };
                tbody.innerHTML = events.map(ev => `
                    <tr>
                        <td class="font-mono text-muted small">${this.escapeHtml(ev.occurred_at || '')}</td>
                        <td><span class="badge ${badge(ev.type)} font-mono">${this.escapeHtml(ev.type || 'HTM')}</span></td>
                        <td>
                            <strong>${this.escapeHtml(ev.title || '')}</strong>
                            <div class="text-muted font-mono" style="font-size:0.72rem;">${this.escapeHtml(ev.asset_tag || '')}</div>
                        </td>
                        <td>${this.escapeHtml(ev.actor || 'P.TTBYT')}</td>
                        <td class="text-center"><span class="badge bg-light text-dark border">${this.escapeHtml((ev.detail || '').slice(0, 48) || 'OK')}</span></td>
                    </tr>
                `).join('');
            } catch (err) {
                console.error('Activity feed failed', err);
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

                        // Quick Filter Chips for 4 Clinical Departments
            const chips = document.querySelectorAll('.chip-filter');
            chips.forEach(chip => {
                chip.addEventListener('click', () => {
                    chips.forEach(c => c.classList.remove('active'));
                    chip.classList.add('active');

                    const filterType = chip.getAttribute('data-chip');
                    const facSelect = document.getElementById('filter-facility');
                    const rSelect = document.getElementById('filter-risk');
                    const sInput = document.getElementById('search-input');

                    if (filterType === 'all') {
                        this.currentFilters.search = '';
                        this.currentFilters.risk_level = '';
                        this.currentFilters.facility = '';
                        if (facSelect) facSelect.value = '';
                    } else if (filterType === 'khambenh') {
                        this.currentFilters.search = 'Khám Bệnh';
                        this.currentFilters.risk_level = '';
                    } else if (filterType === 'cdha') {
                        this.currentFilters.search = 'Chẩn Đoán Hình Ảnh';
                        this.currentFilters.risk_level = '';
                    } else if (filterType === 'nsth') {
                        this.currentFilters.search = 'Nội Soi';
                        this.currentFilters.risk_level = '';
                    } else if (filterType === 'emergency') {
                        this.currentFilters.search = 'Cấp Cứu';
                        this.currentFilters.risk_level = '';
                    } else if (filterType === 'highrisk') {
                        this.currentFilters.search = '';
                        this.currentFilters.risk_level = 'C';
                    }
                    if (sInput) sInput.value = this.currentFilters.search;
                    if (rSelect) rSelect.value = this.currentFilters.risk_level;
                    this.loadDevices();
                });
            });
        },

        printDevicePassport() {
            window.print();
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

                this.renderCurrentDeviceView(); return;
                tbody.innerHTML = this.devices.map(d => {
                    const riskMap = {
                        'A': { bg: '#059669', text: '#ffffff' },
                        'B': { bg: '#0284c7', text: '#ffffff' },
                        'C': { bg: '#d97706', text: '#ffffff' },
                        'D': { bg: '#dc2626', text: '#ffffff' }
                    };
                    const rStyle = riskMap[d.risk_level] || { bg: '#64748b', text: '#ffffff' };
                    const riskBadge = d.risk_level ? `<span class="badge badge-risk-${d.risk_level}" style="background-color: ${rStyle.bg} !important; color: #ffffff !important; font-weight: 800; font-size: 0.82rem; padding: 0.35rem 0.65rem; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.15);">${d.risk_level}</span>` : '<span class="text-muted">-</span>';

                    // Tag Nhà Cung Cấp / Hãng
                    const supplierName = d.supplier_name || (d.manufacturer ? `Hãng ${d.manufacturer}` : 'Chưa có thông tin NCC');
                    const supplierTag = `<span class="badge bg-light text-dark border border-secondary-subtle font-mono" style="font-size: 0.74rem; font-weight: 600; padding: 0.25rem 0.5rem;"><i class="bi bi-building text-primary me-1"></i>${supplierName}</span>`;

                    // Tag Khoa Phòng Quản Lý
                    const facName = d.facility || d.facility_name;
                    const facilityTag = facName ? 
                        `<span class="badge bg-light text-dark border border-primary-subtle fw-bold" style="font-size: 0.8rem; padding: 0.35rem 0.65rem;"><i class="bi bi-geo-alt-fill text-danger me-1"></i>${facName}</span>` : 
                        `<span class="badge bg-warning-subtle text-warning border" style="font-size: 0.75rem;">Chưa phân khoa</span>`;

                    return `
                        <tr style="cursor: pointer;" onclick="app.showDeviceDetails(${d.id})" class="device-row">
                            <td class="ps-3 font-mono fw-semibold text-primary">
                                <div>${d.asset_tag}</div>
                                <div class="text-muted" style="font-size: 0.72rem;">${d.speedmaint_code || ''}</div>
                            </td>
                            <td>
                                <div class="fw-bold text-dark text-hover-primary mb-1">${d.device_name}</div>
                                <div class="d-flex flex-wrap align-items-center gap-1">
                                    <span class="badge bg-secondary-subtle text-dark font-mono" style="font-size: 0.72rem;">Model: ${d.model || 'N/A'}</span>
                                    ${supplierTag}
                                </div>
                            </td>
                            <td class="font-mono fw-semibold text-dark">${d.serial_no || '<span class="text-muted">-</span>'}</td>
                            <td>${facilityTag}</td>
                            <td class="text-center">${riskBadge}</td>
                            <td class="text-center">
                                <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1">${d.status || 'Hoạt động'}</span>
                            </td>
                            <td class="pe-3 text-end" onclick="event.stopPropagation()">
                                <div class="d-flex justify-content-end gap-1">
                                    <button class="btn btn-sm btn-success btn-clinical" onclick="app.openCheckoutModal(${d.id})" title="Checkout / bàn giao">
                                        <i class="bi bi-box-arrow-right"></i>
                                    </button>
                                    <button class="btn btn-sm btn-outline-warning text-dark btn-clinical" onclick="app.checkinDevice(${d.id})" title="Checkin về kho">
                                        <i class="bi bi-box-arrow-in-left"></i>
                                    </button>
                                    <button class="btn btn-sm btn-primary btn-clinical" onclick="app.showDeviceDetails(${d.id})" title="Xem hồ sơ lý lịch chi tiết">
                                        <i class="bi bi-eye"></i> Chi tiết
                                    </button>
                                    <button class="btn btn-sm btn-outline-warning text-dark btn-clinical" onclick="app.openEditDeviceModal(${d.id})" title="Điều chỉnh thông tin thiết bị">
                                        <i class="bi bi-pencil-square"></i> Sửa
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }).join('');
            } catch (err) {
                console.error('Error loading devices:', err);
            }
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
                this.currentSelectedDevice = dev;
                const accessories = accRes.ok ? await accRes.json() : [];
                const prov = provRes.ok ? await provRes.json() : null;

                // 1. Header Information
                document.getElementById('modal-dev-name').textContent = dev.device_name;
                document.getElementById('modal-dev-tag').textContent = dev.asset_tag;
                document.getElementById('modal-dev-sm').textContent = dev.speedmaint_code;
                document.getElementById('modal-dev-sn').textContent = dev.serial_no || 'Chưa có S/N';
                
                const riskMap = {
                    'A': { bg: '#059669', text: '#ffffff' },
                    'B': { bg: '#0284c7', text: '#ffffff' },
                    'C': { bg: '#d97706', text: '#ffffff' },
                    'D': { bg: '#dc2626', text: '#ffffff' }
                };
                const rStyle = riskMap[dev.risk_level] || { bg: '#64748b', text: '#ffffff' };
                const riskBadge = document.getElementById('modal-dev-risk');
                if (riskBadge) {
                    riskBadge.className = `badge badge-risk-${dev.risk_level || 'A'}`;
                    riskBadge.style.cssText = `background-color: ${rStyle.bg} !important; color: #ffffff !important; font-weight: 800; font-size: 0.82rem; padding: 0.35rem 0.65rem; border-radius: 6px;`;
                    riskBadge.textContent = `Loại ${dev.risk_level || 'A'}`;
                }
                const riskTagBody = document.getElementById('modal-dev-risk-tag');
                if (riskTagBody) {
                    riskTagBody.style.cssText = `background-color: ${rStyle.bg} !important; color: #ffffff !important; font-weight: 800; font-size: 0.82rem; padding: 0.35rem 0.65rem; border-radius: 6px;`;
                    riskTagBody.textContent = `Mức ${dev.risk_level || 'A'}`;
                }

                const statusBadge = document.getElementById('modal-dev-status');
                if (statusBadge) {
                    statusBadge.textContent = dev.status || 'IN_SERVICE';
                }

                // 1b. Header Tags for Supplier & Facility
                const headerFacTag = document.getElementById('modal-header-fac-tag');
                if (headerFacTag) headerFacTag.innerHTML = `<i class="bi bi-geo-alt-fill text-danger me-1"></i>${dev.facility || 'Kho thiết bị trung tâm'}`;
                
                const headerSupTag = document.getElementById('modal-header-sup-tag');
                if (headerSupTag) headerSupTag.innerHTML = `<i class="bi bi-building text-info me-1"></i>${dev.supplier_name || dev.manufacturer || 'Tổng kho'}`;

                // 2. Tab 1: General Info
                document.getElementById('modal-dev-facility').textContent = dev.facility || 'Kho thiết bị trung tâm';
                document.getElementById('modal-dev-category').textContent = dev.category || 'Chưa phân nhóm';
                document.getElementById('modal-dev-install-date').textContent = dev.installation_date || '2026-01-01';
                document.getElementById('modal-dev-model').textContent = dev.model || 'Tiêu chuẩn';
                document.getElementById('modal-dev-mfg').textContent = dev.manufacturer || 'Hãng Y Tế';
                document.getElementById('modal-dev-country').textContent = dev.country_of_manufacturer || 'Nhật Bản / Đức / Mỹ';
                document.getElementById('modal-dev-year').textContent = dev.year_of_manufacture || '2024';
                document.getElementById('modal-dev-notes').textContent = dev.notes || 'Hồ sơ lý lịch máy hợp lệ, đầy đủ CO/CQ và biên bản giao nhận.';

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
                const btnCheckout = document.getElementById('modal-btn-checkout');
                if (btnCheckout) {
                    btnCheckout.onclick = () => {
                        bootstrap.Modal.getInstance(document.getElementById('deviceDetailsModal'))?.hide();
                        this.openCheckoutModal(deviceId);
                    };
                }
                const btnCheckin = document.getElementById('modal-btn-checkin');
                if (btnCheckin) {
                    btnCheckin.onclick = () => {
                        bootstrap.Modal.getInstance(document.getElementById('deviceDetailsModal'))?.hide();
                        this.checkinDevice(deviceId);
                    };
                }

                const btnTr = document.getElementById('modal-btn-transfer');
                if (btnTr) {
                    btnTr.onclick = () => {
                        bootstrap.Modal.getInstance(document.getElementById('deviceDetailsModal'))?.hide();
                        const trSelect = document.getElementById('tr-device-id');
                        if (trSelect) trSelect.value = deviceId;
                        document.getElementById('btn-tab-transfers')?.click();
                    };
                }

                const btnWo = document.getElementById('modal-btn-wo');
                if (btnWo) {
                    btnWo.onclick = () => {
                        bootstrap.Modal.getInstance(document.getElementById('deviceDetailsModal'))?.hide();
                        const woSelect = document.getElementById('wo-device-id');
                        if (woSelect) woSelect.value = deviceId;
                        const woModal = new bootstrap.Modal(document.getElementById('speedmaintWorkOrderModal'));
                        woModal.show();
                    };
                }

                const btnEdit = document.getElementById('modal-btn-edit');
                if (btnEdit) {
                    btnEdit.onclick = () => {
                        bootstrap.Modal.getInstance(document.getElementById('deviceDetailsModal'))?.hide();
                        this.openEditDeviceModal(deviceId);
                    };
                }

                // Show modal
                const modal = new bootstrap.Modal(document.getElementById('deviceDetailsModal'));
                modal.show();

            } catch (err) {
                console.error("Error showing device details:", err);
                alert("Không thể tải chi tiết thiết bị: " + err.message);
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

        
        // ==================== BME STAFF MANAGEMENT ENGINE ====================
        staffList: [],

        async loadStaff() {
            try {
                const res = await fetch('/api/staff');
                if (!res.ok) throw new Error('Không thể tải danh sách nhân sự BME');
                this.staffList = await res.json();
                this.renderStaff(this.staffList);
                this.updateStaffKPIs();
            } catch (err) {
                console.error('Error loading BME staff:', err);
            }
        },

        updateStaffKPIs() {
            const total = this.staffList.length;
            const onDuty = this.staffList.filter(s => s.status === 'ON_DUTY').length;
            const specialists = this.staffList.filter(s => (s.role_level && s.role_level.includes('Trưởng')) || (s.role_level && s.role_level.includes('Chuyên Gia'))).length;

            const elTotal = document.getElementById('kpi-total-staff');
            const elOnDuty = document.getElementById('kpi-onduty-staff');
            const elSpecialist = document.getElementById('kpi-specialist-staff');
            const elBadge = document.getElementById('badge-staff-count');

            if (elTotal) elTotal.textContent = total;
            if (elOnDuty) elOnDuty.textContent = onDuty;
            if (elSpecialist) elSpecialist.textContent = specialists;
            if (elBadge) elBadge.textContent = `${total} KS`;
        },

        
        currentStaffView: 'bme', // 'bme', 'leaders', 'suppliers'
        leadersList: [],
        supplierContactsList: [],

        async switchStaffView(viewType) {
            this.currentStaffView = viewType;
            
            // Update Toggle Button Styles
            const btnBme = document.getElementById('btn-view-bme-staff');
            const btnLeaders = document.getElementById('btn-view-leaders');
            const btnSuppliers = document.getElementById('btn-view-suppliers-contacts');
            const btnOncall = document.getElementById('btn-view-oncall');

            [btnBme, btnOncall, btnLeaders, btnSuppliers].forEach(btn => {
                if (btn) {
                    btn.className = 'btn btn-outline-secondary fw-semibold btn-clinical';
                }
            });

            if (viewType === 'bme' && btnBme) btnBme.className = 'btn btn-primary fw-bold btn-clinical';
            if (viewType === 'leaders' && btnLeaders) btnLeaders.className = 'btn btn-primary fw-bold btn-clinical';
            if (viewType === 'suppliers' && btnSuppliers) btnSuppliers.className = 'btn btn-primary fw-bold btn-clinical';
            if (viewType === 'oncall' && btnOncall) btnOncall.className = 'btn btn-primary fw-bold btn-clinical';

            if (viewType === 'oncall') {
                this.renderOncallSchedule();
            } else if (viewType === 'bme') {
                this.renderStaff(this.staffList);
            } else if (viewType === 'leaders') {
                await this.loadAndRenderLeaders();
            } else if (viewType === 'suppliers') {
                await this.loadAndRenderSupplierContacts();
            }
        },

        async loadAndRenderLeaders() {
            try {
                if (this.leadersList.length === 0) {
                    const res = await fetch('/api/directory/leaders');
                    this.leadersList = await res.json();
                }
                const container = document.getElementById('staff-grid-container');
                const countLabel = document.getElementById('staff-count-label');
                if (countLabel) countLabel.textContent = `Hiển thị ${this.leadersList.length} Lãnh Đạo & Trưởng Khoa`;

                if (!container) return;
                container.innerHTML = this.leadersList.map(l => `
                    <div class="col-12 col-md-6 col-xl-4">
                        <div class="clinical-card h-100 p-3 d-flex flex-column justify-content-between shadow-sm" style="border-top: 4px solid #dc2626;">
                            <div>
                                <div class="d-flex align-items-center gap-2 mb-2">
                                    <div class="rounded-circle text-white d-flex align-items-center justify-content-center fw-bold shadow-sm" 
                                         style="width: 44px; height: 44px; font-size: 1.15rem; background: #dc2626;">
                                        ${l.full_name.charAt(0)}
                                    </div>
                                    <div>
                                        <h6 class="fw-bold mb-0 text-dark">${l.full_name}</h6>
                                        <span class="badge bg-danger text-white" style="font-size: 0.68rem;">${l.group_name}</span>
                                    </div>
                                </div>
                                <div class="p-2 rounded bg-light border mb-2">
                                    <span class="small text-muted d-block" style="font-size: 0.72rem; font-weight: 700;">CHỨC VỤ:</span>
                                    <strong class="text-dark small d-block">${l.title}</strong>
                                </div>
                                <div class="mb-3 small text-muted">
                                    <i class="bi bi-info-circle me-1 text-primary"></i>${l.notes || 'Chỉ đạo chuyên môn'}
                                </div>
                            </div>
                            <div class="pt-2 border-top d-flex align-items-center justify-content-between">
                                <a href="tel:${l.phone}" class="btn btn-sm btn-outline-danger btn-clinical font-mono fw-bold">
                                    <i class="bi bi-telephone-fill me-1"></i>${l.phone || 'N/A'}
                                </a>
                                <button type="button" class="btn btn-sm btn-light border btn-clinical text-dark" onclick="app.openEditLeaderModal(${l.id})"><i class="bi bi-pencil-square me-1"></i>Sửa</button>
                                <a href="mailto:${l.email || ''}" class="btn btn-sm btn-light border btn-clinical text-dark">
                                    <i class="bi bi-envelope-fill me-1"></i>Email
                                </a>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error(err);
            }
        },

        async loadAndRenderSupplierContacts() {
            try {
                if (this.supplierContactsList.length === 0) {
                    const res = await fetch('/api/directory/suppliers');
                    this.supplierContactsList = await res.json();
                }
                const container = document.getElementById('staff-grid-container');
                const countLabel = document.getElementById('staff-count-label');
                if (countLabel) countLabel.textContent = `Hiển thị ${this.supplierContactsList.length} Đối Tác Nhà Cung Cấp & Kỹ Sư Hãng`;

                if (!container) return;
                container.innerHTML = this.supplierContactsList.map(s => `
                    <div class="col-12 col-md-6 col-xl-4">
                        <div class="clinical-card h-100 p-3 d-flex flex-column justify-content-between shadow-sm" style="border-top: 4px solid #f59e0b;">
                            <div>
                                <div class="d-flex align-items-start justify-content-between gap-2 mb-2">
                                    <div>
                                        <h6 class="fw-bold mb-0 text-dark" style="font-size: 0.92rem;">${s.supplier_name}</h6>
                                        <span class="badge bg-warning text-dark font-mono mt-1" style="font-size: 0.68rem;">ĐỐI TÁC HÃNG</span>
                                    </div>
                                    <div class="rounded-circle text-white d-flex align-items-center justify-content-center fw-bold shadow-sm" 
                                         style="width: 36px; height: 36px; font-size: 1rem; background: #f59e0b;">
                                        🏢
                                    </div>
                                </div>
                                <div class="p-2 rounded bg-light border mb-2">
                                    <span class="small text-muted d-block" style="font-size: 0.72rem; font-weight: 700;">NGƯỜI LIÊN HỆ / ĐẠI DIỆN HÃNG:</span>
                                    <strong class="text-dark small d-block">${s.contact_person || 'Phòng Kỹ Thuật / Dịch Vụ'}</strong>
                                </div>
                                <div class="mb-3 small text-muted">
                                    <i class="bi bi-wrench me-1 text-warning"></i>${s.service_scope || 'Bảo trì & Cung cấp vật tư'}
                                </div>
                            </div>
                            <div class="pt-2 border-top d-flex align-items-center justify-content-between">
                                <a href="tel:${s.phone}" class="btn btn-sm btn-outline-warning text-dark btn-clinical font-mono fw-bold">
                                    <i class="bi bi-telephone-fill me-1"></i>${s.phone || 'Đang cập nhật'}
                                </a>
                                <button type="button" class="btn btn-sm btn-light border btn-clinical text-dark" onclick="app.openEditSupplierContactModal(${s.id})"><i class="bi bi-pencil-square me-1"></i>Sửa</button>
                            </div>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error(err);
            }
        },

        renderStaff(list) {
            const container = document.getElementById('staff-grid-container');
            const countLabel = document.getElementById('staff-count-label');
            if (!container) return;

            if (countLabel) countLabel.textContent = `Hiển thị ${list.length} nhân sự BME`;

            if (list.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5 text-muted">
                        <i class="bi bi-people fs-1 text-secondary mb-2 d-block"></i>
                        Không tìm thấy nhân sự phù hợp với bộ lọc
                    </div>
                `;
                return;
            }

            container.innerHTML = list.map(s => {
                const statusBadge = s.oncall_status === 'ONCALL_TODAY' 
                    ? '<span class="badge bg-danger pulse-emergency"><i class="bi bi-broadcast-pin me-1"></i>On-call 24h</span>'
                    : '<span class="badge bg-success bg-opacity-10 text-success border border-success">Sẵn Sàng</span>';
                
                const depts = s.assigned_departments ? s.assigned_departments.split(',').map(d => `<span class="badge bg-light text-dark border me-1 mb-1 font-mono" style="font-size: 0.72rem;">📍 ${d.trim()}</span>`).join('') : '<span class="text-muted small">Toàn viện</span>';
                
                const certs = s.certificates && s.certificates.trim() 
                    ? s.certificates.split(',').map(c => `<div class="small text-dark mb-1"><i class="bi bi-file-earmark-check-fill text-success me-1"></i>${this.escapeHtml(c.trim())}</div>`).join('') 
                    : '<span class="badge bg-light text-muted border font-mono" style="font-size: 0.72rem;"><i class="bi bi-shield-lock me-1 text-secondary"></i>Chưa cập nhật hồ sơ minh chứng</span>';

                const initial = s.full_name.replace('KS. ', '').replace('CN. ', '').trim().charAt(0) || 'K';

                return `
                    <div class="col-12 col-md-6 col-xl-4">
                        <div class="clinical-card h-100 p-3 d-flex flex-column justify-content-between shadow-sm position-relative" style="border-top: 4px solid ${s.avatar_color || '#0284c7'};">
                            <div>
                                <div class="d-flex align-items-start justify-content-between gap-2 mb-2">
                                    <div class="d-flex align-items-center gap-2">
                                        <div class="rounded-circle text-white d-flex align-items-center justify-content-center fw-bold shadow-sm flex-shrink-0" 
                                             style="width: 44px; height: 44px; font-size: 1.15rem; background: ${s.avatar_color || '#0284c7'};">
                                            ${initial}
                                        </div>
                                        <div>
                                            <h6 class="fw-bold mb-0 text-dark">${s.full_name}</h6>
                                            <span class="badge bg-dark font-mono text-white" style="font-size: 0.68rem;">${s.staff_code}</span>
                                            <span class="small text-muted d-block fw-semibold">${s.title}</span>
                                        </div>
                                    </div>
                                    <div>${statusBadge}</div>
                                </div>

                                <div class="p-2 rounded bg-light border mb-2">
                                    <span class="small text-muted d-block" style="font-size: 0.72rem; font-weight: 700;">CHUYÊN MÔN PHỤ TRÁCH:</span>
                                    <strong class="text-dark small d-block">${s.specialty}</strong>
                                </div>

                                <div class="mb-2">
                                    <span class="small text-muted d-block mb-1" style="font-size: 0.72rem; font-weight: 700;">KHU VỰC PHỤ TRÁCH:</span>
                                    <div class="d-flex flex-wrap">${depts}</div>
                                </div>

                                <div class="mb-3">
                                    <span class="small text-muted d-block mb-1" style="font-size: 0.72rem; font-weight: 700;">VĂN BẰNG & CHỨNG CHỈ MINH CHỨNG:</span>
                                    ${certs}
                                </div>
                            </div>

                            <div class="pt-2 border-top d-flex align-items-center justify-content-between">
                                <a href="tel:${s.phone}" class="btn btn-sm btn-outline-primary btn-clinical font-mono fw-bold">
                                    <i class="bi bi-telephone-fill me-1"></i>${s.phone || 'N/A'}
                                </a>
                                <button class="btn btn-sm btn-light border btn-clinical text-dark fw-semibold" onclick="app.openViewStaffModal(${s.id})">
                                    <i class="bi bi-pencil-square me-1"></i> Hồ Sơ Chi Tiết
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        },

        setupStaffEventListeners() {
            const searchInput = document.getElementById('staff-search-input');
            const statusFilter = document.getElementById('staff-status-filter');

            const filterFn = () => {
                const query = (searchInput?.value || '').toLowerCase().trim();
                const status = statusFilter?.value || '';

                const filtered = this.staffList.filter(s => {
                    const matchQuery = !query || 
                        s.full_name.toLowerCase().includes(query) || 
                        s.staff_code.toLowerCase().includes(query) || 
                        s.specialty.toLowerCase().includes(query) ||
                        (s.assigned_departments && s.assigned_departments.toLowerCase().includes(query));
                    const matchStatus = !status || s.status === status;
                    return matchQuery && matchStatus;
                });

                this.renderStaff(filtered);
            };

            searchInput?.addEventListener('input', filterFn);
            statusFilter?.addEventListener('change', filterFn);

            // Create Staff Form
            const createForm = document.getElementById('createStaffForm');
            createForm?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const payload = {
                    staff_code: document.getElementById('staff-add-code').value.trim().toUpperCase(),
                    full_name: document.getElementById('staff-add-name').value.trim(),
                    title: document.getElementById('staff-add-title').value.trim(),
                    role_level: document.getElementById('staff-add-role').value,
                    specialty: document.getElementById('staff-add-specialty').value.trim(),
                    phone: document.getElementById('staff-add-phone').value.trim(),
                    email: document.getElementById('staff-add-email').value.trim(),
                    assigned_departments: document.getElementById('staff-add-depts').value.trim(),
                    certificates: document.getElementById('staff-add-certs').value.trim(),
                    duty_shift: document.getElementById('staff-add-shift').value.trim(),
                    status: document.getElementById('staff-add-status').value
                };

                try {
                    const res = await fetch('/api/staff', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi khi thêm nhân sự');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('createStaffModal'))?.hide();
                    createForm.reset();
                    this.loadStaff();
            this.loadOncallData();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });

            // Edit Staff Form
            const editForm = document.getElementById('editStaffForm');
            editForm?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const staffId = document.getElementById('staff-edit-id').value;
                const payload = {
                    title: document.getElementById('staff-edit-title').value.trim(),
                    specialty: document.getElementById('staff-edit-specialty').value.trim(),
                    phone: document.getElementById('staff-edit-phone').value.trim(),
                    email: document.getElementById('staff-edit-email').value.trim(),
                    assigned_departments: document.getElementById('staff-edit-depts').value.trim(),
                    certificates: document.getElementById('staff-edit-certs').value.trim(),
                    status: document.getElementById('staff-edit-status').value
                };

                try {
                    const res = await fetch(`/api/staff/${staffId}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi cập nhật');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('viewStaffModal'))?.hide();
                    this.loadStaff();
            this.loadOncallData();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });

            // Delete Staff Button
            document.getElementById('btn-delete-staff')?.addEventListener('click', async () => {
                const staffId = document.getElementById('staff-edit-id').value;
                const staffName = document.getElementById('staff-modal-name').textContent;
                if (!confirm(`Bạn có chắc muốn xóa nhân sự "${staffName}" khỏi hệ thống?`)) return;

                try {
                    const res = await fetch(`/api/staff/${staffId}`, { method: 'DELETE' });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi khi xóa');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('viewStaffModal'))?.hide();
                    this.loadStaff();
            this.loadOncallData();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });
        },

        async openViewStaffModal(staffId) {
            try {
                const res = await fetch(`/api/staff/${staffId}`);
                if (!res.ok) throw new Error('Không thể tải chi tiết nhân sự');
                const staff = await res.json();

                document.getElementById('staff-edit-id').value = staff.id;
                document.getElementById('staff-modal-name').textContent = staff.full_name;
                document.getElementById('staff-modal-code').textContent = staff.staff_code;
                document.getElementById('staff-edit-title').value = staff.title;
                document.getElementById('staff-edit-specialty').value = staff.specialty;
                document.getElementById('staff-edit-phone').value = staff.phone || '';
                document.getElementById('staff-edit-email').value = staff.email || '';
                document.getElementById('staff-edit-depts').value = staff.assigned_departments || '';
                document.getElementById('staff-edit-certs').value = staff.certificates || '';
                document.getElementById('staff-edit-status').value = staff.status || 'ACTIVE';

                const avatar = document.getElementById('staff-modal-avatar');
                if (avatar) {
                    avatar.textContent = staff.full_name.replace('KS. ', '').replace('CN. ', '').trim().charAt(0) || 'K';
                    avatar.style.background = staff.avatar_color || '#0284c7';
                }

                const modal = new bootstrap.Modal(document.getElementById('viewStaffModal'));
                modal.show();
            } catch (err) {
                alert('❌ Lỗi: ' + err.message);
            }
        },

        
        openEditLeaderModal(id) {
            const l = this.leadersList.find(item => item.id === id);
            if (!l) return;

            document.getElementById('leader-edit-id').value = l.id;
            document.getElementById('leader-edit-name').value = l.full_name;
            document.getElementById('leader-edit-group').value = l.group_name || '';
            document.getElementById('leader-edit-title').value = l.title || '';
            document.getElementById('leader-edit-phone').value = l.phone || '';
            document.getElementById('leader-edit-email').value = l.email || '';
            document.getElementById('leader-edit-notes').value = l.notes || '';

            const modal = new bootstrap.Modal(document.getElementById('editLeaderModal'));
            modal.show();
        },

        openEditSupplierContactModal(id) {
            const s = this.supplierContactsList.find(item => item.id === id);
            if (!s) return;

            document.getElementById('sup-contact-edit-id').value = s.id;
            document.getElementById('sup-contact-edit-name').value = s.supplier_name;
            document.getElementById('sup-contact-edit-person').value = s.contact_person || '';
            document.getElementById('sup-contact-edit-phone').value = s.phone || '';
            document.getElementById('sup-contact-edit-email').value = s.email || '';
            document.getElementById('sup-contact-edit-scope').value = s.service_scope || '';

            const modal = new bootstrap.Modal(document.getElementById('editSupplierContactModal'));
            modal.show();
        },

        setupDirectoryEditForms() {
            // Edit Leader Form
            const leaderForm = document.getElementById('editLeaderForm');
            leaderForm?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const id = document.getElementById('leader-edit-id').value;
                const payload = {
                    full_name: document.getElementById('leader-edit-name').value.trim(),
                    group_name: document.getElementById('leader-edit-group').value.trim(),
                    title: document.getElementById('leader-edit-title').value.trim(),
                    phone: document.getElementById('leader-edit-phone').value.trim(),
                    email: document.getElementById('leader-edit-email').value.trim(),
                    notes: document.getElementById('leader-edit-notes').value.trim()
                };

                try {
                    const res = await fetch(`/api/directory/leaders/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi cập nhật');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('editLeaderModal'))?.hide();
                    this.leadersList = [];
                    this.loadAndRenderLeaders();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });

            // Edit Supplier Contact Form
            const supForm = document.getElementById('editSupplierContactForm');
            supForm?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const id = document.getElementById('sup-contact-edit-id').value;
                const payload = {
                    supplier_name: document.getElementById('sup-contact-edit-name').value.trim(),
                    contact_person: document.getElementById('sup-contact-edit-person').value.trim(),
                    phone: document.getElementById('sup-contact-edit-phone').value.trim(),
                    email: document.getElementById('sup-contact-edit-email').value.trim(),
                    service_scope: document.getElementById('sup-contact-edit-scope').value.trim()
                };

                try {
                    const res = await fetch(`/api/directory/suppliers/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi cập nhật');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('editSupplierContactModal'))?.hide();
                    this.supplierContactsList = [];
                    this.loadAndRenderSupplierContacts();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });
        },

        
        
        currentOncallMonth: 8,
        currentOncallYear: 2026,
        oncallScheduleList: [],

        async loadOncallData(month = null, year = null) {
            if (month) this.currentOncallMonth = month;
            if (year) this.currentOncallYear = year;

            try {
                // 1. Load Today Oncall
                const resToday = await fetch('/api/oncall/today');
                if (resToday.ok) {
                    const today = await resToday.json();
                    if (today.primary_engineer) {
                        const elName = document.getElementById('oncall-today-name');
                        const elBtn = document.getElementById('oncall-today-btn');
                        const elBackup = document.getElementById('oncall-backup-name');
                        const elBackupPhone = document.getElementById('oncall-backup-phone');

                        if (elName) elName.textContent = today.primary_engineer;
                        if (elBtn) {
                            elBtn.href = `tel:${today.primary_phone}`;
                            elBtn.innerHTML = `<i class="bi bi-telephone-fill me-1"></i> ${today.primary_phone}`;
                        }
                        if (elBackup) elBackup.textContent = today.backup_engineer;
                        if (elBackupPhone) elBackupPhone.innerHTML = `<i class="bi bi-telephone me-1"></i>${today.backup_phone}`;
                    }
                }

                // 2. Load Monthly Schedule
                const resSched = await fetch(`/api/oncall/schedule?month=${this.currentOncallMonth}&year=${this.currentOncallYear}`);
                if (resSched.ok) {
                    this.oncallScheduleList = await resSched.json();
                }
            } catch (err) {
                console.error('Error loading oncall data:', err);
            }
        },

        async changeOncallMonth(month, year) {
            this.currentOncallMonth = parseInt(month, 10);
            this.currentOncallYear = parseInt(year, 10);
            await this.loadOncallData(this.currentOncallMonth, this.currentOncallYear);
            this.renderOncallSchedule();
        },

        renderOncallSchedule() {
            const container = document.getElementById('staff-grid-container');
            const countLabel = document.getElementById('staff-count-label');
            if (countLabel) countLabel.textContent = `Lịch Xếp On-Call 24 Giờ Tháng ${this.currentOncallMonth}/${this.currentOncallYear} (${this.oncallScheduleList.length} Ngày)`;
            if (!container) return;

            const completedCount = this.oncallScheduleList.filter(s => s.status === 'COMPLETED').length;
            const scheduledCount = this.oncallScheduleList.filter(s => s.status === 'SCHEDULED' || s.status === 'TODAY').length;

            container.innerHTML = `
                <!-- Month Selector & Controls -->
                <div class="col-12 mb-2">
                    <div class="d-flex flex-wrap align-items-center justify-content-between gap-3 p-3 bg-light rounded border shadow-sm">
                        <div class="d-flex align-items-center gap-2">
                            <span class="fw-bold text-dark"><i class="bi bi-calendar3 me-1 text-primary"></i>Chọn Tháng Xếp Lịch:</span>
                            <select class="form-select form-select-sm font-mono fw-bold" style="width: auto;" onchange="app.changeOncallMonth(this.value.split('-')[0], this.value.split('-')[1])">
                                <option value="8-2026" ${this.currentOncallMonth === 8 ? 'selected' : ''}>Tháng 08/2026 (Hiện tại - 31 ngày)</option>
                                <option value="9-2026" ${this.currentOncallMonth === 9 ? 'selected' : ''}>Tháng 09/2026 (Kế hoạch - 30 ngày)</option>
                                <option value="10-2026" ${this.currentOncallMonth === 10 ? 'selected' : ''}>Tháng 10/2026 (Kế hoạch - 31 ngày)</option>
                            </select>
                        </div>
                        <div class="d-flex align-items-center gap-3">
                            <span class="badge bg-secondary font-mono"><i class="bi bi-check2-circle me-1"></i>Đã xong: ${completedCount} ca</span>
                            <span class="badge bg-primary font-mono"><i class="bi bi-clock-history me-1"></i>Sắp tới: ${scheduledCount} ca</span>
                            <span class="badge bg-success font-mono"><i class="bi bi-shield-check me-1"></i>Bảo đảm 24/24h</span>
                        </div>
                    </div>
                </div>

                <!-- Monthly Schedule Table -->
                <div class="col-12">
                    <div class="clinical-card p-0 overflow-hidden shadow-sm">
                        <div class="table-responsive" style="max-height: 600px; overflow-y: auto;">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light sticky-top shadow-sm" style="z-index: 10;">
                                    <tr>
                                        <th class="ps-3" style="width: 130px;">NGÀY / THỨ</th>
                                        <th>KỸ SƯ ON-CALL CHÍNH (24H)</th>
                                        <th>KỸ SƯ DỰ PHÒNG (BACKUP)</th>
                                        <th>LÃNH ĐẠO TRỰC</th>
                                        <th>KHUNG GIỜ</th>
                                        <th>TRẠNG THÁI</th>
                                        <th>GHI CHÚ</th>
                                        <th class="text-end pe-3">THAO TÁC</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${this.oncallScheduleList.map(s => {
                                        const isToday = s.status === 'TODAY';
                                        const isWeekend = s.day_name === 'Thứ Bảy' || s.day_name === 'Chủ Nhật';
                                        let rowClass = '';
                                        if (isToday) rowClass = 'table-warning bg-opacity-50 fw-semibold';
                                        else if (isWeekend) rowClass = 'table-light bg-opacity-75';

                                        let statusBadge = '<span class="badge bg-light text-dark border">Kế hoạch</span>';
                                        if (isToday) statusBadge = '<span class="badge bg-danger pulse-emergency"><i class="bi bi-broadcast-pin me-1"></i>ĐANG TRỰC HÔM NAY</span>';
                                        else if (s.status === 'COMPLETED') statusBadge = '<span class="badge bg-secondary">Đã xong</span>';

                                        return `
                                            <tr class="${rowClass}">
                                                <td class="ps-3">
                                                    <strong class="${isWeekend ? 'text-danger' : 'text-dark'}">${s.date_str}</strong>
                                                    <div class="small ${isWeekend ? 'text-danger fw-bold' : 'text-muted'}">${s.day_name}</div>
                                                </td>
                                                <td>
                                                    <div class="d-flex align-items-center gap-2">
                                                        <div class="rounded-circle text-white d-flex align-items-center justify-content-center fw-bold shadow-sm" 
                                                             style="width: 32px; height: 32px; font-size: 0.85rem; background: ${isToday ? '#dc2626' : '#0284c7'};">
                                                            ${s.primary_engineer.charAt(0)}
                                                        </div>
                                                        <div>
                                                            <strong class="text-dark d-block">${s.primary_engineer}</strong>
                                                            <a href="tel:${s.primary_phone}" class="small font-mono text-primary">${s.primary_phone}</a>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>
                                                    <strong class="text-dark d-block">${s.backup_engineer}</strong>
                                                    <a href="tel:${s.backup_phone}" class="small font-mono text-muted">${s.backup_phone}</a>
                                                </td>
                                                <td>
                                                    <span class="text-dark small">${s.leader_oncall}</span>
                                                </td>
                                                <td>
                                                    <span class="badge bg-light text-dark border font-mono">24/24 Giờ</span>
                                                </td>
                                                <td>${statusBadge}</td>
                                                <td class="small text-muted" style="max-width: 200px;">
                                                    ${s.notes || '-'}
                                                </td>
                                                <td class="text-end pe-3">
                                                    <button class="btn btn-sm btn-outline-primary btn-clinical fw-semibold" onclick="app.openEditOncallModal(${s.id})">
                                                        <i class="bi bi-pencil-square me-1"></i> Đổi Ca
                                                    </button>
                                                </td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        },


        async loadOncallData() {
            try {
                // 1. Load Today Oncall
                const resToday = await fetch('/api/oncall/today');
                if (resToday.ok) {
                    const today = await resToday.json();
                    if (today.primary_engineer) {
                        const elName = document.getElementById('oncall-today-name');
                        const elBtn = document.getElementById('oncall-today-btn');
                        const elBackup = document.getElementById('oncall-backup-name');
                        const elBackupPhone = document.getElementById('oncall-backup-phone');

                        if (elName) elName.textContent = today.primary_engineer;
                        if (elBtn) {
                            elBtn.href = `tel:${today.primary_phone}`;
                            elBtn.innerHTML = `<i class="bi bi-telephone-fill me-1"></i> ${today.primary_phone}`;
                        }
                        if (elBackup) elBackup.textContent = today.backup_engineer;
                        if (elBackupPhone) elBackupPhone.innerHTML = `<i class="bi bi-telephone me-1"></i>${today.backup_phone}`;
                    }
                }

                // 2. Load Weekly Schedule
                const resSched = await fetch('/api/oncall/schedule');
                if (resSched.ok) {
                    this.oncallScheduleList = await resSched.json();
                }
            } catch (err) {
                console.error('Error loading oncall data:', err);
            }
        },

        renderOncallSchedule() {
            const container = document.getElementById('staff-grid-container');
            const countLabel = document.getElementById('staff-count-label');
            if (countLabel) countLabel.textContent = `Bảng Lịch On-Call 7 Ngày Trong Tuần`;
            if (!container) return;

            container.innerHTML = `
                <div class="col-12">
                    <div class="clinical-card p-0 overflow-hidden shadow-sm">
                        <div class="table-responsive">
                            <table class="table table-hover align-middle mb-0">
                                <thead class="table-light">
                                    <tr>
                                        <th class="ps-3">THỨ / NGÀY</th>
                                        <th>KỸ SƯ ON-CALL CHÍNH</th>
                                        <th>KỸ SƯ DỰ PHÒNG (BACKUP)</th>
                                        <th>LÃNH ĐẠO TRỰC</th>
                                        <th>KHUNG GIỜ</th>
                                        <th>TRẠNG THÁI</th>
                                        <th class="text-end pe-3">THAO TÁC</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${this.oncallScheduleList.map(s => {
                                        const isToday = s.status === 'TODAY';
                                        const rowClass = isToday ? 'table-warning bg-opacity-25' : '';
                                        const statusBadge = isToday 
                                            ? '<span class="badge bg-danger"><i class="bi bi-broadcast-pin me-1"></i>ĐANG TRỰC HÔM NAY</span>'
                                            : (s.status === 'COMPLETED' ? '<span class="badge bg-secondary">Đã xong</span>' : '<span class="badge bg-light text-dark border">Theo kế hoạch</span>');

                                        return `
                                            <tr class="${rowClass}">
                                                <td class="ps-3">
                                                    <strong class="text-dark">${s.day_name}</strong>
                                                    <div class="small font-mono text-muted">${s.date_str}</div>
                                                </td>
                                                <td>
                                                    <div class="d-flex align-items-center gap-2">
                                                        <div class="rounded-circle text-white d-flex align-items-center justify-content-center fw-bold" style="width: 32px; height: 32px; font-size: 0.85rem; background: #0284c7;">
                                                            ${s.primary_engineer.charAt(0)}
                                                        </div>
                                                        <div>
                                                            <strong class="text-dark">${s.primary_engineer}</strong>
                                                            <a href="tel:${s.primary_phone}" class="small font-mono text-primary d-block">${s.primary_phone}</a>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td>
                                                    <strong class="text-dark">${s.backup_engineer}</strong>
                                                    <a href="tel:${s.backup_phone}" class="small font-mono text-muted d-block">${s.backup_phone}</a>
                                                </td>
                                                <td>
                                                    <span class="text-dark small">${s.leader_oncall}</span>
                                                </td>
                                                <td>
                                                    <span class="badge bg-light text-dark border font-mono">${s.time_window}</span>
                                                </td>
                                                <td>${statusBadge}</td>
                                                <td class="text-end pe-3">
                                                    <button class="btn btn-sm btn-outline-primary btn-clinical" onclick="app.openEditOncallModal(${s.id})">
                                                        <i class="bi bi-pencil-square me-1"></i> Đổi Ca
                                                    </button>
                                                </td>
                                            </tr>
                                        `;
                                    }).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        },

        openEditOncallModal(id) {
            const sched = this.oncallScheduleList.find(s => s.id === id);
            if (!sched) return;

            document.getElementById('oncall-edit-id').value = sched.id;
            document.getElementById('oncall-edit-day').textContent = `${sched.day_name} (${sched.date_str})`;
            document.getElementById('oncall-edit-primary').value = sched.primary_engineer;
            document.getElementById('oncall-edit-backup').value = sched.backup_engineer;
            document.getElementById('oncall-edit-time').value = sched.time_window || '16:30 - 07:30 sáng hôm sau';
            document.getElementById('oncall-edit-notes').value = sched.notes || '';

            const modal = new bootstrap.Modal(document.getElementById('editOncallModal'));
            modal.show();
        },

        setupOncallEditForm() {
            const form = document.getElementById('editOncallForm');
            form?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const id = document.getElementById('oncall-edit-id').value;
                const primary = document.getElementById('oncall-edit-primary').value;
                const backup = document.getElementById('oncall-edit-backup').value;

                // Map phone numbers
                const phoneMap = {
                    "Nguyễn Quốc Việt": "0902769710",
                    "Nguyễn Tấn Lợi": "0779798786",
                    "Trần Đăng Hiếu": "0888536278",
                    "Lê Minh Thiện": "0378716561",
                    "Trần Thị Ngọc Châu": "0335802380",
                    "Trần Trọng Tấn": "0334968114"
                };

                const payload = {
                    primary_engineer: primary,
                    primary_phone: phoneMap[primary] || "",
                    backup_engineer: backup,
                    backup_phone: phoneMap[backup] || "",
                    time_window: document.getElementById('oncall-edit-time').value.trim(),
                    notes: document.getElementById('oncall-edit-notes').value.trim()
                };

                try {
                    const res = await fetch(`/api/oncall/schedule/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi cập nhật lịch On-call');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('editOncallModal'))?.hide();
                    await this.loadOncallData();
                    this.renderOncallSchedule();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });
        },

        
        openQuickAssignModal() {
            const modal = new bootstrap.Modal(document.getElementById('quickAssignWeeklyOncallModal'));
            modal.show();
        },

        toggleQuickAssignMode(mode) {
            const autoOpt = document.getElementById('quick-auto-month-options');
            const customOpt = document.getElementById('quick-custom-range-options');
            if (mode === 'AUTO_MONTH') {
                autoOpt?.classList.remove('d-none');
                customOpt?.classList.add('d-none');
            } else {
                autoOpt?.classList.add('d-none');
                customOpt?.classList.remove('d-none');
            }
        },

        setupQuickAssignForm() {
            const form = document.getElementById('quickAssignWeeklyForm');
            form?.addEventListener('submit', async (e) => {
                e.preventDefault();
                const mode = document.getElementById('quick-assign-mode').value;
                const payload = {
                    month: this.currentOncallMonth || 8,
                    year: this.currentOncallYear || 2026,
                    assign_mode: mode,
                    start_engineer: document.getElementById('quick-start-engineer').value,
                    start_day: parseInt(document.getElementById('quick-start-day').value || 1, 10),
                    end_day: parseInt(document.getElementById('quick-end-day').value || 7, 10),
                    target_engineer: document.getElementById('quick-target-engineer').value,
                    backup_engineer: document.getElementById('quick-backup-engineer').value
                };

                try {
                    const res = await fetch('/api/oncall/quick-assign-weekly', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (!res.ok) throw new Error(result.detail || 'Lỗi xếp lịch nhanh');

                    alert('✅ ' + result.message);
                    bootstrap.Modal.getInstance(document.getElementById('quickAssignWeeklyOncallModal'))?.hide();
                    await this.loadOncallData(this.currentOncallMonth, this.currentOncallYear);
                    this.renderOncallSchedule();
                } catch (err) {
                    alert('❌ Lỗi: ' + err.message);
                }
            });
        },

        
        // ==================== GEMINI AI & MISTRAL OCR HUB ENGINE ====================
        currentOCRResult: null,

        async submitAIChat() {
            const input = document.getElementById('ai-chat-input');
            const message = input.value.trim();
            if (!message) return;

            input.value = '';
            this.appendChatMessage('user', message);

            const btnSend = document.getElementById('btn-send-ai-chat');
            if (btnSend) {
                btnSend.disabled = true;
                btnSend.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            }

            try {
                const res = await fetch('/api/ai/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await res.json();
                if (data && data.reply) {
                    this.appendChatMessage('bot', data.reply);
                } else {
                    this.appendChatMessage('bot', '❌ Không nhận được phản hồi từ Trợ lý AI.');
                }
            } catch (err) {
                this.appendChatMessage('bot', '❌ Lỗi kết nối đến Gemini Agent Service: ' + err.message);
            } finally {
                if (btnSend) {
                    btnSend.disabled = false;
                    btnSend.innerHTML = '<i class="bi bi-send-fill me-1"></i> Gửi';
                }
            }
        },

        sendQuickPrompt(promptText) {
            const input = document.getElementById('ai-chat-input');
            if (input) {
                input.value = promptText;
                this.submitAIChat();
            }
        },

        appendChatMessage(sender, text) {
            const container = document.getElementById('ai-chat-messages');
            if (!container) return;

            const isUser = sender === 'user';
            const initial = isUser ? '<i class="bi bi-person-fill"></i>' : '<i class="bi bi-robot"></i>';
            const bgClass = isUser ? 'bg-primary text-white' : 'bg-white text-dark shadow-sm border';
            const title = isUser ? 'Bạn' : 'Trợ Lý AI Y Sinh (Gemini):';

            // Format markdown newlines and bold
            let formatted = text
                .replace(/\n\n/g, '<br><br>')
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/`([^`]+)`/g, '<code class="font-mono bg-light text-dark p-1 rounded">$1</code>');

            const msgHtml = `
                <div class="d-flex align-items-start gap-2 mb-3 ${isUser ? 'flex-row-reverse' : ''}">
                    <div class="rounded-circle ${isUser ? 'bg-secondary' : 'bg-primary'} text-white d-flex align-items-center justify-content-center fw-bold flex-shrink-0" style="width: 34px; height: 34px;">
                        ${initial}
                    </div>
                    <div class="${bgClass} p-3 rounded-3" style="max-width: 85%;">
                        <strong class="${isUser ? 'text-white' : 'text-primary'} d-block mb-1 small">${title}</strong>
                        <div class="small">${formatted}</div>
                    </div>
                </div>
            `;

            container.insertAdjacentHTML('beforeend', msgHtml);
            container.scrollTop = container.scrollHeight;
        },

        clearAIChat() {
            const container = document.getElementById('ai-chat-messages');
            if (container) {
                container.innerHTML = `
                    <div class="d-flex align-items-start gap-2 mb-3">
                        <div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center fw-bold flex-shrink-0" style="width: 34px; height: 34px;">
                            <i class="bi bi-robot"></i>
                        </div>
                        <div class="bg-white p-3 rounded-3 shadow-sm border text-dark" style="max-width: 85%;">
                            <strong class="text-primary d-block mb-1">Trợ Lý AI Kỹ Thuật Y Sinh (BME AI Assistant):</strong>
                            Đã làm mới phiên hội thoại. Tôi sẵn sàng hỗ trợ các câu hỏi về trang thiết bị y tế và quy trình SOPs tại PKĐK Tâm Anh Quận 7!
                        </div>
                    </div>
                `;
            }
        },

        async runSampleOCR(sampleFilename) {
            const spinner = document.getElementById('ocr-loading-spinner');
            const resultsPanel = document.getElementById('ocr-results-panel');
            spinner?.classList.remove('d-none');
            resultsPanel?.classList.add('d-none');

            try {
                const res = await fetch('/api/ocr/process', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: sampleFilename })
                });
                const data = await res.json();
                this.currentOCRResult = data;
                this.renderOCRResult(data);
            } catch (err) {
                alert('❌ Lỗi xử lý OCR: ' + err.message);
            } finally {
                spinner?.classList.add('d-none');
                resultsPanel?.classList.remove('d-none');
            }
        },

        async handleOCRFileUpload(files) {
            if (!files || files.length === 0) return;
            const file = files[0];

            const spinner = document.getElementById('ocr-loading-spinner');
            const resultsPanel = document.getElementById('ocr-results-panel');
            spinner?.classList.remove('d-none');
            resultsPanel?.classList.add('d-none');

            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/api/ocr/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                this.currentOCRResult = data;
                this.renderOCRResult(data);
            } catch (err) {
                alert('❌ Lỗi xử lý OCR: ' + err.message);
            } finally {
                spinner?.classList.add('d-none');
                resultsPanel?.classList.remove('d-none');
            }
        },

        renderOCRResult(data) {
            const engineBadge = document.getElementById('ocr-result-engine');
            const fieldsSummary = document.getElementById('ocr-fields-summary');
            if (engineBadge) engineBadge.textContent = data.engine || 'Mistral OCR-4';

            if (fieldsSummary && data.extracted_fields) {
                const f = data.extracted_fields;
                fieldsSummary.innerHTML = `
                    <div class="row g-1">
                        <div class="col-12"><strong>Tên thiết bị:</strong> <span class="text-primary">${f.device_name || 'N/A'}</span></div>
                        <div class="col-6"><strong>Model:</strong> ${f.model || 'N/A'}</div>
                        <div class="col-6"><strong>Serial:</strong> <span class="badge bg-dark">${f.serial_no || 'N/A'}</span></div>
                        <div class="col-6"><strong>Hãng SX:</strong> ${f.manufacturer || 'N/A'}</div>
                        <div class="col-6"><strong>Khoa phòng:</strong> ${f.facility || 'N/A'}</div>
                        <div class="col-6"><strong>Ngày KĐ:</strong> ${f.calibration_date || 'N/A'}</div>
                        <div class="col-6"><strong>Hạn KĐ:</strong> ${f.recalibration_date || 'N/A'}</div>
                        <div class="col-6"><strong>Số GCN:</strong> ${f.certificate_no || 'N/A'}</div>
                        <div class="col-6"><strong>Mức rủi ro:</strong> <span class="badge bg-warning text-dark">Loại ${f.risk_level || 'A'}</span></div>
                    </div>
                `;
            }
        },

        showFullOCRMarkdownModal() {
            if (!this.currentOCRResult) return;
            const container = document.getElementById('ocr-full-markdown-content');
            if (container) container.textContent = this.currentOCRResult.markdown || '';
            const modal = new bootstrap.Modal(document.getElementById('ocrMarkdownModal'));
            modal.show();
        },

        populateExtractedOCRToDevice() {
            if (!this.currentOCRResult || !this.currentOCRResult.extracted_fields) {
                alert('Chưa có thông tin bóc tách!');
                return;
            }
            const f = this.currentOCRResult.extracted_fields;
            alert(`✅ Đã nạp thành công dữ liệu trích xuất từ Mistral OCR:\n• Thiết bị: ${f.device_name}\n• Model: ${f.model}\n• S/N: ${f.serial_no}\n• Khoa phòng: ${f.facility}`);
        },

        openKeyConfigModal() {
            const modal = new bootstrap.Modal(document.getElementById('keyConfigModal'));
            modal.show();
        },

        async submitNewAPIKey() {
            const service = document.getElementById('key-service-select').value;
            const keys = document.getElementById('key-input-textarea').value.trim();
            if (!keys) return;

            try {
                const res = await fetch('/api/keys/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ service: service, keys: keys })
                });
                const data = await res.json();
                alert('✅ ' + data.message);
                bootstrap.Modal.getInstance(document.getElementById('keyConfigModal'))?.hide();
                document.getElementById('key-input-textarea').value = '';
                this.loadAPIKeysStatus();
            } catch (err) {
                alert('❌ Lỗi thêm key: ' + err.message);
            }
        },

        async loadAPIKeysStatus() {
            try {
                const res = await fetch('/api/keys/config');
                const data = await res.json();
                const geminiBadge = document.getElementById('gemini-key-count-badge');
                const mistralBadge = document.getElementById('mistral-key-count-badge');
                if (geminiBadge && data.gemini) {
                    geminiBadge.textContent = `${data.gemini.active_keys} Keys Hoạt Động (Pool ${data.gemini.total_keys})`;
                }
                if (mistralBadge && data.mistral) {
                    mistralBadge.textContent = `${data.mistral.active_keys} Keys Hoạt Động (Pool ${data.mistral.total_keys})`;
                }
            } catch (err) {
                console.error(err);
            }
        },

        
        // ==================== COLLAPSIBLE SIDEBAR & MULTI-VIEW DEVICE ENGINE ====================
        currentDeviceViewMode: 'table', // 'table' | 'grid' | 'department' | 'risk'

        toggleSidebar() {
            document.body.classList.toggle('sidebar-collapsed');
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebar_collapsed', isCollapsed ? 'true' : 'false');
            
            // Adjust icon
            const btn = document.getElementById('btn-toggle-sidebar');
            if (btn) {
                btn.innerHTML = isCollapsed 
                    ? '<i class="bi bi-layout-sidebar text-primary fs-6"></i>' 
                    : '<i class="bi bi-layout-sidebar-inset text-primary fs-6"></i>';
            }
        },

        initSidebarState() {
            if (localStorage.getItem('sidebar_collapsed') === 'true') {
                document.body.classList.add('sidebar-collapsed');
                const btn = document.getElementById('btn-toggle-sidebar');
                if (btn) btn.innerHTML = '<i class="bi bi-layout-sidebar text-primary fs-6"></i>';
            }

            // Keyboard shortcut Ctrl+B or Cmd+B
            window.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
                    e.preventDefault();
                    this.toggleSidebar();
                }
            });
        },

        setDeviceViewMode(mode) {
            this.currentDeviceViewMode = mode;

            // Update toolbar buttons
            ['table', 'grid', 'department', 'risk'].forEach(m => {
                const btn = document.getElementById(`btn-view-${m}`);
                const container = document.getElementById(`device-view-container-${m}`);
                if (btn) {
                    if (m === mode) btn.classList.add('active');
                    else btn.classList.remove('active');
                }
                if (container) {
                    if (m === mode) container.classList.remove('d-none');
                    else container.classList.add('d-none');
                }
            });

            this.renderCurrentDeviceView();
        },

        filterByQuickRisk(risk) {
            const riskSelect = document.getElementById('filter-risk');
            if (riskSelect) {
                riskSelect.value = risk;
                this.currentFilters.risk_level = risk;
                this.loadDevices();
            }
        },

        renderCurrentDeviceView() {
            if (!this.devices) return;

            if (this.currentDeviceViewMode === 'table') {
                this.renderDeviceTableView(this.devices);
            } else if (this.currentDeviceViewMode === 'grid') {
                this.renderDeviceGridView(this.devices);
            } else if (this.currentDeviceViewMode === 'department') {
                this.renderDeviceDepartmentView(this.devices);
            } else if (this.currentDeviceViewMode === 'risk') {
                this.renderDeviceRiskView(this.devices);
            }
        },

        renderDeviceTableView(list) {
            const tbody = document.getElementById('device-table-body');
            if (!tbody) return;

            if (!list || list.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">Không tìm thấy thiết bị nào phù hợp.</td></tr>';
                return;
            }

            const riskMap = {
                'A': { bg: '#059669', label: 'Loại A' },
                'B': { bg: '#0284c7', label: 'Loại B' },
                'C': { bg: '#d97706', label: 'Loại C' },
                'D': { bg: '#dc2626', label: 'Loại D' }
            };

            tbody.innerHTML = list.map(d => {
                const rStyle = riskMap[d.risk_level] || { bg: '#64748b', label: 'Chưa rõ' };
                const riskBadge = `<span class="badge" style="background-color: ${rStyle.bg}; color: #fff; font-weight: 700; font-size: 0.75rem;">${d.risk_level || 'A'}</span>`;
                const facName = d.facility || d.facility_name || 'Chưa phân khoa';
                const supplierName = d.supplier_name || (d.manufacturer ? `Hãng ${d.manufacturer}` : 'N/A');

                return `
                    <tr style="cursor: pointer;" onclick="app.showDeviceDetails(${d.id})" class="device-row">
                        <td class="ps-3 font-mono fw-semibold text-primary">
                            <div>${d.asset_tag}</div>
                            <div class="text-muted" style="font-size: 0.72rem;">${d.speedmaint_code || ''}</div>
                        </td>
                        <td>
                            <div class="fw-bold text-dark text-hover-primary mb-1">${d.device_name}</div>
                            <div class="d-flex flex-wrap align-items-center gap-1">
                                <span class="badge bg-secondary-subtle text-dark font-mono" style="font-size: 0.72rem;">Model: ${d.model || 'N/A'}</span>
                                <span class="badge bg-light text-dark border font-mono" style="font-size: 0.72rem;"><i class="bi bi-building text-primary me-1"></i>${supplierName}</span>
                            </div>
                        </td>
                        <td class="font-mono fw-semibold text-dark">${d.serial_no || '<span class="text-muted">-</span>'}</td>
                        <td><span class="badge bg-light text-dark border"><i class="bi bi-geo-alt-fill text-danger me-1"></i>${facName}</span></td>
                        <td class="text-center">${riskBadge}</td>
                        <td class="text-center">
                            <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1">${d.status || 'Hoạt động'}</span>
                        </td>
                        <td class="pe-3 text-end" onclick="event.stopPropagation()">
                            <div class="d-flex justify-content-end gap-1">
                                <button class="btn btn-sm btn-primary btn-clinical" onclick="app.showDeviceDetails(${d.id})" title="Xem hồ sơ máy">
                                    <i class="bi bi-eye"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-warning text-dark btn-clinical" onclick="app.openEditDeviceModal(${d.id})" title="Chỉnh sửa">
                                    <i class="bi bi-pencil-square"></i>
                                </button>
                                <button class="btn btn-sm btn-success btn-clinical" onclick="app.openCheckoutModal(${d.id})" title="Bàn giao">
                                    <i class="bi bi-box-arrow-right"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
        },

        renderDeviceGridView(list) {
            const container = document.getElementById('device-cards-grid');
            if (!container) return;

            if (!list || list.length === 0) {
                container.innerHTML = '<div class="col-12 text-center py-5 text-muted">Không tìm thấy thiết bị nào.</div>';
                return;
            }

            const riskColors = { 'A': '#16a34a', 'B': '#2563eb', 'C': '#d97706', 'D': '#dc2626' };

            container.innerHTML = list.slice(0, 150).map(d => {
                const borderCol = riskColors[d.risk_level] || '#0284c7';
                const facName = d.facility || d.facility_name || 'Khoa phòng chung';

                return `
                    <div class="col-12 col-md-6 col-xl-4">
                        <div class="clinical-card h-100 p-3 d-flex flex-column justify-content-between shadow-sm" style="border-top: 4px solid ${borderCol};">
                            <div>
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <span class="badge font-mono" style="background-color: ${borderCol}; color: white;">Loại ${d.risk_level || 'A'}</span>
                                    <span class="badge bg-dark font-mono text-white">${d.asset_tag}</span>
                                </div>
                                <h6 class="fw-bold text-dark mb-1 text-truncate" title="${d.device_name}">${d.device_name}</h6>
                                <div class="text-muted small font-mono mb-2">
                                    Model: <strong>${d.model || 'N/A'}</strong> • S/N: <strong>${d.serial_no || 'N/A'}</strong>
                                </div>
                                <div class="p-2 rounded bg-light border small mb-2">
                                    <div class="d-flex justify-content-between mb-1">
                                        <span class="text-muted">Vị trí:</span>
                                        <strong class="text-dark">📍 ${facName}</strong>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span class="text-muted">Nhà cung cấp:</span>
                                        <span class="text-truncate" style="max-width: 140px;">${d.supplier_name || d.manufacturer || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="pt-2 border-top d-flex justify-content-between align-items-center">
                                <span class="badge bg-success-subtle text-success">${d.status || 'Hoạt động'}</span>
                                <div class="d-flex gap-1">
                                    <button class="btn btn-sm btn-outline-warning text-dark btn-clinical" onclick="app.openEditDeviceModal(${d.id})" title="Sửa thông tin">
                                        <i class="bi bi-pencil-square"></i>
                                    </button>
                                    <button class="btn btn-sm btn-primary btn-clinical fw-semibold" onclick="app.showDeviceDetails(${d.id})">
                                        <i class="bi bi-journal-text me-1"></i> Hồ Sơ Máy
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        },

        renderDeviceDepartmentView(list) {
            const container = document.getElementById('device-department-groups-container');
            if (!container) return;

            // Group devices by facility
            const groups = {};
            list.forEach(d => {
                const fac = d.facility || d.facility_name || 'Kho Lưu Trữ / Chưa Gán';
                if (!groups[fac]) groups[fac] = [];
                groups[fac].push(d);
            });

            const sortedFacs = Object.keys(groups).sort((a, b) => groups[b].length - groups[a].length);

            container.innerHTML = sortedFacs.map((facName, idx) => {
                const devs = groups[facName];
                const collapseId = `dept-collapse-${idx}`;

                return `
                    <div class="dept-group-card">
                        <div class="dept-group-header" data-bs-toggle="collapse" data-bs-target="#${collapseId}">
                            <div class="d-flex align-items-center gap-2">
                                <i class="bi bi-hospital-fill text-primary fs-5"></i>
                                <div>
                                    <strong class="text-dark fs-6">${facName}</strong>
                                    <span class="text-muted small ms-2">(${devs.length} thiết bị)</span>
                                </div>
                            </div>
                            <div class="d-flex align-items-center gap-2">
                                <span class="badge bg-primary bg-opacity-10 text-primary border border-primary font-mono">${devs.length} máy</span>
                                <i class="bi bi-chevron-down text-muted"></i>
                            </div>
                        </div>
                        <div class="collapse ${idx < 3 ? 'show' : ''}" id="${collapseId}">
                            <div class="p-3">
                                <div class="row g-2">
                                    ${devs.map(d => `
                                        <div class="col-12 col-md-6 col-lg-4">
                                            <div class="p-2 border rounded bg-light d-flex justify-content-between align-items-center" style="cursor: pointer;" onclick="app.showDeviceDetails(${d.id})">
                                                <div>
                                                    <strong class="d-block text-dark small text-truncate" style="max-width: 200px;">${d.device_name}</strong>
                                                    <span class="font-mono text-muted" style="font-size: 0.72rem;">${d.asset_tag} • Model: ${d.model || 'N/A'}</span>
                                                </div>
                                                <span class="badge bg-secondary font-mono">${d.risk_level || 'A'}</span>
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        },

        renderDeviceRiskView(list) {
            const container = document.getElementById('device-risk-groups-container');
            if (!container) return;

            const risks = [
                { key: 'D', name: '🔴 MỨC ĐỘ RỦI RO D — RẤT CAO / DUY TRÌ SỰ SỐNG (Máy thở, Máy sốc tim, RO Thận)', headerClass: 'risk-group-header-d', badgeClass: 'bg-danger' },
                { key: 'C', name: '🟠 MỨC ĐỘ RỦI RO C — TRUNG BÌNH CAO (X-Quang, Siêu âm, Nội soi, Dao mổ điện)', headerClass: 'risk-group-header-c', badgeClass: 'bg-warning text-dark' },
                { key: 'B', name: '🔵 MỨC ĐỘ RỦI RO B — TRUNG BÌNH THẤP (Monitor theo dõi, ECG, Bơm tiêm điện)', headerClass: 'risk-group-header-b', badgeClass: 'bg-primary' },
                { key: 'A', name: '🟢 MỨC ĐỘ RỦI RO A — THẤP (Dụng cụ đo lường, Bàn khám, Đèn mổ)', headerClass: 'risk-group-header-a', badgeClass: 'bg-success' }
            ];

            container.innerHTML = risks.map(r => {
                const devs = list.filter(d => (d.risk_level || 'A').toUpperCase() === r.key);
                return `
                    <div class="risk-group-card mb-4">
                        <div class="p-3 ${r.headerClass} d-flex justify-content-between align-items-center">
                            <div>
                                <strong class="fs-6">${r.name}</strong>
                            </div>
                            <span class="badge ${r.badgeClass} font-mono px-3 py-1 fs-6">${devs.length} Thiết Bị</span>
                        </div>
                        <div class="p-3">
                            <div class="row g-2">
                                ${devs.slice(0, 60).map(d => `
                                    <div class="col-12 col-md-6 col-lg-4">
                                        <div class="p-2 border rounded bg-white shadow-sm d-flex justify-content-between align-items-center" style="cursor: pointer;" onclick="app.showDeviceDetails(${d.id})">
                                            <div>
                                                <strong class="d-block text-dark small text-truncate" style="max-width: 190px;">${d.device_name}</strong>
                                                <span class="font-mono text-muted" style="font-size: 0.72rem;">${d.asset_tag} • S/N: ${d.serial_no || 'N/A'}</span>
                                            </div>
                                            <button class="btn btn-sm btn-outline-primary btn-clinical py-0 px-2" style="font-size: 0.72rem;">Hồ sơ</button>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                            ${devs.length > 60 ? `<div class="text-center pt-2 text-muted small">Và còn ${devs.length - 60} thiết bị khác...</div>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        },

        setupFormSubmissions() {
            this.setupCheckoutForm();
            this.setupStaffEventListeners();
            this.setupDirectoryEditForms();
            this.setupOncallEditForm();
            this.setupQuickAssignForm();

            document.getElementById('btn-tab-staff')?.addEventListener('click', () => {
                this.loadStaff();
            this.loadOncallData();
            });
    
            this.setupGlobalShortcuts();
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

            // Edit Device Form Submit
            const editForm = document.getElementById('editDeviceForm');
            if (editForm) {
                editForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const devId = parseInt(document.getElementById('edit-dev-id').value);
                    const payload = {
                        device_name: document.getElementById('edit-dev-name').value,
                        model: document.getElementById('edit-dev-model').value,
                        serial_no: document.getElementById('edit-dev-serial').value,
                        facility_id: parseInt(document.getElementById('edit-dev-facility').value),
                        category_id: parseInt(document.getElementById('edit-dev-category').value),
                        manufacturer: document.getElementById('edit-dev-mfg').value,
                        country_of_manufacturer: document.getElementById('edit-dev-country').value,
                        year_of_manufacture: document.getElementById('edit-dev-year').value,
                        risk_level: document.getElementById('edit-dev-risk').value,
                        status: document.getElementById('edit-dev-status').value,
                        installation_date: document.getElementById('edit-dev-install-date').value || null,
                        notes: document.getElementById('edit-dev-notes').value
                    };

                    try {
                        const res = await fetch(`/api/devices/${devId}`, {
                            method: 'PUT',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(payload)
                        });

                        const result = await res.json();
                        if (!res.ok) throw new Error(result.detail || 'Lỗi khi cập nhật thiết bị');

                        alert('✅ ' + result.message);
                        bootstrap.Modal.getInstance(document.getElementById('editDeviceModal'))?.hide();
                        this.loadDevices();
                    } catch (err) {
                        alert('❌ Lỗi cập nhật: ' + err.message);
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
            this.loadStaff();
            this.loadOncallData();
                    }
                });
            }
        }
    };

    window.app = app;
    app.init();
});
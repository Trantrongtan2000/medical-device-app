import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
js_path = app_dir / "web" / "js" / "app.js"

with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

contract_supplier_js_methods = """
        // ==================== CONTRACTS & SUPPLIERS CONTROLLER ====================
        currentSupplierSubTab: 'contracts',
        contractsList: [],
        suppliersList: [],

        switchSupplierSubTab(tabName) {
            this.currentSupplierSubTab = tabName;
            const pillContracts = document.getElementById('pill-tab-contracts');
            const pillSuppliers = document.getElementById('pill-tab-suppliers-list');
            const viewContracts = document.getElementById('contracts-view-container');
            const viewSuppliers = document.getElementById('suppliers-view-container');

            if (tabName === 'contracts') {
                pillContracts?.classList.add('active', 'text-white');
                pillContracts?.classList.remove('text-dark');
                pillSuppliers?.classList.remove('active', 'text-white');
                pillSuppliers?.classList.add('text-dark');

                viewContracts?.classList.remove('d-none');
                viewSuppliers?.classList.add('d-none');
                this.loadContractsData();
            } else {
                pillSuppliers?.classList.add('active', 'text-white');
                pillSuppliers?.classList.remove('text-dark');
                pillContracts?.classList.remove('active', 'text-white');
                pillContracts?.classList.add('text-dark');

                viewSuppliers?.classList.remove('d-none');
                viewContracts?.classList.add('d-none');
                this.loadSuppliersData();
            }
        },

        async loadContractsData() {
            try {
                const res = await fetch('/api/contracts');
                const data = await res.json();
                this.contractsList = data;
                
                const badge = document.getElementById('contracts-count-badge');
                const label = document.getElementById('contracts-summary-label');
                if (badge) badge.textContent = `${data.length} Hợp Đồng`;
                if (label) {
                    const totalDevs = data.reduce((acc, c) => acc + (c.device_count || 0), 0);
                    label.textContent = `${data.length} Hợp Đồng • ${totalDevs} Thiết Bị Gắn Kết`;
                }

                this.renderContractsTable(data);
                this.populateSupplierDatalist();
            } catch (err) {
                console.error('Lỗi tải danh sách hợp đồng:', err);
            }
        },

        renderContractsTable(contracts) {
            const tbody = document.getElementById('contracts-table-body');
            if (!tbody) return;

            if (contracts.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4 text-muted">Không tìm thấy hợp đồng nào phù hợp.</td></tr>`;
                return;
            }

            let html = '';
            contracts.forEach((c, idx) => {
                const devCount = c.device_count || 0;
                const statusBadge = (c.status === 'ACTIVE') ?
                    `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>Đang Hiệu Lực</span>` :
                    `<span class="badge bg-secondary">${c.status || 'Hết Hạn'}</span>`;
                
                const formattedDate = c.handover_date ? new Date(c.handover_date).toLocaleDateString('vi-VN') : 'N/A';

                html += `
                    <tr>
                        <td class="fw-bold text-muted">${idx + 1}</td>
                        <td class="font-mono fw-bold text-primary">${c.contract_no}</td>
                        <td>
                            <strong class="text-dark d-block">${c.contract_name || 'Hợp đồng mua sắm TTBYT'}</strong>
                            <small class="text-muted d-block text-truncate" style="max-width: 280px;">${c.notes || 'Không có ghi chú'}</small>
                        </td>
                        <td>
                            <span class="fw-semibold text-dark"><i class="bi bi-building text-secondary me-1"></i>${c.supplier_name || 'N/A'}</span>
                        </td>
                        <td class="font-mono text-muted">${formattedDate}</td>
                        <td>
                            <button class="btn btn-sm btn-light border btn-clinical font-mono fw-bold text-primary" onclick="app.viewContractDevices(${c.id}, '${c.contract_no}')" title="Xem danh sách máy">
                                <i class="bi bi-cpu me-1"></i>${devCount} máy
                            </button>
                        </td>
                        <td>${statusBadge}</td>
                        <td class="text-end">
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" onclick="app.openEditContractModal(${c.id})" title="Chỉnh sửa Hợp đồng">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-outline-info" onclick="app.viewContractDevices(${c.id}, '${c.contract_no}')" title="Xem thiết bị">
                                    <i class="bi bi-search"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="app.deleteContract(${c.id}, '${c.contract_no}')" title="Xóa Hợp đồng">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });

            tbody.innerHTML = html;
        },

        async loadSuppliersData() {
            try {
                const res = await fetch('/api/directory/suppliers');
                const data = await res.json();
                this.suppliersList = data;

                const badge = document.getElementById('suppliers-count-badge');
                const label = document.getElementById('suppliers-summary-label');
                if (badge) badge.textContent = `${data.length} Nhà Cung Cấp`;
                if (label) label.textContent = `${data.length} Nhà Cung Cấp / Đối Tác Kỹ Thuật Hãng`;

                this.renderSuppliersTable(data);
                this.populateSupplierDatalist();
            } catch (err) {
                console.error('Lỗi tải danh bạ nhà cung cấp:', err);
            }
        },

        renderSuppliersTable(suppliers) {
            const tbody = document.getElementById('suppliers-table-body');
            if (!tbody) return;

            if (suppliers.length === 0) {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">Không tìm thấy nhà cung cấp nào.</td></tr>`;
                return;
            }

            let html = '';
            suppliers.forEach((s, idx) => {
                html += `
                    <tr>
                        <td class="fw-bold text-muted">${idx + 1}</td>
                        <td>
                            <strong class="text-dark d-block"><i class="bi bi-building text-warning me-1"></i>${s.supplier_name}</strong>
                        </td>
                        <td>
                            <span class="text-dark fw-semibold">${s.contact_person || 'Đại diện kỹ thuật'}</span>
                        </td>
                        <td>
                            <a href="tel:${s.phone}" class="btn btn-sm btn-outline-primary btn-clinical font-mono fw-bold">
                                <i class="bi bi-telephone-fill me-1"></i>${s.phone || 'N/A'}
                            </a>
                        </td>
                        <td class="font-mono text-muted">${s.email || 'N/A'}</td>
                        <td>
                            <small class="text-muted d-block text-truncate" style="max-width: 240px;">${s.service_scope || 'Hỗ trợ kỹ thuật & bảo hành thiết bị'}</small>
                        </td>
                        <td class="text-end">
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" onclick="app.openEditSupplierModal(${s.id})" title="Chỉnh sửa Nhà cung cấp">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-outline-info" onclick="app.viewSupplierDevices(${s.id}, '${s.supplier_name}')" title="Xem thiết bị do NCC cung cấp">
                                    <i class="bi bi-search"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="app.deleteSupplier(${s.id}, '${s.supplier_name}')" title="Xóa Nhà cung cấp">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });

            tbody.innerHTML = html;
        },

        populateSupplierDatalist() {
            const dl = document.getElementById('supplier-names-list');
            if (!dl) return;
            const names = this.suppliersList.map(s => s.supplier_name);
            dl.innerHTML = names.map(n => `<option value="${n}">`).join('');
        },

        filterContractsSuppliers() {
            const query = (document.getElementById('contract-supplier-search-input')?.value || '').toLowerCase().trim();
            
            if (this.currentSupplierSubTab === 'contracts') {
                const filtered = this.contractsList.filter(c => 
                    (c.contract_no && c.contract_no.toLowerCase().includes(query)) ||
                    (c.contract_name && c.contract_name.toLowerCase().includes(query)) ||
                    (c.supplier_name && c.supplier_name.toLowerCase().includes(query)) ||
                    (c.notes && c.notes.toLowerCase().includes(query))
                );
                this.renderContractsTable(filtered);
            } else {
                const filtered = this.suppliersList.filter(s => 
                    (s.supplier_name && s.supplier_name.toLowerCase().includes(query)) ||
                    (s.contact_person && s.contact_person.toLowerCase().includes(query)) ||
                    (s.phone && s.phone.toLowerCase().includes(query)) ||
                    (s.email && s.email.toLowerCase().includes(query)) ||
                    (s.service_scope && s.service_scope.toLowerCase().includes(query))
                );
                this.renderSuppliersTable(filtered);
            }
        },

        openCreateContractModal() {
            document.getElementById('contract-modal-title').innerHTML = `<i class="bi bi-file-earmark-plus me-2"></i>Thêm Hợp Đồng Mới`;
            document.getElementById('contract-form-id').value = '';
            document.getElementById('contract-form-no').value = '';
            document.getElementById('contract-form-no').readOnly = false;
            document.getElementById('contract-form-name').value = '';
            document.getElementById('contract-form-supplier').value = '';
            document.getElementById('contract-form-date').value = new Date().toISOString().split('T')[0];
            document.getElementById('contract-form-warranty').value = '24';
            document.getElementById('contract-form-status').value = 'ACTIVE';
            document.getElementById('contract-form-notes').value = '';

            const modal = new bootstrap.Modal(document.getElementById('contractModal'));
            modal.show();
        },

        openEditContractModal(contractId) {
            const c = this.contractsList.find(item => item.id === contractId);
            if (!c) return;

            document.getElementById('contract-modal-title').innerHTML = `<i class="bi bi-pencil-square me-2"></i>Chỉnh Sửa Hợp Đồng: ${c.contract_no}`;
            document.getElementById('contract-form-id').value = c.id;
            document.getElementById('contract-form-no').value = c.contract_no;
            document.getElementById('contract-form-name').value = c.contract_name || '';
            document.getElementById('contract-form-supplier').value = c.supplier_name || '';
            document.getElementById('contract-form-date').value = c.handover_date || '';
            document.getElementById('contract-form-warranty').value = c.warranty_period_months || 24;
            document.getElementById('contract-form-status').value = c.status || 'ACTIVE';
            document.getElementById('contract-form-notes').value = c.notes || '';

            const modal = new bootstrap.Modal(document.getElementById('contractModal'));
            modal.show();
        },

        async submitContractForm() {
            const id = document.getElementById('contract-form-id').value;
            const payload = {
                contract_no: document.getElementById('contract-form-no').value.trim(),
                contract_name: document.getElementById('contract-form-name').value.trim(),
                supplier_name: document.getElementById('contract-form-supplier').value.trim(),
                handover_date: document.getElementById('contract-form-date').value || null,
                warranty_period_months: parseInt(document.getElementById('contract-form-warranty').value) || 24,
                status: document.getElementById('contract-form-status').value,
                notes: document.getElementById('contract-form-notes').value.trim()
            };

            try {
                let res;
                if (id) {
                    res = await fetch(`/api/contracts/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                } else {
                    res = await fetch('/api/contracts', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                }
                const data = await res.json();
                if (res.ok) {
                    alert('✅ ' + data.message);
                    bootstrap.Modal.getInstance(document.getElementById('contractModal'))?.hide();
                    this.loadContractsData();
                } else {
                    alert('❌ Lỗi: ' + (data.detail || 'Không thể lưu hợp đồng'));
                }
            } catch (err) {
                alert('❌ Lỗi kết nối: ' + err.message);
            }
        },

        async deleteContract(contractId, contractNo) {
            if (!confirm(`Bạn có chắc chắn muốn xóa hợp đồng "${contractNo}"?`)) return;

            try {
                const res = await fetch(`/api/contracts/${contractId}`, { method: 'DELETE' });
                const data = await res.json();
                alert('✅ ' + data.message);
                this.loadContractsData();
            } catch (err) {
                alert('❌ Lỗi xóa hợp đồng: ' + err.message);
            }
        },

        async viewContractDevices(contractId, contractNo) {
            try {
                const res = await fetch(`/api/contracts/${contractId}/devices`);
                const data = await res.json();

                document.getElementById('linked-devices-modal-title').textContent = `Thiết Bị Thuộc HĐ: ${data.contract.contract_no}`;
                document.getElementById('linked-devices-modal-subtitle').textContent = `${data.contract.contract_name} • Tổng số: ${data.total_devices} thiết bị`;

                const tbody = document.getElementById('linked-devices-table-body');
                if (data.devices.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">Chưa có thiết bị nào được gắn với hợp đồng này.</td></tr>`;
                } else {
                    tbody.innerHTML = data.devices.map((d, idx) => `
                        <tr>
                            <td class="text-muted fw-bold">${idx + 1}</td>
                            <td class="font-mono fw-bold text-primary">BVQ7-TTB-${String(d.id).padStart(5, '0')}</td>
                            <td><strong class="text-dark">${d.device_name}</strong></td>
                            <td class="font-mono">${d.model || 'N/A'}</td>
                            <td class="font-mono text-secondary">${d.serial_no || 'N/A'}</td>
                            <td><span class="badge bg-light text-dark border">${d.facility_name || 'N/A'}</span></td>
                            <td><span class="badge bg-success-subtle text-success">${d.status}</span></td>
                        </tr>
                    `).join('');
                }

                const modal = new bootstrap.Modal(document.getElementById('viewLinkedDevicesModal'));
                modal.show();
            } catch (err) {
                alert('Lỗi tải danh sách thiết bị: ' + err.message);
            }
        },

        openCreateSupplierModal() {
            document.getElementById('supplier-modal-title').innerHTML = `<i class="bi bi-building me-2"></i>Thêm Nhà Cung Cấp Mới`;
            document.getElementById('supplier-form-id').value = '';
            document.getElementById('supplier-form-name').value = '';
            document.getElementById('supplier-form-person').value = '';
            document.getElementById('supplier-form-phone').value = '';
            document.getElementById('supplier-form-email').value = '';
            document.getElementById('supplier-form-scope').value = '';

            const modal = new bootstrap.Modal(document.getElementById('supplierModal'));
            modal.show();
        },

        openEditSupplierModal(supplierId) {
            const s = this.suppliersList.find(item => item.id === supplierId);
            if (!s) return;

            document.getElementById('supplier-modal-title').innerHTML = `<i class="bi bi-pencil-square me-2"></i>Chỉnh Sửa Nhà Cung Cấp`;
            document.getElementById('supplier-form-id').value = s.id;
            document.getElementById('supplier-form-name').value = s.supplier_name;
            document.getElementById('supplier-form-person').value = s.contact_person || '';
            document.getElementById('supplier-form-phone').value = s.phone || '';
            document.getElementById('supplier-form-email').value = s.email || '';
            document.getElementById('supplier-form-scope').value = s.service_scope || '';

            const modal = new bootstrap.Modal(document.getElementById('supplierModal'));
            modal.show();
        },

        async submitSupplierForm() {
            const id = document.getElementById('supplier-form-id').value;
            const payload = {
                supplier_name: document.getElementById('supplier-form-name').value.trim(),
                contact_person: document.getElementById('supplier-form-person').value.trim(),
                phone: document.getElementById('supplier-form-phone').value.trim(),
                email: document.getElementById('supplier-form-email').value.trim(),
                service_scope: document.getElementById('supplier-form-scope').value.trim()
            };

            try {
                let res;
                if (id) {
                    res = await fetch(`/api/directory/suppliers/${id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                } else {
                    res = await fetch('/api/directory/suppliers', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                }
                const data = await res.json();
                if (res.ok) {
                    alert('✅ ' + data.message);
                    bootstrap.Modal.getInstance(document.getElementById('supplierModal'))?.hide();
                    this.loadSuppliersData();
                } else {
                    alert('❌ Lỗi: ' + (data.detail || 'Không thể lưu nhà cung cấp'));
                }
            } catch (err) {
                alert('❌ Lỗi kết nối: ' + err.message);
            }
        },

        async deleteSupplier(supplierId, supplierName) {
            if (!confirm(`Bạn có chắc chắn muốn xóa nhà cung cấp "${supplierName}"?`)) return;

            try {
                const res = await fetch(`/api/directory/suppliers/${supplierId}`, { method: 'DELETE' });
                const data = await res.json();
                alert('✅ ' + data.message);
                this.loadSuppliersData();
            } catch (err) {
                alert('❌ Lỗi xóa nhà cung cấp: ' + err.message);
            }
        },

        async viewSupplierDevices(supplierId, supplierName) {
            try {
                const res = await fetch(`/api/directory/suppliers/${supplierId}/devices`);
                const data = await res.json();

                document.getElementById('linked-devices-modal-title').textContent = `Thiết Bị Của Nhà Thầu: ${data.supplier.supplier_name}`;
                document.getElementById('linked-devices-modal-subtitle').textContent = `Đại diện: ${data.supplier.contact_person || 'Kỹ sư hãng'} • Tổng số: ${data.total_devices} máy`;

                const tbody = document.getElementById('linked-devices-table-body');
                if (data.devices.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-muted">Chưa ghi nhận thiết bị nào do nhà thầu này cung cấp trong CSDL.</td></tr>`;
                } else {
                    tbody.innerHTML = data.devices.map((d, idx) => `
                        <tr>
                            <td class="text-muted fw-bold">${idx + 1}</td>
                            <td class="font-mono fw-bold text-primary">BVQ7-TTB-${String(d.id).padStart(5, '0')}</td>
                            <td><strong class="text-dark">${d.device_name}</strong></td>
                            <td class="font-mono">${d.model || 'N/A'}</td>
                            <td class="font-mono text-secondary">${d.serial_no || 'N/A'}</td>
                            <td><span class="badge bg-light text-dark border">${d.facility_name || 'N/A'}</span></td>
                            <td><span class="badge bg-success-subtle text-success">${d.status}</span></td>
                        </tr>
                    `).join('');
                }

                const modal = new bootstrap.Modal(document.getElementById('viewLinkedDevicesModal'));
                modal.show();
            } catch (err) {
                alert('Lỗi tải danh sách thiết bị: ' + err.message);
            }
        },
"""

# Append to app object in app.js
if "currentSupplierSubTab" not in js_content:
    # insert before init() in app.js
    pattern = r'(\s+init\(\)\s*\{)'
    replacement = contract_supplier_js_methods + r'\1'
    js_content = re.sub(pattern, replacement, js_content, count=1)
    
    # In init(), add call to loadContractsData()
    js_content = js_content.replace(
        "this.loadAPIKeysStatus();",
        "this.loadAPIKeysStatus();\n            this.loadContractsData();\n            this.loadSuppliersData();"
    )

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print("✅ Đã tích hợp đầy đủ Controller Quản lý Hợp đồng & Nhà cung cấp vào `web/js/app.js`!")

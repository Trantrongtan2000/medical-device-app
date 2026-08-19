import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")
js_path = app_dir / "web" / "js" / "app.js"

with open(js_path, "r", encoding="utf-8") as f:
    js_content = f.read()

new_key_js_methods = """
        // ==================== API KEY ROTATION & MANAGEMENT CONTROLLER ====================
        currentKeyService: 'gemini',
        keyVisibilityMap: {},

        openKeyConfigModal(service = 'gemini') {
            this.currentKeyService = service;
            const modal = new bootstrap.Modal(document.getElementById('keyConfigModal'));
            modal.show();
            this.switchKeyServiceTab(service);
        },

        switchKeyServiceTab(service) {
            this.currentKeyService = service;
            const pillGemini = document.getElementById('pill-gemini-keys');
            const pillMistral = document.getElementById('pill-mistral-keys');

            if (service === 'gemini') {
                pillGemini?.classList.add('active', 'text-white');
                pillGemini?.classList.remove('text-dark');
                pillMistral?.classList.remove('active', 'text-white');
                pillMistral?.classList.add('text-dark');
            } else {
                pillMistral?.classList.add('active', 'text-white');
                pillMistral?.classList.remove('text-dark');
                pillGemini?.classList.remove('active', 'text-white');
                pillGemini?.classList.add('text-dark');
            }

            this.loadAndRenderKeys(service);
        },

        async loadAndRenderKeys(service = this.currentKeyService) {
            const container = document.getElementById('keys-table-container');
            if (container) {
                container.innerHTML = `
                    <div class="text-center py-4 text-muted">
                        <div class="spinner-border spinner-border-sm text-primary me-2" role="status"></div>
                        Đang tải danh sách API Keys của ${service.toUpperCase()}...
                    </div>
                `;
            }

            try {
                const res = await fetch('/api/keys/config');
                const data = await res.json();
                
                // Update badges
                const geminiModalBadge = document.getElementById('gemini-modal-badge');
                const mistralModalBadge = document.getElementById('mistral-modal-badge');
                const geminiKeyCountBadge = document.getElementById('gemini-key-count-badge');
                const mistralKeyCountBadge = document.getElementById('mistral-key-count-badge');

                if (geminiModalBadge && data.gemini) {
                    geminiModalBadge.textContent = `${data.gemini.active_keys}/${data.gemini.total_keys} Active`;
                }
                if (mistralModalBadge && data.mistral) {
                    mistralModalBadge.textContent = `${data.mistral.active_keys}/${data.mistral.total_keys} Active`;
                }
                if (geminiKeyCountBadge && data.gemini) {
                    geminiKeyCountBadge.textContent = `${data.gemini.active_keys} Keys Hoạt Động (Pool ${data.gemini.total_keys})`;
                }
                if (mistralKeyCountBadge && data.mistral) {
                    mistralKeyCountBadge.textContent = `${data.mistral.active_keys} Keys Hoạt Động (Pool ${data.mistral.total_keys})`;
                }

                const currentStats = data[service] || { total_keys: 0, active_keys: 0, inactive_keys: 0, rate_limited_keys: 0, keys_list: [] };
                
                // Update summary counters
                document.getElementById('stat-total-keys').textContent = currentStats.total_keys || 0;
                document.getElementById('stat-active-keys').textContent = currentStats.active_keys || 0;
                document.getElementById('stat-inactive-keys').textContent = currentStats.inactive_keys || 0;
                document.getElementById('stat-ratelimit-keys').textContent = currentStats.rate_limited_keys || 0;

                this.renderKeysTable(service, currentStats.keys_list || []);
            } catch (err) {
                if (container) {
                    container.innerHTML = `<div class="alert alert-danger py-2 mb-0">Lỗi kết nối CSDL: ${err.message}</div>`;
                }
            }
        },

        renderKeysTable(service, keys) {
            const container = document.getElementById('keys-table-container');
            if (!container) return;

            if (keys.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-4 text-muted">
                        <i class="bi bi-key fs-2 d-block text-secondary mb-1"></i>
                        Chưa có API Key nào được đăng ký cho ${service.toUpperCase()}. Vui lòng dán key mới vào ô bên dưới!
                    </div>
                `;
                return;
            }

            let html = `
                <table class="table table-hover align-middle mb-0" style="font-size: 0.85rem;">
                    <thead class="table-light">
                        <tr>
                            <th style="width: 50px;">#</th>
                            <th>API Key / Định Danh</th>
                            <th style="width: 140px;">Trạng Thái</th>
                            <th style="width: 110px;">Độ Trễ Live</th>
                            <th style="width: 220px;" class="text-end">Thao Tác</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            keys.forEach((k, idx) => {
                const isRevealed = !!this.keyVisibilityMap[`${service}_${idx}`];
                const displayKey = isRevealed ? k.raw_key : k.masked_key;
                
                let statusBadge = `<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>ACTIVE</span>`;
                if (k.status === 'INACTIVE') {
                    statusBadge = `<span class="badge bg-secondary"><i class="bi bi-pause-circle me-1"></i>TẠM DỪNG</span>`;
                } else if (k.status === 'RATE_LIMITED') {
                    statusBadge = `<span class="badge bg-warning text-dark"><i class="bi bi-hourglass-split me-1"></i>COOLDOWN</span>`;
                } else if (k.status === 'INVALID') {
                    statusBadge = `<span class="badge bg-danger"><i class="bi bi-x-circle me-1"></i>INVALID</span>`;
                }

                const primaryBadge = k.is_primary ? `<span class="badge bg-primary-subtle text-primary border border-primary-subtle ms-1"><i class="bi bi-award-fill me-1"></i>Ưu Tiên #1</span>` : '';
                const latencyBadge = k.last_latency_ms ? `<span class="badge bg-info-subtle text-info border"><i class="bi bi-lightning-charge-fill me-1"></i>${k.last_latency_ms}ms</span>` : `<span class="text-muted small">Chưa test</span>`;

                html += `
                    <tr>
                        <td class="fw-bold text-muted">${idx + 1}</td>
                        <td>
                            <div class="d-flex align-items-center gap-2">
                                <code class="p-1 px-2 rounded bg-light border font-mono text-dark fw-bold" style="font-size: 0.82rem; word-break: break-all;">
                                    ${displayKey}
                                </code>
                                <button class="btn btn-sm btn-link text-secondary p-0" onclick="app.toggleKeyVisibility('${service}', ${idx})" title="${isRevealed ? 'Ẩn key' : 'Hiện đầy đủ key'}">
                                    <i class="bi bi-${isRevealed ? 'eye-slash' : 'eye'}"></i>
                                </button>
                                <button class="btn btn-sm btn-link text-secondary p-0" onclick="app.copyKeyToClipboard('${k.raw_key}')" title="Sao chép key">
                                    <i class="bi bi-clipboard"></i>
                                </button>
                                ${primaryBadge}
                            </div>
                        </td>
                        <td>${statusBadge}</td>
                        <td><span id="latency-badge-${service}-${idx}">${latencyBadge}</span></td>
                        <td class="text-end">
                            <div class="btn-group btn-group-sm" role="group">
                                <button class="btn btn-outline-info" id="btn-test-${service}-${idx}" onclick="app.testSingleKey('${service}', '${k.raw_key}', 'btn-test-${service}-${idx}', 'latency-badge-${service}-${idx}')" title="Kiểm tra kết nối Live">
                                    <i class="bi bi-lightning-charge"></i>
                                </button>
                                <button class="btn btn-outline-primary" onclick="app.openEditKeyModal('${service}', '${k.raw_key}', '${k.status}')" title="Chỉnh sửa Key / Trạng thái">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                ${!k.is_primary ? `
                                <button class="btn btn-outline-warning text-dark" onclick="app.setPrimaryKey('${service}', '${k.raw_key}')" title="Đặt làm khóa ưu tiên số 1">
                                    <i class="bi bi-arrow-up-circle"></i>
                                </button>` : ''}
                                <button class="btn btn-outline-${k.status === 'ACTIVE' ? 'secondary' : 'success'}" onclick="app.toggleKeyStatus('${service}', '${k.raw_key}', '${k.status}')" title="${k.status === 'ACTIVE' ? 'Tạm dừng key' : 'Kích hoạt key'}">
                                    <i class="bi bi-${k.status === 'ACTIVE' ? 'pause-fill' : 'play-fill'}"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="app.deleteKey('${service}', '${k.raw_key}')" title="Xóa key khỏi pool">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });

            html += `
                    </tbody>
                </table>
            `;

            container.innerHTML = html;
        },

        toggleKeyVisibility(service, idx) {
            const keyId = `${service}_${idx}`;
            this.keyVisibilityMap[keyId] = !this.keyVisibilityMap[keyId];
            this.loadAndRenderKeys(service);
        },

        copyKeyToClipboard(rawKey) {
            navigator.clipboard.writeText(rawKey).then(() => {
                alert('📋 Đã sao chép API Key vào bộ nhớ tạm!');
            }).catch(err => {
                alert('Lỗi sao chép: ' + err.message);
            });
        },

        async testSingleKey(service, rawKey, btnId, latencyBadgeId) {
            const btn = document.getElementById(btnId);
            const badge = document.getElementById(latencyBadgeId);
            const originalBtnHtml = btn ? btn.innerHTML : '';
            
            if (btn) {
                btn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status"></span>`;
                btn.disabled = true;
            }
            if (badge) {
                badge.innerHTML = `<span class="badge bg-warning text-dark"><i class="bi bi-arrow-repeat spin me-1"></i>Testing...</span>`;
            }

            try {
                const res = await fetch('/api/keys/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ service: service, key: rawKey })
                });
                const data = await res.json();
                
                if (data.valid) {
                    if (badge) {
                        badge.innerHTML = `<span class="badge bg-success"><i class="bi bi-check-lg me-1"></i>${data.latency_ms}ms</span>`;
                    }
                    alert(`✅ KẾT NỐI THÀNH CÔNG!\n${data.message}`);
                } else {
                    if (badge) {
                        badge.innerHTML = `<span class="badge bg-danger"><i class="bi bi-x-lg me-1"></i>Lỗi</span>`;
                    }
                    alert(`❌ KẾT NỐI THẤT BẠI!\n${data.message}`);
                }
            } catch (err) {
                if (badge) {
                    badge.innerHTML = `<span class="badge bg-danger">Lỗi mạng</span>`;
                }
                alert('❌ Lỗi kiểm tra API: ' + err.message);
            } finally {
                if (btn) {
                    btn.innerHTML = originalBtnHtml;
                    btn.disabled = false;
                }
            }
        },

        openEditKeyModal(service, rawKey, status) {
            document.getElementById('edit-key-service').value = service;
            document.getElementById('edit-key-service-display').value = (service === 'gemini') ? 'Google Gemini AI (Interactions / 3.7 Flash)' : 'Mistral AI OCR Engine';
            document.getElementById('edit-key-old-value').value = rawKey;
            document.getElementById('edit-key-new-value').value = rawKey;
            document.getElementById('edit-key-status').value = status || 'ACTIVE';

            const editModal = new bootstrap.Modal(document.getElementById('editSingleKeyModal'));
            editModal.show();
        },

        async testModalKeyLive() {
            const service = document.getElementById('edit-key-service').value;
            const newKey = document.getElementById('edit-key-new-value').value.trim();
            const btn = document.getElementById('btn-test-modal-key');
            if (!newKey) {
                alert('Vui lòng nhập API Key để kiểm tra!');
                return;
            }

            const originalHtml = btn.innerHTML;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Đang ping test...`;
            btn.disabled = true;

            try {
                const res = await fetch('/api/keys/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ service: service, key: newKey })
                });
                const data = await res.json();
                if (data.valid) {
                    alert(`✅ KEY HỢP LỆ!\n${data.message}`);
                } else {
                    alert(`❌ KEY KHÔNG HỢP LỆ!\n${data.message}`);
                }
            } catch (err) {
                alert('❌ Lỗi kết nối: ' + err.message);
            } finally {
                btn.innerHTML = originalHtml;
                btn.disabled = false;
            }
        },

        async submitEditSingleKey() {
            const service = document.getElementById('edit-key-service').value;
            const oldKey = document.getElementById('edit-key-old-value').value;
            const newKey = document.getElementById('edit-key-new-value').value.trim();
            const status = document.getElementById('edit-key-status').value;

            if (!newKey) {
                alert('API Key không được để trống!');
                return;
            }

            try {
                const res = await fetch('/api/keys/update', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        service: service,
                        old_key: oldKey,
                        new_key: newKey,
                        status: status
                    })
                });
                const data = await res.json();
                if (res.ok) {
                    alert('✅ ' + data.message);
                    bootstrap.Modal.getInstance(document.getElementById('editSingleKeyModal'))?.hide();
                    this.loadAndRenderKeys(service);
                } else {
                    alert('❌ Lỗi cập nhật: ' + (data.detail || 'Không xác định'));
                }
            } catch (err) {
                alert('❌ Lỗi kết nối API: ' + err.message);
            }
        },

        async toggleKeyStatus(service, rawKey, currentStatus) {
            const newStatus = (currentStatus === 'ACTIVE') ? 'INACTIVE' : 'ACTIVE';
            try {
                const res = await fetch('/api/keys/set-status', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        service: service,
                        key: rawKey,
                        status: newStatus
                    })
                });
                if (res.ok) {
                    this.loadAndRenderKeys(service);
                } else {
                    alert('Lỗi cập nhật trạng thái');
                }
            } catch (err) {
                alert('Lỗi: ' + err.message);
            }
        },

        async setPrimaryKey(service, rawKey) {
            try {
                const res = await fetch('/api/keys/set-primary', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        service: service,
                        key: rawKey
                    })
                });
                if (res.ok) {
                    this.loadAndRenderKeys(service);
                } else {
                    alert('Lỗi đổi khóa ưu tiên');
                }
            } catch (err) {
                alert('Lỗi: ' + err.message);
            }
        },

        async deleteKey(service, rawKey) {
            if (!confirm(`Bạn có chắc chắn muốn xóa API Key này khỏi ${service.toUpperCase()}?`)) return;

            try {
                const res = await fetch('/api/keys/remove', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        service: service,
                        key: rawKey
                    })
                });
                const data = await res.json();
                alert('✅ ' + data.message);
                this.loadAndRenderKeys(service);
            } catch (err) {
                alert('Lỗi khi xóa key: ' + err.message);
            }
        },

        async submitNewAPIKey() {
            const service = this.currentKeyService;
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
                document.getElementById('key-input-textarea').value = '';
                this.loadAndRenderKeys(service);
            } catch (err) {
                alert('❌ Lỗi thêm key: ' + err.message);
            }
        },
"""

# Replace old key methods in app.js
pattern = r'openKeyConfigModal\(\) \{.*?loadAPIKeysStatus\(\) \{.*?\}'
replacement = new_key_js_methods.strip() + "\n\n        async loadAPIKeysStatus() {"

# Search and replace in app.js
pattern_full = r'openKeyConfigModal\(\) \{.*?async loadAPIKeysStatus\(\) \{'
js_content = re.sub(pattern_full, new_key_js_methods.strip() + "\n\n        async loadAPIKeysStatus() {", js_content, flags=re.DOTALL)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print("✅ [3] Đã cập nhật `web/js/app.js` với toàn bộ bộ điều khiển Key Controller (Sửa, Xóa, Test Live, Đổi trạng thái)!")

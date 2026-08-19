/**
 * 🎨 Editorial Diagram Visualizer Engine
 * Áp dụng triết lý thiết kế chuẩn mực từ cathrynlavery/diagram-design
 * Đặc tính: Thuần SVG + HTML, không phụ thuộc thư viện ngoài, nét vẽ chuẩn xác, bảng màu y tế cao cấp
 */

const DiagramEngine = {
    diagrams: {
        qt04: {
            title: "Quy Trình Tiếp Nhận, Lắp Đặt, Nghiệm Thu & Sổ Lý Lịch Máy (QT.04)",
            subtitle: "Chuỗi 5 Biểu Mẫu Chuẩn: BM01 → BM02 → BM03 → BM04 → BM05",
            svg: `
            <svg viewBox="0 0 960 260" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Plus Jakarta Sans', sans-serif;">
                <defs>
                    <linearGradient id="grad-blue" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#0284c7" />
                        <stop offset="100%" stop-color="#0369a1" />
                    </linearGradient>
                    <linearGradient id="grad-teal" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#0d9488" />
                        <stop offset="100%" stop-color="#0f766e" />
                    </linearGradient>
                    <linearGradient id="grad-indigo" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#6366f1" />
                        <stop offset="100%" stop-color="#4f46e5" />
                    </linearGradient>
                    <linearGradient id="grad-emerald" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#10b981" />
                        <stop offset="100%" stop-color="#059669" />
                    </linearGradient>
                    <filter id="shadow" x="-5%" y="-10%" width="110%" height="130%">
                        <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.08"/>
                    </filter>
                    <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                        <path d="M 0 1 L 8 5 L 0 9 z" fill="#94a3b8" />
                    </marker>
                </defs>

                <!-- Background Connectors -->
                <line x1="160" y1="120" x2="220" y2="120" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow)"/>
                <line x1="350" y1="120" x2="410" y2="120" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow)"/>
                <line x1="540" y1="120" x2="600" y2="120" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow)"/>
                <line x1="730" y1="120" x2="790" y2="120" stroke="#cbd5e1" stroke-width="3" stroke-dasharray="6,6" marker-end="url(#arrow)"/>

                <!-- Step 1: BM01 -->
                <g class="diagram-node" transform="translate(30, 40)" filter="url(#shadow)" style="cursor: pointer;">
                    <rect width="130" height="150" rx="12" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>
                    <rect width="130" height="36" rx="10" fill="url(#grad-blue)"/>
                    <text x="65" y="24" fill="#ffffff" font-size="13" font-weight="700" text-anchor="middle">BƯỚC 1: BM01</text>
                    <text x="65" y="70" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Bàn Giao &</text>
                    <text x="65" y="88" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Lắp Đặt</text>
                    <circle cx="65" cy="120" r="14" fill="#f0f9ff"/>
                    <text x="65" y="125" fill="#0284c7" font-size="12" font-weight="800" text-anchor="middle">📦</text>
                    <text x="65" y="160" fill="#64748b" font-size="10" font-weight="600" text-anchor="middle">Hãng → P.TTB</text>
                </g>

                <!-- Step 2: BM02 -->
                <g class="diagram-node" transform="translate(220, 40)" filter="url(#shadow)" style="cursor: pointer;">
                    <rect width="130" height="150" rx="12" fill="#ffffff" stroke="#0d9488" stroke-width="2"/>
                    <rect width="130" height="36" rx="10" fill="url(#grad-teal)"/>
                    <text x="65" y="24" fill="#ffffff" font-size="13" font-weight="700" text-anchor="middle">BƯỚC 2: BM02</text>
                    <text x="65" y="70" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Nghiệm Thu</text>
                    <text x="65" y="88" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Kỹ Thuật</text>
                    <circle cx="65" cy="120" r="14" fill="#ccfbf1"/>
                    <text x="65" y="125" fill="#0d9488" font-size="12" font-weight="800" text-anchor="middle">🔬</text>
                    <text x="65" y="160" fill="#64748b" font-size="10" font-weight="600" text-anchor="middle">Chạy thử tải</text>
                </g>

                <!-- Step 3: BM03 -->
                <g class="diagram-node" transform="translate(410, 40)" filter="url(#shadow)" style="cursor: pointer;">
                    <rect width="130" height="150" rx="12" fill="#ffffff" stroke="#6366f1" stroke-width="2"/>
                    <rect width="130" height="36" rx="10" fill="url(#grad-indigo)"/>
                    <text x="65" y="24" fill="#ffffff" font-size="13" font-weight="700" text-anchor="middle">BƯỚC 3: BM03</text>
                    <text x="65" y="70" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Đào Tạo &</text>
                    <text x="65" y="88" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Huấn Luyện</text>
                    <circle cx="65" cy="120" r="14" fill="#e0e7ff"/>
                    <text x="65" y="125" fill="#6366f1" font-size="12" font-weight="800" text-anchor="middle">🎓</text>
                    <text x="65" y="160" fill="#64748b" font-size="10" font-weight="600" text-anchor="middle">Bác sĩ / ĐD</text>
                </g>

                <!-- Step 4: BM04 -->
                <g class="diagram-node" transform="translate(600, 40)" filter="url(#shadow)" style="cursor: pointer;">
                    <rect width="130" height="150" rx="12" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>
                    <rect width="130" height="36" rx="10" fill="url(#grad-blue)"/>
                    <text x="65" y="24" fill="#ffffff" font-size="13" font-weight="700" text-anchor="middle">BƯỚC 4: BM04</text>
                    <text x="65" y="70" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Bàn Giao</text>
                    <text x="65" y="88" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Khoa Lâm Sàng</text>
                    <circle cx="65" cy="120" r="14" fill="#f0f9ff"/>
                    <text x="65" y="125" fill="#0284c7" font-size="12" font-weight="800" text-anchor="middle">🤝</text>
                    <text x="65" y="160" fill="#64748b" font-size="10" font-weight="600" text-anchor="middle">P.TTB → Khoa</text>
                </g>

                <!-- Step 5: BM05 -->
                <g class="diagram-node" transform="translate(790, 40)" filter="url(#shadow)" style="cursor: pointer;">
                    <rect width="140" height="150" rx="12" fill="#ffffff" stroke="#10b981" stroke-width="2"/>
                    <rect width="140" height="36" rx="10" fill="url(#grad-emerald)"/>
                    <text x="70" y="24" fill="#ffffff" font-size="13" font-weight="700" text-anchor="middle">BƯỚC 5: BM05</text>
                    <text x="70" y="70" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Sổ Lý Lịch</text>
                    <text x="70" y="88" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Passport Máy</text>
                    <circle cx="70" cy="120" r="14" fill="#d1fae5"/>
                    <text x="70" y="125" fill="#10b981" font-size="12" font-weight="800" text-anchor="middle">📑</text>
                    <text x="70" y="160" fill="#059669" font-size="10" font-weight="700" text-anchor="middle">KÍCH HOẠT QR</text>
                </g>
            </svg>
            `
        },
        ro_loop: {
            title: "Vòng Lặp Kiểm Soát An Toàn Nước R.O Thận Nhân Tạo (QT.01 & QT.02)",
            subtitle: "Tiêu chuẩn AAMI / ISO 23500 & Theo Dõi 5 Thông Số Vàng Mỗi Ca",
            svg: `
            <svg viewBox="0 0 960 280" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Plus Jakarta Sans', sans-serif;">
                <defs>
                    <linearGradient id="grad-water" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#0284c7" />
                        <stop offset="100%" stop-color="#0ea5e9" />
                    </linearGradient>
                    <filter id="shadow2" x="-5%" y="-10%" width="110%" height="130%">
                        <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.08"/>
                    </filter>
                </defs>

                <!-- Central Flow Path -->
                <path d="M 120 140 H 840" stroke="#0284c7" stroke-width="4" stroke-linecap="round"/>
                
                <!-- Stage 1: Raw Water & Softener -->
                <g transform="translate(60, 60)" filter="url(#shadow2)">
                    <rect width="150" height="150" rx="12" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>
                    <rect width="150" height="32" rx="10" fill="#0284c7"/>
                    <text x="75" y="21" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">TIỀN XỬ LÝ</text>
                    <text x="75" y="65" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Làm Mềm Nước</text>
                    <text x="75" y="85" fill="#64748b" font-size="11" text-anchor="middle">Pha Muối Tái Sinh</text>
                    <text x="75" y="105" fill="#0284c7" font-size="11" font-weight="700" text-anchor="middle">(BM02_QT.02)</text>
                    <text x="75" y="135" fill="#059669" font-size="11" font-weight="700" text-anchor="middle">Độ cứng &lt; 1 gpg</text>
                </g>

                <!-- Stage 2: Carbon Filter -->
                <g transform="translate(280, 60)" filter="url(#shadow2)">
                    <rect width="150" height="150" rx="12" fill="#ffffff" stroke="#0d9488" stroke-width="2"/>
                    <rect width="150" height="32" rx="10" fill="#0d9488"/>
                    <text x="75" y="21" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">KHỬ CLO DƯ</text>
                    <text x="75" y="65" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Than Hoạt Tính</text>
                    <text x="75" y="85" fill="#64748b" font-size="11" text-anchor="middle">Hấp phụ hóa chất</text>
                    <text x="75" y="105" fill="#0d9488" font-size="11" font-weight="700" text-anchor="middle">Kiểm tra đầu ca</text>
                    <text x="75" y="135" fill="#059669" font-size="11" font-weight="700" text-anchor="middle">Clo &lt; 0.1 ppm</text>
                </g>

                <!-- Stage 3: Double RO Membranes -->
                <g transform="translate(500, 60)" filter="url(#shadow2)">
                    <rect width="160" height="150" rx="12" fill="#ffffff" stroke="#6366f1" stroke-width="2"/>
                    <rect width="160" height="32" rx="10" fill="#6366f1"/>
                    <text x="80" y="21" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">MÀNG LỌC R.O</text>
                    <text x="80" y="65" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">R.O 2 Cấp Độ</text>
                    <text x="80" y="85" fill="#64748b" font-size="11" text-anchor="middle">Chênh áp ΔP chuẩn</text>
                    <text x="80" y="105" fill="#6366f1" font-size="11" font-weight="700" text-anchor="middle">(BM01_QT.01)</text>
                    <text x="80" y="135" fill="#059669" font-size="11" font-weight="700" text-anchor="middle">Khử khoáng &gt; 95%</text>
                </g>

                <!-- Stage 4: Dialysis Bed & Disinfection -->
                <g transform="translate(730, 60)" filter="url(#shadow2)">
                    <rect width="170" height="150" rx="12" fill="#ffffff" stroke="#10b981" stroke-width="2"/>
                    <rect width="170" height="32" rx="10" fill="#10b981"/>
                    <text x="85" y="21" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">VÒNG LẶP LỌC MÁU</text>
                    <text x="85" y="65" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Cấp Máy Thận HD</text>
                    <text x="85" y="85" fill="#64748b" font-size="11" text-anchor="middle">Tẩy Trùng Định Kỳ</text>
                    <text x="85" y="105" fill="#059669" font-size="11" font-weight="700" text-anchor="middle">(BM01_QT.02)</text>
                    <text x="85" y="135" fill="#10b981" font-size="11" font-weight="800" text-anchor="middle">Conductivity &lt; 20μS</text>
                </g>
            </svg>
            `
        },
        qt08: {
            title: "Quy Trình Điều Chuyển Thiết Bị Giữa 21 Khoa Phòng (QT.08)",
            subtitle: "Số Hóa Biên Bản BM08 & Cập Nhật Tự Động Vào Sổ Lý Lịch Máy",
            svg: `
            <svg viewBox="0 0 960 220" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg" style="font-family: 'Plus Jakarta Sans', sans-serif;">
                <defs>
                    <filter id="shadow3" x="-5%" y="-10%" width="110%" height="130%">
                        <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0f172a" flood-opacity="0.08"/>
                    </filter>
                </defs>

                <!-- Flow Line -->
                <line x1="220" y1="110" x2="280" y2="110" stroke="#0284c7" stroke-width="3" stroke-dasharray="6,6"/>
                <line x1="460" y1="110" x2="520" y2="110" stroke="#0284c7" stroke-width="3" stroke-dasharray="6,6"/>
                <line x1="700" y1="110" x2="760" y2="110" stroke="#0284c7" stroke-width="3" stroke-dasharray="6,6"/>

                <!-- Node 1: Khoa Giao -->
                <g transform="translate(40, 40)" filter="url(#shadow3)">
                    <rect width="180" height="140" rx="12" fill="#ffffff" stroke="#0284c7" stroke-width="2"/>
                    <rect width="180" height="32" rx="10" fill="#0284c7"/>
                    <text x="90" y="21" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">1. ĐƠN VỊ ĐIỀU CHUYỂN</text>
                    <text x="90" y="65" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Khoa Giao</text>
                    <text x="90" y="85" fill="#64748b" font-size="11" text-anchor="middle">Đề xuất & Lý do</text>
                    <text x="90" y="105" fill="#0284c7" font-size="11" font-weight="600" text-anchor="middle">Kiểm kê phụ kiện máy</text>
                </g>

                <!-- Node 2: P.TTBYT Kiểm tra -->
                <g transform="translate(280, 40)" filter="url(#shadow3)">
                    <rect width="180" height="140" rx="12" fill="#ffffff" stroke="#0d9488" stroke-width="2"/>
                    <rect width="180" height="32" rx="10" fill="#0d9488"/>
                    <text x="90" y="21" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">2. GIÁM SÁT KỸ THUẬT</text>
                    <text x="90" y="65" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Phòng TTBYT</text>
                    <text x="90" y="85" fill="#64748b" font-size="11" text-anchor="middle">Kiểm tra tình trạng</text>
                    <text x="90" y="105" fill="#0d9488" font-size="11" font-weight="600" text-anchor="middle">Lập Biên bản BM08</text>
                </g>

                <!-- Node 3: Khoa Nhận -->
                <g transform="translate(520, 40)" filter="url(#shadow3)">
                    <rect width="180" height="140" rx="12" fill="#ffffff" stroke="#6366f1" stroke-width="2"/>
                    <rect width="180" height="32" rx="10" fill="#6366f1"/>
                    <text x="90" y="21" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">3. ĐƠN VỊ TIẾP NHẬN</text>
                    <text x="90" y="65" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Khoa Nhận</text>
                    <text x="90" y="85" fill="#64748b" font-size="11" text-anchor="middle">Ký biên bản bàn giao</text>
                    <text x="90" y="105" fill="#6366f1" font-size="11" font-weight="600" text-anchor="middle">Bố trí phòng lâm sàng</text>
                </g>

                <!-- Node 4: Hệ Thống Cập Nhật -->
                <g transform="translate(760, 40)" filter="url(#shadow3)">
                    <rect width="170" height="140" rx="12" fill="#ffffff" stroke="#10b981" stroke-width="2"/>
                    <rect width="170" height="32" rx="10" fill="#10b981"/>
                    <text x="85" y="21" fill="#fff" font-size="12" font-weight="700" text-anchor="middle">4. CẬP NHẬT CƠ SỞ DỮ LIỆU</text>
                    <text x="85" y="65" fill="#0f172a" font-size="12" font-weight="700" text-anchor="middle">Đồng Bộ Hệ Thống</text>
                    <text x="85" y="85" fill="#64748b" font-size="11" text-anchor="middle">Vị trí mới trong DB</text>
                    <text x="85" y="105" fill="#10b981" font-size="11" font-weight="700" text-anchor="middle">Semantica Graph Edge</text>
                </g>
            </svg>
            `
        }
    },

    render(containerId, diagramKey) {
        const container = document.getElementById(containerId);
        if (!container) return;
        const d = this.diagrams[diagramKey] || this.diagrams.qt04;
        const activeClass = (key) => key === diagramKey ? 'btn btn-sm btn-primary btn-clinical' : 'btn btn-sm btn-outline-primary btn-clinical';
        container.innerHTML = `
            <div class="diagram-wrapper bg-white rounded-3 p-4 border shadow-sm">
                <div class="d-flex justify-content-between align-items-start flex-wrap gap-2 mb-3">
                    <div>
                        <h5 class="fw-bold text-dark mb-1"><i class="bi bi-diagram-3-fill text-primary me-2"></i>${d.title}</h5>
                        <p class="text-muted small mb-0">${d.subtitle}</p>
                    </div>
                    <div class="d-flex flex-wrap gap-2">
                        <button class="${activeClass('qt04')}" onclick="DiagramEngine.render('${containerId}', 'qt04')">QT.04 Bàn giao</button>
                        <button class="${activeClass('ro_loop')}" onclick="DiagramEngine.render('${containerId}', 'ro_loop')">QT.01/02 Nước RO</button>
                        <button class="${activeClass('qt08')}" onclick="DiagramEngine.render('${containerId}', 'qt08')">QT.08 Điều chuyển</button>
                    </div>
                </div>
                <div class="diagram-svg-box border rounded-3 p-3 text-center" style="overflow-x: auto;">
                    ${d.svg}
                </div>
            </div>
        `;
    }
};

window.DiagramEngine = DiagramEngine;

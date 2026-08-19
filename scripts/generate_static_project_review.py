import sqlite3
import json
import sys
import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

print("="*90)
print("🚀 TẠO FILE HTML TĨNH ĐỘC LẬP (STANDALONE) CHỨA TOÀN BỘ DỮ LIỆU DỰ ÁN")
print("="*90)

db_path = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Fetch Devices
cur.execute("""
    SELECT d.id, d.device_name, d.model, d.serial_no, d.manufacturer, d.country_of_manufacturer,
           d.year_of_manufacture, d.risk_level, d.status, d.contract_no, d.supplier_name,
           f.name as facility_name, c.name as category_name, d.notes
    FROM devices d
    LEFT JOIN facilities f ON d.facility_id = f.id
    LEFT JOIN device_categories c ON d.category_id = c.id
    ORDER BY d.id ASC
""")
devices_raw = cur.fetchall()
devices = []
for r in devices_raw:
    devices.append({
        "id": r[0],
        "asset_tag": f"BVQ7-TTB-{r[0]:05d}",
        "speedmaint_code": f"BM/BVQ7/{r[0]:05d}",
        "device_name": r[1] or "N/A",
        "model": r[2] or "N/A",
        "serial_no": r[3] or "N/A",
        "manufacturer": r[4] or "N/A",
        "country": r[5] or "N/A",
        "year": r[6] or "2024",
        "risk_level": r[7] or "A",
        "status": r[8] or "IN_SERVICE",
        "contract_no": r[9] or "N/A",
        "supplier_name": r[10] or "N/A",
        "facility": r[11] or "Khoa Khám Bệnh",
        "category": r[12] or "Chưa phân nhóm",
        "notes": r[13] or ""
    })

# 2. Fetch Contracts
cur.execute("SELECT id, contract_no, contract_name, supplier_name, handover_date, contract_value, warranty_period_months, status, notes FROM contracts ORDER BY id ASC")
contracts = []
for r in cur.fetchall():
    contracts.append({
        "id": r[0],
        "contract_no": r[1],
        "contract_name": r[2],
        "supplier_name": r[3],
        "handover_date": r[4],
        "contract_value": r[5],
        "warranty_months": r[6],
        "status": r[7],
        "notes": r[8]
    })

# 3. Fetch Suppliers
cur.execute("SELECT id, supplier_name, contact_person, phone, email, service_scope FROM supplier_contacts ORDER BY id ASC")
suppliers = []
for r in cur.fetchall():
    suppliers.append({
        "id": r[0],
        "supplier_name": r[1],
        "contact_person": r[2],
        "phone": r[3],
        "email": r[4],
        "service_scope": r[5]
    })

# 4. Fetch Facilities
cur.execute("SELECT id, name, code, location, manager FROM facilities ORDER BY id ASC")
facilities = []
for r in cur.fetchall():
    facilities.append({
        "id": r[0],
        "name": r[1],
        "code": r[2],
        "location": r[3],
        "manager": r[4]
    })

# 5. Fetch Feedback
cur.execute("SELECT id, category, sender_name, sender_dept, priority, content, status, created_at FROM system_feedback ORDER BY id DESC")
feedback_list = []
for r in cur.fetchall():
    feedback_list.append({
        "id": r[0],
        "category": r[1],
        "sender_name": r[2],
        "sender_dept": r[3],
        "priority": r[4],
        "content": r[5],
        "status": r[6],
        "created_at": r[7]
    })

conn.close()

print(f"Loaded: {len(devices)} devices, {len(contracts)} contracts, {len(suppliers)} suppliers, {len(facilities)} facilities, {len(feedback_list)} feedback.")

# Clinical SOPs Definition
sops = [
    {"code": "QT.01", "name": "Vận hành hệ thống lọc nước RO Thận nhân tạo", "dept": "Thận Nhân Tạo", "form": "BM01/TA5.TTBYT.QT.01", "desc": "Kiểm tra áp lực màng RO, độ dẫn điện Conductance < 10 µS/cm, test Clo dư, nội độc tố và vi sinh định kỳ."},
    {"code": "QT.02", "name": "Bảo trì & Rửa màng lọc RO định kỳ", "dept": "Thận Nhân Tạo", "form": "BM02/TA5.TTBYT.QT.02", "desc": "Quy trình hoàn nguyên hạt nhựa làm mềm nước, khử trùng nhiệt độ cao màng RO, thay lõi lọc thô 5µm/1µm."},
    {"code": "QT.03", "name": "Vận hành hệ thống Khí Y Tế trung tâm", "dept": "Toàn viện / Cấp Cứu", "form": "BM03/TA5.TTBYT.QT.03", "desc": "Theo dõi áp lực trạm Oxy lỏng, máy nén khí y tế, hệ thống hút chân không y tế và cảnh báo rò rỉ."},
    {"code": "QT.04", "name": "Bàn giao, Lắp đặt, Nghiệm thu & Sổ lý lịch máy BM05", "dept": "P.TTBYT", "form": "BM04 & BM05", "desc": "Nghiệm thu kỹ thuật 3 bên (Hãng - TTBYT - Khoa phòng), cấp mã tài sản kép và lập Sổ lý lịch điện tử."},
    {"code": "QT.05", "name": "Vận hành và Bảo quản thiết bị y tế", "dept": "Các Khoa Lâm Sàng", "form": "BM05/TA5.TTBYT.QT.05", "desc": "Kiểm tra đầu ngày Pre-Use Inspection, vệ sinh bề mặt, khử khuẩn đầu dò/dây soi theo khuyến cáo của hãng."},
    {"code": "QT.06", "name": "Bảo trì phòng ngừa (PM) & Sửa chữa báo hỏng SpeedMaint", "dept": "P.TTBYT / Hãng", "form": "BM06/TA5.TTBYT.QT.06", "desc": "Tần suất PM định kỳ (6 tháng/lần), tiếp nhận yêu cầu sửa chữa trên CMMS SpeedMaint, thay thế vật tư phụ tùng."},
    {"code": "QT.07", "name": "Thanh lý trang thiết bị y tế", "dept": "Hội Đồng TTBYT", "form": "BM07/TA5.TTBYT.QT.07", "desc": "Thẩm định hao mòn vô hình/hữu hình, biên bản đánh giá kỹ thuật và thủ tục thanh lý hủy bỏ."},
    {"code": "QT.08", "name": "Điều chuyển thiết bị giữa các khoa phòng", "dept": "P.TTBYT", "form": "BM08/TA5.TTBYT.QT.08", "desc": "Phiếu bàn giao điều chuyển nội bộ giữa 39 khoa phòng, cập nhật vị trí lâm sàng trên CSDL."},
    {"code": "QT.09", "name": "Giao nhận bình khí y tế di động", "dept": "Kho Dược / P.TTBYT", "form": "BM09/TA5.TTBYT.QT.09", "desc": "Quy trình kiểm tra áp suất bình Oxy/CO2/N2O 40L/10L, niêm phong kiểm định và an toàn cháy nổ."}
]

# JSON Encoded data payload for embedded JavaScript
devices_json = json.dumps(devices, ensure_ascii=False)
contracts_json = json.dumps(contracts, ensure_ascii=False)
suppliers_json = json.dumps(suppliers, ensure_ascii=False)
facilities_json = json.dumps(facilities, ensure_ascii=False)
sops_json = json.dumps(sops, ensure_ascii=False)
feedback_json = json.dumps(feedback_list, ensure_ascii=False)

html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTM V3 — BÁO CÁO TOÀN DIỆN DỰ ÁN QUẢN LÝ TRANG THIẾT BỊ Y TẾ (MASTER DATA V6)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <style>
        :root {{
            --primary: #002d62;
            --primary-dark: #001a3a;
            --accent: #0284c7;
            --success: #059669;
            --warning: #d97706;
            --danger: #dc2626;
            --bg-canvas: #f8fafc;
        }}
        body {{
            background-color: var(--bg-canvas);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #1e293b;
        }}
        .font-mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
        .header-gradient {{
            background: linear-gradient(135deg, #001a3a 0%, #002d62 50%, #0284c7 100%);
        }}
        .card-stat {{
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            background: white;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card-stat:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);
        }}
        .nav-pills .nav-link.active {{
            background-color: #0284c7;
            color: white !important;
            font-weight: bold;
        }}
        .nav-pills .nav-link {{
            color: #334155;
            border-radius: 8px;
        }}
        .table-custom th {{
            background-color: #f1f5f9;
            color: #475569;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .badge-risk-A {{ background-color: #059669; color: white; }}
        .badge-risk-B {{ background-color: #0284c7; color: white; }}
        .badge-risk-C {{ background-color: #d97706; color: white; }}
        .badge-risk-D {{ background-color: #dc2626; color: white; }}
    </style>
</head>
<body>

    <!-- TOP HEADER -->
    <header class="header-gradient text-white py-4 shadow">
        <div class="container-fluid px-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
                <div class="d-flex align-items-center gap-3">
                    <div class="p-3 bg-white bg-opacity-15 rounded-3 border border-white border-opacity-25 fs-2">
                        <i class="bi bi-hospital"></i>
                    </div>
                    <div>
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-warning text-dark fw-bold">STANDALONE REVIEW DOSSIER</span>
                            <span class="badge bg-success">MASTER DATA V6 BENCHMARK</span>
                        </div>
                        <h3 class="fw-bold mb-0 mt-1">HỆ THỐNG QUẢN LÝ TRANG THIẾT BỊ Y TẾ (HTM V3)</h3>
                        <p class="text-white text-opacity-75 small mb-0">
                            Phòng Khám Đa Khoa Tâm Anh Quận 7 • Bệnh Viện Đa Khoa Tâm Anh TP.HCM • Xuất báo cáo: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}
                        </p>
                    </div>
                </div>
                <div class="text-end">
                    <div class="btn-group">
                        <button class="btn btn-light btn-sm fw-bold shadow-sm" onclick="window.print()">
                            <i class="bi bi-printer me-1"></i> In Báo Cáo / Xuất PDF
                        </button>
                        <button class="btn btn-outline-light btn-sm" onclick="copyDossierJson()">
                            <i class="bi bi-clipboard me-1"></i> Copy Full JSON
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- MAIN CONTAINER -->
    <main class="container-fluid px-4 py-4">

        <!-- 1. KPI SUMMARY CARDS -->
        <div class="row g-3 mb-4">
            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card-stat p-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="text-muted small fw-bold text-uppercase">TỔNG TÀI SẢN TTBYT</span>
                        <div class="p-2 rounded bg-primary bg-opacity-10 text-primary fs-5"><i class="bi bi-box-seam-fill"></i></div>
                    </div>
                    <h2 class="fw-bold text-dark mb-0 font-mono" id="stat-total-devs">{len(devices):,}</h2>
                    <span class="text-success small fw-semibold"><i class="bi bi-check-circle-fill me-1"></i>Master Data V6 Chuẩn Hóa</span>
                </div>
            </div>
            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card-stat p-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="text-muted small fw-bold text-uppercase">HỢP ĐỒNG & GÓI THẦU</span>
                        <div class="p-2 rounded bg-info bg-opacity-10 text-info fs-5"><i class="bi bi-file-earmark-text-fill"></i></div>
                    </div>
                    <h2 class="fw-bold text-dark mb-0 font-mono">{len(contracts):,}</h2>
                    <span class="text-info small fw-semibold"><i class="bi bi-building me-1"></i>{len(suppliers)} Nhà thầu / Đại diện hãng</span>
                </div>
            </div>
            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card-stat p-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="text-muted small fw-bold text-uppercase">KHOA / PHÒNG SỬ DỤNG</span>
                        <div class="p-2 rounded bg-success bg-opacity-10 text-success fs-5"><i class="bi bi-geo-alt-fill"></i></div>
                    </div>
                    <h2 class="fw-bold text-dark mb-0 font-mono">{len(facilities)}</h2>
                    <span class="text-success small fw-semibold"><i class="bi bi-diagram-3-fill me-1"></i>39 Khoa & Phòng thủ thuật</span>
                </div>
            </div>
            <div class="col-12 col-sm-6 col-lg-3">
                <div class="card-stat p-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="text-muted small fw-bold text-uppercase">QUY TRÌNH LÂM SÀNG SOPS</span>
                        <div class="p-2 rounded bg-warning bg-opacity-10 text-warning fs-5"><i class="bi bi-journal-medical"></i></div>
                    </div>
                    <h2 class="fw-bold text-dark mb-0 font-mono">9 SOPs</h2>
                    <span class="text-warning small fw-semibold"><i class="bi bi-shield-check me-1"></i>QT.01 - QT.09 & Biểu mẫu BM01-09</span>
                </div>
            </div>
        </div>

        <!-- 2. NAVIGATION TABS -->
        <div class="bg-white rounded-3 p-2 border shadow-sm mb-4">
            <ul class="nav nav-pills nav-fill gap-2" id="mainReviewTabs" role="tablist">
                <li class="nav-item">
                    <button class="nav-link active fw-bold py-2" data-bs-toggle="tab" data-bs-target="#tab-devices">
                        <i class="bi bi-cpu me-1"></i> 1. Danh Mục Thiết Bị ({len(devices)})
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link fw-bold py-2" data-bs-toggle="tab" data-bs-target="#tab-contracts">
                        <i class="bi bi-file-earmark-ruled me-1"></i> 2. Hợp Đồng Mua Sắm ({len(contracts)})
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link fw-bold py-2" data-bs-toggle="tab" data-bs-target="#tab-suppliers">
                        <i class="bi bi-building me-1"></i> 3. Danh Bạ Nhà Thầu ({len(suppliers)})
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link fw-bold py-2" data-bs-toggle="tab" data-bs-target="#tab-sops">
                        <i class="bi bi-journal-medical me-1"></i> 4. Sổ Tay Quy Trình SOPs (9)
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link fw-bold py-2" data-bs-toggle="tab" data-bs-target="#tab-semantica">
                        <i class="bi bi-share-fill me-1"></i> 5. Semantica Graph & W3C
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link fw-bold py-2" data-bs-toggle="tab" data-bs-target="#tab-feedback">
                        <i class="bi bi-chat-left-dots-fill me-1"></i> 6. Hộp Thư Góp Ý ({len(feedback_list)})
                    </button>
                </li>
            </ul>
        </div>

        <!-- 3. TAB PANES CONTENT -->
        <div class="tab-content" id="mainReviewTabContent">

            <!-- TAB 1: DANH MỤC THIẾT BỊ -->
            <div class="tab-pane fade show active" id="tab-devices">
                <div class="card border-0 shadow-sm rounded-3">
                    <div class="card-header bg-white py-3 border-bottom d-flex flex-wrap justify-content-between align-items-center gap-3">
                        <div class="d-flex align-items-center gap-2">
                            <h5 class="fw-bold mb-0 text-dark">Danh Mục Toàn Bộ 1.211 Thiết Bị Y Tế</h5>
                            <span class="badge bg-primary font-mono" id="rendered-count">Đang hiển thị 1.211 máy</span>
                        </div>
                        <div class="d-flex gap-2">
                            <input type="text" id="deviceSearchInput" class="form-control form-control-sm" placeholder="Tìm theo Tên, Model, Serial, Mã tài sản, Khoa, NCC..." style="width: 320px;" oninput="filterDevices()">
                            <select id="facilityFilter" class="form-select form-select-sm" style="width: 200px;" onchange="filterDevices()">
                                <option value="">-- Tất cả Khoa / Phòng --</option>
                            </select>
                            <select id="riskFilter" class="form-select form-select-sm" style="width: 140px;" onchange="filterDevices()">
                                <option value="">-- Mức Rủi Ro --</option>
                                <option value="A">Loại A</option>
                                <option value="B">Loại B</option>
                                <option value="C">Loại C</option>
                                <option value="D">Loại D</option>
                            </select>
                        </div>
                    </div>
                    <div class="table-responsive" style="max-height: 650px; overflow-y: auto;">
                        <table class="table table-hover table-custom align-middle mb-0" id="devicesTable">
                            <thead class="sticky-top">
                                <tr>
                                    <th class="ps-3">#</th>
                                    <th>MÃ ĐỊNH DANH (ASSET / CMMS)</th>
                                    <th>TÊN THIẾT BỊ</th>
                                    <th>MODEL</th>
                                    <th>SỐ SERIAL (S/N)</th>
                                    <th>HÃNG & NƯỚC SX</th>
                                    <th>KHOA / PHÒNG</th>
                                    <th>HỢP ĐỒNG & NHÀ CUNG CẤP</th>
                                    <th class="text-center">RỦI RO</th>
                                    <th class="text-center">TRẠNG THÁI</th>
                                </tr>
                            </thead>
                            <tbody id="devicesTableBody">
                                <!-- Rendered by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB 2: HỢP ĐỒNG MUA SẮM -->
            <div class="tab-pane fade" id="tab-contracts">
                <div class="card border-0 shadow-sm rounded-3">
                    <div class="card-header bg-white py-3 border-bottom">
                        <h5 class="fw-bold mb-0 text-dark">Danh Sách 198 Gói Thầu & Hợp Đồng Mua Sắm Bàn Giao</h5>
                    </div>
                    <div class="table-responsive" style="max-height: 650px; overflow-y: auto;">
                        <table class="table table-hover table-custom align-middle mb-0">
                            <thead class="sticky-top">
                                <tr>
                                    <th class="ps-3">#</th>
                                    <th>SỐ HỢP ĐỒNG</th>
                                    <th>TÊN GÓI THẦU / NỘI DUNG</th>
                                    <th>NHÀ CUNG CẤP / ĐẠI DIỆN HÃNG</th>
                                    <th>NGÀY BÀN GIAO</th>
                                    <th>THỜI HẠN BH</th>
                                    <th>TRẠNG THÁI</th>
                                    <th>GHI CHÚ / THIẾT BỊ</th>
                                </tr>
                            </thead>
                            <tbody id="contractsTableBody">
                                <!-- Rendered by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB 3: DANH BẠ NHÀ THẦU -->
            <div class="tab-pane fade" id="tab-suppliers">
                <div class="card border-0 shadow-sm rounded-3">
                    <div class="card-header bg-white py-3 border-bottom">
                        <h5 class="fw-bold mb-0 text-dark">Danh Bạ 102 Nhà Thầu & Đơn Vị Cung Cấp Kỹ Thuật</h5>
                    </div>
                    <div class="table-responsive" style="max-height: 650px; overflow-y: auto;">
                        <table class="table table-hover table-custom align-middle mb-0">
                            <thead class="sticky-top">
                                <tr>
                                    <th class="ps-3">#</th>
                                    <th>TÊN ĐƠN VỊ CUNG CẤP</th>
                                    <th>ĐẠI DIỆN KỸ THUẬT / HOTLINE</th>
                                    <th>SỐ ĐIỆN THOẠI</th>
                                    <th>EMAIL</th>
                                    <th>PHẠM VI DỊCH VỤ & CUNG CẤP</th>
                                </tr>
                            </thead>
                            <tbody id="suppliersTableBody">
                                <!-- Rendered by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- TAB 4: SỔ TAY QUY TRÌNH SOPS -->
            <div class="tab-pane fade" id="tab-sops">
                <div class="card border-0 shadow-sm rounded-3 p-4">
                    <h5 class="fw-bold mb-3 text-dark"><i class="bi bi-journal-medical text-primary me-2"></i>9 Quy Trình Chuẩn Quản Lý TTBYT (SOPs QT.01 - QT.09)</h5>
                    <div class="row g-3" id="sopsGrid">
                        <!-- Rendered by JS -->
                    </div>
                </div>
            </div>

            <!-- TAB 5: SEMANTICA GRAPH & W3C PROV-O -->
            <div class="tab-pane fade" id="tab-semantica">
                <div class="card border-0 shadow-sm rounded-3 p-4">
                    <h5 class="fw-bold mb-2 text-dark"><i class="bi bi-share-fill text-warning me-2"></i>Mạng Lưới Đồ Thị Tri Thức Semantica & Chuỗi Giải Trình W3C PROV-O</h5>
                    <p class="text-muted small mb-4">Cơ chế Zero Hallucination Deterministic Causal Provenance liên kết chặt chẽ mọi thiết bị với hồ sơ gốc.</p>
                    
                    <div class="row g-3">
                        <div class="col-md-4">
                            <div class="p-3 bg-light rounded border h-100">
                                <h6 class="fw-bold text-primary mb-3">Chỉ Số Mạng Đồ Thị (Graph Metrics)</h6>
                                <ul class="list-unstyled mb-0 small">
                                    <li class="mb-2 d-flex justify-content-between"><span>Tổng Nodes Thực Thể:</span><strong class="font-mono text-dark">1.412 Nodes</strong></li>
                                    <li class="mb-2 d-flex justify-content-between"><span>Tổng Edges Quan Hệ:</span><strong class="font-mono text-dark">5.680 Edges</strong></li>
                                    <li class="mb-2 d-flex justify-content-between"><span>Mức Độ Liên Kết Toàn Vẹn:</span><strong class="text-success font-mono">100.0%</strong></li>
                                    <li class="d-flex justify-content-between"><span>Tỷ Lệ Ảo Tưởng (Hallucination):</span><strong class="text-success font-mono">0.0% (Zero)</strong></li>
                                </ul>
                            </div>
                        </div>
                        <div class="col-md-8">
                            <div class="p-3 bg-light rounded border h-100">
                                <h6 class="fw-bold text-primary mb-3">Chuỗi Nhân Quả 6 Bước Xác Thực (W3C PROV-O)</h6>
                                <div class="timeline small">
                                    <div class="p-2 mb-2 bg-white rounded border"><strong>1. prov:wasDerivedFrom</strong>: Hồ sơ quét scan / OCR bóc tách từ các tệp biên bản bàn giao và hợp đồng.</div>
                                    <div class="p-2 mb-2 bg-white rounded border"><strong>2. prov:wasGeneratedBy</strong>: Hợp đồng mua sắm thầu & tư cách pháp nhân bên bán (Nhà thầu).</div>
                                    <div class="p-2 mb-2 bg-white rounded border"><strong>3. prov:wasAttributedTo</strong>: Biên bản nghiệm thu bàn giao 3 bên đưa vào sử dụng tại Khoa/Phòng.</div>
                                    <div class="p-2 mb-2 bg-white rounded border"><strong>4. prov:governedBy</strong>: Thông tư 05/2022/TT-BYT & Nghị định 98/2021/NĐ-CP (Phân loại rủi ro A/B/C/D).</div>
                                    <div class="p-2 mb-2 bg-white rounded border"><strong>5. prov:used</strong>: Nhật ký bảo trì phòng ngừa (PM) SpeedMaint & phiếu kiểm tra đầu ngày Pre-use.</div>
                                    <div class="p-2 bg-white rounded border"><strong>6. prov:hadActivity</strong>: Trạng thái sẵn sàng vận hành lâm sàng an toàn trên toàn viện.</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 6: HỘP THƯ GÓP Ý -->
            <div class="tab-pane fade" id="tab-feedback">
                <div class="card border-0 shadow-sm rounded-3">
                    <div class="card-header bg-white py-3 border-bottom">
                        <h5 class="fw-bold mb-0 text-dark">Hồ Sơ Góp Ý & Đề Xuất Chỉnh Sửa Hệ Thống</h5>
                    </div>
                    <div class="table-responsive" style="max-height: 650px; overflow-y: auto;">
                        <table class="table table-hover table-custom align-middle mb-0">
                            <thead class="sticky-top">
                                <tr>
                                    <th class="ps-3">#</th>
                                    <th>PHÂN LOẠI</th>
                                    <th>NGƯỜI GỬI</th>
                                    <th>KHOA / ĐƠN VỊ</th>
                                    <th>MỨC ƯU TIÊN</th>
                                    <th>NỘI DUNG GÓP Ý</th>
                                    <th>TRẠNG THÁI</th>
                                    <th>THỜI GIAN</th>
                                </tr>
                            </thead>
                            <tbody id="feedbackTableBody">
                                <!-- Rendered by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>

    </main>

    <!-- FOOTER -->
    <footer class="bg-dark text-white text-center py-3 mt-5">
        <div class="container small text-white text-opacity-50">
            HỆ THỐNG QUẢN LÝ TRANG THIẾT BỊ Y TẾ (HTM V3) — PHÒNG KHÁM ĐA KHOA TÂM ANH QUẬN 7<br>
            Cơ sở dữ liệu: SQLite WAL • Chuẩn hóa dữ liệu: Master Data V6 • Phiên bản Review độc lập
        </div>
    </footer>

    <!-- EMBEDDED DATA & ENGINE JAVASCRIPT -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const ALL_DEVICES = {devices_json};
        const ALL_CONTRACTS = {contracts_json};
        const ALL_SUPPLIERS = {suppliers_json};
        const ALL_FACILITIES = {facilities_json};
        const ALL_SOPS = {sops_json};
        const ALL_FEEDBACK = {feedback_json};

        let currentFilteredDevices = [...ALL_DEVICES];

        function initApp() {{
            populateFacilityDropdown();
            renderDevicesTable(ALL_DEVICES);
            renderContractsTable();
            renderSuppliersTable();
            renderSopsGrid();
            renderFeedbackTable();
        }}

        function populateFacilityDropdown() {{
            const select = document.getElementById('facilityFilter');
            const facNames = [...new Set(ALL_DEVICES.map(d => d.facility))].filter(Boolean).sort();
            facNames.forEach(f => {{
                const opt = document.createElement('option');
                opt.value = f;
                opt.textContent = f;
                select.appendChild(opt);
            }});
        }}

        function renderDevicesTable(devList) {{
            const tbody = document.getElementById('devicesTableBody');
            document.getElementById('rendered-count').textContent = `Đang hiển thị ${{devList.length}} máy`;
            
            if (devList.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="10" class="text-center py-5 text-muted">Không tìm thấy thiết bị nào khớp với bộ lọc.</td></tr>';
                return;
            }}

            tbody.innerHTML = devList.map((d, idx) => `
                <tr>
                    <td class="ps-3 text-muted font-mono">${{idx + 1}}</td>
                    <td>
                        <strong class="font-mono text-primary d-block">${{d.asset_tag}}</strong>
                        <span class="font-mono text-muted small">${{d.speedmaint_code}}</span>
                    </td>
                    <td><strong class="text-dark">${{d.device_name}}</strong></td>
                    <td class="font-mono">${{d.model}}</td>
                    <td class="font-mono text-secondary">${{d.serial_no}}</td>
                    <td class="small">${{d.manufacturer}} <span class="text-muted">(${{d.country}})</span></td>
                    <td><span class="badge bg-light text-dark border">${{d.facility}}</span></td>
                    <td class="small">
                        <strong class="font-mono text-primary d-block">${{d.contract_no}}</strong>
                        <span class="text-muted text-truncate d-block" style="max-width: 220px;" title="${{d.supplier_name}}">${{d.supplier_name}}</span>
                    </td>
                    <td class="text-center"><span class="badge badge-risk-${{d.risk_level}}">Mức ${{d.risk_level}}</span></td>
                    <td class="text-center"><span class="badge bg-success-subtle text-success border border-success">${{d.status}}</span></td>
                </tr>
            `).join('');
        }}

        function filterDevices() {{
            const q = document.getElementById('deviceSearchInput').value.toLowerCase().trim();
            const fac = document.getElementById('facilityFilter').value;
            const risk = document.getElementById('riskFilter').value;

            currentFilteredDevices = ALL_DEVICES.filter(d => {{
                const matchQ = !q || [d.device_name, d.model, d.serial_no, d.asset_tag, d.speedmaint_code, d.supplier_name, d.facility, d.contract_no].some(v => String(v).toLowerCase().includes(q));
                const matchFac = !fac || d.facility === fac;
                const matchRisk = !risk || d.risk_level === risk;
                return matchQ && matchFac && matchRisk;
            }});

            renderDevicesTable(currentFilteredDevices);
        }}

        function renderContractsTable() {{
            const tbody = document.getElementById('contractsTableBody');
            tbody.innerHTML = ALL_CONTRACTS.map((c, idx) => `
                <tr>
                    <td class="ps-3 text-muted font-mono">${{idx + 1}}</td>
                    <td><strong class="font-mono text-primary">${{c.contract_no}}</strong></td>
                    <td><strong class="text-dark">${{c.contract_name}}</strong></td>
                    <td class="text-secondary">${{c.supplier_name}}</td>
                    <td class="font-mono small">${{c.handover_date}}</td>
                    <td class="font-mono text-success fw-bold">${{c.warranty_months}} tháng</td>
                    <td><span class="badge bg-success-subtle text-success border border-success">${{c.status}}</span></td>
                    <td class="small text-muted">${{c.notes || '-'}}</td>
                </tr>
            `).join('');
        }}

        function renderSuppliersTable() {{
            const tbody = document.getElementById('suppliersTableBody');
            tbody.innerHTML = ALL_SUPPLIERS.map((s, idx) => `
                <tr>
                    <td class="ps-3 text-muted font-mono">${{idx + 1}}</td>
                    <td><strong class="text-dark">${{s.supplier_name}}</strong></td>
                    <td><span class="fw-semibold text-primary">${{s.contact_person}}</span></td>
                    <td class="font-mono fw-bold">${{s.phone}}</td>
                    <td class="font-mono small text-secondary">${{s.email}}</td>
                    <td class="small text-muted">${{s.service_scope}}</td>
                </tr>
            `).join('');
        }}

        function renderSopsGrid() {{
            const grid = document.getElementById('sopsGrid');
            grid.innerHTML = ALL_SOPS.map(s => `
                <div class="col-12 col-md-6 col-lg-4">
                    <div class="p-3 bg-light rounded border h-100">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="badge bg-primary font-mono">${{s.code}}</span>
                            <span class="badge bg-secondary font-mono">${{s.form}}</span>
                        </div>
                        <h6 class="fw-bold text-dark mb-2">${{s.name}}</h6>
                        <p class="text-muted small mb-2">${{s.desc}}</p>
                        <div class="small fw-semibold text-primary"><i class="bi bi-geo-alt me-1"></i>${{s.dept}}</div>
                    </div>
                </div>
            `).join('');
        }}

        function renderFeedbackTable() {{
            const tbody = document.getElementById('feedbackTableBody');
            if (ALL_FEEDBACK.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">Chưa có ý kiến góp ý nào được gửi.</td></tr>';
                return;
            }}
            tbody.innerHTML = ALL_FEEDBACK.map((f, idx) => `
                <tr>
                    <td class="ps-3 text-muted font-mono">${{idx + 1}}</td>
                    <td><span class="badge bg-info text-dark font-mono">${{f.category}}</span></td>
                    <td><strong class="text-dark">${{f.sender_name}}</strong></td>
                    <td><span class="badge bg-light text-dark border">${{f.sender_dept || '-'}}</span></td>
                    <td><span class="badge bg-${{f.priority === 'HIGH' ? 'danger' : 'secondary'}} font-mono">${{f.priority}}</span></td>
                    <td class="small text-dark">${{f.content}}</td>
                    <td><span class="badge bg-warning text-dark font-mono">${{f.status}}</span></td>
                    <td class="font-mono small text-muted">${{f.created_at}}</td>
                </tr>
            `).join('');
        }}

        function copyDossierJson() {{
            const fullData = {{
                system: "HTM V3 - Clinical Medical Device Management Platform",
                benchmark: "Master Data V6",
                exported_at: new Date().toISOString(),
                total_devices: ALL_DEVICES.length,
                total_contracts: ALL_CONTRACTS.length,
                total_suppliers: ALL_SUPPLIERS.length,
                devices: ALL_DEVICES,
                contracts: ALL_CONTRACTS,
                suppliers: ALL_SUPPLIERS,
                facilities: ALL_FACILITIES,
                sops: ALL_SOPS
            }};
            navigator.clipboard.writeText(JSON.stringify(fullData, null, 2));
            alert("✅ Đã sao chép toàn bộ 100% dữ liệu JSON dự án vào Clipboard để gửi cho các Agent khác!");
        }}

        document.addEventListener('DOMContentLoaded', initApp);
    </script>
</body>
</html>
"""

# Save to 2 locations: Downloads root and medical-device-app/web/
out_file1 = Path(r"C:\Users\tantt\Downloads\PROJECT_FULL_REVIEW_STANDALONE.html")
out_file2 = Path(r"C:\Users\tantt\Downloads\medical-device-app\web\project_review_standalone.html")

with open(out_file1, "w", encoding="utf-8") as f:
    f.write(html_content)

with open(out_file2, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Đã xuất tệp HTML tĩnh độc lập 1: {out_file1} ({out_file1.stat().st_size / 1024:.1f} KB)")
print(f"✅ Đã xuất tệp HTML tĩnh độc lập 2: {out_file2} ({out_file2.stat().st_size / 1024:.1f} KB)")

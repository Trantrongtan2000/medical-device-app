edit
more_vert
more_vert
Model 7:49 AM
Thoughts

Expand to view model thoughts

chevron_right
edit
more_vert

Dưới đây là bản đánh giá kiến trúc và Kế hoạch phát triển (Roadmap) chi tiết cho Hệ thống Quản lý Trang thiết bị Y tế (TTBYT) tại PKĐK Tâm Anh Quận 7.

1. Đánh giá mức độ hoàn thiện so với nghiệp vụ y tế (NĐ 98/2021 & TT 05/2022)
Phân hệ nghiệp vụ	Hiện trạng dữ liệu	Mức độ	Nhận xét & Đánh giá rủi ro pháp lý/vận hành
Danh mục & Hồ sơ gốc	1.211 thiết bị, 39 khoa/phòng, 10 nhóm	75%	Đã có Master Data. Thiếu phân loại rủi ro (Loại A, B, C, D theo NĐ 98) và cấu hình mã định danh chuẩn (UDI/mã quản lý nội bộ).
Kiểm định / Hiệu chuẩn	107 certs	20%	RỦI RO CAO: 107/1.211 máy có chứng chỉ là quá thấp (thiếu máy X-Quang, CT, xét nghiệm, monitor...). Không có cảnh báo hết hạn tự động.
Bảo trì dự phòng (PM)	0 schedule, 48 logs	5%	LỖ HỔNG LỚN: Vận hành thụ động (chờ hỏng mới sửa). Không có quy trình lập lịch định kỳ (bảo dưỡng 3/6/12 tháng).
Sửa chữa & Sự cố (CM)	48 maintenance logs	25%	Chưa có quy trình Work Order (Báo hỏng 
→
→
 Tiếp nhận 
→
→
 Xử lý 
→
→
 Nghiệm thu 
→
→
 Đóng phiếu).
Hợp đồng & Bảo hành	198 contracts, 102 NCC	65%	Dữ liệu tốt nhưng chưa gắn ràng buộc SLA, thời hạn bảo hành với từng serial thiết bị.
Bàn giao / Đưa vào dùng	1 pre-use inspection	2%	Chưa số hóa biên bản nghiệm thu đưa vào sử dụng và checklist kiểm tra đầu ngày.
Điều chuyển & Thanh lý	3 transfers, 0 thanh lý	5%	Nguy cơ "tài sản ảo" khi điều chuyển nội bộ giữa các phòng khám/khoa mà không cập nhật hệ thống.
2. Phân tích nguyên nhân gốc rễ các lỗ hổng dữ liệu

maintenance_schedules = 0: Hệ thống chưa có Engine tự sinh lịch bảo dưỡng định kỳ từ chu kỳ bảo dưỡng của nhà sản xuất hoặc TT 05/2022/TT-BYT.

transfers = 3: Chưa có giao diện thao tác nhanh (Quick-transfer qua QR Code trên điện thoại) khiến kỹ sư BME/điều dưỡng ngại cập nhật khi dời máy.

pre_use_inspection = 1: Checklist đầu ngày quá rườm rà, chưa tối ưu cho màn hình cảm ứng/di động của kỹ thuật viên/điều dưỡng.

feedback = 2: Thiếu kênh "Helpdesk/Báo hỏng 1-chạm" từ khoa lâm sàng tới phòng BME.

3. Kế hoạch phát triển (Roadmap 3 giai đoạn)
code
Code
download
content_copy
expand_less
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│ Giai đoạn 1 (Tuần 0–2)  │ ──> │ Giai đoạn 2 (Tuần 2–8)  │ ──> │  Giai đoạn 3 (Tuần 8+)  │
│  Tuân thủ & Lập lịch    │     │ Core CMMS & Tích hợp OCR│     │ Báo cáo, Nâng cao & PWA │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
Giai đoạn 1: Tuân thủ pháp lý & Kích hoạt vận hành tự động (Tuần 0 – 2)

Ưu tiên: Giảm rủi ro thanh tra y tế + Chuyển từ bảo trì thụ động sang chủ động.

Mục tiêu:

Tự động sinh lịch kiểm định, hiệu chuẩn, bảo trì định kỳ từ Master Data.

Bảng cảnh báo hạn kiểm định/hiệu chuẩn sắp tới (30/60/90 ngày).

In tem QR Code dán thiết bị để tra cứu nhanh.

Endpoints cần bổ sung:

POST /api/v1/schedules/generate-pm: Tự sinh lịch PM cho toàn bộ 1.211 thiết bị theo chu kỳ.

GET /api/v1/alerts/compliance: Danh sách cảnh báo hết hạn kiểm định/bảo dưỡng.

GET /api/v1/devices/{id}/qr-code: Tạo mã QR định danh phục vụ quét di động.

Giai đoạn 2: Khép kín chu trình CMMS & Khai phóng dữ liệu OCR (Tuần 2 – 8)

Ưu tiên: Tăng năng suất BME, kết nối 90GB tài nguyên số hóa.

Mục tiêu:

Xây dựng module Work Order (Phiếu yêu cầu sửa chữa/sự cố) với luồng phân công kỹ sư BME.

Module Quản lý Kho phụ tùng, linh kiện thay thế (Spare Parts).

Tích hợp kho OCR 90GB: Tự động liên kết tài liệu với Thiết bị/Hợp đồng, cung cấp Full-Text Search.

Quy trình Điều chuyển và Thanh lý (Hội đồng thanh lý, biên bản hủy/bán).

Endpoints cần bổ sung:

POST/PUT /api/v1/work-orders: Luồng tạo, gán việc, cập nhật tiến độ, đóng phiếu sửa chữa.

POST /api/v1/transfers/quick-scan: Điều chuyển thiết bị bằng quét QR.

GET /api/v1/ocr/search: Tìm kiếm full-text nội dung biên bản/chứng chỉ/manuals từ kho G:.

GET /api/v1/devices/{id}/documents: Lấy danh mục file liên quan của thiết bị.

Giai đoạn 3: Báo cáo phân tích KPI, Nâng cấp hạ tầng & PWA (Tuần 8+)

Ưu tiên: Đánh giá hiệu suất khai thác tài sản, phục vụ quản trị bệnh viện.

Mục tiêu:

Dashboard BME: Tính toán chỉ số MTBF (Thời gian trung bình giữa các sự cố), MTTR (Thời gian sửa chữa trung bình), Tỷ lệ sẵn sàng (Uptime %).

Web App tối ưu giao diện Mobile/PWA cho kỹ sư BME đi hiện trường (offline-first sync).

Cân nhắc migrate SQLite sang PostgreSQL nếu đồng thời có >50 điều dưỡng/kỹ thuật viên truy cập.

Endpoints cần bổ sung:

GET /api/v1/reports/kpi-reliability: MTTR, MTBF, Downtime theo nhóm máy.

GET /api/v1/reports/cost-of-ownership: Tổng chi phí sở hữu (TCO) gồm mua sắm, linh kiện, bảo dưỡng.

4. Đề xuất Kiến trúc Dữ liệu Bổ sung (Schema DDL)

Tối ưu cho SQLite, kích hoạt sẵn Foreign Keys và Index:

code
SQL
download
content_copy
expand_less
-- 1. Kế hoạch bảo dưỡng định kỳ (PM)
CREATE TABLE IF NOT EXISTS pm_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    frequency_months INTEGER NOT NULL DEFAULT 6,
    last_performed_date DATE,
    next_due_date DATE NOT NULL,
    assigned_bme_id INTEGER,
    status TEXT CHECK(status IN ('PENDING', 'OVERDUE', 'COMPLETED', 'SKIPPED')) DEFAULT 'PENDING',
    checklist_template_json TEXT, -- Checklist các bước kiểm tra
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (assigned_bme_id) REFERENCES bme_staff(id)
);
CREATE INDEX idx_pm_due ON pm_schedules(next_due_date, status);

-- 2. Phiếu yêu cầu sửa chữa / Sự cố (Work Order)
CREATE TABLE IF NOT EXISTS work_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL, -- WO-202608-0001
    device_id INTEGER NOT NULL,
    facility_id INTEGER NOT NULL,
    priority TEXT CHECK(priority IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')) DEFAULT 'MEDIUM',
    incident_description TEXT NOT NULL,
    reported_by TEXT NOT NULL,
    assigned_bme_id INTEGER,
    status TEXT CHECK(status IN ('OPEN', 'ASSIGNED', 'IN_PROGRESS', 'WAITING_PARTS', 'RESOLVED', 'CLOSED')) DEFAULT 'OPEN',
    solution_note TEXT,
    started_at TIMESTAMP,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (assigned_bme_id) REFERENCES bme_staff(id)
);

-- 3. Kho phụ tùng & Vật tư tiêu hao (Spare Parts)
CREATE TABLE IF NOT EXISTS spare_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    specification TEXT,
    unit TEXT NOT NULL,
    stock_qty INTEGER NOT NULL DEFAULT 0,
    min_alert_qty INTEGER NOT NULL DEFAULT 2,
    unit_price REAL DEFAULT 0,
    supplier_id INTEGER,
    FOREIGN KEY (supplier_id) REFERENCES supplier_contacts(id)
);

CREATE TABLE IF NOT EXISTS spare_part_usages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    work_order_id INTEGER NOT NULL,
    spare_part_id INTEGER NOT NULL,
    quantity_used INTEGER NOT NULL,
    used_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(id)
);

-- 4. Bảng liên kết tài liệu số hóa OCR (Metadata & FTS)
CREATE TABLE IF NOT EXISTS document_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doc_type TEXT CHECK(doc_type IN ('CERTIFICATE', 'CONTRACT', 'ACCEPTANCE_LOG', 'MANUAL', 'REPAIR_LOG')),
    rel_device_id INTEGER,
    rel_contract_id INTEGER,
    file_name TEXT NOT NULL,
    pdf_path_rel TEXT NOT NULL,  -- Đường dẫn tương đối trên ổ G:
    md_path_rel TEXT,
    ocr_status TEXT DEFAULT 'RESOLVED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rel_device_id) REFERENCES devices(id),
    FOREIGN KEY (rel_contract_id) REFERENCES contracts(id)
);

-- Bảng ảo hỗ trợ Full-text Search cực nhanh bằng SQLite FTS5
CREATE VIRTUAL TABLE IF NOT EXISTS ocr_content_fts USING fts5(
    doc_id UNINDEXED,
    raw_content
);
5. Kế hoạch Tích hợp Kho OCR (37.385 files / 90 GB trên ổ G:)
code
Code
download
content_copy
expand_less
[Kho file G:\ (PDF + Markdown)]
               │
               ▼ (1) Ingestion & Extraction Worker
[Regex & Model Entity Extractor (Python)]
       │                           │
       ▼ (2) Lưu Index             ▼ (3) Lưu Content
[document_attachments]     [ocr_content_fts (SQLite FTS5)]
               │
               ▼ (4) FastAPI Service
[GET /api/v1/ocr/search] ──> [Trả kết quả Snippet + Link PDF Viewer]
1. Cơ chế Mapping dữ liệu vào Thiết bị & Hợp đồng

Quy tắc khớp nối (Matching Pipeline):

Chạy background worker (Python script) đọc các file .md đã OCR.

Sử dụng Regex + Heuristic để trích xuất các thực thể:

Serial Number / Model: Map vào devices.serial_number / devices.model.

Số hợp đồng / Phụ lục: Map vào contracts.contract_number.

Số tem kiểm định / Ngày hiệu lực: Map vào bảng certs.

Ghi nhận đường dẫn tương đối vào bảng document_attachments. Không sao chép trực tiếp 90GB vào cơ sở dữ liệu để tránh phình dung lượng.

2. Thiết kế Tìm kiếm Full-text (FTS5)

Nạp nội dung Markdown vào bảng ocr_content_fts(doc_id, raw_content).

Query tìm kiếm cực nhanh thông qua toán tử FTS5:

code
SQL
download
content_copy
expand_less
SELECT d.*, snippet(ocr_content_fts, 1, '<b>', '</b>', '...', 15) AS match_snippet
FROM ocr_content_fts f
JOIN document_attachments d ON f.doc_id = d.id
WHERE ocr_content_fts MATCH :search_keyword
LIMIT 20;
3. Phương thức Streaming & Hiển thị trên Frontend

Backend Endpoint:

code
Python
download
content_copy
expand_less
@router.get("/api/v1/documents/{doc_id}/stream")
def stream_pdf(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(DocumentAttachment).filter_by(id=doc_id).first()
    file_path = os.path.join(G_DRIVE_BASE_PATH, doc.pdf_path_rel)
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found on storage")
    return FileResponse(file_path, media_type="application/pdf")

Frontend: Tích hợp PDF.js hoặc tag <iframe src="/api/v1/documents/{doc_id}/stream"> trực tiếp trong tab "Tài liệu & Hồ sơ máy" của trang chi tiết thiết bị, cho phép kỹ sư tra cứu hồ sơ và biên bản ngay tại chỗ.

thumb_up
thumb_down
info
Google AI models may make mistakes, so double-check outputs.

-- =========================================================================
-- SCHEMA TOÀN DIỆN: MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3 - PKĐK TÂM ANH Q7)
-- Tiêu chuẩn: Bộ Y Tế, Nghị Định 98/2021/NĐ-CP, Thông Tư 05/2022/TT-BYT & W3C PROV-O
-- =========================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. Core Master Tables
CREATE TABLE IF NOT EXISTS "facilities" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    code TEXT UNIQUE NOT NULL,
    location TEXT,
    manager TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS device_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    safety_level TEXT CHECK(safety_level IN ('Basic', 'Advanced', 'Critical'))
);

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    immutable_asset_tag TEXT UNIQUE,
    device_name TEXT NOT NULL,
    model TEXT NOT NULL,
    serial_no TEXT NOT NULL UNIQUE,
    certification_no TEXT,
    calibration_stamp_no TEXT,
    facility_id INTEGER,
    category_id INTEGER,
    manufacturer TEXT,
    country_of_manufacturer TEXT,
    year_of_manufacture INTEGER,
    risk_level TEXT CHECK(risk_level IN ('A', 'B', 'C', 'D')),
    regulatory_class TEXT CHECK(regulatory_class IN ('A', 'B', 'C', 'D')),
    regulatory_regime TEXT DEFAULT 'TT_24_2026_TT_BYT',
    effective_date DATE DEFAULT '2026-07-01',
    status TEXT DEFAULT 'IN_SERVICE' CHECK(status IN ('IN_SERVICE', 'CALIBRATION_DUE', 'CALIBRATION_EXPIRED', 'MAINTENANCE', 'REPAIR', 'QUARANTINED', 'RECALLED', 'RETIRED')),
    safety_locked INTEGER DEFAULT 0,
    verification_status TEXT DEFAULT 'VERIFIED_GROUND_TRUTH',
    is_frozen INTEGER DEFAULT 0,
    legal_owner_name TEXT DEFAULT 'CÔNG TY CỔ PHẦN BỆNH VIỆN ĐA KHOA TÂM ANH TP. HỒ CHÍ MINH',
    operating_facility_name TEXT DEFAULT 'PHÒNG KHÁM ĐA KHOA TÂM ANH QUẬN 7',
    internal_allocation_doc TEXT,
    installation_date DATE,
    calibration_date DATE,
    recalibration_date DATE,
    source_pdf TEXT,
    pdf_path TEXT,
    md_path TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contract_no TEXT,
    supplier_name TEXT,
    handover_date TEXT,
    form_code TEXT,
    party_giver TEXT,
    party_receiver TEXT,
    md_source_path TEXT,
    FOREIGN KEY (facility_id) REFERENCES facilities(id),
    FOREIGN KEY (category_id) REFERENCES device_categories(id)
);

-- Bảng Evidence Ledger (Lưu vết chứng cứ kiểm toán chi tiết từng trường)
CREATE TABLE IF NOT EXISTS evidence_ledger (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id               INTEGER NOT NULL,
    field_name              TEXT NOT NULL,
    raw_ocr_value           TEXT,
    verified_value          TEXT NOT NULL,
    source_pdf              TEXT NOT NULL,
    source_page             INTEGER DEFAULT 1,
    exact_text_snippet      TEXT,
    pdf_sha256              TEXT,
    verification_method     TEXT DEFAULT 'GEMINI_3_7_FLASH_VISION',
    trust_level             TEXT DEFAULT 'VERIFIED_EVIDENCE',
    verified_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Bảng Quản trị Vòng đời HTM/CMMS (Append-only Event Sourcing)
CREATE TABLE IF NOT EXISTS asset_lifecycle_events (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    idempotency_key         TEXT UNIQUE NOT NULL,
    device_id               INTEGER NOT NULL,
    event_type              TEXT NOT NULL CHECK(event_type IN (
                                'PROCUREMENT', 'RECEIPT', 'ACCEPTANCE', 'INSTALLATION',
                                'COMMISSIONING', 'IN_SERVICE', 'PREVENTIVE_MAINTENANCE',
                                'CORRECTIVE_MAINTENANCE', 'CALIBRATION', 'INSPECTION',
                                'QUARANTINED', 'RECALLED', 'TRANSFER', 'DECOMMISSIONED'
                            )),
    event_date              DATE NOT NULL,
    performed_by            TEXT,
    certificate_or_doc_no   TEXT,
    safety_check_passed     INTEGER DEFAULT 1,
    metadata_json           TEXT,
    notes                   TEXT,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Bảng Khóa An Toàn Lâm Sàng (Safety Interlock Logs)
CREATE TABLE IF NOT EXISTS safety_interlock_logs (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id               INTEGER NOT NULL,
    attempted_transition    TEXT NOT NULL,
    interlock_reason        TEXT NOT NULL,
    blocked_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attempted_by            TEXT,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_devices_immutable_tag ON devices(immutable_asset_tag);
CREATE INDEX IF NOT EXISTS idx_evidence_device_field ON evidence_ledger(device_id, field_name);
CREATE INDEX IF NOT EXISTS idx_evidence_pdf_hash ON evidence_ledger(pdf_sha256);
CREATE INDEX IF NOT EXISTS idx_lifecycle_device_date ON asset_lifecycle_events(device_id, event_date DESC, id DESC);
CREATE INDEX IF NOT EXISTS idx_lifecycle_idempotency ON asset_lifecycle_events(idempotency_key);


CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_no TEXT NOT NULL UNIQUE,
    contract_name TEXT,
    supplier_name TEXT,
    handover_date TEXT,
    contract_value REAL,
    warranty_period_months INTEGER DEFAULT 12,
    status TEXT DEFAULT 'ACTIVE',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS device_accessories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_device_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    model TEXT,
    serial_no TEXT,
    accessory_type TEXT,
    status TEXT DEFAULT 'Sẵn sàng sử dụng',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_device_id) REFERENCES devices (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS bme_staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_code TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    title TEXT NOT NULL,
    role_level TEXT DEFAULT 'Kỹ Sư Chính',
    department_unit TEXT DEFAULT 'Phòng TTBYT Quận 7',
    specialty TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    assigned_departments TEXT,
    certificates TEXT,
    status TEXT DEFAULT 'ACTIVE',
    oncall_status TEXT DEFAULT 'AVAILABLE',
    avatar_color TEXT DEFAULT '#0284c7',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hospital_directory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    title TEXT,
    phone TEXT,
    email TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS supplier_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    service_scope TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Compliance, Calibration & Inspection Tables
CREATE TABLE IF NOT EXISTS calibration_certificates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    certificate_no TEXT NOT NULL,
    calibration_date DATE NOT NULL,
    recalibration_date DATE,
    stamp_no TEXT,
    result_status TEXT DEFAULT 'OK' CHECK(result_status IN ('OK', 'NG', 'PENDING')),
    uncertainty REAL,
    standard_reference TEXT,
    calibrated_by TEXT,
    source_pdf TEXT,
    pdf_path TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS pre_use_inspections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    inspector_name TEXT NOT NULL,
    department TEXT NOT NULL,
    power_ok BOOLEAN DEFAULT 1,
    physical_ok BOOLEAN DEFAULT 1,
    gas_pressure_ok BOOLEAN DEFAULT 1,
    selftest_ok BOOLEAN DEFAULT 1,
    overall_status TEXT DEFAULT 'PASSED' CHECK(overall_status IN ('PASSED', 'FAILED', 'WARNING')),
    notes TEXT,
    inspection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
);

-- 3. Maintenance, Repairs & Transfers Tables
CREATE TABLE IF NOT EXISTS maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    maintenance_date DATE NOT NULL,
    performed_by TEXT,
    maintenance_type TEXT CHECK(maintenance_type IN ('CALIBRATION', 'REPAIR', 'PREVENTIVE', 'INSPECTION', 'HANDOVER')),
    description TEXT,
    source_pdf TEXT,
    pdf_path TEXT,
    next_due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS maintenance_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    due_date DATE NOT NULL,
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'OVERDUE')),
    notes TEXT,
    maintenance_type TEXT DEFAULT 'PREVENTIVE' CHECK(maintenance_type IN ('PREVENTIVE', 'CALIBRATION', 'REPAIR', 'INSPECTION', 'HANDOVER')),
    frequency_days INTEGER,
    last_completed_at DATE,
    next_due_at DATE,
    assigned_staff_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS repairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    repair_type TEXT DEFAULT 'REPAIR' CHECK(repair_type IN ('CALIBRATION', 'REPAIR', 'REPLACEMENT', 'PREVENTIVE', 'INSPECTION', 'HANDOVER')),
    description TEXT NOT NULL,
    actual_cost REAL DEFAULT 0,
    parts_used TEXT,
    technician_name TEXT,
    reported_by TEXT,
    status TEXT DEFAULT 'REPORTED' CHECK(status IN ('REPORTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    start_date DATE,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS device_transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    from_facility_id INTEGER NOT NULL,
    to_facility_id INTEGER NOT NULL,
    giver_name TEXT NOT NULL,
    receiver_name TEXT NOT NULL,
    transfer_reason TEXT,
    transfer_date DATE NOT NULL,
    form_code TEXT DEFAULT 'BM08_TA5.TTBYT.QT.08',
    status TEXT DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE,
    FOREIGN KEY (from_facility_id) REFERENCES facilities (id),
    FOREIGN KEY (to_facility_id) REFERENCES facilities (id)
);

-- 4. Operations, Notifications & System Config Tables
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_type TEXT NOT NULL CHECK(ref_type IN ('CALIBRATION', 'MAINTENANCE', 'TRANSFER', 'DEVICE', 'FEEDBACK')),
    ref_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'WARNING' CHECK(level IN ('INFO', 'WARNING', 'CRITICAL')),
    days_left INTEGER,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS oncall_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_num INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    date_str TEXT NOT NULL,
    primary_engineer TEXT NOT NULL,
    primary_phone TEXT NOT NULL,
    backup_engineer TEXT NOT NULL,
    backup_phone TEXT NOT NULL,
    leader_oncall TEXT DEFAULT 'Nguyễn Quốc Việt (0902769710)',
    time_window TEXT DEFAULT '24/24 Giờ (07:30 - 07:30 sáng hôm sau)',
    status TEXT DEFAULT 'SCHEDULED',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, day_num)
);

CREATE TABLE IF NOT EXISTS api_keys_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    api_key TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    sender_name TEXT,
    sender_dept TEXT,
    priority TEXT DEFAULT 'NORMAL',
    content TEXT NOT NULL,
    status TEXT DEFAULT 'PENDING',
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Hồ sơ PDF gốc đính kèm thiết bị (đường dẫn tương đối POSIX)
CREATE TABLE IF NOT EXISTS device_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    doc_type TEXT NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    file_ext TEXT DEFAULT 'pdf',
    match_method TEXT DEFAULT 'SERIAL',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Phân đoạn chứng từ trong PDF gộp (composite scan): giữ nguyên file gốc
CREATE TABLE IF NOT EXISTS document_segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    page_start INTEGER NOT NULL CHECK (page_start >= 1),
    page_end INTEGER NOT NULL CHECK (page_end >= page_start),
    doc_type TEXT NOT NULL,
    form_code TEXT,
    title TEXT,
    extracted_serial TEXT,
    confidence REAL DEFAULT 0.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    md_anchor TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES device_documents(id) ON DELETE CASCADE
);

-- 5. Views
CREATE VIEW IF NOT EXISTS device_status_summary AS
SELECT 
    d.id,
    d.device_name,
    d.model,
    d.serial_no,
    d.contract_no,
    d.supplier_name,
    d.handover_date,
    d.manufacturer,
    d.country_of_manufacturer,
    d.risk_level,
    d.status,
    f.id AS facility_id,
    f.name AS facility,
    f.code AS facility_code,
    c.id AS category_id,
    c.name AS category,
    c.safety_level,
    d.calibration_date,
    d.recalibration_date,
    cert.certificate_no,
    cert.stamp_no,
    cert.source_pdf,
    CASE
        WHEN d.recalibration_date IS NULL THEN 'NO_CALIBRATION'
        WHEN date(d.recalibration_date) < date('now') THEN 'OVERDUE'
        WHEN date(d.recalibration_date) <= date('now', '+30 days') THEN 'WARNING'
        ELSE 'OK'
    END AS alert_status,
    CAST((julianday(d.recalibration_date) - julianday('now')) AS INTEGER) AS days_remaining
FROM devices d
LEFT JOIN facilities f ON d.facility_id = f.id
LEFT JOIN device_categories c ON d.category_id = c.id
LEFT JOIN calibration_certificates cert ON d.id = cert.device_id;

-- 6. Performance Indices (Created AFTER all tables and views)
CREATE INDEX IF NOT EXISTS idx_devices_category ON devices(category_id);
CREATE INDEX IF NOT EXISTS idx_devices_facility ON devices(facility_id);
CREATE INDEX IF NOT EXISTS idx_devices_serial ON devices(serial_no);
CREATE INDEX IF NOT EXISTS idx_devices_status_risk ON devices(status, risk_level);

CREATE INDEX IF NOT EXISTS idx_accessories_parent ON device_accessories(parent_device_id);
CREATE INDEX IF NOT EXISTS idx_certificates_date ON calibration_certificates(calibration_date, recalibration_date);
CREATE INDEX IF NOT EXISTS idx_certificates_device ON calibration_certificates(device_id);

CREATE INDEX IF NOT EXISTS idx_logs_device_date ON maintenance_logs(device_id, maintenance_date DESC);
CREATE INDEX IF NOT EXISTS idx_maintenances_device ON maintenance_schedules(device_id);
CREATE INDEX IF NOT EXISTS idx_maintenances_status ON maintenance_schedules(status, due_date);

CREATE INDEX IF NOT EXISTS idx_repairs_device ON repairs(device_id);
CREATE INDEX IF NOT EXISTS idx_repairs_status ON repairs(status, start_date);

CREATE INDEX IF NOT EXISTS idx_transfers_device ON device_transfers(device_id);
CREATE INDEX IF NOT EXISTS idx_transfers_status ON device_transfers(status, transfer_date);

CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read, created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_ref ON notifications(ref_type, ref_id);

CREATE INDEX IF NOT EXISTS idx_doc_device_id ON device_documents(device_id);
CREATE INDEX IF NOT EXISTS idx_doc_type ON device_documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_doc_segments_document ON document_segments(document_id);
CREATE INDEX IF NOT EXISTS idx_doc_segments_pages ON document_segments(document_id, page_start);

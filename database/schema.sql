-- =========================================================================
-- SCHEMA TOÀN DIỆN: MEDICAL DEVICE MANAGEMENT SYSTEM (HTM V3 - PKĐK TÂM ANH Q7)
-- Tiêu chuẩn: Bộ Y Tế, Nghị Định 98/2021/NĐ-CP, Thông Tư 05/2022/TT-BYT & W3C PROV-O
-- =========================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE INDEX IF NOT EXISTS idx_accessories_parent ON device_accessories(parent_device_id);

CREATE INDEX IF NOT EXISTS idx_certificates_date ON calibration_certificates(calibration_date, recalibration_date);

CREATE INDEX IF NOT EXISTS idx_certificates_device ON calibration_certificates(device_id);

CREATE INDEX IF NOT EXISTS idx_devices_category ON devices(category_id);

CREATE INDEX IF NOT EXISTS idx_devices_facility ON devices(facility_id);

CREATE INDEX IF NOT EXISTS idx_devices_serial ON devices(serial_no);

CREATE INDEX IF NOT EXISTS idx_devices_status_risk ON devices(status, risk_level);

CREATE INDEX IF NOT EXISTS idx_logs_device_date ON maintenance_logs(device_id, maintenance_date DESC);

CREATE INDEX IF NOT EXISTS idx_maintenances_device ON maintenance_schedules(device_id);

CREATE INDEX IF NOT EXISTS idx_maintenances_status ON maintenance_schedules(status, due_date);

CREATE INDEX IF NOT EXISTS idx_transfers_device ON device_transfers(device_id);

CREATE TABLE IF NOT EXISTS api_keys_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        api_key TEXT NOT NULL UNIQUE,
        status TEXT DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        accessory_type TEXT, -- Probe, Cable, Electrode, Blade, Battery, Cart, Adapter
        status TEXT DEFAULT 'Sẵn sàng sử dụng',
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (parent_device_id) REFERENCES devices (id) ON DELETE CASCADE
    );

CREATE TABLE IF NOT EXISTS device_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    safety_level TEXT CHECK(safety_level IN ('Basic', 'Advanced', 'Critical'))
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
        status TEXT DEFAULT 'COMPLETED', -- PENDING, COMPLETED, CANCELLED
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (id),
        FOREIGN KEY (from_facility_id) REFERENCES facilities (id),
        FOREIGN KEY (to_facility_id) REFERENCES facilities (id)
    );

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    status TEXT DEFAULT 'IN_SERVICE' CHECK(status IN ('IN_SERVICE', 'CALIBRATION_DUE', 'MAINTENANCE', 'REPAIR', 'RETIRED')),
    installation_date DATE,
    calibration_date DATE,
    recalibration_date DATE,
    source_pdf TEXT,
    pdf_path TEXT,
    md_path TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, contract_no TEXT, supplier_name TEXT, handover_date TEXT, form_code TEXT, party_giver TEXT, party_receiver TEXT, md_source_path TEXT,
    FOREIGN KEY (facility_id) REFERENCES facilities(id),
    FOREIGN KEY (category_id) REFERENCES device_categories(id)
);

CREATE TABLE IF NOT EXISTS "facilities" (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        code TEXT UNIQUE NOT NULL,
        location TEXT,
        manager TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS oncall_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_num INTEGER NOT NULL,
    day_name TEXT NOT NULL,
    date_str TEXT NOT NULL, -- DD/MM/YYYY
    primary_engineer TEXT NOT NULL,
    primary_phone TEXT NOT NULL,
    backup_engineer TEXT NOT NULL,
    backup_phone TEXT NOT NULL,
    leader_oncall TEXT DEFAULT 'Nguyễn Quốc Việt (0902769710)',
    time_window TEXT DEFAULT '24/24 Giờ (07:30 - 07:30 sáng hôm sau)',
    status TEXT DEFAULT 'SCHEDULED', -- TODAY, SCHEDULED, COMPLETED
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(year, month, day_num)
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
        overall_status TEXT DEFAULT 'PASSED', -- PASSED, FAILED, WARNING
        notes TEXT,
        inspection_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (id) ON DELETE CASCADE
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

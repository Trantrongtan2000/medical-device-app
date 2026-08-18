-- Schema cho Medical Device Management System (BV Quận 7)
-- SQLite Database

-- Bảng khoa/phòng ban
CREATE TABLE IF NOT EXISTS facilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    code TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bảng loại thiết bị
CREATE TABLE IF NOT EXISTS device_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    safety_level TEXT CHECK(safety_level IN ('Basic', 'Advanced', 'Critical'))
);

-- Bảng thiết bị y tế
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facility_id) REFERENCES facilities(id),
    FOREIGN KEY (category_id) REFERENCES device_categories(id)
);

-- Bảng giấy chứng nhận hiệu chuẩn / kiểm định
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

-- Bảng lịch bảo trì phòng ngừa (PM)
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

-- Bảng nhật ký bảo trì / sửa chữa
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

-- Indexes tối ưu hiệu năng
CREATE INDEX IF NOT EXISTS idx_devices_serial ON devices(serial_no);
CREATE INDEX IF NOT EXISTS idx_devices_facility ON devices(facility_id);
CREATE INDEX IF NOT EXISTS idx_devices_category ON devices(category_id);
CREATE INDEX IF NOT EXISTS idx_certificates_date ON calibration_certificates(calibration_date, recalibration_date);
CREATE INDEX IF NOT EXISTS idx_maintenances_status ON maintenance_schedules(status, due_date);
CREATE INDEX IF NOT EXISTS idx_maintenances_device ON maintenance_schedules(device_id);

-- Trigger cập nhật updated_at tự động
CREATE TRIGGER IF NOT EXISTS trg_devices_updated_at 
AFTER UPDATE ON devices
BEGIN
    UPDATE devices SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- View thống kê thiết bị theo trạng thái
CREATE VIEW IF NOT EXISTS device_status_summary AS
SELECT 
    d.id,
    d.device_name,
    d.model,
    d.serial_no,
    d.manufacturer,
    d.country_of_manufacturer,
    d.risk_level,
    d.status,
    d.source_pdf,
    d.pdf_path,
    f.name as facility,
    c.name as category,
    COALESCE(cc.calibration_date, d.calibration_date) as calibration_date,
    COALESCE(cc.recalibration_date, d.recalibration_date) as recalibration_date,
    COALESCE(cc.certificate_no, d.certification_no) as certificate_no,
    COALESCE(cc.stamp_no, d.calibration_stamp_no) as stamp_no,
    COALESCE(cc.result_status, 'OK') as result_status,
    CASE 
        WHEN COALESCE(cc.recalibration_date, d.recalibration_date) IS NULL THEN 'NO_DATA'
        WHEN COALESCE(cc.recalibration_date, d.recalibration_date) < DATE('now') THEN 'OVERDUE'
        WHEN COALESCE(cc.recalibration_date, d.recalibration_date) <= DATE('now', '+30 days') THEN 'WARNING'
        ELSE 'OK'
    END as alert_status
FROM devices d
LEFT JOIN facilities f ON d.facility_id = f.id
LEFT JOIN device_categories c ON d.category_id = c.id
LEFT JOIN calibration_certificates cc ON d.id = cc.device_id 
    AND cc.id = (SELECT MAX(id) FROM calibration_certificates WHERE device_id = d.id);
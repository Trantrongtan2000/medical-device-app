#!/usr/bin/env python3
r"""
Script Import Dữ Liệu Thiết Bị Y Tế & Kiểm Định từ Markdown OCR
Nguồn: G:\BV QUẬN 7_OCR_WORK_20260712\md
Liên kết: File PDF gốc tại G:\BV QUẬN 7_OCR_WORK_20260712
"""

import os
import sys
import yaml
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass


class MedicalDeviceImporter:
    def __init__(self, db_path: str, md_source_dir: str, pdf_source_dir: str):
        self.db_path = Path(db_path)
        self.md_dir = Path(md_source_dir)
        self.pdf_dir = Path(pdf_source_dir)
        self.conn = None
        self.stats = {
            'total_files': 0,
            'files_with_frontmatter': 0,
            'devices_created': 0,
            'devices_updated': 0,
            'certificates_imported': 0,
            'handovers_created': 0,
            'errors': 0
        }
        self.facility_cache = {}
        self.category_cache = {}

    def connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA journal_mode = WAL;")

        # Áp dụng schema
        schema_path = self.db_path.parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                self.conn.executescript(f.read())
        self.conn.commit()

        # Cache existing facilities
        for row in self.conn.execute("SELECT id, name FROM facilities").fetchall():
            self.facility_cache[row["name"].strip().upper()] = row["id"]

        # Cache existing categories
        for row in self.conn.execute("SELECT id, name FROM device_categories").fetchall():
            self.category_cache[row["name"].strip().upper()] = row["id"]

    def get_or_create_facility(self, facility_name: Optional[str]) -> Optional[int]:
        if not facility_name or str(facility_name).strip() in ("", "-", "None", "null"):
            facility_name = "Khoa/Phòng Chưa Phân Loại"
        
        name_clean = str(facility_name).strip()
        key = name_clean.upper()
        
        if key in self.facility_cache:
            return self.facility_cache[key]
        
        # Tạo mã khoa tự động
        code = re.sub(r'[^A-Za-z0-9]', '', name_clean)[:6].upper()
        if not code:
            code = f"FAC{len(self.facility_cache) + 1}"
            
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO facilities (name, code) VALUES (?, ?)",
            (name_clean, code)
        )
        self.conn.commit()
        
        cur.execute("SELECT id FROM facilities WHERE name = ?", (name_clean,))
        row = cur.fetchone()
        if row:
            fac_id = row[0]
            self.facility_cache[key] = fac_id
            return fac_id
        return None

    def get_or_create_category(self, device_name: Optional[str]) -> Optional[int]:
        if not device_name:
            device_name = "Thiết Bị Chung"
            
        name_lower = str(device_name).lower()
        
        mapping = {
            ('thở', 'ventilator'): ('Máy thở & Hô hấp', 'Critical', 'B'),
            ('thận', 'dialysis', 'r.o', 'ro'): ('Thận nhân tạo & Lọc máu', 'Critical', 'B'),
            ('tiêm điện', 'truyền dịch', 'infusion', 'syringe'): ('Bơm tiêm & Máy truyền dịch', 'Advanced', 'B'),
            ('monitor', 'theo dõi', 'ecg', 'điện tim', 'sp02', 'spo2'): ('Theo dõi bệnh nhân & Điện tim', 'Advanced', 'B'),
            ('dao mổ', 'electrosurgical', 'phẫu thuật'): ('Phẫu thuật & Dao mổ điện', 'Critical', 'C'),
            ('phá rung', 'defibrillator', 'sốc tim'): ('Cấp cứu & Máy phá rung tim', 'Critical', 'C'),
            ('x-quang', 'c-arm', 'ct scanner', 'mri', 'chẩn đoán hình ảnh', 'siêu âm', 'ultrasound'): ('Chẩn đoán hình ảnh', 'Critical', 'C'),
            ('nội soi', 'endoscopy'): ('Hệ thống nội soi', 'Advanced', 'B'),
            ('hút dịch', 'suction'): ('Máy hút dịch & áp lực', 'Basic', 'A'),
            ('đèn mổ', 'bàn mổ', 'giường'): ('Trang thiết bị phòng mổ & buồng bệnh', 'Basic', 'A'),
            ('xét nghiệm', 'hóa sinh', 'huyết học', 'ly tâm', 'pipette'): ('Thiết bị xét nghiệm & lab', 'Advanced', 'B'),
            ('nồi hấp', 'tiệt trùng', 'autoclave'): ('Thiết bị tiệt trùng & khử khuẩn', 'Advanced', 'B'),
            ('áp kế', 'huyết áp', 'nhiệt kế', 'nhiệt ẩm'): ('Dụng cụ đo lường y tế', 'Basic', 'A'),
        }
        
        category_name = "Thiết bị y tế khác"
        safety_level = "Basic"
        risk_level = "A"
        
        for keywords, (cat_name, s_level, r_level) in mapping.items():
            if any(kw in name_lower for kw in keywords):
                category_name = cat_name
                safety_level = s_level
                risk_level = r_level
                break
                
        key = category_name.upper()
        if key in self.category_cache:
            return self.category_cache[key]
            
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO device_categories (name, description, safety_level) VALUES (?, ?, ?)",
            (category_name, f"Nhóm {category_name}", safety_level)
        )
        self.conn.commit()
        
        cur.execute("SELECT id FROM device_categories WHERE name = ?", (category_name,))
        row = cur.fetchone()
        if row:
            cat_id = row[0]
            self.category_cache[key] = cat_id
            return cat_id
        return None

    def parse_date(self, date_val: Any) -> Optional[str]:
        if not date_val:
            return None
        if isinstance(date_val, datetime):
            return date_val.strftime('%Y-%m-%d')
        
        val_str = str(date_val).strip()
        # Clean patterns like "12 tháng 05 năm 2026"
        vn_match = re.search(r'(\d{1,2})\s*tháng\s*(\d{1,2})\s*năm\s*(\d{4})', val_str, re.IGNORECASE)
        if vn_match:
            d, m, y = vn_match.groups()
            return f"{y}-{int(m):02d}-{int(d):02d}"
            
        # Common date patterns
        for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%d.%m.%Y', '%Y/%m/%d'):
            try:
                return datetime.strptime(val_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return None

    def infer_risk_level(self, device_name: str) -> str:
        name_l = device_name.lower()
        if any(w in name_l for w in ['thở', 'phá rung', 'chạy thận', 'dao mổ', 'c-arm', 'x-quang']):
            return 'C'
        elif any(w in name_l for w in ['monitor', 'bơm tiêm', 'truyền dịch', 'nội soi', 'siêu âm']):
            return 'B'
        elif any(w in name_l for w in ['cấy ghép', 'van tim']):
            return 'D'
        return 'A'

    def import_single_md(self, md_path: Path):
        self.stats['total_files'] += 1
        try:
            content = md_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            self.stats['errors'] += 1
            return

        m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not m:
            return

        try:
            self.stats['files_with_frontmatter'] += 1
            meta = yaml.safe_load(m.group(1))
            if not isinstance(meta, dict):
                return

            doc_type = str(meta.get('doc_type', '')).strip().upper()
            
            # Lấy thông tin thiết bị
            device_name = meta.get('device_name') or meta.get('equipment_name') or meta.get('name')
            model = meta.get('model') or meta.get('model_no')
            serial_no = meta.get('serial_no') or meta.get('serial') or meta.get('sn')
            
            # Nếu chưa có device_name nhưng có model/serial, trích xuất từ tên file
            if not device_name and (model or serial_no):
                device_name = md_path.stem.split('_')[0]
                
            # Nếu không có serial_no hoặc model, thử tìm trong tên file
            if not serial_no:
                sn_match = re.search(r'SN[_\s-]?([A-Za-z0-9-]+)', md_path.stem, re.IGNORECASE)
                if sn_match:
                    serial_no = sn_match.group(1)
                    
            if not device_name and not model and not serial_no:
                return

            device_name = str(device_name or "Thiết bị y tế").strip()
            model = str(model or "N/A").strip()
            serial_no = str(serial_no or f"GEN-{abs(hash(str(md_path)))}").strip()

            facility_str = meta.get('facility') or meta.get('department') or meta.get('location')
            facility_id = self.get_or_create_facility(facility_str)
            category_id = self.get_or_create_category(device_name)

            manufacturer = meta.get('manufacturer') or meta.get('brand')
            country = meta.get('country') or meta.get('origin_country')
            year = meta.get('year') or meta.get('manufacturing_year')
            try:
                year = int(year) if year else None
            except Exception:
                year = None

            calib_date = self.parse_date(meta.get('calibration_date') or meta.get('calibrated_date'))
            recalib_date = self.parse_date(meta.get('recalibration_date') or meta.get('valid_to_date') or meta.get('next_due_date'))
            cert_no = meta.get('cert_no') or meta.get('certification_no')
            stamp_no = meta.get('stamp_no') or meta.get('calibration_stamp_no')
            
            source_pdf = meta.get('source_pdf') or (md_path.stem + '.pdf')
            pdf_path = meta.get('pdf_path') or str(source_pdf)
            rel_md_path = str(md_path.relative_to(self.md_dir))

            risk_level = self.infer_risk_level(device_name)
            status = 'IN_SERVICE'

            # Chèn hoặc cập nhật thiết bị
            cur = self.conn.cursor()
            cur.execute("SELECT id, calibration_date, recalibration_date FROM devices WHERE serial_no = ?", (serial_no,))
            existing = cur.fetchone()

            if existing:
                device_id = existing[0]
                cur.execute("""
                    UPDATE devices SET
                        device_name = COALESCE(NULLIF(device_name, 'Thiết bị y tế'), ?),
                        model = COALESCE(NULLIF(model, 'N/A'), ?),
                        facility_id = COALESCE(facility_id, ?),
                        category_id = COALESCE(category_id, ?),
                        manufacturer = COALESCE(manufacturer, ?),
                        country_of_manufacturer = COALESCE(country_of_manufacturer, ?),
                        year_of_manufacture = COALESCE(year_of_manufacture, ?),
                        calibration_date = COALESCE(?, calibration_date),
                        recalibration_date = COALESCE(?, recalibration_date),
                        certification_no = COALESCE(?, certification_no),
                        calibration_stamp_no = COALESCE(?, calibration_stamp_no),
                        source_pdf = COALESCE(source_pdf, ?),
                        pdf_path = COALESCE(pdf_path, ?)
                    WHERE id = ?
                """, (
                    device_name, model, facility_id, category_id,
                    manufacturer, country, year,
                    calib_date, recalib_date, cert_no, stamp_no,
                    str(source_pdf), str(pdf_path), device_id
                ))
                self.stats['devices_updated'] += 1
            else:
                cur.execute("""
                    INSERT INTO devices 
                    (device_name, model, serial_no, certification_no, calibration_stamp_no,
                     facility_id, category_id, manufacturer, country_of_manufacturer,
                     year_of_manufacture, risk_level, status, calibration_date, recalibration_date,
                     source_pdf, pdf_path, md_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    device_name, model, serial_no, cert_no, stamp_no,
                    facility_id, category_id, manufacturer, country,
                    year, risk_level, status, calib_date, recalib_date,
                    str(source_pdf), str(pdf_path), rel_md_path
                ))
                device_id = cur.lastrowid
                self.stats['devices_created'] += 1

            # Lưu giấy chứng nhận kiểm định nếu là HIEU_CHUAN / KIEM_DINH hoặc có cert_no
            if (doc_type in ('HIEU_CHUAN', 'KIEM_DINH') or cert_no) and calib_date:
                raw_res = str(meta.get('status', 'OK')).strip().upper()
                if any(ok_word in raw_res for ok_word in ('ĐẠT', 'DAT', 'PASS', 'OK', 'GOOD')):
                    norm_status = 'OK'
                elif any(ng_word in raw_res for ng_word in ('KHÔNG ĐẠT', 'KHONG DAT', 'FAIL', 'NG', 'HỎNG', 'HONG')):
                    norm_status = 'NG'
                else:
                    norm_status = 'OK'

                cur.execute("""
                    INSERT INTO calibration_certificates
                    (device_id, certificate_no, calibration_date, recalibration_date,
                     stamp_no, result_status, calibrated_by, source_pdf, pdf_path, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    device_id, cert_no or f"GCN-{serial_no}", calib_date, recalib_date,
                    stamp_no, norm_status, meta.get('calibrated_by') or meta.get('note'),
                    str(source_pdf), str(pdf_path), meta.get('note')
                ))
                self.stats['certificates_imported'] += 1

            # Lưu nhật ký bảo trì / bàn giao
            if doc_type == 'BAN_GIAO':
                handover_date = self.parse_date(meta.get('handover_date')) or calib_date or datetime.now().strftime('%Y-%m-%d')
                cur.execute("""
                    INSERT INTO maintenance_logs
                    (device_id, maintenance_date, performed_by, maintenance_type, description, source_pdf, pdf_path)
                    VALUES (?, ?, ?, 'HANDOVER', ?, ?, ?)
                """, (
                    device_id, handover_date, meta.get('handover_by') or 'Phòng TTBYT',
                    f"Biên bản bàn giao thiết bị: {device_name} ({model})",
                    str(source_pdf), str(pdf_path)
                ))
                self.stats['handovers_created'] += 1
        except Exception as e:
            self.stats['errors'] += 1

    def run(self):
        print("=" * 70)
        print("🚀 BẮT ĐẦU IMPORT TOÀN DIỆN DỮ LIỆU THIẾT BỊ Y TẾ (BV QUẬN 7)")
        print(f"📁 Nguồn Markdown: {self.md_dir}")
        print(f"📁 Nguồn PDF:      {self.pdf_dir}")
        print(f"💾 CSDL SQLite:    {self.db_path}")
        print("=" * 70)

        self.connect()

        all_md = list(self.md_dir.rglob("*.md"))
        print(f"\n🔍 Tìm thấy {len(all_md)} tệp Markdown cần xử lý...")

        for idx, md_file in enumerate(all_md):
            self.import_single_md(md_file)
            if (idx + 1) % 500 == 0 or (idx + 1) == len(all_md):
                self.conn.commit()
                print(f"  ⚡ Đã xử lý {idx + 1}/{len(all_md)} tệp | Thiết bị mới: {self.stats['devices_created']} | GCN: {self.stats['certificates_imported']}")

        self.conn.commit()
        self.conn.close()

        print("\n" + "=" * 70)
        print("✅ HOÀN TẤT NẠP DỮ LIỆU:")
        print(f"  • Tổng file đã quét:         {self.stats['total_files']}")
        print(f"  • File có metadata:          {self.stats['files_with_frontmatter']}")
        print(f"  • Thiết bị tạo mới:          {self.stats['devices_created']}")
        print(f"  • Thiết bị cập nhật:         {self.stats['devices_updated']}")
        print(f"  • Giấy chứng nhận kiểm định: {self.stats['certificates_imported']}")
        print(f"  • Biên bản bàn giao:         {self.stats['handovers_created']}")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    importer = MedicalDeviceImporter(
        db_path=r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db",
        md_source_dir=r"G:\BV QUẬN 7_OCR_WORK_20260712\md",
        pdf_source_dir=r"G:\BV QUẬN 7_OCR_WORK_20260712"
    )
    importer.run()
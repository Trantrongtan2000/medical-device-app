#!/usr/bin/env python3
"""
Script Xuất Dữ Liệu Thiết Bị Y Tế & Kiểm Định Sang Tệp Markdown (BV Quận 7)
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# UTF-8 Encoding
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent.parent / "database" / "devices.db"
DOCS_DIR = Path(__file__).parent.parent / "docs"


def export_devices_to_markdown():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 1. Thống kê tổng quan
    total_devices = conn.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    total_certs = conn.execute("SELECT COUNT(*) FROM calibration_certificates").fetchone()[0]
    total_facilities = conn.execute("SELECT COUNT(*) FROM facilities").fetchone()[0]

    overdue_count = conn.execute("SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'OVERDUE'").fetchone()[0]
    warning_count = conn.execute("SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'WARNING'").fetchone()[0]
    ok_count = conn.execute("SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'OK'").fetchone()[0]
    nodata_count = conn.execute("SELECT COUNT(*) FROM device_status_summary WHERE alert_status = 'NO_DATA'").fetchone()[0]

    md_export_path = DOCS_DIR / "DANH_MUC_THIET_BI_Y_TE_BVQ7.md"

    with open(md_export_path, "w", encoding="utf-8") as f:
        f.write("# SỔ QUẢN LÝ TRANG THIẾT BỊ Y TẾ — BỆNH VIỆN QUẬN 7\n\n")
        f.write(f"> **Thời gian xuất báo cáo:** `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`  \n")
        f.write(f"> **Cơ sở dữ liệu:** SQLite WAL (`devices.db`) | **Nguồn dữ liệu gốc:** `G:\\BV QUẬN 7_OCR_WORK_20260712`\n\n")
        f.write("---\n\n")

        # KPI Summary
        f.write("## 1. TỔNG HỢP CHỈ SỐ KPI VÀ AN TOÀN TRANG THIẾT BỊ\n\n")
        f.write("| Chỉ số quản trị | Giá trị | Đơn vị | Ghi chú & Đánh giá |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        f.write(f"| **Tổng số thiết bị quản lý** | `{total_devices:,}` | Thiết bị | Toàn viện |\n")
        f.write(f"| **Tổng số hồ sơ/chứng chỉ kiểm định** | `{total_certs:,}` | Giấy chứng nhận | Đính kèm PDF gốc |\n")
        f.write(f"| **Tổng số Khoa / Phòng ban** | `{total_facilities}` | Đơn vị sử dụng | Phân bổ toàn viện |\n")
        f.write(f"| **🟢 Thiết bị kiểm định ĐẠT CHUẨN** | `{ok_count:,}` | Thiết bị | Đang vận hành an toàn |\n")
        f.write(f"| **🟡 Thiết bị CẢNH BÁO (Hạn < 30 ngày)** | `{warning_count:,}` | Thiết bị | Cần lập kế hoạch KĐ/HC |\n")
        f.write(f"| **🔴 Thiết bị QUÁ HẠN KIỂM ĐỊNH** | `{overdue_count:,}` | Thiết bị | Yêu cầu dừng/ưu tiên KĐ |\n")
        f.write(f"| **⚪ Thiết bị chưa có dữ liệu KĐ** | `{nodata_count:,}` | Thiết bị | Thiết bị thông thường / chờ nạp |\n\n")

        f.write("---\n\n")

        # Facilities Summary
        f.write("## 2. PHÂN BỔ THIẾT BỊ THEO KHOA / PHÒNG BAN\n\n")
        f.write("| STT | Khoa / Phòng Ban | Mã Khoa | Số Lượng Thiết Bị |\n")
        f.write("| :---: | :--- | :---: | :---: |\n")

        fac_rows = conn.execute("""
            SELECT f.name, f.code, COUNT(d.id) as device_count
            FROM facilities f
            LEFT JOIN devices d ON f.id = d.facility_id
            GROUP BY f.id, f.name, f.code
            ORDER BY device_count DESC, f.name ASC
        """).fetchall()

        for idx, row in enumerate(fac_rows, 1):
            f.write(f"| {idx} | **{row['name']}** | `{row['code'] or '-'}` | **{row['device_count']}** |\n")

        f.write("\n---\n\n")

        # Full Devices Catalog
        f.write("## 3. DANH MỤC CHI TIẾT TRANG THIẾT BỊ Y TẾ & HỒ SƠ KIỂM ĐỊNH\n\n")
        f.write("| STT | Mã Serial (S/N) | Tên Trang Thiết Bị | Model | Hãng & Nước SX | Rủi ro | Khoa / Vị Trí | Ngày KĐ | Hạn KĐ | Trạng Thái KĐ | Tệp PDF Gốc |\n")
        f.write("| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :--- |\n")

        devices = conn.execute("""
            SELECT * FROM device_status_summary
            ORDER BY CASE alert_status WHEN 'OVERDUE' THEN 1 WHEN 'WARNING' THEN 2 WHEN 'OK' THEN 3 ELSE 4 END, facility, device_name
        """).fetchall()

        for idx, d in enumerate(devices, 1):
            alert = d['alert_status']
            if alert == 'OVERDUE':
                status_txt = "🔴 Quá hạn"
            elif alert == 'WARNING':
                status_txt = "🟡 Cảnh báo 30N"
            elif alert == 'OK':
                status_txt = "🟢 Đạt chuẩn"
            else:
                status_txt = "⚪ Chưa có KĐ"

            sn = d['serial_no'] or '-'
            name = d['device_name'] or 'Thiết bị y tế'
            model = d['model'] or '-'
            mfg = f"{d['manufacturer'] or '-'} ({d['country_of_manufacturer'] or '-'})"
            risk = f"Mức {d['risk_level'] or 'A'}"
            fac = d['facility'] or 'Chưa phân bổ'
            cal_date = d['calibration_date'] or '-'
            recal_date = d['recalibration_date'] or '-'
            pdf = f"`{d['source_pdf']}`" if d['source_pdf'] else '-'

            f.write(f"| {idx} | `{sn}` | **{name}** | `{model}` | {mfg} | {risk} | {fac} | {cal_date} | **{recal_date}** | {status_txt} | {pdf} |\n")

        f.write("\n---\n\n")

        # Detailed Calibration List
        f.write("## 4. BẢNG CHI TIẾT GIẤY CHỨNG NHẬN KIỂM ĐỊNH / HIỆU CHUẨN\n\n")
        f.write("| STT | Mã Serial | Tên Thiết Bị | Số Giấy Chứng Nhận (GCN) | Số Tem KĐ | Ngày KĐ | Hạn KĐ | Đơn Vị KĐ | Kết Quả | Tệp Chứng Chỉ PDF |\n")
        f.write("| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: | :--- |\n")

        certs = conn.execute("""
            SELECT c.*, d.device_name, d.model, d.serial_no, f.name as facility
            FROM calibration_certificates c
            JOIN devices d ON c.device_id = d.id
            LEFT JOIN facilities f ON d.facility_id = f.id
            ORDER BY c.recalibration_date ASC
        """).fetchall()

        for idx, c in enumerate(certs, 1):
            sn = c['serial_no'] or '-'
            dev_name = c['device_name'] or '-'
            cert_no = c['certificate_no'] or '-'
            stamp_no = c['stamp_no'] or '-'
            cal_d = c['calibration_date'] or '-'
            recal_d = c['recalibration_date'] or '-'
            by = c['calibrated_by'] or '-'
            res = f"**{c['result_status'] or 'OK'}**"
            pdf_link = f"`{c['source_pdf']}`" if c['source_pdf'] else '-'

            f.write(f"| {idx} | `{sn}` | **{dev_name}** | `{cert_no}` | `{stamp_no}` | {cal_d} | {recal_d} | {by} | {res} | {pdf_link} |\n")

    conn.close()
    print(f"✅ Đã xuất báo cáo Markdown thành công tại: {md_export_path}")
    print(f"   • Tổng số thiết bị: {total_devices}")
    print(f"   • Tổng số chứng chỉ: {total_certs}")


if __name__ == "__main__":
    export_devices_to_markdown()

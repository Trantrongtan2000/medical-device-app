#!/usr/bin/env python3
"""
Script Lọc Sạch & Khử Trùng Lặp Dữ Liệu Thiết Bị Y Tế & Kiểm Định (BV Quận 7)
"""

import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")


def deduplicate_and_clean():
    print("=" * 70)
    print("🧹 BẮT ĐẦU QUY TRÌNH LỌC SẠCH & KHỬ TRÙNG LẶP DỮ LIỆU CSDL")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Thống kê trước khi khử trùng
    before_devs = cur.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    before_certs = cur.execute("SELECT COUNT(*) FROM calibration_certificates").fetchone()[0]
    print(f"📊 Dữ liệu ban đầu: {before_devs} thiết bị | {before_certs} giấy chứng nhận kiểm định")

    # 2. Xóa các chứng chỉ kiểm định trùng lặp (giữ lại 1 bản ghi duy nhất cho mỗi certificate_no + device_id + calibration_date)
    cur.execute("""
        DELETE FROM calibration_certificates
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM calibration_certificates
            GROUP BY device_id, certificate_no, calibration_date
        )
    """)
    certs_removed = cur.rowcount
    print(f"  • Đã loại bỏ {certs_removed} chứng chỉ kiểm định bị trùng lặp.")

    # 3. Hợp nhất / xóa các thiết bị rác có tên generic và không có serial hợp lệ (GEN- hash) và không có bất kỳ chứng chỉ/nhật ký nào
    cur.execute("""
        DELETE FROM devices
        WHERE serial_no LIKE 'GEN-%'
          AND device_name IN ('Thiết bị y tế', 'Thiết bị chẩn đoán & điều trị y tế', 'N/A', 'Unknown', 'BBBG', 'BBNT', 'Giấy kiểm định')
          AND id NOT IN (SELECT DISTINCT device_id FROM calibration_certificates)
          AND id NOT IN (SELECT DISTINCT device_id FROM maintenance_logs)
    """)
    devs_removed = cur.rowcount
    print(f"  • Đã dọn dẹp {devs_removed} bản ghi thiết bị rác/không có thông tin định danh hợp lệ.")

    # 4. Loại bỏ nhật ký bảo trì trùng lặp
    cur.execute("""
        DELETE FROM maintenance_logs
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM maintenance_logs
            GROUP BY device_id, maintenance_date, maintenance_type, description
        )
    """)
    logs_removed = cur.rowcount
    print(f"  • Đã loại bỏ {logs_removed} nhật ký bảo trì/bàn giao trùng lặp.")

    # 5. Cập nhật ngày kiểm định mới nhất từ bảng certificates vào bảng devices
    cur.execute("""
        UPDATE devices
        SET 
            calibration_date = (
                SELECT MAX(calibration_date) 
                FROM calibration_certificates 
                WHERE device_id = devices.id
            ),
            recalibration_date = (
                SELECT recalibration_date 
                FROM calibration_certificates 
                WHERE device_id = devices.id 
                ORDER BY calibration_date DESC LIMIT 1
            ),
            certification_no = (
                SELECT certificate_no 
                FROM calibration_certificates 
                WHERE device_id = devices.id 
                ORDER BY calibration_date DESC LIMIT 1
            ),
            calibration_stamp_no = (
                SELECT stamp_no 
                FROM calibration_certificates 
                WHERE device_id = devices.id 
                ORDER BY calibration_date DESC LIMIT 1
            )
        WHERE id IN (SELECT DISTINCT device_id FROM calibration_certificates)
    """)

    conn.commit()

    # 6. Thống kê sau khi hoàn tất
    after_devs = cur.execute("SELECT COUNT(*) FROM devices").fetchone()[0]
    after_certs = cur.execute("SELECT COUNT(*) FROM calibration_certificates").fetchone()[0]
    after_logs = cur.execute("SELECT COUNT(*) FROM maintenance_logs").fetchone()[0]

    conn.close()

    print("\n" + "=" * 70)
    print("✅ HOÀN TẤT KHỬ TRÙNG LẶP & CHUẨN HÓA DỮ LIỆU:")
    print(f"  • Tổng thiết bị chuẩn sau lọc:     {after_devs} máy (Đã giảm {before_devs - after_devs} bản ghi rác)")
    print(f"  • Tổng chứng chỉ kiểm định chuẩn: {after_certs} GCN (Đã loại bỏ {certs_removed} bản ghi trùng)")
    print(f"  • Tổng nhật ký bảo trì/bàn giao:  {after_logs} biên bản")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    deduplicate_and_clean()

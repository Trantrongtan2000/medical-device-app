"""
Script chuẩn hóa toàn bộ các tên thiết bị chung chung, lỗi gõ và hãng chưa định danh
"""
import sys
import io
import sqlite3

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

conn = sqlite3.connect('database/devices.db')
cur = conn.cursor()

updates = [
    # 1. Bàn và Ghế Saikang
    ("UPDATE devices SET device_name = 'Bàn khám sản phụ khoa điện' WHERE model LIKE '%A99-5%'", 
     "Chuẩn hóa A99-5 thành Bàn khám sản phụ khoa điện"),
    ("UPDATE devices SET device_name = 'Ghế truyền dịch & lọc máu đa năng điện' WHERE model LIKE '%SKE-120A%'", 
     "Chuẩn hóa SKE-120A thành Ghế truyền dịch & lọc máu đa năng điện"),
     
    # 2. Bàn khám & Ghế khám TMH
    ("UPDATE devices SET manufacturer = 'Medtrix / MI ONE' WHERE model LIKE '%IU 3000%' AND manufacturer = 'Chính hãng'",
     "Gán hãng Medtrix / MI ONE cho Bàn khám TMH IU 3000"),
    ("UPDATE devices SET manufacturer = 'Medtrix' WHERE model LIKE '%GI-100%' AND manufacturer = 'Chính hãng'",
     "Gán hãng Medtrix cho Ghế khám TMH GI-100"),
     
    # 3. Thiết bị chuyên khoa sâu
    ("UPDATE devices SET manufacturer = 'BTL Industries' WHERE model LIKE '%BTL 6000%'",
     "Gán hãng BTL Industries cho Laser cường độ cao 30W"),
    ("UPDATE devices SET manufacturer = 'Haier Biomedical' WHERE model LIKE '%HYC-118A%'",
     "Gán hãng Haier Biomedical cho Tủ bảo quản dược phẩm"),
    ("UPDATE devices SET manufacturer = 'Neurosoft' WHERE model LIKE '%Neuro-MSX%'",
     "Gán hãng Neurosoft cho Hệ thống kích thích từ trường xuyên sọ TMS"),
    ("UPDATE devices SET manufacturer = 'Tosoh Corporation' WHERE model LIKE '%HLC-723G11%' OR model LIKE '%G11-90SL%'",
     "Gán hãng Tosoh cho Máy xét nghiệm HbA1c HLC-723G11"),
    ("UPDATE devices SET manufacturer = 'Nonin Medical' WHERE model LIKE '%7500F0%' OR model LIKE '%7500FO%'",
     "Gán hãng Nonin Medical cho SpO2 phòng MRI"),
    ("UPDATE devices SET manufacturer = 'Keling Medical' WHERE model LIKE '%KL05L%'",
     "Gán hãng Keling Medical cho Đèn mổ di động KL05L.ILED"),
    ("UPDATE devices SET manufacturer = 'Salicru' WHERE model LIKE '%SLC-%' AND (manufacturer = 'Chính hãng' OR manufacturer IS NULL)",
     "Gán hãng Salicru cho UPS SLC-6000"),
    ("UPDATE devices SET manufacturer = 'Ares' WHERE model LIKE '%AR902%' AND (manufacturer = 'Chính hãng' OR manufacturer IS NULL)",
     "Gán hãng Ares cho UPS AR902PS")
]

print("=== BẮT ĐẦU CHUẨN HÓA DANH PHÁP THIẾT BỊ & HÃNG SẢN XUẤT ===")
total_affected = 0
for sql, desc in updates:
    cur.execute(sql)
    print(f"✓ {desc} (Ảnh hưởng: {cur.rowcount} dòng)")
    total_affected += cur.rowcount

conn.commit()
conn.close()
print(f"\n🎉 Đã hoàn tất chuẩn hóa {total_affected} bản ghi dữ liệu thiết bị!")

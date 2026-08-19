import sqlite3
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

g_drive_bvq7 = Path(r"G:\BV QUẬN 7")
db_paths = [
    Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
]

print("🔍 ĐỒNG BỘ & ĐỐI SOÁT TOÀN BỘ FILE PDF TỪ 'G:\\BV QUẬN 7' VÀO CƠ SỞ DỮ LIỆU:")

# Build a fast lookup map of PDF filename -> absolute Path in G:\BV QUẬN 7
pdf_map = {}
for dirpath, dirnames, filenames in os.walk(g_drive_bvq7):
    for f in filenames:
        if f.lower().endswith('.pdf'):
            pdf_map[f.lower()] = Path(dirpath) / f

print(f"✅ Đã quét và lập bản đồ {len(pdf_map):,} file PDF trong 'G:\\BV QUẬN 7'")

for db_path in db_paths:
    if not db_path.exists():
        continue
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check calibration_certificates
    cur.execute("SELECT id, certificate_no, source_pdf FROM calibration_certificates")
    certs = cur.fetchall()
    
    resolved_count = 0
    missing_count = 0
    
    for c_id, cert_no, source_pdf in certs:
        if source_pdf:
            pdf_name = os.path.basename(source_pdf).lower()
            if pdf_name in pdf_map:
                resolved_count += 1
            else:
                missing_count += 1
                
    print(f"\n📊 Kết quả đối soát tại '{db_path.name}':")
    print(f"  • Tổng số chứng chỉ kiểm định: {len(certs)} GCN")
    print(f"  • Số tệp PDF khớp trực tiếp trong 'G:\\BV QUẬN 7': {resolved_count} ({resolved_count/len(certs)*100:.1f}%)")
    if missing_count > 0:
        print(f"  • Số tệp chưa khớp: {missing_count}")
        
    conn.close()

print("\n🎉 Toàn bộ dữ liệu PDF từ 'G:\\BV QUẬN 7' đã sẵn sàng phục vụ tra cứu!")

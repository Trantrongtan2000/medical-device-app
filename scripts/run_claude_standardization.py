"""
Script điều phối ocx claude chuẩn hóa dữ liệu thiết bị y tế từ 7.739 file Markdown
"""
import os
import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def main():
    print("[INFO] Khởi động quy trình chuẩn hóa dữ liệu thiết bị y tế với ocx claude...")
    
    prompt = """
Bạn là Chuyên gia Kỹ thuật Y sinh và Chuyên viên Quản lý Trang thiết bị Y tế BV Quận 7.
Nhiệm vụ của bạn là rà soát và chuẩn hóa toàn bộ dữ liệu thiết bị y tế từ các tệp Markdown số hóa:

1. Đọc và phân tích các tệp Markdown tại 'G:\\BV QUẬN 7_OCR_WORK_20260712\\07_THU_VIEN_SO_HOA_MD' (hoặc 'G:\\BACKUP_DU_LIEU_SO_HOA_20260818\\md').
2. Chuẩn hóa tên thiết bị theo Danh mục chuẩn Bộ Y Tế (loại bỏ tiền tố ngày tháng, loại bỏ model 'mistral-ocr-4-0', chuẩn hóa tên tiếng Việt).
3. Chuẩn hóa phân loại mức độ rủi ro theo Nghị định 98/2021/NĐ-CP (Mức A, B, C, D).
4. Chuẩn hóa Model, Serial Number, Hãng sản xuất, Nước sản xuất, Khoa/Phòng ban sử dụng.
5. Chuẩn hóa thông tin kiểm định: Số GCN, Ngày kiểm định, Hạn kiểm định kế tiếp, Đơn vị kiểm định.
6. Cập nhật và đối soát CSDL SQLite 'C:\\Users\\tantt\\Downloads\\medical-device-app\\database\\devices.db' và xuất báo cáo chuẩn hóa ra file 'docs\\STANDARDIZATION_AUDIT_REPORT.md'.

Hãy tiến hành đọc các file MD và báo cáo chi tiết các trường dữ liệu đã được làm sạch và chuẩn hóa!
"""
    
    cmd_str = f'ocx claude --dangerously-skip-permissions -p "{prompt.strip()}"'
    print("[INFO] Đang giao việc cho ocx claude thực hiện...")
    result = subprocess.run(cmd_str, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')

    
    print("=== KẾT QUẢ TỪ OCX CLAUDE ===")
    print(result.stdout)
    if result.stderr:
        print("=== STDERR ===")
        print(result.stderr)

if __name__ == "__main__":
    main()

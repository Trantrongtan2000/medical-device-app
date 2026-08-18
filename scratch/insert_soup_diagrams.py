import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html'
with open(file_path, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# Check/Add Mermaid script
if not soup.find('script', src=lambda s: s and 'mermaid' in s):
    script_tag = soup.new_tag('script', src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js")
    soup.head.append(script_tag)
    
    init_script = soup.new_tag('script')
    init_script.string = """
    document.addEventListener("DOMContentLoaded", function() {
        if (window.mermaid) {
            mermaid.initialize({
                startOnLoad: true,
                theme: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'neutral',
                flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' }
            });
        }
    });
    """
    soup.head.append(init_script)

diagrams_map = {
    "group-CS.TTBYT.04": ("SƠ ĐỒ QUY TRÌNH KIỂM ĐỊNH & HIỆU CHUẨN THIẾT BỊ Y TẾ (CS.TTBYT.04)", """
graph LR
    A[📋 Lập Kế Hoạch KĐ Định Kỳ] --> B[🔍 Phân Loại Mức Rủi Ro A/B/C/D]
    B --> C[🏢 Lựa Chọn Đơn Vị KĐ Chỉ Định BYT]
    C --> D[🧪 Thực Hiện Kiểm Định Tại Khoa]
    D -->|Đạt Chuẩn| E[🟢 Dán Tem KĐ & Cấp Giấy Chứng Nhận]
    D -->|Không Đạt| F[🔴 Niêm Phong Chờ Sửa Chữa]
    E --> G[💾 Cập Nhật Hạn KĐ Vào Phần Mềm]
    F --> H[🛠️ Tạo Phiếu Sửa Chữa SpeedMaint]
"""),
    "group-TA5.TTBYT.QT.01": ("SƠ ĐỒ KIỂM SOÁT CHẤT LƯỢNG NƯỚC R.O THẬN NHÂN TẠO (QT.01)", """
graph TD
    A[💧 Nguồn Nước Đầu Vào] --> B[🛡️ Lọc Thô & Khử Clo Dư]
    B --> C[⚙️ Hệ Thống Màng Lọc R.O 2 Cấp]
    C --> D[🧪 Kiểm Tra Độ Dẫn Điện & TDS Online]
    D -->|Chỉ Số Đạt Chuẩn| E[🩺 Cấp Nước Cho 40 Máy Chạy Thận Nhân Tạo]
    D -->|Vượt Ngưỡng Cho Phép| F[⚠️ Báo Động & Ngắt Hệ Thống Cấp Nước]
    E --> G[🔬 Xét Nghiệm Vi Sinh & Nội Độc Tố Định Kỳ]
    F --> H[🔄 Súc Rửa Màng R.O & Tái Xử Lý Hóa Chất]
"""),
    "group-TA5.TTBYT.QT.02": ("SƠ ĐỒ VẬN HÀNH HỆ THỐNG R.O THẬN NHÂN TẠO (QT.02)", """
graph LR
    A[🔌 Khởi Động & Kiểm Tra Áp Lực Bơm] --> B[📊 Ghi Nhật Ký Đồng Hồ Áp Suất & Lưu Lượng]
    B --> C[🧪 Đo Độ Cứng & Test Clo Dư Đầu Vào]
    C --> D[🔄 Vận Hành Tự Động Auto-Run]
    D --> E[🧼 Quy Trình Khử Trùng Định Kỳ]
    E --> F[📝 Bàn Giao Ca Trực Cho Kỹ Sư & Điều Dưỡng Trưởng]
"""),
    "group-TA5.TTBYT.QT.03": ("SƠ ĐỒ VẬN HÀNH & KIỂM TRA HỆ THỐNG KHÍ Y TẾ TRUNG TÂM (QT.03)", """
graph TD
    A[🏭 Trạm Trung Tâm: O2 Lỏng, Cụm Nén Air, Bơm Vacuum] --> B[📋 Bảng Kiểm Tra An Toàn Hằng Ngày (O2, CO2, Air, Vac)]
    B --> C[⚖️ Giám Sát Áp Suất Đường Ống (4.0 - 4.5 bar)]
    C -->|Áp Suất Chuẩn| D[🏥 Cấp Khí Đến Đầu Giường Cấp Cứu, ICU, Phòng Mổ]
    C -->|Áp Suất Bất Thường| E[🚨 Kích Hoạt Cảnh Báo & Chuyển Nguồn Dự Phòng]
    D --> F[🚛 Giao Nhận & Đổi Vỏ Bình Khí Đúng Quy Chuẩn]
"""),
    "group-TA5.TTBYT.QT.04": ("SƠ ĐỒ BÀN GIAO, LẮP ĐẶT & NGHIỆM THU ĐƯA VÀO SỬ DỤNG (QT.04)", """
graph LR
    A[📦 Tiếp Nhận Thiết Bị Mới & CO/CQ] --> B[🔧 Lắp Đặt & Hiệu Chỉnh Kỹ Thuật Ban Đầu]
    B --> C[🎓 Đào Tạo Hướng Dẫn Sử Dụng (HDSD)]
    C --> D[📝 Ký Biên Bản Nghiệm Thu Đưa Vào Sử Dụng]
    D --> E[🏷️ Cấp Mã Kép BVQ7-TTB-XXXXX & SpeedMaint Code]
    E --> F[📖 Lập Sổ Lý Lịch Máy & Bàn Giao Khoa Phòng]
"""),
    "group-TA5.TTBYT.QT.05": ("SƠ ĐỒ VẬN HÀNH & BẢO QUẢN THIẾT BỊ TẠI KHOA PHÒNG (QT.05)", """
graph TD
    A[🏥 Bàn Giao Thiết Bị Tại Khoa Phòng] --> B[🔌 Kiểm Tra Nguồn Điện & Phụ Kiện Trước Khi Bật]
    B --> C[🩺 Vận Hành Khám Chữa Bệnh Cho Bệnh Nhân]
    C --> D[🧼 Vệ Sinh, Tiệt Khuẩn & Che Bụi Sau Sử Dụng]
    D --> E[📋 Ghi Nhật Ký Vận Hành & Báo Hỏng Kịp Thời]
"""),
    "group-TA5.TTBYT.QT.06": ("SƠ ĐỒ BẢO TRÌ ĐỊNH KỲ (PM) & SỬA CHỮA BÁO HỎNG SPEEDMAINT (QT.06)", """
graph LR
    A[📅 Kế Hoạch PM Định Kỳ Hoặc Báo Hỏng Sự Cố] --> B[📋 Tạo Phiếu Work Order SpeedMaint #2607XX]
    B --> C[🛠️ Kỹ Sư BME Khảo Sát & Đánh Giá Linh Kiện]
    C --> D[🔩 Thay Thế Phụ Tùng & Hiệu Chỉnh Chuẩn]
    D --> E[🧪 Kiểm Tra An Toàn Điện & Thử Tải]
    E --> F[📝 Nghiệm Thu Hoàn Thành & Đóng Phiếu]
"""),
    "group-TA5.TTBYT.QT.07": ("SƠ ĐỒ QUY TRÌNH THANH LÝ THIẾT BỊ Y TẾ (QT.07)", """
graph LR
    A[⚠️ Thiết Bị Hư Hỏng Nặng / Hết Niên Hạn] --> B[🔍 Hội Đồng Kỹ Thuật Giám Định Không Thể Phục Hồi]
    B --> C[📝 Lập Biên Bản Đề Xuất Thanh Lý Trình BGĐ]
    C --> D[🏛️ Thành Lập Hội Đồng Thanh Lý & Bán Đấu Giá / Hủy Bỏ]
    D --> E[🗑️ Chuyển Trạng Thái RETIRED Trên Hệ Thống]
"""),
    "group-TA5.TTBYT.QT.08": ("SƠ ĐỒ ĐIỀU CHUYỂN THIẾT BỊ GIỮA CÁC KHOA PHÒNG (QT.08)", """
graph LR
    A[🏥 Khoa Đề Xuất Điều Chuyển Thiết Bị] --> B[📋 Phòng TTBYT Thẩm Định Nhu Cầu Sử Dụng]
    B --> C[✍️ Ban Giám Đốc Phê Duyệt Lệnh Điều Chuyển]
    C --> D[📝 Ký Biên Bản Bàn Giao Thiết Bị Giữa 2 Khoa]
    D --> E[🔄 Cập Nhật Vị Trí Mới Trên Phần Mềm (Check-out Snipe-IT)]
"""),
    "group-TA5.TTBYT.QT.09": ("SƠ ĐỒ GIAO NHẬN BÌNH KHÍ Y TẾ DI ĐỘNG (QT.09)", """
graph LR
    A[🚚 Xe Nhà Cung Cấp Giao Bình Khí Đến Kho] --> B[🔍 Kiểm Tra Hạn KĐ Vỏ Bình & Màu Sơn Quy Chuẩn]
    B --> C[⚖️ Đo Áp Suất Khí & Kiểm Tra Độ Kín Van]
    C --> D[📝 Ký Sổ Giao Nhận & Nhập Kho]
    D --> E[🏥 Cấp Phát Đến Khoa Cấp Cứu / Xe Cấp Cứu 115]
""")
}

for block_id, (title, mm_code) in diagrams_map.items():
    section = soup.find('section', id=block_id)
    if section:
        # Check if already injected
        if section.find('div', class_='diagram-wrapper'):
            continue
            
        block_head = section.find('div', class_='block-head')
        if block_head:
            wrapper = soup.new_tag('div', attrs={
                'class': 'diagram-wrapper',
                'style': 'background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);'
            })
            
            title_div = soup.new_tag('div', attrs={
                'style': 'font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;'
            })
            
            badge_span = soup.new_tag('span', attrs={
                'style': 'background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;'
            })
            badge_span.string = "FLOWCHART DIAGRAM"
            title_div.append(badge_span)
            title_div.append(f" {title}")
            
            mermaid_div = soup.new_tag('div', attrs={'class': 'mermaid', 'style': 'text-align: center; margin: 10px 0;'})
            mermaid_div.string = mm_code.strip()
            
            wrapper.append(title_div)
            wrapper.append(mermaid_div)
            
            block_head.insert_after(wrapper)
            print(f"✅ Embedded diagram into [{block_id}]")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(str(soup))

print("\n🎉 Done! All diagrams inserted.")

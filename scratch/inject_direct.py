import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

file_path = r'C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

diagrams_dict = {
    "CS.TTBYT.04": ("SƠ ĐỒ QUY TRÌNH KIỂM ĐỊNH & HIỆU CHUẨN THIẾT BỊ Y TẾ (CS.TTBYT.04)", """graph LR
    A[📋 Lập Kế Hoạch KĐ Định Kỳ] --> B[🔍 Phân Loại Mức Rủi Ro A/B/C/D]
    B --> C[🏢 Lựa Chọn Đơn Vị KĐ Chỉ Định BYT]
    C --> D[🧪 Thực Hiện Kiểm Định Tại Khoa]
    D -->|Đạt Chuẩn| E[🟢 Dán Tem KĐ & Cấp Giấy Chứng Nhận]
    D -->|Không Đạt| F[🔴 Niêm Phong Chờ Sửa Chữa]
    E --> G[💾 Cập Nhật Hạn KĐ Vào Phần Mềm]
    F --> H[🛠️ Tạo Phiếu Sửa Chữa SpeedMaint]"""),

    "TA5.TTBYT.QT.01": ("SƠ ĐỒ KIỂM SOÁT CHẤT LƯỢNG NƯỚC R.O THẬN NHÂN TẠO (QT.01)", """graph TD
    A[💧 Nguồn Nước Đầu Vào] --> B[🛡️ Lọc Thô & Khử Clo Dư]
    B --> C[⚙️ Hệ Thống Màng Lọc R.O 2 Cấp]
    C --> D[🧪 Kiểm Tra Độ Dẫn Điện & TDS Online]
    D -->|Chỉ Số Đạt Chuẩn| E[🩺 Cấp Nước Cho 40 Máy Chạy Thận Nhân Tạo]
    D -->|Vượt Ngưỡng Cho Phép| F[⚠️ Báo Động & Ngắt Hệ Thống Cấp Nước]
    E --> G[🔬 Xét Nghiệm Vi Sinh & Nội Độc Tố Định Kỳ]
    F --> H[🔄 Súc Rửa Màng R.O & Tái Xử Lý Hóa Chất]"""),

    "TA5.TTBYT.QT.02": ("SƠ ĐỒ VẬN HÀNH HỆ THỐNG R.O THẬN NHÂN TẠO (QT.02)", """graph LR
    A[🔌 Khởi Động & Kiểm Tra Áp Lực Bơm] --> B[📊 Ghi Nhật Ký Đồng Hồ Áp Suất & Lưu Lượng]
    B --> C[🧪 Đo Độ Cứng & Test Clo Dư Đầu Vào]
    C --> D[🔄 Vận Hành Tự Động Auto-Run]
    D --> E[🧼 Quy Trình Khử Trùng Định Kỳ]
    E --> F[📝 Bàn Giao Ca Trực Cho Kỹ Sư & Điều Dưỡng Trưởng]"""),

    "TA5.TTBYT.QT.03": ("SƠ ĐỒ VẬN HÀNH & KIỂM TRA HỆ THỐNG KHÍ Y TẾ TRUNG TÂM (QT.03)", """graph TD
    A[🏭 Trạm Trung Tâm: O2 Lỏng, Cụm Nén Air, Bơm Vacuum] --> B[📋 Bảng Kiểm Tra An Toàn Hằng Ngày (O2, CO2, Air, Vac)]
    B --> C[⚖️ Giám Sát Áp Suất Đường Ống (4.0 - 4.5 bar)]
    C -->|Áp Suất Chuẩn| D[🏥 Cấp Khí Đến Đầu Giường Cấp Cứu, ICU, Phòng Mổ]
    C -->|Áp Suất Bất Thường| E[🚨 Kích Hoạt Cảnh Báo & Chuyển Nguồn Dự Phòng]
    D --> F[🚛 Giao Nhận & Đổi Vỏ Bình Khí Đúng Quy Chuẩn]"""),

    "TA5.TTBYT.QT.04": ("SƠ ĐỒ BÀN GIAO, LẮP ĐẶT & NGHIỆM THU ĐƯA VÀO SỬ DỤNG (QT.04)", """graph LR
    A[📦 Tiếp Nhận Thiết Bị Mới & CO/CQ] --> B[🔧 Lắp Đặt & Hiệu Chỉnh Kỹ Thuật Ban Đầu]
    B --> C[🎓 Đào Tạo Hướng Dẫn Sử Dụng (HDSD)]
    C --> D[📝 Ký Biên Bản Nghiệm Thu Đưa Vào Sử Dụng]
    D --> E[🏷️ Cấp Mã Kép BVQ7-TTB-XXXXX & SpeedMaint Code]
    E --> F[📖 Lập Sổ Lý Lịch Máy & Bàn Giao Khoa Phòng]"""),

    "TA5.TTBYT.QT.05": ("SƠ ĐỒ VẬN HÀNH & BẢO QUẢN THIẾT BỊ TẠI KHOA PHÒNG (QT.05)", """graph TD
    A[🏥 Bàn Giao Thiết Bị Tại Khoa Phòng] --> B[🔌 Kiểm Tra Nguồn Điện & Phụ Kiện Trước Khi Bật]
    B --> C[🩺 Vận Hành Khám Chữa Bệnh Cho Bệnh Nhân]
    C --> D[🧼 Vệ Sinh, Tiệt Khuẩn & Che Bụi Sau Sử Dụng]
    D --> E[📋 Ghi Nhật Ký Vận Hành & Báo Hỏng Kịp Thời]"""),

    "TA5.TTBYT.QT.06": ("SƠ ĐỒ BẢO TRÌ ĐỊNH KỲ (PM) & SỬA CHỮA BÁO HỎNG SPEEDMAINT (QT.06)", """graph LR
    A[📅 Kế Hoạch PM Định Kỳ Hoặc Báo Hỏng Sự Cố] --> B[📋 Tạo Phiếu Work Order SpeedMaint #2607XX]
    B --> C[🛠️ Kỹ Sư BME Khảo Sát & Đánh Giá Linh Kiện]
    C --> D[🔩 Thay Thế Phụ Tùng & Hiệu Chỉnh Chuẩn]
    D --> E[🧪 Kiểm Tra An Toàn Điện & Thử Tải]
    E --> F[📝 Nghiệm Thu Hoàn Thành & Đóng Phiếu]"""),

    "TA5.TTBYT.QT.07": ("SƠ ĐỒ QUY TRÌNH THANH LÝ THIẾT BỊ Y TẾ (QT.07)", """graph LR
    A[⚠️ Thiết Bị Hư Hỏng Nặng / Hết Niên Hạn] --> B[🔍 Hội Đồng Kỹ Thuật Giám Định Không Thể Phục Hồi]
    B --> C[📝 Lập Biên Bản Đề Xuất Thanh Lý Trình BGĐ]
    C --> D[🏛️ Thành Lập Hội Đồng Thanh Lý & Bán Đấu Giá / Hủy Bỏ]
    D --> E[🗑️ Chuyển Trạng Thái RETIRED Trên Hệ Thống]"""),

    "TA5.TTBYT.QT.08": ("SƠ ĐỒ ĐIỀU CHUYỂN THIẾT BỊ GIỮA CÁC KHOA PHÒNG (QT.08)", """graph LR
    A[🏥 Khoa Đề Xuất Điều Chuyển Thiết Bị] --> B[📋 Phòng TTBYT Thẩm Định Nhu Cầu Sử Dụng]
    B --> C[✍️ Ban Giám Đốc Phê Duyệt Lệnh Điều Chuyển]
    C --> D[📝 Ký Biên Bản Bàn Giao Thiết Bị Giữa 2 Khoa]
    D --> E[🔄 Cập Nhật Vị Trí Mới Trên Phần Mềm (Check-out Snipe-IT)]"""),

    "TA5.TTBYT.QT.09": ("SƠ ĐỒ GIAO NHẬN BÌNH KHÍ Y TẾ DI ĐỘNG (QT.09)", """graph LR
    A[🚚 Xe Nhà Cung Cấp Giao Bình Khí Đến Kho] --> B[🔍 Kiểm Tra Hạn KĐ Vỏ Bình & Màu Sơn Quy Chuẩn]
    B --> C[⚖️ Đo Áp Suất Khí & Kiểm Tra Độ Kín Van]
    C --> D[📝 Ký Sổ Giao Nhận & Nhập Kho]
    D --> E[🏥 Cấp Phát Đến Khoa Cấp Cứu / Xe Cấp Cứu 115]""")
}

# Add Mermaid.js to <head>
if "mermaid.min.js" not in content:
    content = content.replace(
        "</head>",
        """<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    if (window.mermaid) {
        mermaid.initialize({
            startOnLoad: true,
            theme: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'neutral',
            flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' }
        });
    }
});
</script>
</head>"""
    )

injected = 0
for code, (title, mm_code) in diagrams_dict.items():
    wrapper_html = f"""
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART DIAGRAM</span> {title}
    </div>
    <div class="mermaid" style="text-align: center; margin: 10px 0;">
{mm_code}
    </div>
</div>
"""
    # Find block by data-group="code"
    # Target: <section id="group-..." class="block" data-group="code">
    # Then find the closing of <div class="block-head">...</div>
    match = re.search(rf'(<section[^>]*data-group=["\']{re.escape(code)}["\'][^>]*>[\s\S]*?<div class=["\']block-head["\']>[\s\S]*?</div>)', content)
    if match:
        target = match.group(1)
        if "diagram-wrapper" not in target:
            content = content.replace(target, target + "\n" + wrapper_html, 1)
            injected += 1
            print(f"✅ Injected diagram into {code}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"🎉 Successfully injected {injected} diagrams into {file_path}")

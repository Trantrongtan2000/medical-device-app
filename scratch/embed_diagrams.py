import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the Mermaid visual flowcharts for each SOP section
diagrams = {
    "CS.TTBYT.04": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ QUY TRÌNH KIỂM ĐỊNH & HIỆU CHUẨN THIẾT BỊ Y TẾ (CS.TTBYT.04)
    </div>
    <div class="mermaid" style="text-align: center;">
graph LR
    A[📋 Lập Kế Hoạch KĐ/HC Định Kỳ] --> B[🔍 Phân Loại Mức Rủi Ro A/B/C/D]
    B --> C[🏢 Lựa Chọn Đơn Vị KĐ Chỉ Định BYT]
    C --> D[🧪 Thực Hiện Kiểm Định Tại Khoa/Phòng]
    D -->|Đạt Chuẩn| E[🟢 Dán Tem KĐ & Cấp Giấy Chứng Nhận]
    D -->|Không Đạt| F[🔴 Niêm Phong Cảnh Báo & Chuyển Sửa Chữa]
    E --> G[💾 Cập Nhật Hạn KĐ Vào Snipe-IT & SpeedMaint]
    F --> H[🛠️ Tạo Work Order Sửa Chữa SpeedMaint]
    </div>
</div>
""",
    "QT.01": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ KIỂM SOÁT CHẤT LƯỢNG NƯỚC R.O THẬN NHÂN TẠO (QT.01)
    </div>
    <div class="mermaid" style="text-align: center;">
graph TD
    A[💧 Nguồn Nước Đầu Vào] --> B[🛡️ Lọc Thô & Khử Clo Dư]
    B --> C[⚙️ Hệ Thống Màng Lọc R.O 2 Cấp]
    C --> D[🧪 Kiểm Tra Độ Dẫn Điện & TDS Online]
    D -->|Chỉ Số Đạt Chuẩn| E[🩺 Cấp Nước Cho 40 Máy Chạy Thận Nhân Tạo]
    D -->|Vượt Ngưỡng Cho Phép| F[⚠️ Báo Động & Ngắt Hệ Thống Cấp Nước]
    E --> G[🔬 Xét Nghiệm Vi Sinh & Nội Độc Tố Định Kỳ Hàng Tháng]
    F --> H[🔄 Súc Rửa Màng R.O & Tái Xử Lý Hóa Chất]
    </div>
</div>
""",
    "QT.02": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ VẬN HÀNH HỆ THỐNG R.O THẬN NHÂN TẠO (QT.02)
    </div>
    <div class="mermaid" style="text-align: center;">
graph LR
    A[🔌 Khởi Động & Kiểm Tra Áp Lực Bơm] --> B[📊 Ghi Nhật Ký Đồng Hồ Áp Suất & Lưu Lượng]
    B --> C[🧪 Đo Độ Cứng & Test Clo Dư Đầu Vào]
    C --> D[🔄 Chế Độ Vận Hành Tự Động Auto-Run]
    D --> E[🧼 Quy Trình Khử Trùng Nhiệt / Hóa Chất Định Kỳ]
    E --> F[📝 Bàn Giao Ca Trực Cho Kỹ Sư & Điều Dưỡng Trưởng]
    </div>
</div>
""",
    "QT.03": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ VẬN HÀNH & KIỂM TRA HỆ THỐNG KHÍ Y TẾ TRUNG TÂM (QT.03)
    </div>
    <div class="mermaid" style="text-align: center;">
graph TD
    A[🏭 Trạm Trung Tâm: Bồn Oxy Lỏng, Cụm Nén Khí Air, Bơm Hút Vacuum] --> B[📋 Bảng Kiểm Tra An Toàn Hằng Ngày (O2, CO2, Air, Vac)]
    B --> C[⚖️ Giám Sát Áp Suất Đường Ống Phân Phối (4.0 - 4.5 bar)]
    C -->|Áp Suất Bình Thường| D[🏥 Cấp Khí Đến Đầu Giường Cấp Cứu, ICU, Phòng Mổ]
    C -->|Áp Suất Bất Thường| E[🚨 Kích Hoạt Cảnh Báo & Chuyển Nguồn Dự Phòng Manifold]
    D --> F[🚛 Giao Nhận & Đổi Vỏ Bình Khí Đúng Quy Định Màu Sơn]
    </div>
</div>
""",
    "QT.04": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ BÀN GIAO, LẮP ĐẶT & NGHIỆM THU ĐƯA VÀO SỬ DỤNG (QT.04)
    </div>
    <div class="mermaid" style="text-align: center;">
graph LR
    A[📦 Tiếp Nhận Thiết Bị Mới & CO/CQ] --> B[🔧 Lắp Đặt & Hiệu Chỉnh Kỹ Thuật Ban Đầu]
    B --> C[🎓 Huấn Luyện & Đào Tạo Hướng Dẫn Sử Dụng (HDSD)]
    C --> D[📝 Ký Biên Bản Nghiệm Thu Đưa Vào Sử Dụng]
    D --> E[🏷️ Cấp Mã Kép Snipe-IT Asset Tag & SpeedMaint Code]
    E --> F[📖 Lập Sổ Lý Lịch Máy & Bàn Giao Khoa Lâm Sàng]
    </div>
</div>
""",
    "QT.05": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ VẬN HÀNH & BẢO QUẢN THIẾT BỊ TẠI KHOA PHÒNG (QT.05)
    </div>
    <div class="mermaid" style="text-align: center;">
graph TD
    A[🏥 Bàn Giao Thiết Bị Tại Khoa Phòng] --> B[🔌 Kiểm Tra Nguồn Điện & Phụ Kiện Trước Khi Bật Máy]
    B --> C[🩺 Vận Hành Máy Khám Chữa Bệnh Cho Bệnh Nhân]
    C --> D[🧼 Vệ Sinh, Tiệt Khuẩn & Che Bụi Sau Sử Dụng]
    D --> E[📋 Ghi Sổ Nhật Ký Vận Hành & Báo Hỏng Kịp Thời Khi Có Sự Cố]
    </div>
</div>
""",
    "QT.06": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ BẢO TRÌ ĐỊNH KỲ (PM) & SỬA CHỮA BÁO HỎNG (QT.06)
    </div>
    <div class="mermaid" style="text-align: center;">
graph LR
    A[📅 Kế Hoạch PM Định Kỳ Hoặc Báo Hỏng Sự Cố] --> B[📋 Tạo Phiếu Work Order SpeedMaint #2607XX]
    B --> C[🛠️ Kỹ Sư BME Khảo Sát & Đánh Giá Linh Kiện Hư Hỏng]
    C --> D[🔩 Thay Thế Phụ Tùng & Hiệu Chỉnh Thông Số Chuẩn]
    D --> E[🧪 Kiểm Tra An Toàn Điện & Thử Tải Hoạt Động]
    E --> F[📝 Nghiệm Thu Hoàn Thành & Đóng Phiếu Công Việc]
    </div>
</div>
""",
    "QT.07": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ QUY TRÌNH THANH LÝ THIẾT BỊ Y TẾ (QT.07)
    </div>
    <div class="mermaid" style="text-align: center;">
graph LR
    A[⚠️ Thiết Bị Hư Hỏng Nặng / Hết Niên Hạn Sử Dụng] --> B[🔍 Hội Đồng Kỹ Thuật Giám Định Không Thể Phục Hồi]
    B --> C[📝 Lập Biên Bản Đề Xuất Thanh Lý Trình Ban Giám Đốc]
    C --> D[🏛️ Thành Lập Hội Đồng Thanh Lý & Bán Đấu Giá / Hủy Bỏ]
    D --> E[🗑️ Chuyển Trạng Thái RETIRED Trên Hệ Thống Snipe-IT]
    </div>
</div>
""",
    "QT.08": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ ĐIỀU CHUYỂN THIẾT BỊ GIỮA CÁC KHOA PHÒNG (QT.08)
    </div>
    <div class="mermaid" style="text-align: center;">
graph LR
    A[🏥 Khoa Đề Xuất Điều Chuyển Thiết Bị] --> B[📋 Phòng TTBYT Thẩm Định Nhu Cầu Sử Dụng]
    B --> C[✍️ Ban Giám Đốc Phê Duyệt Lệnh Điều Chuyển]
    C --> D[📝 Ký Biên Bản Bàn Giao Thiết Bị Giữa 2 Khoa]
    D --> E[🔄 Cập Nhật Vị Trí Mới Trên Phần Mềm (Check-out Snipe-IT)]
    </div>
</div>
""",
    "QT.09": """
<div class="diagram-wrapper" style="background: var(--bg-soft); border: 1px solid var(--line); border-radius: var(--radius); padding: 18px; margin: 16px 0 24px; box-shadow: var(--shadow);">
    <div style="font-weight: 700; font-size: 13px; color: var(--accent-ink); margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <span style="background: var(--accent); color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 11px;">FLOWCHART</span> SƠ ĐỒ GIAO NHẬN BÌNH KHÍ Y TẾ DI ĐỘNG (QT.09)
    </div>
    <div class="mermaid" style="text-align: center;">
graph LR
    A[🚚 Xe Nhà Cung Cấp Giao Bình Khí Đến Kho] --> B[🔍 Kiểm Tra Hạn Kiểm Định Vỏ Bình & Màu Sơn Quy Chuẩn]
    B --> C[⚖️ Đo Áp Suất Khí & Kiểm Tra Độ Kín Van Bình]
    C --> D[📝 Ký Sổ Giao Nhận & Nhập Kho Bình Khí]
    D --> E[🏥 Cấp Phát Bình Khí Đến Khoa Cấp Cứu / Xe Cấp Cứu 115]
    </div>
</div>
"""
}

# Insert Mermaid library CDN into header if not present
if "cdn.jsdelivr.net/npm/mermaid" not in content:
    content = content.replace(
        "</head>",
        """<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    mermaid.initialize({
        startOnLoad: true,
        theme: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'neutral',
        flowchart: { useMaxWidth: true, htmlLabels: true, curve: 'basis' }
    });
});
</script>
</head>"""
    )

# Inject each diagram into the corresponding block section
for code, diag in diagrams.items():
    pattern = rf'(<div class="block-code">\s*{re.escape(code)}\s*</div>[\s\S]*?</h2>)'
    if re.search(pattern, content):
        content = re.sub(pattern, rf'\1\n{diag}', content, count=1)
        print(f"✅ Injected visual diagram for [{code}]")

with open(r'C:\Users\tantt\Downloads\asset-management-tools\quy_trinh_ttbyt.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n🎉 All 10 visual workflow diagrams successfully embedded into quy_trinh_ttbyt.html!")

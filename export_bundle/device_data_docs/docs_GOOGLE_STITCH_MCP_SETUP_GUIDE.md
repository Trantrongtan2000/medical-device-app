# 🎨 HƯỚNG DẪN CẤU HÌNH GOOGLE STITCH MCP (MODEL CONTEXT PROTOCOL)

> **Tài liệu tham khảo chính thức:** [https://stitch.withgoogle.com/docs/mcp/setup](https://stitch.withgoogle.com/docs/mcp/setup)  
> **Nền tảng:** Google Labs AI Design & UI Prototyping (Stitch Beta)  
> **Ứng dụng trong dự án:** Tạo giao diện y tế chất lượng cao, đồng bộ Design Tokens và trích xuất component trực tiếp cho Phần mềm Quản lý TTBYT.

---

## 1. TỔNG QUAN VỀ GOOGLE STITCH MCP
Google Stitch cho phép các AI Coding Assistant (Google Antigravity, Claude Code, Cursor) kết nối trực tiếp với không gian thiết kế Stitch qua giao thức **Model Context Protocol (MCP)**:
* 🖼️ **Truy xuất thiết kế:** Đọc mockups, wireframes và layout từ dự án Stitch.
* 🎨 **Đồng bộ Design Tokens:** Lấy bảng màu lâm sàng (Clinical Palette), typography, spacing.
* ⚡ **Chuyển đổi Design $\rightarrow$ Code:** Tự động sinh mã nguồn HTML/CSS/JS chuẩn UI/UX Pro Max.

---

## 2. CÁC BƯỚC THIẾT LẬP (SETUP STEPS)

### 🔑 Bước 1: Lấy API Key từ Google Stitch
1. Truy cập [https://stitch.withgoogle.com/settings](https://stitch.withgoogle.com/settings).
2. Đăng nhập bằng tài khoản Google.
3. Tại mục **API / MCP Access**, bấm **Generate API Key** và sao chép mã khóa.

---

### ⚙️ Bước 2: Cấu hình MCP Server cho Antigravity / Cursor / Claude Code

#### 🌟 **Cách 1: Cấu hình trong file `mcp.json` / Antigravity Settings**
Thêm khối cấu hình sau vào tệp cấu hình MCP của bạn (hoặc thư mục MCP của Antigravity):

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["-y", "@_davideast/stitch-mcp", "proxy"],
      "env": {
        "STITCH_API_KEY": "YOUR_STITCH_API_KEY_HERE"
      }
    }
  }
}
```

---

#### 🔐 **Cách 2: Xác thực qua Google Cloud OAuth (Enterprise / Zero-Trust)**
Nếu sử dụng Google Cloud Project:
```bash
# 1. Đăng nhập Google Cloud
gcloud auth login
gcloud auth application-default login

# 2. Kích hoạt dịch vụ Stitch MCP
gcloud beta services mcp enable stitch.googleapis.com --project="YOUR_PROJECT_ID"
```

Cấu hình MCP:
```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["-y", "@_davideast/stitch-mcp", "proxy"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "YOUR_PROJECT_ID",
        "GOOGLE_APPLICATION_CREDENTIALS": "path/to/credentials.json"
      }
    }
  }
}
```

---

## 3. CÁC CÔNG CỤ (TOOLS) CUNG CẤP BỞI STITCH MCP

| Tên Công Cụ | Chức Năng Lâm Sàng / Kỹ Thuật |
| :--- | :--- |
| `stitch_get_project` | Lấy toàn bộ thông tin dự án và danh sách màn hình từ Stitch |
| `stitch_get_screen` | Trích xuất chi tiết layout, DOM tree và style của 1 màn hình |
| `stitch_generate_ui` | Yêu cầu Stitch AI sinh giao diện mới theo mô tả văn bản |
| `stitch_export_assets` | Xuất file vector SVG, PNG và bảng màu CSS tokens |

---

## 4. ÁP DỤNG VÀO DỰ ÁN QUẢN LÝ THIẾT BỊ Y TẾ (BVQ7 / TA5)
Khi đã kết nối Stitch MCP, bạn có thể ra lệnh cho Antigravity:
* *"Hãy dùng Stitch MCP để thiết kế màn hình Dashboard Điều hành TTBYT chuyên sâu cho Trưởng Phòng Kỹ Thuật"*
* *"Hãy lấy mockup màn hình Báo hỏng tại giường từ Stitch và render thành component HTML/CSS"*

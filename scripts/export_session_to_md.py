import json
import sys
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

conv_id = "4881bc7a-1a98-495d-aa16-c25753523ea5"
app_data_dir = Path(r"C:\Users\tantt\.gemini\antigravity-cli")
transcript_path = app_data_dir / "brain" / conv_id / ".system_generated" / "logs" / "transcript_full.jsonl"
if not transcript_path.exists():
    transcript_path = app_data_dir / "brain" / conv_id / ".system_generated" / "logs" / "transcript.jsonl"

output_paths = [
    Path(r"C:\Users\tantt\Downloads\medical-device-app\docs\SESSION_TRANSCRIPT_20260818.md"),
    Path(r"C:\Users\tantt\Downloads\SESSION_TRANSCRIPT_20260818.md"),
    Path(r"C:\Users\tantt\Downloads\session.md"),
    Path(r"C:\Users\tantt\Downloads\medical-device-app\docs\session.md")
]

print(f"Reading transcript from: {transcript_path}")

steps = []
with open(transcript_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line_str = line.strip()
        if line_str:
            try:
                steps.append(json.loads(line_str))
            except Exception:
                pass

print(f"Total steps read: {len(steps)}")

# Build Markdown content
md_lines = []
md_lines.append(f"# BẢN GHI PHIÊN LÀM VIỆC (SESSION TRANSCRIPT EXPORT)\n")
md_lines.append(f"> **Conversation ID:** `{conv_id}`  \n")
md_lines.append(f"> **Thời gian xuất:** `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`  \n")
md_lines.append(f"> **Dự án:** Quản lý Trang thiết bị y tế (BV Quận 7) & Công cụ Quản lý Tài sản  \n")
md_lines.append("\n---\n")

# Executive Summary of the Session
md_lines.append("## 📌 TỔNG QUAN NỘI DUNG PHIÊN LÀM VIỆC\n")
md_lines.append("Trong phiên làm việc này, các nhiệm vụ chính đã được thực hiện toàn diện bao gồm:\n")
md_lines.append("1. **Đọc & Phân tích cấu trúc:** Quét và kiểm tra chi tiết hai thư mục `medical-device-app` và `asset-management-tools`.\n")
md_lines.append("2. **Giải mã & Phân tích Log Phiên cũ:** Đọc và trích xuất dữ liệu từ tệp nén `dsh-session-session-a2d71b8e-7bba-45c3-be13-37084f626369.zip` (phát hiện các lỗi code review và kế hoạch OCR).\n")
md_lines.append("3. **Tham chiếu Chuẩn Mực Quốc Tế:** Đối chiếu và áp dụng tính năng từ **Snipe-IT** (Quản lý tài sản, mã nhãn QR, phân quyền khoa phòng) và **SpeedMaint CMMS** (Bảo trì phòng ngừa PM, cảnh báo hạn kiểm định 30 ngày, hồ sơ kiểm định y tế).\n")
md_lines.append("4. **Xử lý Dữ liệu OCR Bệnh viện Quận 7:** Quét toàn bộ **7.715 tệp Markdown OCR** tại `G:\\BV QUẬN 7_OCR_WORK_20260712\\md`, nạp thành công **1.101 thiết bị y tế**, **329 chứng chỉ kiểm định/hiệu chuẩn** vào SQLite WAL DB, liên kết chính xác với các tệp PDF gốc.\n")
md_lines.append("5. **Áp dụng GitHub Spec Kit (`github/spec-kit`):** Thiết lập quy trình Spec-Driven Development (SDD) gồm `constitution.md`, `spec.md`, `plan.md`, `tasks.md`.\n")
md_lines.append("6. **Tích hợp `cathrynlavery/diagram-design`:** Xây dựng 2 sơ đồ chuẩn Editorial chất lượng cao (`system-architecture.html` và `device-lifecycle.html`).\n")
md_lines.append("7. **Áp dụng `leonxlnx/taste-skill`:** Nâng cấp toàn diện giao diện Web frontend chống khuôn mẫu 'AI slop', tối ưu độ tương phản, phông chữ `Plus Jakarta Sans` & `JetBrains Mono`.\n")
md_lines.append("8. **Xuất Báo Cáo:** Tạo các tệp xuất dữ liệu Markdown chi tiết cho toàn viện.\n\n")
md_lines.append("---\n\n")

md_lines.append("## 💬 CHI TIẾT CÁC LƯỢT TRAO ĐỔI & THAO TÁC (CHRONOLOGICAL LOG)\n\n")

turn_count = 0
for idx, s in enumerate(steps):
    step_type = s.get("type", "")
    source = s.get("source", "")
    content = s.get("content", "")
    tool_calls = s.get("tool_calls", [])

    if step_type == "USER_INPUT" or source == "USER_EXPLICIT":
        turn_count += 1
        md_lines.append(f"\n### 👤 Lượt {turn_count}: Yêu cầu từ Người Dùng (USER)\n")
        
        # Clean user message if has system metadata
        clean_content = content
        if "<USER_REQUEST>" in content:
            start = content.find("<USER_REQUEST>") + len("<USER_REQUEST>")
            end = content.find("</USER_REQUEST>")
            if end != -1:
                clean_content = content[start:end].strip()
        md_lines.append(f"```text\n{clean_content}\n```\n")

    elif step_type == "PLANNER_RESPONSE" or source == "MODEL":
        if content:
            md_lines.append(f"\n#### 🤖 Phản hồi của Trợ lý AI (Antigravity):\n\n")
            md_lines.append(f"{content.strip()}\n\n")

        if tool_calls:
            md_lines.append(f"**🛠️ Các công cụ & lệnh đã thực thi:**\n")
            for tc in tool_calls:
                fn_name = tc.get("name") or tc.get("tool_name", "tool")
                args = tc.get("args") or tc.get("arguments", {})
                summary = tc.get("toolSummary") or tc.get("toolAction") or fn_name
                md_lines.append(f"- `{fn_name}`: *{summary}*\n")
            md_lines.append("\n")

full_md_content = "".join(md_lines)

for p in output_paths:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(full_md_content, encoding="utf-8")
    print(f"Saved session export to: {p}")


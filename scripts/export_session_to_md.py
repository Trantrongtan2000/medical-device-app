import json
import sys
import re
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
md_lines.append(f"> **Dự án:** Quản lý Trang thiết bị y tế (BV Quận 7 / PKĐK Tâm Anh Q7)  \n")
md_lines.append("\n---\n")

md_lines.append("## 📌 TỔNG QUAN NỘI DUNG PHIÊN LÀM VIỆC\n")
md_lines.append("Toàn bộ mã nguồn, dữ liệu 1.073 thiết bị y tế, quy trình SOPs, sơ đồ SVG và tài liệu đã được chuẩn hóa.\n\n")
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
                summary = tc.get("toolSummary") or tc.get("toolAction") or fn_name
                md_lines.append(f"- `{fn_name}`: *{summary}*\n")
            md_lines.append("\n")

full_md_content = "".join(md_lines)

# Sanitize all sensitive token and API key patterns
sanitize_patterns = [
    (r"AQ\.[A-Za-z0-9_\-]{15,}", "YOUR_STITCH_API_KEY_HERE"),
    (r"AIzaSy[A-Za-z0-9_\-]{33}", "AIzaSyDemoMaskedKeyForSecurityOnly000"),
    (r"ya29\.[A-Za-z0-9_\-]+", "AIzaSyDemoMaskedKeyForSecurityOnly000"),
    (r"1//0[A-Za-z0-9_\-]+", "AIzaSyDemoMaskedKeyForSecurityOnly000"),
    (r'AIzaSyDemoMaskedKeyForSecurityOnly000]+"', 'AIzaSyDemoMaskedKeyForSecurityOnly000'),
    (r'AIzaSyDemoMaskedKeyForSecurityOnly000]+"', 'AIzaSyDemoMaskedKeyForSecurityOnly000'),
]
for pat, repl in sanitize_patterns:
    full_md_content = re.sub(pat, repl, full_md_content)

for p in output_paths:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(full_md_content, encoding="utf-8")
    print(f"Saved session export to: {p}")

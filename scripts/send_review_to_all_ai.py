"""
Gửi file REVIEW_QUESTIONS.md cho tất cả các AI có sẵn trong hệ thống.
Sử dụng ocx.cmd cho Claude, hoặc API keys tương ứng cho các nền tảng khác.
"""
import sys
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REVIEW_FILE = Path("docs/REVIEW_QUESTIONS.md")

def read_review_file():
    if not REVIEW_FILE.exists():
        print(f"[ERROR] File {REVIEW_FILE} không tồn tại")
        return None
    return REVIEW_FILE.read_text(encoding='utf-8')

def run_claude(content):
    """Gửi cho Claude qua ocx.cmd"""
    prompt = f"""
Bạn là Chuyên gia Kỹ sư Y sinh (BME) và Kiểm định thiết bị y tế. Hãy review nội dung sau và đưa ra nhận xét chi tiết.

Nội dung cần review:
{content}

Vui lòng trả lời theo định dạng YAML với các trường:
- score_total: điểm tổng (0-100)
- api_design: {{"score": int, "comments": string, "suggestions": [string]}}
- frontend_integration: {{...}}
- ui_ux_consistency: {{...}}
- database_schema: {{...}}
- security_compliance: {{...}}
- overall_recommendation: string

Chỉ trả về YAML thuần túy.
"""
    try:
        cmd = ["ocx.cmd", "claude", "--dangerously-skip-permissions", "-p", prompt]
        res = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
        return res.stdout
    except Exception as e:
        return f"Error: {e}"

def send_reviews():
    content = read_review_file()
    if not content:
        return
    
    print("=" * 60)
    print("📤 ĐANG GỬI REVIEW CHO CÁC AI")
    print("=" * 60)
    
    # 1. Claude
    print("\n[1/5] 🤖 Claude (Anthropic)...")
    result = run_claude(content)
    claude_file = Path("docs/CL_AUDIT_REVIEW.md")
    claude_file.parent.mkdir(parents=True, exist_ok=True)
    with open(claude_file, "w", encoding="utf-8") as f:
        f.write("# 🔍 Claude AI Review Results\n\n")
        f.write("```yaml\n")
        f.write(result)
        f.write("\n```\n")
    print(f"[OK] Lưu kết quả: {claude_file}")
    
    # 2. ChatGPT
    print("\n[2/5] 💬 ChatGPT (OpenAI)...")
    print("[INFO] Vui lòng dán nộiung dưới đây vào https://chat.openai.com")
    print("-" * 40)
    print(content[:2000] + "\n...(tiếp tục trong file REVIEW_QUESTIONS.md)")
    
    # 3. DeepSeek
    print("\n[3/5] ⚡ DeepSeek...")
    print("[INFO] Vui lòng dán nộiung vào https://chat.deepseek.com")
    
    # 4. GroK
    print("\n[4/5] 🚀 GroK (xAI)...")
    print("[INFO] Vui lòng dán nộiung vào https://grok.x.ai")
    
    # 5. AI Studio (Gemini)
    print("\n[5/5] 🌟 AI Studio (Google)...")
    print("[INFO] Vui lòng dán nộiung vào Google AI Studio")
    
    # Tạo file hướng dẫn
    guide_file = Path("docs/REVIEW_SEND_GUIDE.md")
    guide_file.write_text(f"""# 📤 Hướng Dẫn Gửi Review cho Các AI

## File gốc
- `docs/REVIEW_QUESTIONS.md`

## Kết quả đã có
- `docs/CL_AUDIT_REVIEW.md` - Kết quả Claude

## Hướng dẫn gửi cho các AI còn lại

### 1. ChatGPT
Truy cập: https://chat.openai.com
Dán nội dung file REVIEW_QUESTIONS.md vào hộp chat.

### 2. DeepSeek
Truy cập: https://chat.deepseek.com
Dán nội dung file REVIEW_QUESTIONS.md vào hộp chat.

### 3. GroK
Truy cập: https://grok.x.ai
Dán nội dung file REVIEW_QUESTIONS.md vào hộp chat.

### 4. AI Studio (Gemini)
Truy cập Google AI Studio hoặc https://gemini.google.com
Dán nội dung file REVIEW_QUESTIONS.md vào hộp chat.

---
*Được tạo tự động: {Path(__file__).parent.name}""", encoding='utf-8')
    print(f"\n[OK] Đã tạo hướng dẫn: {guide_file}")
    print("\n" + "=" * 60)
    print("✅ Hoàn thành! Vui lòng hoàn thành gửi file cho các AI còn lại.")
    print("=" * 60)

if __name__ == "__main__":
    send_reviews()
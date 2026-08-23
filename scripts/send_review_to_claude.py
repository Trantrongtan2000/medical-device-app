"""
Gửi file REVIEW_QUESTIONS.md cho Claude để review hệ thống quản lý thiết bị y tế
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def send_review_to_claude():
    review_file = Path("docs/REVIEW_QUESTIONS.md")
    
    if not review_file.exists():
        print(f"[ERROR] File {review_file} không tồn tại")
        return
    
    content = review_file.read_text(encoding='utf-8')
    
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
        print(f"[INFO] Đang gửi file REVIEW_QUESTIONS.md cho Claude...")
        res = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
        
        output_file = Path("docs/CL_AUDIT_REVIEW.md")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# 🔍 Claude AI Review Results\n\n")
            f.write("```yaml\n")
            f.write(res.stdout)
            f.write("\n```\n")
        
        print(f"[OK] Đã lưu kết quả vào: {output_file}")
        print(res.stdout[:2000])
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout khi gọi Claude")
    except Exception as e:
        print(f"[ERROR] Lỗi: {e}")

if __name__ == "__main__":
    send_review_to_claude()
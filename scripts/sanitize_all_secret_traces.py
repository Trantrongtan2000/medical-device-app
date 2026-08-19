import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_dir = Path(r"C:\Users\tantt\Downloads\medical-device-app")

# Patterns to mask
secret_patterns = [
    r'AQ\.[a-zA-Z0-9_\-]{30,}',
    r'EiYnjls[a-zA-Z0-9]{20,}',
    r'AIzaSy[a-zA-Z0-9_\-]{33}',
    r'ya29\.[a-zA-Z0-9_\-]+',
    r'1//0[a-zA-Z0-9_\-]+',
    r'"access_token":"[^"]+"',
    r'"refresh_token":"[^"]+"'
]

def sanitize_file(file_path: Path):
    if not file_path.exists():
        return
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        for pat in secret_patterns:
            content = re.sub(pat, 'AIzaSyDemoMaskedKeyForSecurityOnly000', content)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Sanitized: {file_path.name}")
    except Exception as ex:
        print(f"❌ Error sanitizing {file_path.name}: {ex}")

# Sanitize doc files
for p in [
    app_dir / "docs" / "session.md",
    app_dir / "docs" / "SESSION_TRANSCRIPT_20260818.md",
    Path(r"C:\Users\tantt\Downloads\session.md"),
    Path(r"C:\Users\tantt\Downloads\SESSION_TRANSCRIPT_20260818.md"),
    app_dir / "scripts" / "export_session_to_md.py",
]:
    sanitize_file(p)

print("✅ Đã làm sạch toàn bộ dấu vết key trong các tệp docs và scripts!")

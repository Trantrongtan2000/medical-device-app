import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

app_docs = Path(r"C:\Users\tantt\Downloads\medical-device-app\docs")
for p in app_docs.glob("*.md"):
    print(f"Docs: {p.name} ({p.stat().st_size / 1024:.1f} KB)")

amt_docs = Path(r"C:\Users\tantt\Downloads\asset-management-tools")
for p in amt_docs.glob("*.md"):
    print(f"Asset-Tools: {p.name} ({p.stat().st_size / 1024:.1f} KB)")

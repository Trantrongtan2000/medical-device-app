import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r"C:\Users\tantt\Downloads")
print(f"Scanning directory: {root}")

files_found = []
for p in root.rglob("*"):
    if p.is_file() and p.suffix.lower() in [".csv", ".xlsx", ".xltm", ".xls", ".md", ".jsonl", ".json"]:
        # ignore git and node_modules
        if ".git" in p.parts or "node_modules" in p.parts or ".gemini" in p.parts:
            continue
        rel = p.relative_to(root)
        files_found.append((str(rel), p.stat().st_size))

print(f"Total relevant data files found: {len(files_found)}")
print("\n--- SAMPLE TOP RELEVANT FILES ---")
for f, s in sorted(files_found, key=lambda x: x[1], reverse=True)[:40]:
    print(f"  • {f} ({s/1024:.1f} KB)")

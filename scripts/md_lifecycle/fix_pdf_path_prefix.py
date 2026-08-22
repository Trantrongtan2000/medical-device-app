#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sửa pdf_path frontmatter: bỏ prefix //?/ sau tái cấu trúc."""
import os
import re
import sys
from pathlib import Path

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MD = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712\md")
RE_PDF = re.compile(r'^(pdf_path:\s*["\']?)(.+?)(["\']?\s*)$', re.M)
RE_FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

fixed = 0
for p in MD.rglob("*.md"):
    txt = p.read_text(encoding="utf-8", errors="ignore")
    m = RE_FM.match(txt)
    if not m:
        continue
    fm = m.group(1)
    pm = RE_PDF.search(fm)
    if not pm:
        continue
    val = pm.group(2).strip().strip('"\'')
    clean = val.replace("\\\\?\\", "").replace("\\", "/")
    if clean.startswith("//?/"):
        clean = clean[4:]
    if clean == val:
        continue
    new_fm = RE_PDF.sub(f'pdf_path: "{clean}"', fm, count=1)
    new_txt = f"---\n{new_fm}\n---" + txt[m.end():]
    p.write_text(new_txt, encoding="utf-8")
    fixed += 1

print(f"Fixed pdf_path in {fixed} files")

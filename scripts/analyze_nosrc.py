#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phân loại 5723 md không có source_pdf:
- Có dòng tiêu đề # ....pdf -> trích tên PDF -> resolve được hay không
- Còn lại: tài liệu hệ thống / md thuần
"""
import os, re, unicodedata, collections

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'
MD = os.path.join(G_ROOT, 'md')
OUT = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_nosrc2_report.txt'

def norm3(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r'[\s_.\-]+', '', s)
    return s

YEAR = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)
TITLE_PDF = re.compile(r'^#\s+(.+?\.pdf)\s*$', re.M)

pdf_n3 = collections.defaultdict(list)
for dp, dn, fn in os.walk(G_ROOT):
    for f in fn:
        if f.lower().endswith('.pdf'):
            pdf_n3[norm3(f)].append(os.path.join(dp, f))

stats = collections.Counter()
with_title = []
no_title = []
examples_title_ok = []
examples_title_miss = []

for base in [MD, os.path.join(G_ROOT, '04_KIEM_DINH_VA_HIEU_CHUAN')]:
    for dp, dn, fn in os.walk(base):
        for f in fn:
            if not f.lower().endswith('.md'):
                continue
            p = os.path.join(dp, f)
            try:
                with open(p, encoding='utf-8', errors='ignore') as fh:
                    head = fh.read(4000)
            except Exception:
                continue
            if YEAR.search(head):
                continue
            m = TITLE_PDF.search(head)
            if not m:
                no_title.append(p)
                continue
            src = m.group(1).strip()
            hits = pdf_n3.get(norm3(src))
            if hits:
                with_title.append((p, src, hits[0]))
                if len(examples_title_ok) < 8:
                    examples_title_ok.append(f'{p}  |  {src}  ->  {hits[0]}')
            else:
                stats['title_no_pdf'] += 1
                if len(examples_title_miss) < 8:
                    examples_title_miss.append(f'{p}  |  {src}')

lines = []
lines.append(f'tổng md không src: {5723}')
lines.append(f'  có tiêu đề # ....pdf và PDF tồn tại: {len(with_title)}')
lines.append(f'  có tiêu đề # ....pdf nhưng PDF không có: {stats["title_no_pdf"]}')
lines.append(f'  không có tiêu đề pdf (tài liệu hệ thống/md thuần): {len(no_title)}')
lines.append('')
lines.append('--- khớp tiêu đề -> PDF (8 ví dụ) ---')
lines += examples_title_ok
lines.append('')
lines.append('--- tiêu đề pdf nhưng không thấy PDF (8 ví dụ) ---')
lines += examples_title_miss
lines.append('')
lines.append('--- không tiêu đề (10 ví dụ) ---')
for p in no_title[:10]:
    lines.append(p)

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
print('done')
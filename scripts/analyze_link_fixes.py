#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phân tích & đề xuất sửa liên kết md <-> pdf trên G:\BV QUẬN 7_OCR_WORK_20260712.
Dry-run: chỉ ghi báo cáo, không sửa file gốc.
"""
import os, re, unicodedata, collections, json

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'
MD = os.path.join(G_ROOT, 'md')
KHO = os.path.join(G_ROOT, '08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP')
OUT = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix_report.txt'
OUT_JSON = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix_report.json'

def norm(s):
    """Chuẩn hóa tên: bỏ dấu, lowercase, gom khoảng trắng/_/-/., bỏ hậu tố _1."""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[\s_.\-]+', '', s)
    s = re.sub(r'_1$', '', s)
    return s

YEAR = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)

# 1) Index mọi PDF trong G_ROOT (cả KHO, ghi chú nơi chứa)
pdf_index = collections.defaultdict(list)  # norm -> [(path, is_kho)]
pdf_by_exact = {}
def walk_pdf(base, is_kho=False):
    for dp, dn, fn in os.walk(base):
        for f in fn:
            if f.lower().endswith('.pdf'):
                p = os.path.join(dp, f)
                pdf_index[norm(f)].append((p, is_kho))
                pdf_by_exact.setdefault(f.lower(), p)
walk_pdf(G_ROOT)
walk_pdf(KHO, True)

# 2) Quét md trong md/ + 04_KIEM_DINH_VA_HIEU_CHUAN
md_files = []
for base in [MD, os.path.join(G_ROOT, '04_KIEM_DINH_VA_HIEU_CHUAN')]:
    for dp, dn, fn in os.walk(base):
        for f in fn:
            if f.lower().endswith('.md'):
                p = os.path.join(dp, f)
                try:
                    with open(p, encoding='utf-8', errors='ignore') as fh:
                        head = fh.read(4000)
                except Exception:
                    head = ''
                m = YEAR.search(head)
                md_files.append({
                    'path': p, 'name': f, 'norm': norm(f),
                    'src': m.group(1).strip().strip('"\'') if m else None,
                })

# 3) A. md có src nhưng không resolve được
A_fix = []  # sửa tên src
A_still_missing = []  # không tìm thấy PDF nào gần
for mf in md_files:
    if not mf['src']:
        continue
    srcn = norm(os.path.basename(mf['src']))
    cands = pdf_index.get(srcn, [])
    if cands:
        continue  # đã resolve
    # fuzzy: đúng chuẩn hóa (kể cả khác extension path) — thử các biến thể
    hits = pdf_index.get(mf['norm'], [])
    if hits:
        A_fix.append((mf, hits[0][0]))
    else:
        A_still_missing.append(mf)

# 4) B. md không có src nhưng PDF trùng tên chuẩn hóa tồn tại -> thêm front-matter
B_add = []
for mf in md_files:
    if mf['src']:
        continue
    hits = pdf_index.get(mf['norm'], [])
    if hits:
        B_add.append((mf, hits[0][0]))

# 5) C. PDF chưa có md nào (trừ KHO trùng lặp)
have_md_norms = collections.Counter(mf['norm'] for mf in md_files)
C_no_md = []
for n, lst in pdf_index.items():
    if have_md_norms.get(n):
        continue
    # chỉ xét bản gốc (không phải KHO)
    orig = [p for p, is_kho in lst if not is_kho]
    if orig:
        C_no_md.append((n, orig))

lines = []
lines.append('=' * 70)
lines.append('A) md CÓ source_pdf SAI TÊN (sửa được, tìm thấy PDF theo tên chuẩn hóa): %d' % len(A_fix))
for mf, pdf in A_fix[:25]:
    lines.append(f'  MD : {mf["path"]}')
    lines.append(f'    src cũ : {mf["src"]}')
    lines.append(f'    PDF thật: {pdf}')
lines.append('')
lines.append('A2) md CÓ source_pdf NHƯNG KHÔNG TÌM THẤY PDF nào (chờ xử lý thủ công): %d' % len(A_still_missing))
for mf in A_still_missing[:20]:
    lines.append(f'  {mf["path"]}  |  src={mf["src"]}')
lines.append('')
lines.append('B) md KHÔNG CÓ source_pdf NHƯNG CÓ PDF trùng tên (thêm front-matter): %d' % len(B_add))
lines.append('')
lines.append('C) PDF KHÔNG CÓ md tương ứng (chưa OCR hoặc thiếu md): %d file gốc' % len(C_no_md))
grp = collections.Counter()
for n, lst in C_no_md:
    d = os.path.dirname(lst[0])
    grp[os.path.relpath(d, G_ROOT).split(os.sep)[0]] += 1
for k, v in grp.most_common():
    lines.append(f'  {k}: {v}')
lines.append('')
lines.append('TỔNG: md=%d | A_fix=%d | A_missing=%d | B_add=%d | C_no_md=%d' % (
    len(md_files), len(A_fix), len(A_still_missing), len(B_add), len(C_no_md)))

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
with open(OUT_JSON, 'w', encoding='utf-8') as fh:
    json.dump({
        'A_fix': [{'md': mf['path'], 'src': mf['src'], 'pdf': p} for mf, p in A_fix],
        'A_still_missing': [{'md': mf['path'], 'src': mf['src']} for mf in A_still_missing],
        'B_add': [{'md': mf['path'], 'pdf': p} for mf, p in B_add],
        'C_no_md': [{'pdf': lst[0]} for n, lst in C_no_md],
    }, fh, ensure_ascii=False, indent=1)
print('done')
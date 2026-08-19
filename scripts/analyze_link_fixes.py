#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phân tích liên kết md <-> pdf trên G:\BV QUẬN 7_OCR_WORK_20260712.
V1.2: resolve theo source_pdf, fuzzy cho phần còn lại; đếm pdf không được md trỏ tới.
Dry-run: chỉ ghi báo cáo + đề xuất sửa, không đụng file gốc.
"""
import os, re, unicodedata, collections, json, difflib

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'
MD = os.path.join(G_ROOT, 'md')
KHO = os.path.join(G_ROOT, '08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP')
OUT = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix_report.txt'
OUT_JSON = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix_report.json'

def norm2(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'_1(?=\.|$)', '', s)
    return s

def norm3(s):
    """Tương đương norm2 nhưng gom _-. và space -> rỗng, dùng cho fuzzy index."""
    s = norm2(s)
    s = re.sub(r'[\s_.\-]+', '', s)
    return s

YEAR = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)

# 1) Index PDF theo norm2 và norm3
pdf_by_n2 = collections.defaultdict(list)   # norm2 -> [(path, is_kho)]
pdf_by_n3 = collections.defaultdict(list)   # norm3 -> [(path, is_kho)]
def walk_pdf(base, is_kho=False):
    for dp, dn, fn in os.walk(base):
        for f in fn:
            if f.lower().endswith('.pdf'):
                p = os.path.join(dp, f)
                pdf_by_n2[norm2(f)].append((p, is_kho))
                pdf_by_n3[norm3(f)].append((p, is_kho))
walk_pdf(G_ROOT)
walk_pdf(KHO, True)

def resolve(src):
    """Trả về (path, is_kho) của pdf khớp src, hoặc None."""
    b = os.path.basename(src)
    for n in (norm2(b), norm3(b)):
        if pdf_by_n2.get(n):
            return pdf_by_n2[n][0]
        if pdf_by_n3.get(n):
            return pdf_by_n3[n][0]
    return None

# 2) Quét md (md/ + 04_KIEM_DINH_VA_HIEU_CHUAN + 08_KHO md trùng)
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
                    'path': p, 'name': f,
                    'src': m.group(1).strip().strip('"\'') if m else None,
                })

# 3) Phân loại md có src
md_ok = []          # src resolve chính xác
md_fix = []         # src sai tên, fuzzy tìm được 1 ứng viên
md_ambiguous = []   # src sai, nhiều ứng viên
md_missing = []     # src sai, không tìm thấy gần
md_nosrc = []       # không có src

for mf in md_files:
    if not mf['src']:
        md_nosrc.append(mf)
        continue
    hit = resolve(mf['src'])
    if hit and not hit[1]:
        md_ok.append((mf, hit[0]))
        continue
    # fuzzy theo norm3 của src (so với tên file md trong cùng thư mục)
    src_n3 = norm3(os.path.basename(mf['src']))
    if src_n3 in pdf_by_n3:
        md_fix.append((mf, pdf_by_n3[src_n3][0][0]))
        continue
    keys = list(pdf_by_n3.keys())
    close = difflib.get_close_matches(src_n3, keys, n=3, cutoff=0.55)
    if close:
        cands = [p for c in close for p, isk in pdf_by_n3[c] if not isk]
        if len(set(cands)) == 1:
            md_fix.append((mf, cands[0]))
        else:
            md_ambiguous.append((mf, cands[:3]))
    else:
        md_missing.append(mf)

# 4) PDF không được md nào trỏ tới
resolved_all = set()
for mf in md_files:
    if not mf['src']:
        continue
    hit = resolve(mf['src'])
    if hit:
        resolved_all.add(hit[0].lower())

C_no_md = []
for n2, lst in pdf_by_n2.items():
    for p, isk in lst:
        if isk:
            continue
        if p.lower() in resolved_all:
            continue
        C_no_md.append(p)

lines = []
lines.append('=' * 70)
lines.append('PHÂN TÍCH LIÊN KẾT md <-> pdf (V1.2)')
lines.append(f'Tổng md quét: {len(md_files)}  (có source_pdf: {len(md_files)-len(md_nosrc)}, không có: {len(md_nosrc)})')
lines.append(f'PDF tổng ở G_ROOT: {sum(len(v) for v in pdf_by_n2.values())} (gồm cả kho trùng)')
lines.append('')
lines.append(f'[OK]  md có src, PDF resolve chính xác         : {len(md_ok)}')
lines.append(f'[FIX] md có src SAI TÊN, tìm được PDF duy nhất : {len(md_fix)}')
lines.append(f'[AMB] md src sai, nhiều ứng viên PDF            : {len(md_ambiguous)}')
lines.append(f'[MISS] md src sai, KHÔNG tìm thấy PDF nào       : {len(md_missing)}')
lines.append('')
lines.append('--- [FIX] Đề xuất sửa source_pdf (tất cả) ---')
for mf, pdf in md_fix:
    lines.append(f'{mf["path"]}')
    lines.append(f'    src cũ : {mf["src"]}')
    lines.append(f'    PDF mới: {pdf}')
lines.append('')
lines.append('--- [AMB] Nhiều ứng viên ---')
for mf, cands in md_ambiguous:
    lines.append(f'{mf["path"]}  src={mf["src"]}')
    for c in cands:
        lines.append(f'    ? {c}')
lines.append('')
lines.append('--- [MISS] Không tìm thấy (danh sách đầy đủ trong JSON) ---')
for mf in md_missing[:30]:
    lines.append(f'  {mf["path"]}  |  src={mf["src"]}')
lines.append('')
g2 = collections.Counter(os.path.relpath(os.path.dirname(p), G_ROOT).split(os.sep)[0] for p in C_no_md)
lines.append(f'[NO-MD] PDF KHÔNG được md nào trỏ tới: {len(C_no_md)}')
for k, v in g2.most_common():
    lines.append(f'    {k}: {v}')

with open(OUT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
with open(OUT_JSON, 'w', encoding='utf-8') as fh:
    json.dump({
        'fix': [{'md': mf['path'], 'src_old': mf['src'], 'pdf_new': pdf} for mf, pdf in md_fix],
        'ambiguous': [{'md': mf['path'], 'src': mf['src'], 'cands': cands} for mf, cands in md_ambiguous],
        'missing': [{'md': mf['path'], 'src': mf['src']} for mf in md_missing],
        'no_md': C_no_md,
        'stats': {'total_md': len(md_files), 'ok': len(md_ok), 'fix': len(md_fix),
                  'ambiguous': len(md_ambiguous), 'missing': len(md_missing),
                  'no_md_pdfs': len(C_no_md)},
    }, fh, ensure_ascii=False, indent=1)
print('done')
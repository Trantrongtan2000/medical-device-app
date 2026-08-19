#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sửa liên kết md <-> pdf trên G:\BV QUẬN 7_OCR_WORK_20260712.

Nhóm 1: md có source_pdf sai tên -> cập nhật sang tên PDF thực (chọn ứng viên tốt nhất,
         yêu cầu tỉ lệ khớp >= 0.72 + trùng token định danh; dưới ngưỡng -> bỏ qua).
Nhóm 2: md không có source_pdf nhưng có tiêu đề `# Ten.pdf` và PDF tồn tại
         -> chèn front-matter source_pdf (tên file, theo đúng convention sẵn có).

Backup mọi file bị sửa vào 08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP\_backup_md_links trước khi ghi.
Chạy: DRY=1 python ...          (chỉ báo cáo, không ghi)
      python ...                (backup + ghi)
"""
import os, re, unicodedata, collections, json, shutil, sys, datetime

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'
MD = os.path.join(G_ROOT, 'md')
KHO = os.path.join(G_ROOT, '08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP')
BK_ROOT = os.path.join(KHO, '_backup_md_links')
OUT_LOG = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix_log.json'
OUT_TXT = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix_result.txt'

DRY = os.environ.get('DRY') == '1'

def norm2(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower().replace('_1', '').strip()
    return s

def norm3(s):
    s = norm2(s)
    s = re.sub(r'[\s_.\-]+', '', s)
    return s

def tokens(s):
    """Token định danh (serial/PO/HD) >= 5 ký tự alnum."""
    return set(re.findall(r'[A-Za-z0-9]{5,}', norm3(s)))

YEAR = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)
TITLE_PDF = re.compile(r'^#\s+(.+?\.pdf)\s*$', re.M)

# ---- Index PDF ----
pdf_by_n3 = collections.defaultdict(list)
pdf_by_n2 = collections.defaultdict(list)
all_pdf_paths = []
for dp, dn, fn in os.walk(G_ROOT):
    for f in fn:
        if f.lower().endswith('.pdf'):
            p = os.path.join(dp, f)
            pdf_by_n3[norm3(f)].append(p)
            pdf_by_n2[norm2(f)].append(p)
            all_pdf_paths.append(p)

n3_keys = list(pdf_by_n3.keys())

def find_best(src):
    """Tìm pdf tốt nhất cho src. Trả (path, ratio) hoặc (None, 0)."""
    b = norm3(os.path.basename(src))
    if b in pdf_by_n3:
        return pdf_by_n3[b][0], 1.0
    t = tokens(src)
    cands = set()
    if t:
        for k in n3_keys:
            if t & tokens(k+'.pdf') if False else (t & set(re.findall(r'[A-Za-z0-9]{5,}', k))):
                cands.update(pdf_by_n3[k])
    else:
        cands = set(all_pdf_paths)
    if not cands:
        return None, 0.0
    from difflib import SequenceMatcher
    best = None; best_r = 0
    for c in cands:
        r = SequenceMatcher(None, b, norm3(os.path.basename(c))).ratio()
        if r > best_r:
            best_r, best = r, c
    return best, best_r

# ---- Quét md ----
md_rows = []
for base in [MD, os.path.join(G_ROOT, '04_KIEM_DINH_VA_HIEU_CHUAN')]:
    for dp, dn, fn in os.walk(base):
        for f in fn:
            if not f.lower().endswith('.md'):
                continue
            p = os.path.join(dp, f)
            try:
                with open(p, encoding='utf-8', errors='ignore') as fh:
                    txt = fh.read()
            except Exception:
                continue
            m = YEAR.search(txt)
            md_rows.append({'path': p, 'txt': txt, 'src': m.group(1).strip().strip('"\'') if m else None})

# ---- Phân loại ----
fix_group = []      # (mf, pdf_new)
insert_group = []   # (mf, pdf_basename)
unresolved = []     # src sai, không tìm được pdf đủ tin cậy
ok_count = 0

for mf in md_rows:
    if mf['src']:
        ok, r = find_best(mf['src'])
        if ok and r >= 0.9999:
            ok_count += 1
        elif ok and r >= 0.72:
            fix_group.append((mf, ok, r))
        else:
            unresolved.append((mf, ok, r))
    else:
        tm = TITLE_PDF.search(mf['txt'])
        if tm:
            src = tm.group(1).strip()
            if norm3(src) in pdf_by_n3:
                insert_group.append((mf, os.path.basename(src)))

# ---- Ghi log ----
log = {
    'generated': datetime.datetime.now().isoformat(),
    'dry': DRY,
    'ok_already': ok_count,
    'fix_count': len(fix_group),
    'insert_count': len(insert_group),
    'unresolved_count': len(unresolved),
    'fix': [],
    'insert': [],
    'unresolved': [],
}

def lp(p):
    """Long-path prefix cho Windows nếu path vượt ngưỡng."""
    return '\\\\?\\' + os.path.abspath(p) if len(os.path.abspath(p)) > 240 else p

def backup_and_write(mf, newtxt, reason, detail):
    rel = os.path.relpath(mf['path'], G_ROOT)
    if not DRY:
        bk = os.path.join(BK_ROOT, rel)
        os.makedirs(lp(os.path.dirname(bk)), exist_ok=True)
        if not os.path.exists(lp(bk)):
            shutil.copy2(lp(mf['path']), lp(bk))
        with open(lp(mf['path']), 'w', encoding='utf-8') as fh:
            fh.write(newtxt)
    return {'md': mf['path'], 'rel': rel, 'reason': reason, 'detail': detail}

for mf, pdf, r in fix_group:
    newtxt = re.sub(YEAR, lambda mo: f'source_pdf: "{os.path.basename(pdf)}"', mf['txt'], count=1)
    log['fix'].append(backup_and_write(mf, newtxt, 'fix_source_pdf',
        {'src_old': mf['src'], 'pdf_new': pdf, 'ratio': round(r, 3)}))

for mf, base in insert_group:
    # nếu file đã bắt đầu bằng '---' (front-matter khác) thì không chèn (tránh vỡ YAML)
    if mf['txt'].startswith('---'):
        log['unresolved'].append({'md': mf['path'], 'reason': 'existing_frontmatter_without_source_pdf', 'title': base})
        continue
    fm = f'---\nsource_pdf: "{base}"\n---\n'
    newtxt = fm + mf['txt']
    log['insert'].append(backup_and_write(mf, newtxt, 'insert_source_pdf', {'pdf': base}))

for mf, cand, r in unresolved:
    log['unresolved'].append({'md': mf['path'], 'src': mf['src'],
                              'best_candidate': cand, 'ratio': round(r, 3) if cand else None})
    if cand:
        pass  # giữ trong log để xem xét thủ công

with open(OUT_LOG, 'w', encoding='utf-8') as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)

lines = []
lines.append(f'DRY RUN: {DRY}')
lines.append(f'[OK] đã đúng                                 : {ok_count}')
lines.append(f'[FIX] sửa source_pdf sai tên (ratio>=0.72)   : {len(fix_group)}')
lines.append(f'[INSERT] chèn front-matter từ tiêu đề         : {len(insert_group)}')
lines.append(f'[UNRESOLVED] chưa tự sửa được                  : {len(unresolved)}')
lines.append('')
lines.append('--- FIX (toàn bộ) ---')
for e in log['fix']:
    lines.append(f"{e['rel']}")
    lines.append(f"    {e['detail']['src_old']}  ->  {os.path.basename(e['detail']['pdf_new'])}  (r={e['detail']['ratio']})")
lines.append('')
lines.append('--- UNRESOLVED (chờ xử lý thủ công) ---')
for e in log['unresolved']:
    lines.append(f"{e.get('rel', e['md'])}  |  src={e.get('src')}  |  best={e.get('best_candidate') if e.get('best_candidate') else 'NONE'} (r={e.get('ratio')})")

with open(OUT_TXT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
# stdout ngắn gọn
sys.stdout.write(f'DRY={DRY} ok={ok_count} fix={len(fix_group)} insert={len(insert_group)} unresolved={len(unresolved)}')
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Xử lý 117 md unresolved: nối bằng token số máy (ví dụ 056388) + SequenceMatcher."""
import os, re, unicodedata, json, shutil, sys, datetime
from difflib import SequenceMatcher

G_ROOT = r'G:\BV QUẬN 7_OCR_WORK_20260712'
MD = os.path.join(G_ROOT, 'md')
KHO = os.path.join(G_ROOT, '08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP')
BK_ROOT = os.path.join(KHO, '_backup_md_links')
OUT_LOG = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix2_log.json'
OUT_TXT = r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix2_result.txt'
DRY = os.environ.get('DRY') == '1'

def norm3(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r'[\s_.\-]+', '', s)
    return s

def keep_sep(s):
    """Bỏ dấu, giữ separator -> token hóa được theo từng run chữ-số."""
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower()

def serial_tokens(s):
    """Token định danh:
    - run chữ-số >= 6 ký tự, có chứa chữ số (giữ separator) — serial/PO/HD
    - chuỗi số liên tục >= 6 chữ số trong norm3 (số máy như 056389 bị separator cắt)
    """
    toks = set(t for t in re.findall(r'[A-Za-z0-9]{6,}', keep_sep(s)) if any(c.isdigit() for c in t))
    for t in re.findall(r'\d{6,}', norm3(s)):
        toks.add(t)
    return toks

def lp(p):
    return '\\\\?\\' + os.path.abspath(p) if len(os.path.abspath(p)) > 240 else p

YEAR = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)

# PDF index theo serial token (run chữ-số có chứa số, >= 6 ký tự) trên tên gốc
pdf_by_bigtoken = {}
all_pdf = []
for dp, dn, fn in os.walk(G_ROOT):
    for f in fn:
        if f.lower().endswith('.pdf'):
            p = os.path.join(dp, f)
            all_pdf.append(p)
            for tok in serial_tokens(f):
                pdf_by_bigtoken.setdefault(tok, set()).add(p)

def pdf_priority(p):
    """Bản chuẩn hóa được ưu tiên hơn bản trùng trong kho 08_KHO."""
    if '_duplicates_archive' in p or '_backup_md_links' in p:
        return 3
    if p.lower().startswith(os.path.join(G_ROOT, '08_KHO').lower()):
        return 2
    return 1

def find_best2(src):
    """Dùng serial/PO token làm khóa, rồi SequenceMatcher trên tên chuẩn hóa."""
    n3 = norm3(os.path.basename(src))
    toks = serial_tokens(os.path.basename(src))
    cands = set()
    for t in toks:
        cands |= pdf_by_bigtoken.get(t, set())
    if not cands:
        return None, 0.0
    # loại bản trùng trong kho, giữ bản chuẩn hóa
    cands = {c for c in cands if pdf_priority(c) == 1}
    if not cands:
        return None, 0.0
    best, br = None, 0.0
    for c in cands:
        r = SequenceMatcher(None, n3, norm3(os.path.basename(c))).ratio()
        if r > br:
            br, best = r, c
    # Nếu mọi ứng viên cùng 1 basename (bản sao đặt nhiều nơi) -> coi như 1 bản duy nhất
    if len({os.path.basename(c) for c in cands}) == 1:
        return best, max(br, 0.9)
    # Nếu mọi ứng viên cùng tập serial token (cùng tài liệu, tên lệch OCR) -> chấp nhận bản tốt nhất
    if len(cands) > 1 and toks:
        shared = all(toks & serial_tokens(os.path.basename(c)) for c in cands)
        if shared and br >= 0.5:
            return best, 0.9
    return best, br

log = {'generated': datetime.datetime.now().isoformat(), 'dry': DRY, 'items': []}
def backup_and_write(mf_path, newtxt, detail):
    rel = os.path.relpath(mf_path, G_ROOT)
    if not DRY:
        bk = os.path.join(BK_ROOT, rel)
        os.makedirs(lp(os.path.dirname(bk)), exist_ok=True)
        if not os.path.exists(lp(bk)):
            shutil.copy2(lp(mf_path), lp(bk))
        with open(lp(mf_path), 'w', encoding='utf-8') as fh:
            fh.write(newtxt)
    return {'md': mf_path, 'rel': rel, 'detail': detail}

# lấy danh sách unresolved từ log trước
prev = json.load(open(r'C:\Users\tantt\Downloads\medical-device-app\scripts\_link_fix_log.json', encoding='utf-8'))
unresolved = [e for e in prev['unresolved'] if 'src' in e]

fixed = 0; untouched = 0
for e in unresolved:
    p = e['md']; src = e['src']
    # bỏ qua file _debug_test
    if 'debug_test' in p:
        untouched += 1
        log['items'].append({'md': p, 'action': 'skip_debug'})
        continue
    best, r = find_best2(src)
    if best and (r >= 0.75 or (r >= 0.6 and len(serial_tokens(src)) >= 1)):
        try:
            txt = open(lp(p), encoding='utf-8', errors='ignore').read()
        except Exception:
            continue
        newtxt = re.sub(YEAR, lambda mo: f'source_pdf: "{os.path.basename(best)}"', txt, count=1)
        log['items'].append(backup_and_write(p, newtxt, {'src_old': src, 'pdf_new': best, 'ratio': round(r, 3)}))
        fixed += 1
    else:
        untouched += 1
        log['items'].append({'md': p, 'src': src, 'best': best, 'ratio': round(r, 3) if best else None, 'action': 'skip_low_confidence'})

with open(OUT_LOG, 'w', encoding='utf-8') as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)

lines = [f'DRY={DRY} fixed={fixed} untouched={untouched}']
for it in log['items']:
    if it.get('action') == 'skip_low_confidence':
        lines.append(f'SKIP {it["md"]} | best={it.get("best")} (r={it.get("ratio")})')
    elif it.get('action') == 'skip_debug':
        lines.append(f'SKIP-DEBUG {it["md"]}')
    else:
        d = it['detail']
        lines.append(f'FIX {it["rel"]}')
        lines.append(f'    {d["src_old"]}  ->  {os.path.basename(d["pdf_new"])}  (r={d["ratio"]})')
with open(OUT_TXT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines))
sys.stdout.write(f'DRY={DRY} fixed={fixed} untouched={untouched}')
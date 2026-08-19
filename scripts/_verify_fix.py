#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, sys, glob, os

def lp(p):
    return '\\\\?\\' + os.path.abspath(p) if len(os.path.abspath(p)) > 240 else p

# 1) file thuộc nhóm FIX
for p in glob.glob(r'G:\BV QUẬN 7_OCR_WORK_20260712\md\05_KIEM DINH\backup_original\0084*.md'):
    t = open(lp(p), encoding='utf-8', errors='ignore').read()
    m = re.search(r'^source_pdf:\s*(.+)$', t, re.M)
    sys.stdout.write(os.path.basename(p)[:40] + '  ->  ' + (m.group(1) if m else 'NONE') + '\n')

# 2) file thuộc nhóm INSERT
p2 = r'G:\BV QUẬN 7_OCR_WORK_20260712\md\02_HOP DONG MUA SAM\Bàn giao lắp đặt + Chứng từ CO,CQ\DEAWON\BBBG_1 đầu xịt phun khí bàn khám TMH IU 3000 PO Q725080155 CT Deawon.md'
if os.path.exists(lp(p2)):
    t2 = open(lp(p2), encoding='utf-8', errors='ignore').read()
    m2 = re.search(r'^source_pdf:\s*(.+)$', t2, re.M)
    sys.stdout.write('INSERT head: ' + repr(t2[:100]) + '\n')
else:
    sys.stdout.write('INSERT target missing\n')
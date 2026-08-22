#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sửa phân loại 03_KIEM_DINH — chỉ giữ GCN thật, chuyển file hỗn hợp sang đúng phân hệ.

Chạy:
  DRY=1 python fix_kiemdinh_classification.py
  python fix_kiemdinh_classification.py
"""
from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

G_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
MD = G_ROOT / "md"
KIEM = MD / "03_KIEM_DINH"
KHO = G_ROOT / "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP" / "_backup_kiemdinh_reclass"
MANIFEST_IN = G_ROOT / "md_restructure_manifest.json"
MANIFEST_OUT = G_ROOT / "kiemdinh_reclass_manifest.json"
REPORT_OUT = G_ROOT / "kiemdinh_reclass_report.txt"

DRY = os.environ.get("DRY") == "1"

RE_DOC_TYPE = re.compile(r'^doc_type:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_CERT = re.compile(r'^cert_no:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_STAMP = re.compile(r'^stamp_no:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_MD_PATH = re.compile(r'^md_path:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

FN_GCN = re.compile(r"^056-\d+|^056-\d+_01\.\d{2}[HP]-", re.I)

SIG = {
    "03_KIEM_DINH": re.compile(
        r"(giấy chứng nhận kiểm định|chứng nhận kiểm định|tem kiểm định|"
        r"trung tâm đo lường|ttbyt.*kiểm định|056-\d+/01\.\d{2})",
        re.I,
    ),
    "01_MUA_SAM": re.compile(
        r"(cộng hòa xã hội|hợp đồng mua bán|hđmb|hđ số|điều \d+\.|"
        r"giá trị hợp đồng|bên mua|bên bán|thanh toán|phụ lục|"
        r"phiếu giao hàng|hóa đơn|tờ khai|co/cq|chứng nhận xuất xứ)",
        re.I,
    ),
    "02_BAN_GIAO": re.compile(
        r"(biên bản bàn giao|bbbg|nghiệm thu|bàn giao thiết bị|"
        r"lắp đặt nghiệm thu|giao nhận thiết bị)",
        re.I,
    ),
    "04_BAO_TRI": re.compile(r"(bảo trì định kỳ|bảo dưỡng|nhật ký bảo trì)", re.I),
    "05_SUA_CHUA": re.compile(r"(sửa chữa thiết bị|yêu cầu sửa chữa|sc thiết bị)", re.I),
    "06_PHAP_LY": re.compile(
        r"(thẩm định chất lượng|sở y tế|cấp phép|bhxh|lý lịch thiết bị|"
        r"quy trình.*ttbyt|bm\d+.*qt\.\d+)",
        re.I,
    ),
}

FN_HINT = {
    "01_MUA_SAM": re.compile(r"\bH[DĐ]\b|HDMB|HDKT|HĐ-|NT\s\d|Scan_\d|CO\.|CQ\.|HOP.?DONG", re.I),
    "02_BAN_GIAO": re.compile(r"^BBBG|BAN.?GIAO|BG_|NGHIEM.?THU", re.I),
    "04_BAO_TRI": re.compile(r"BAO.?TRI|BAO.?DUONG", re.I),
    "05_SUA_CHUA": re.compile(r"SUA.?CHUA|\bSC\b", re.I),
    "06_PHAP_LY": re.compile(r"THAM.?DINH|BHXH|QUY.?TRINH|LY.?LICH", re.I),
}


def long_path(p: Path | str) -> str:
    s = os.path.abspath(str(p))
    return s if s.startswith("\\\\?\\") else "\\\\?\\" + s


def read_text(p: Path) -> str:
    return Path(long_path(p)).read_text(encoding="utf-8", errors="ignore")


def is_true_gcn(stem: str, head: str, body: str) -> bool:
    dt = RE_DOC_TYPE.search(head)
    doc_type = dt.group(1).strip().strip('"\'').upper() if dt else ""
    if doc_type in ("HIEU_CHUAN", "KIEM_DINH", "CALIBRATION"):
        cert = RE_CERT.search(head)
        stamp = RE_STAMP.search(head)
        if cert or stamp:
            return True
    if FN_GCN.search(stem):
        if RE_CERT.search(head) or RE_STAMP.search(head):
            return True
        if SIG["03_KIEM_DINH"].search(head + body[:2000]):
            return True
    return False


def classify_content(stem: str, head: str, body: str) -> str:
    text = head + body[:4000]
    scores: Counter = Counter()

    for cat, pat in FN_HINT.items():
        if pat.search(stem):
            scores[cat] += 3

    for cat, pat in SIG.items():
        if cat == "03_KIEM_DINH":
            continue
        if pat.search(text):
            scores[cat] += 2

    if not scores:
        return "99_CHUA_PHAN_LOAI"
    return scores.most_common(1)[0][0]


def update_md_path(content: str, new_rel: str) -> str:
    m = RE_FM.match(content)
    if not m:
        return content
    fm = m.group(1)
    if RE_MD_PATH.search(fm):
        fm = RE_MD_PATH.sub(f'md_path: "{new_rel}"', fm, count=1)
    else:
        fm = fm.rstrip() + f'\nmd_path: "{new_rel}"'
    return f"---\n{fm}\n---" + content[m.end():]


def unique_dest(base: Path, name: str, used: set[str]) -> Path:
    dest = base / name
    if str(dest) not in used and not os.path.exists(long_path(dest)):
        used.add(str(dest))
        return dest
    stem, ext = Path(name).stem, Path(name).suffix
    i = 1
    while True:
        c = base / f"{stem}_{i}{ext}"
        if str(c) not in used and not os.path.exists(long_path(c)):
            used.add(str(c))
            return c
        i += 1


def main() -> None:
    files = list(KIEM.glob("*.md"))
    print(f"Audit + reclassify {len(files)} files in 03_KIEM_DINH (DRY={DRY})")

    moves: list[dict] = []
    keep = 0
    by_target: Counter = Counter()

    for p in files:
        head = read_text(p)[:4000]
        body = read_text(p)[4000:8000]

        if is_true_gcn(p.stem, head, body):
            keep += 1
            continue

        target = classify_content(p.stem, head, body)
        by_target[target] += 1
        moves.append({"src": str(p), "name": p.name, "target": target})

    lines = [
        f"Generated: {datetime.datetime.now().isoformat()}",
        f"DRY: {DRY}",
        f"Total in 03_KIEM_DINH: {len(files)}",
        f"Giữ lại (GCN thật): {keep}",
        f"Di chuyển: {len(moves)}",
        "",
        "Phân bổ di chuyển:",
    ]
    for k, v in by_target.most_common():
        lines.append(f"  {k}: {v}")

    if not DRY:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bk = KHO / ts
        bk.mkdir(parents=True, exist_ok=True)
        used: set[str] = set()
        done = 0

        for m in moves:
            src = Path(m["src"])
            dst_dir = MD / m["target"]
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = unique_dest(dst_dir, m["name"], used)

            shutil.copy2(long_path(src), long_path(bk / m["name"]))
            content = read_text(src)
            new_rel = str(dst.relative_to(MD)).replace("\\", "/")
            Path(long_path(dst)).write_text(update_md_path(content, new_rel), encoding="utf-8")
            os.remove(long_path(src))
            m["dest"] = str(dst)
            m["new_md_path"] = new_rel
            done += 1

        lines.append(f"\nExecuted moves: {done}")
        lines.append(f"Backup: {bk}")

    manifest = {
        "generated_at": datetime.datetime.now().isoformat(),
        "dry_run": DRY,
        "kept_in_kiemdinh": keep,
        "moved": len(moves),
        "by_target": dict(by_target),
        "entries": moves,
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

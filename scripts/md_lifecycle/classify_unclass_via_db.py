#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phân loại 99_CHUA_PHAN_LOAI bằng đối chiếu device_documents + fallback nội dung."""
from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import sys
import unicodedata
from collections import Counter
from pathlib import Path

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

G_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
MD = G_ROOT / "md"
UNCLASS = MD / "99_CHUA_PHAN_LOAI"
DB = Path(r"C:\Users\tantt\Downloads\medical-device-app\database\devices.db")
BK = G_ROOT / "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP" / "_backup_unclass_reclass"
MANIFEST = G_ROOT / "unclass_reclass_manifest.json"
REPORT = G_ROOT / "unclass_reclass_report.txt"

DRY = os.environ.get("DRY") == "1"

DOC_TO_LIFECYCLE = {
    "CALIBRATION": "03_KIEM_DINH",
    "HANDOVER": "02_BAN_GIAO",
    "CONTRACT": "01_MUA_SAM",
    "MAINTENANCE": "04_BAO_TRI",
    "LEGAL": "06_PHAP_LY",
    "OTHER": "99_CHUA_PHAN_LOAI",
}

RE_MD_PATH = re.compile(r'^md_path:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_YAML_SRC = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_YAML_PDF = re.compile(r'^pdf_path:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_JSON_SRC = re.compile(r'"source_pdf"\s*:\s*"([^"]+)"')
RE_FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
RE_TITLE_PDF = re.compile(r"^#\s+(.+?\.pdf)\s*$", re.M)

SIG = {
    "03_KIEM_DINH": re.compile(
        r"(giấy chứng nhận hiệu chuẩn|giấy chứng nhận kiểm định|calibration certificate|056-\d+|01\.\d{2}[HP]-|tem kiểm định)",
        re.I,
    ),
    "01_MUA_SAM": re.compile(r"(hợp đồng mua bán|hđmb|giá trị hợp đồng|bên mua|bên bán|phiếu giao hàng)", re.I),
    "02_BAN_GIAO": re.compile(r"(biên bản bàn giao|bbbg|nghiệm thu|giao nhận thiết bị)", re.I),
    "04_BAO_TRI": re.compile(r"(bảo trì định kỳ|bảo dưỡng|nhật ký bảo trì)", re.I),
    "05_SUA_CHUA": re.compile(r"(sửa chữa thiết bị|yêu cầu sửa chữa)", re.I),
    "06_PHAP_LY": re.compile(r"(thẩm định|sở y tế|bhxh|lý lịch thiết bị|quy trình.*ttbyt)", re.I),
}


def long_path(p: Path | str) -> str:
    s = os.path.abspath(str(p))
    return s if s.startswith("\\\\?\\") else "\\\\?\\" + s


def norm2(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().replace("_1", "").strip()


def norm3(s: str) -> str:
    return re.sub(r"[\s_.\-/\\]+", "", norm2(s))


def extract_pdf_refs(content: str, stem: str) -> list[str]:
    refs: list[str] = []
    head = content[:5000]
    m = RE_YAML_SRC.search(head)
    if m:
        refs.append(m.group(1).strip().strip('"\''))
    m = RE_JSON_SRC.search(head)
    if m:
        refs.append(m.group(1).strip())
    m = RE_YAML_PDF.search(head)
    if m:
        refs.append(m.group(1).strip().strip('"\''))
    tm = RE_TITLE_PDF.search(content)
    if tm:
        refs.append(tm.group(1).strip())
    if not refs:
        refs.append(stem.replace(".audit", "") + ".pdf")
    return refs


def build_db_index(conn) -> tuple[dict[str, str], dict[str, str]]:
    """norm_basename -> doc_type, norm3_basename -> doc_type (first wins)."""
    by_n2: dict[str, str] = {}
    by_n3: dict[str, str] = {}
    for row in conn.execute("SELECT doc_type, title, file_path FROM device_documents"):
        doc_type, title, file_path = row
        for name in (title, os.path.basename(file_path)):
            if not name:
                continue
            n2 = norm2(name)
            n3 = norm3(name)
            by_n2.setdefault(n2, doc_type)
            by_n3.setdefault(n3, doc_type)
    return by_n2, by_n3


def match_db(refs: list[str], by_n2, by_n3) -> tuple[str | None, str]:
    for ref in refs:
        base = os.path.basename(ref.replace("/", os.sep))
        n2 = norm2(base)
        n3 = norm3(base)
        if n2 in by_n2:
            return by_n2[n2], "db_norm2"
        if n3 in by_n3:
            return by_n3[n3], "db_norm3"
        stem_n3 = norm3(Path(base).stem)
        for k, dt in by_n3.items():
            if stem_n3 and (stem_n3 in k or k in stem_n3) and len(stem_n3) >= 8:
                return dt, "db_stem_partial"
    return None, "no_db_match"


def classify_content(stem: str, content: str) -> str:
    text = content[:6000]
    scores: Counter = Counter()
    if stem.endswith(".audit") or ".audit." in stem:
        if SIG["03_KIEM_DINH"].search(text):
            return "03_KIEM_DINH"
    for cat, pat in SIG.items():
        if pat.search(text):
            scores[cat] += 2
    if re.match(r"^056-\d+|^009\d+\.\d{2}\.", stem):
        scores["03_KIEM_DINH"] += 3
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
    files = list(UNCLASS.glob("*.md"))
    conn = __import__("sqlite3").connect(DB)
    by_n2, by_n3 = build_db_index(conn)
    conn.close()

    stats = Counter()
    method_stats = Counter()
    moves: list[dict] = []
    remain = 0

    for p in files:
        content = Path(long_path(p)).read_text(encoding="utf-8", errors="ignore")
        refs = extract_pdf_refs(content, p.stem)
        doc_type, method = match_db(refs, by_n2, by_n3)

        if doc_type:
            target = DOC_TO_LIFECYCLE.get(doc_type, "99_CHUA_PHAN_LOAI")
        else:
            target = classify_content(p.stem, content)
            method = "content_fallback"

        if target == "99_CHUA_PHAN_LOAI":
            remain += 1
        else:
            moves.append({
                "src": str(p),
                "name": p.name,
                "target": target,
                "doc_type": doc_type,
                "method": method,
                "refs": refs[:2],
            })
            stats[target] += 1
            method_stats[method] += 1

    lines = [
        f"Generated: {datetime.datetime.now().isoformat()}",
        f"DRY: {DRY}",
        f"Input 99_CHUA_PHAN_LOAI: {len(files)}",
        f"Di chuyển: {len(moves)}",
        f"Còn lại: {remain}",
        "",
        "Theo thư mục đích:",
    ]
    for k, v in stats.most_common():
        lines.append(f"  {k}: {v}")
    lines.extend(["", "Theo phương pháp:"])
    for k, v in method_stats.most_common():
        lines.append(f"  {k}: {v}")

    if not DRY and moves:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bk = BK / ts
        bk.mkdir(parents=True, exist_ok=True)
        used: set[str] = set()
        for m in moves:
            src = Path(m["src"])
            dst_dir = MD / m["target"]
            dst_dir.mkdir(parents=True, exist_ok=True)
            dst = unique_dest(dst_dir, m["name"], used)
            shutil.copy2(long_path(src), long_path(bk / m["name"]))
            new_rel = str(dst.relative_to(MD)).replace("\\", "/")
            Path(long_path(dst)).write_text(update_md_path(
                Path(long_path(src)).read_text(encoding="utf-8", errors="ignore"), new_rel
            ), encoding="utf-8")
            os.remove(long_path(src))
            m["dest"] = str(dst)
            m["new_md_path"] = new_rel
        lines.append(f"\nBackup: {bk}")

    manifest = {
        "generated_at": datetime.datetime.now().isoformat(),
        "dry_run": DRY,
        "input": len(files),
        "moved": len(moves),
        "remaining": remain,
        "by_target": dict(stats),
        "by_method": dict(method_stats),
        "entries": moves[:500],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

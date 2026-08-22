#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phân loại 99_CHUA_PHAN_LOAI bằng rule + Mistral Vision OCR trên PDF gốc.

Chạy:
  DRY=1 python vision_classify_unclass.py       # xem trước
  LIMIT=50 python vision_classify_unclass.py    # thử 50 file
  python vision_classify_unclass.py             # toàn bộ
"""
from __future__ import annotations

import base64
import datetime
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import fitz
import requests

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

G_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
MD = G_ROOT / "md"
UNCLASS = MD / "99_CHUA_PHAN_LOAI"
ENV = G_ROOT / "00_HE_THONG_VA_SCRIPTS" / ".env"
BK = G_ROOT / "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP" / "_backup_vision_classify"
PROGRESS = G_ROOT / "vision_classify_progress.json"
MANIFEST = G_ROOT / "vision_classify_manifest.json"
REPORT = G_ROOT / "vision_classify_report.txt"

DRY = os.environ.get("DRY") == "1"
LIMIT = int(os.environ.get("LIMIT", "0"))

DOC_TO_DIR = {
    "CALIBRATION": "03_KIEM_DINH",
    "HANDOVER": "02_BAN_GIAO",
    "CONTRACT": "01_MUA_SAM",
    "MAINTENANCE": "04_BAO_TRI",
    "REPAIR": "05_SUA_CHUA",
    "LEGAL": "06_PHAP_LY",
    "SYSTEM": "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP/_md_system_artifacts",
    "OTHER": "99_CHUA_PHAN_LOAI",
}

RE_YAML_SRC = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_YAML_PDF = re.compile(r'^pdf_path:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_JSON_SRC = re.compile(r'"source_pdf"\s*:\s*"([^"]+)"')
RE_WIKI_PDF = re.compile(r"PDF gốc\*\*:\s*\[[^\]]*\]\([^)]*?([^/\\)]+\.pdf)\)", re.I)
RE_WIKI_MD = re.compile(r"Hồ sơ gốc\*\*:\s*\[[^\]]*\]\([^)]*?([^/\\)]+\.md)\)", re.I)
RE_MD_PATH = re.compile(r'^md_path:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

# --- keys ---
MISTRAL_KEYS: list[str] = []
_key_i = 0


def load_keys() -> None:
    global MISTRAL_KEYS
    if ENV.exists():
        for line in ENV.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("MISTRAL_KEYS="):
                MISTRAL_KEYS.extend(k.strip() for k in line.split("=", 1)[1].split(";") if k.strip())
            m = re.match(r"MISTRAL_(?:API_)?KEY(?:_\d+)?=(\S+)", line)
            if m:
                MISTRAL_KEYS.append(m.group(1))
    seen: set[str] = set()
    MISTRAL_KEYS = [k for k in MISTRAL_KEYS if k not in seen and not seen.add(k)]


def next_key() -> str:
    global _key_i
    if not MISTRAL_KEYS:
        raise RuntimeError("Không có Mistral API key trong .env")
    k = MISTRAL_KEYS[_key_i % len(MISTRAL_KEYS)]
    _key_i += 1
    return k


def long_path(p: Path | str) -> str:
    s = os.path.abspath(str(p))
    return s if s.startswith("\\\\?\\") else "\\\\?\\" + s


def norm3(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[\s_.\-/\\]+", "", s.lower())


def build_pdf_index() -> dict[str, list[str]]:
    idx: dict[str, list[str]] = {}
    for dp, _, fn in os.walk(long_path(G_ROOT)):
        for f in fn:
            if not f.lower().endswith(".pdf"):
                continue
            p = os.path.join(dp, f)
            idx.setdefault(norm3(f), []).append(p)
    return idx


def extract_pdf_refs(content: str, stem: str) -> list[str]:
    refs: list[str] = []
    for pat in (RE_YAML_SRC, RE_JSON_SRC):
        m = pat.search(content[:8000])
        if m:
            refs.append(m.group(1).strip())
    m = RE_YAML_PDF.search(content[:8000])
    if m:
        refs.append(m.group(1).strip().strip('"\''))
    m = RE_WIKI_PDF.search(content[:4000])
    if m:
        refs.append(m.group(1).strip())
    if not refs:
        refs.append(stem.replace(".audit", "") + ".pdf")
    return refs


def map_legacy_path(ref: str) -> list[str]:
    candidates = []
    ref = ref.replace("file:////media/tan/T93/", "G:/").replace("/", os.sep)
    if os.path.isabs(ref):
        candidates.append(ref)
    p = ref
    mappings = [
        ("G:" + os.sep + "BV QUẬN 7" + os.sep + "05_KIEM DINH", str(G_ROOT / "04_KIEM_DINH_VA_HIEU_CHUAN")),
        ("G:" + os.sep + "BV QUẬN 7" + os.sep + "02_HOP DONG MUA SAM", str(G_ROOT / "02_HOP_DONG_MUA_SAM")),
        ("G:" + os.sep + "BV QUẬN 7", str(G_ROOT)),
    ]
    for old, new in mappings:
        idx = p.lower().find(old.lower())
        if idx >= 0:
            candidates.append(p[:idx] + new + p[idx + len(old):])
    candidates.append(str(G_ROOT / os.path.basename(ref)))
    return list(dict.fromkeys(candidates))


def resolve_pdf(refs: list[str], pdf_idx: dict[str, list[str]]) -> str | None:
    for ref in refs:
        for cand in map_legacy_path(ref):
            if os.path.exists(long_path(cand)):
                return cand
        base = os.path.basename(ref.replace("/", os.sep))
        n3 = norm3(base)
        if n3 in pdf_idx:
            return pdf_idx[n3][0]
        # fuzzy
        best, best_r = None, 0.0
        for k, paths in pdf_idx.items():
            r = SequenceMatcher(None, n3, k).ratio()
            if r > best_r:
                best_r, best = r, paths[0]
        if best and best_r >= 0.90:
            return best
    return None


def render_page1_png(pdf_path: str) -> bytes:
    doc = fitz.open(long_path(pdf_path))
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=120)
    data = pix.tobytes("png")
    doc.close()
    return data


def ocr_page_mistral(pdf_path: str) -> str:
    """OCR trang 1 PDF qua Mistral OCR API."""
    doc = fitz.open(long_path(pdf_path))
    part = fitz.open()
    part.insert_pdf(doc, from_page=0, to_page=0)
    pdf_bytes = part.tobytes()
    part.close()
    doc.close()

    key = next_key()
    b64 = base64.b64encode(pdf_bytes).decode()
    resp = requests.post(
        "https://api.mistral.ai/v1/ocr",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "mistral-ocr-latest",
            "document": {"type": "document_url", "document_url": f"data:application/pdf;base64,{b64}"},
        },
        timeout=90,
    )
    if resp.status_code != 200:
        return ""
    pages = resp.json().get("pages", [])
    return "\n".join(p.get("markdown", "") for p in pages).strip()


def classify_text(text: str, filename: str) -> tuple[str, str, float]:
    fn = filename.lower().replace("_", " ")
    t = (text + "\n" + fn).lower()

    if any(x in filename.lower() for x in ("trace_missing", "refresh_due")):
        if "giấy chứng nhận" not in t and "056-" not in t:
            return "SYSTEM", "artifact", 0.95

    sys_names = (
        "readme", "session", "notes", "design.md", "log.md", "so_sanh", "kiem_tra",
        "doi_chieu", "dem_", "hanh_dong", "thiet_bi_kham", "notes.original",
    )
    if any(x in filename.lower() for x in sys_names):
        return "SYSTEM", "artifact", 0.92

    if re.search(r"hdsd|huong dan|hướng dẫn|pl\d+\.v\d+.*qt\.04|quick.?guide|protocol", fn):
        return "HANDOVER", "manual_hdsd", 0.85

    if "tệp rỗng" in t or "0 bytes" in t:
        return "SYSTEM", "empty_pdf", 0.90

    scores: Counter = Counter()
    rules = [
        ("CALIBRATION", r"giấy chứng nhận|calibration certificate|056-\d+|01\.\d{2}[hp]-|tem kiểm định|kiểm định an toàn|kiểm xạ|hiệu chuẩn|kết quả kiểm tra.*đạt"),
        ("HANDOVER", r"biên bản bàn giao|bbbg|nghiệm thu|giao nhận thiết bị|bàn giao thiết bị"),
        ("CONTRACT", r"hợp đồng mua bán|hđmb|giá trị hợp đồng|bên mua|bên bán|phiếu giao hàng|bảng kê|bang ke"),
        ("MAINTENANCE", r"bảo trì định kỳ|bảo dưỡng|nhật ký bảo trì"),
        ("REPAIR", r"sửa chữa thiết bị|yêu cầu sửa chữa"),
        ("LEGAL", r"giấy phép|thẩm định|sở y tế|bhxh|lý lịch thiết bị|quy trình.*ttbyt|giay phep"),
    ]
    for cat, pat in rules:
        if re.search(pat, t, re.I):
            scores[cat] += 2
    if re.search(r"giấy kiểm định|kiểm định|mục \d+.*kiểm|gcn|hieu chuan", fn):
        scores["CALIBRATION"] += 3
    if re.search(r"bbbg|ban giao|nghiem thu", fn):
        scores["HANDOVER"] += 3
    if re.search(r"scan_\d", fn):
        scores["CONTRACT"] += 1

    if not scores:
        return "OTHER", "none", 0.0
    cat, score = scores.most_common(1)[0]
    conf = min(0.99, 0.45 + score * 0.18)
    return cat, "text_rules", conf


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
    load_keys()
    pdf_idx = build_pdf_index()
    files = sorted(UNCLASS.glob("*.md"))
    if LIMIT:
        files = files[:LIMIT]

    print(f"Vision classify {len(files)} files | keys={len(MISTRAL_KEYS)} | DRY={DRY}")

    results: list[dict] = []
    stats = Counter()
    method_stats = Counter()
    moved = 0
    used_dest: set[str] = set()

    for i, p in enumerate(files, 1):
        content = Path(long_path(p)).read_text(encoding="utf-8", errors="ignore")
        refs = extract_pdf_refs(content, p.stem)
        pdf = resolve_pdf(refs, pdf_idx)

        # Pass 1: rule trên nội dung md hiện có
        doc_type, method, conf = classify_text(content, p.name)

        # Pass 2: Mistral OCR trang 1 khi có PDF (bắt buộc nếu chưa chắc)
        if pdf and os.path.getsize(long_path(pdf)) > 100 and conf < 0.80:
            try:
                ocr_text = ocr_page_mistral(pdf)
                if ocr_text:
                    doc_type2, method2, conf2 = classify_text(ocr_text, p.name)
                    if conf2 > conf:
                        doc_type, method, conf = doc_type2, "mistral_ocr", conf2
                time.sleep(0.3)
            except Exception as e:
                method = f"ocr_error:{e.__class__.__name__}"

        target_dir_name = DOC_TO_DIR.get(doc_type, "99_CHUA_PHAN_LOAI")
        if doc_type == "SYSTEM":
            target = G_ROOT / "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP" / "_md_system_artifacts"
        else:
            target = MD / target_dir_name

        entry = {
            "file": p.name,
            "pdf": pdf,
            "doc_type": doc_type,
            "target": str(target.relative_to(G_ROOT) if target.is_relative_to(G_ROOT) else target),
            "method": method,
            "confidence": round(conf, 2),
        }
        results.append(entry)
        stats[doc_type] += 1
        method_stats[method] += 1

        if doc_type == "OTHER" or conf < 0.45:
            continue

        if not DRY:
            target.mkdir(parents=True, exist_ok=True)
            dst = unique_dest(target, p.name, used_dest)
            bk_dir = BK / datetime.datetime.now().strftime("%Y%m%d")
            bk_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(long_path(p), long_path(bk_dir / p.name))
            if str(target).startswith(str(MD)):
                new_rel = str(dst.relative_to(MD)).replace("\\", "/")
            else:
                new_rel = str(dst.relative_to(G_ROOT)).replace("\\", "/")
            Path(long_path(dst)).write_text(update_md_path(content, new_rel), encoding="utf-8")
            os.remove(long_path(p))
            moved += 1
            entry["dest"] = str(dst)

        if i % 25 == 0:
            print(f"  [{i}/{len(files)}] last={p.name[:40]} -> {doc_type} ({method})")
            PROGRESS.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"Generated: {datetime.datetime.now().isoformat()}",
        f"Processed: {len(files)}",
        f"Moved: {moved if not DRY else 'DRY'}",
        "",
        "By doc_type:",
    ]
    for k, v in stats.most_common():
        lines.append(f"  {k}: {v}")
    lines.extend(["", "By method:"])
    for k, v in method_stats.most_common():
        lines.append(f"  {k}: {v}")
    remaining = len(list(UNCLASS.glob("*.md")))
    lines.append(f"\nRemaining in 99_CHUA_PHAN_LOAI: {remaining}")

    MANIFEST.write_text(json.dumps({"results": results, "stats": dict(stats)}, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    PROGRESS.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tái cấu trúc md/ theo 6 phân hệ vòng đời, giữ liên kết PDF qua source_pdf + pdf_path.

Chạy:
  DRY=1 python restructure_md_lifecycle.py   # chỉ báo cáo
  python restructure_md_lifecycle.py         # thực thi (backup trước)
"""
from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

G_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
MD_DIR = G_ROOT / "md"
KHO = G_ROOT / "08_KHO_LUU_TRU_TRUNG_LAP_VA_TEMP"
BACKUP_ROOT = KHO / "_backup_md_pre_restructure"
STAGING = MD_DIR / "_restructure_staging"
MANIFEST_OUT = G_ROOT / "md_restructure_manifest.json"
REPORT_OUT = G_ROOT / "md_restructure_report.txt"

DRY = os.environ.get("DRY") == "1"

LIFECYCLE_DIRS = {
    "01_MUA_SAM": "Mua sắm & Hợp đồng",
    "02_BAN_GIAO": "Bàn giao & Nghiệm thu",
    "03_KIEM_DINH": "Kiểm định & Hiệu chuẩn",
    "04_BAO_TRI": "Bảo trì định kỳ",
    "05_SUA_CHUA": "Sửa chữa thiết bị",
    "06_PHAP_LY": "Thẩm định & Pháp lý",
    "99_CHUA_PHAN_LOAI": "Chưa phân loại",
}

SKIP_TOP_FOLDERS = set(LIFECYCLE_DIRS.keys()) | {"_restructure_staging"}

RE_SOURCE_PDF = re.compile(r'^source_pdf:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_PDF_PATH = re.compile(r'^pdf_path:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_MD_PATH = re.compile(r'^md_path:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_DOC_TYPE = re.compile(r'^doc_type:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

DOC_TYPE_TO_LIFECYCLE = {
    "HOP_DONG": "01_MUA_SAM",
    "MUA_SAM": "01_MUA_SAM",
    "CONTRACT": "01_MUA_SAM",
    "HIEU_CHUAN": "03_KIEM_DINH",
    "KIEM_DINH": "03_KIEM_DINH",
    "CALIBRATION": "03_KIEM_DINH",
    "BAN_GIAO": "02_BAN_GIAO",
    "HANDOVER": "02_BAN_GIAO",
    "NGHIEM_THU": "02_BAN_GIAO",
    "BAO_TRI": "04_BAO_TRI",
    "MAINTENANCE": "04_BAO_TRI",
    "SUA_CHUA": "05_SUA_CHUA",
    "REPAIR": "05_SUA_CHUA",
    "PHAP_LY": "06_PHAP_LY",
    "LEGAL": "06_PHAP_LY",
    "THAM_DINH": "06_PHAP_LY",
    "BHXH": "06_PHAP_LY",
}

FOLDER_TO_LIFECYCLE = {
    "02_hop dong mua sam": "01_MUA_SAM",
    "02_hop_dong_mua_sam": "01_MUA_SAM",
    "hop_dong_goc": "01_MUA_SAM",
    "hinh anh tham khao": "01_MUA_SAM",
    "cap cuu - than nhan tao": "02_BAN_GIAO",
    "docs_raw": "02_BAN_GIAO",
    "_ocr_handover_assets": "02_BAN_GIAO",
    "05_kiem dinh": "03_KIEM_DINH",
    "backup_original": "03_KIEM_DINH",
    "2024": "03_KIEM_DINH",
    "2025": "03_KIEM_DINH",
    "2026": "03_KIEM_DINH",
    "kiemdinh_tachfile": "03_KIEM_DINH",
    "04_kiem_dinh_va_hieu_chuan": "03_KIEM_DINH",
    "03_bao tri thiet bi": "04_BAO_TRI",
    "bao_tri_dinh_ky": "04_BAO_TRI",
    "04_sua chua thiet bi": "05_SUA_CHUA",
    "sua_chua_thiet bi": "05_SUA_CHUA",
    "hop ong noi soi": "05_SUA_CHUA",
    "06_tham dinh": "06_PHAP_LY",
    "07_bao hiem xa hoi": "06_PHAP_LY",
    "tham_dinh_so_y_te": "06_PHAP_LY",
    "bao_hiem_xa_hoi": "06_PHAP_LY",
}


def norm2(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().replace("_1", "").strip()


def norm3(s: str) -> str:
    return re.sub(r"[\s_.\-]+", "", norm2(s))


def long_path(p: Path | str) -> str:
    s = os.path.abspath(str(p))
    if s.startswith("\\\\?\\"):
        return s
    return "\\\\?\\" + s


def ensure_dir(p: Path) -> None:
    os.makedirs(long_path(p), exist_ok=True)


def safe_copy2(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(long_path(src), long_path(dst))


def safe_move(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.move(long_path(src), long_path(dst))


def safe_rmtree(p: Path) -> None:
    if p.exists():
        shutil.rmtree(long_path(p))


def flat_backup_name(rel_path: str) -> str:
    """Tên phẳng tránh vượt MAX_PATH khi backup."""
    return rel_path.replace("\\", "__").replace("/", "__")


def build_pdf_index() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    by_n2: dict[str, list[str]] = defaultdict(list)
    by_n3: dict[str, list[str]] = defaultdict(list)
    for dp, _, fn in os.walk(long_path(G_ROOT)):
        for f in fn:
            if not f.lower().endswith(".pdf"):
                continue
            p = os.path.join(dp, f)
            by_n2[norm2(f)].append(p)
            by_n3[norm3(f)].append(p)
    return by_n2, by_n3


def resolve_pdf(source_pdf: str | None, pdf_path_val: str | None, by_n2, by_n3) -> tuple[str | None, str]:
    """Trả (absolute_path, method)."""
    candidates: list[str] = []
    for val in (pdf_path_val, source_pdf):
        if not val:
            continue
        val = val.strip().strip('"\'')
        if os.path.isabs(val) and os.path.exists(long_path(val)):
            return val, "pdf_path_exists"
        basename = os.path.basename(val.replace("/", os.sep))
        if os.path.exists(long_path(G_ROOT / basename)):
            return str(G_ROOT / basename), "basename_at_root"
        if norm2(basename) in by_n2:
            return by_n2[norm2(basename)][0], "index_norm2"
        if norm3(basename) in by_n3:
            return by_n3[norm3(basename)][0], "index_norm3"

    if source_pdf:
        b = norm3(os.path.basename(source_pdf))
        if b in by_n3:
            return by_n3[b][0], "source_norm3"
        # fuzzy fallback
        best = None
        best_r = 0.0
        for k, paths in by_n3.items():
            r = SequenceMatcher(None, b, k).ratio()
            if r > best_r:
                best_r, best = r, paths[0]
        if best and best_r >= 0.88:
            return best, f"fuzzy_{best_r:.2f}"

    return None, "unresolved"


def classify_lifecycle(rel_path: str, doc_type: str | None, stem: str) -> str:
    if doc_type:
        dt = doc_type.strip().upper().replace(" ", "_")
        if dt in DOC_TYPE_TO_LIFECYCLE:
            return DOC_TYPE_TO_LIFECYCLE[dt]

    rel_lower = norm2(rel_path.replace("\\", "/"))
    parts = [norm2(p) for p in rel_path.replace("\\", "/").split("/") if p and p != "."]

    for part in parts:
        if part in FOLDER_TO_LIFECYCLE:
            return FOLDER_TO_LIFECYCLE[part]

    stem_u = stem.upper()
    if stem_u.startswith("BBBG") or "BAN GIAO" in stem_u or "NGHIEM THU" in stem_u:
        return "02_BAN_GIAO"
    if re.search(r"\bH[DĐ]\b|HOP.?DONG|HDMB|HDKT", stem_u):
        return "01_MUA_SAM"
    if re.match(r"^056-", stem) or "KIEM DINH" in stem_u or "HIEU CHUAN" in stem_u:
        return "03_KIEM_DINH"
    if "BAO TRI" in stem_u or "BAO DUONG" in stem_u:
        return "04_BAO_TRI"
    if "SUA CHUA" in stem_u or "SC-" in stem_u:
        return "05_SUA_CHUA"
    if "THAM DINH" in stem_u or "BHXH" in stem_u or "PHAP LY" in stem_u:
        return "06_PHAP_LY"

    if any(x in rel_lower for x in ("hop dong", "mua sam", "co cq", "to khai")):
        return "01_MUA_SAM"
    if any(x in rel_lower for x in ("ban giao", "nghiem thu", "bbbg")):
        return "02_BAN_GIAO"
    if any(x in rel_lower for x in ("kiem dinh", "hieu chuan", "2024", "2025", "2026")):
        return "03_KIEM_DINH"
    if "bao tri" in rel_lower:
        return "04_BAO_TRI"
    if "sua chua" in rel_lower:
        return "05_SUA_CHUA"
    if any(x in rel_lower for x in ("tham dinh", "phap ly", "bao hiem")):
        return "06_PHAP_LY"

    return "99_CHUA_PHAN_LOAI"


def clean_path_for_frontmatter(p: str) -> str:
    s = p.replace("\\\\?\\", "").replace("\\", "/")
    if s.startswith("//?/"):
        s = s[4:]
    return s


def update_frontmatter(content: str, new_md_rel: str, resolved_pdf: str | None) -> str:
    m = RE_FRONTMATTER.match(content)
    if not m:
        return content

    body = content[m.end():]
    fm = m.group(1)

    if RE_MD_PATH.search(fm):
        fm = RE_MD_PATH.sub(f'md_path: "{new_md_rel}"', fm, count=1)
    else:
        fm = fm.rstrip() + f'\nmd_path: "{new_md_rel}"'

    if resolved_pdf:
        pdf_fm = clean_path_for_frontmatter(resolved_pdf)
        if RE_PDF_PATH.search(fm):
            fm = RE_PDF_PATH.sub(f'pdf_path: "{pdf_fm}"', fm, count=1)
        else:
            fm = fm.rstrip() + f'\npdf_path: "{pdf_fm}"'

    return f"---\n{fm}\n---{body}"


def unique_dest(base_dir: Path, filename: str, used: set[str]) -> Path:
    dest = base_dir / filename
    if str(dest) not in used and not os.path.exists(long_path(dest)):
        used.add(str(dest))
        return dest
    stem = Path(filename).stem
    ext = Path(filename).suffix
    i = 1
    while True:
        candidate = base_dir / f"{stem}_{i}{ext}"
        if str(candidate) not in used and not os.path.exists(long_path(candidate)):
            used.add(str(candidate))
            return candidate
        i += 1


def collect_md_files() -> list[Path]:
    files: list[Path] = []
    for p in MD_DIR.rglob("*.md"):
        rel = p.relative_to(MD_DIR)
        top = rel.parts[0] if len(rel.parts) > 1 else None
        if top in SKIP_TOP_FOLDERS:
            continue
        files.append(p)
    return files


def main() -> None:
    print("=" * 70)
    print("TÁI CẤU TRÚC md/ THEO 6 PHÂN HỆ VÒNG ĐỜI")
    print(f"DRY RUN: {DRY}")
    print("=" * 70)

    by_n2, by_n3 = build_pdf_index()
    print(f"PDF index: {sum(len(v) for v in by_n2.values())} entries")

    md_files = collect_md_files()
    print(f"MD files to process: {len(md_files)}")

    plan: list[dict] = []
    lifecycle_counts: Counter = Counter()
    pdf_resolved = 0
    pdf_unresolved = 0

    for md_path in md_files:
        rel_old = str(md_path.relative_to(MD_DIR)).replace("\\", "/")
        try:
            content = md_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as e:
            plan.append({"old_path": rel_old, "error": str(e)})
            continue

        doc_type = None
        m_dt = RE_DOC_TYPE.search(content[:3000])
        if m_dt:
            doc_type = m_dt.group(1).strip().strip('"\'')
        m_src = RE_SOURCE_PDF.search(content[:3000])
        source_pdf = m_src.group(1).strip().strip('"\'') if m_src else None
        m_pp = RE_PDF_PATH.search(content[:3000])
        pdf_path_val = m_pp.group(1).strip().strip('"\'') if m_pp else None

        lifecycle = classify_lifecycle(rel_old, doc_type, md_path.stem)
        lifecycle_counts[lifecycle] += 1

        resolved, method = resolve_pdf(source_pdf, pdf_path_val, by_n2, by_n3)
        if resolved:
            pdf_resolved += 1
        else:
            pdf_unresolved += 1

        new_rel = f"{lifecycle}/{md_path.name}"
        plan.append({
            "old_path": rel_old,
            "new_path": new_rel,
            "lifecycle": lifecycle,
            "doc_type": doc_type,
            "source_pdf": source_pdf,
            "old_pdf_path": pdf_path_val,
            "resolved_pdf": resolved,
            "resolve_method": method,
            "pdf_exists": bool(resolved and os.path.exists(long_path(resolved))),
        })

    manifest = {
        "generated_at": datetime.datetime.now().isoformat(),
        "dry_run": DRY,
        "total_md": len(md_files),
        "lifecycle_counts": dict(lifecycle_counts),
        "pdf_resolved": pdf_resolved,
        "pdf_unresolved": pdf_unresolved,
        "entries": plan,
    }

    lines = [
        f"Generated: {manifest['generated_at']}",
        f"DRY RUN: {DRY}",
        f"Total MD: {len(md_files)}",
        f"PDF resolved: {pdf_resolved}",
        f"PDF unresolved: {pdf_unresolved}",
        "",
        "Lifecycle breakdown:",
    ]
    for k, v in lifecycle_counts.most_common():
        lines.append(f"  {k} ({LIFECYCLE_DIRS.get(k, k)}): {v}")

    broken = [e for e in plan if e.get("source_pdf") and not e.get("pdf_exists")]
    lines.extend(["", f"Broken PDF links after resolve: {len(broken)}"])
    for e in broken[:50]:
        lines.append(f"  {e['old_path']} | src={e.get('source_pdf')}")
    if len(broken) > 50:
        lines.append(f"  ... and {len(broken) - 50} more")

    if not DRY:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = BACKUP_ROOT / ts
        ensure_dir(backup_dir)

        safe_rmtree(STAGING)
        ensure_dir(STAGING)

        used_dest: set[str] = set()
        moved = 0
        skipped = 0

        for entry in plan:
            if "error" in entry:
                continue
            src = MD_DIR / entry["old_path"].replace("/", os.sep)
            if not src.exists():
                skipped += 1
                continue

            dest_dir = STAGING / entry["lifecycle"]
            ensure_dir(dest_dir)
            dest = unique_dest(dest_dir, src.name, used_dest)

            safe_copy2(src, backup_dir / flat_backup_name(entry["old_path"]))

            content = Path(long_path(src)).read_text(encoding="utf-8", errors="ignore")
            new_rel = str(dest.relative_to(STAGING)).replace("\\", "/")
            new_content = update_frontmatter(content, new_rel, entry.get("resolved_pdf"))
            Path(long_path(dest)).write_text(new_content, encoding="utf-8")
            entry["new_path"] = new_rel
            moved += 1

        # Remove old non-lifecycle folders/files from md/
        for item in list(MD_DIR.iterdir()):
            if item.name in SKIP_TOP_FOLDERS:
                continue
            if item.is_dir():
                safe_rmtree(item)
            elif item.is_file() and item.suffix.lower() == ".md":
                safe_copy2(item, backup_dir / flat_backup_name(item.name))
                os.remove(long_path(item))

        # Promote staging -> md lifecycle folders
        for lifecycle in LIFECYCLE_DIRS:
            src_dir = STAGING / lifecycle
            if not src_dir.exists():
                continue
            dst_dir = MD_DIR / lifecycle
            safe_rmtree(dst_dir)
            safe_move(src_dir, dst_dir)

        safe_rmtree(STAGING)

        manifest["moved"] = moved
        manifest["skipped_missing"] = skipped
        lines.append(f"\nMoved files: {moved}")
        lines.append(f"Skipped (already moved): {skipped}")
        lines.append(f"Backup at: {backup_dir}")

    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines[:20]))
    print(f"\nManifest: {MANIFEST_OUT}")
    print(f"Report:   {REPORT_OUT}")


if __name__ == "__main__":
    main()

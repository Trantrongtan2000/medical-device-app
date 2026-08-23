#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit phân loại 03_KIEM_DINH — tìm file bị gán nhầm."""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

G_ROOT = Path(r"G:\BV QUẬN 7_OCR_WORK_20260712")
KIEM_DIR = G_ROOT / "md" / "03_KIEM_DINH"
MANIFEST = G_ROOT / "md_restructure_manifest.json"
OUT_JSON = G_ROOT / "kiemdinh_audit_report.json"
OUT_TXT = G_ROOT / "kiemdinh_audit_report.txt"

RE_DOC_TYPE = re.compile(r'^doc_type:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_CERT = re.compile(r'^cert_no:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_STAMP = re.compile(r'^stamp_no:\s*["\']?(.+?)["\']?\s*$', re.M)
RE_CALIB = re.compile(r'^calibration_date:\s*["\']?(.+?)["\']?\s*$', re.M)

# Tín hiệu nội dung thực sự là GCN kiểm định
SIG_KIEMDINH = re.compile(
    r"(giấy chứng nhận|chứng nhận kiểm định|kiểm định định kỳ|tem kiểm định|"
    r"đo lường chuẩn|hiệu chuẩn|056-\d+|01\.\d{2}[HP]-|stamp|tem kd)",
    re.I,
)
SIG_HOPDONG = re.compile(
    r"(hợp đồng|hđmb|hđkt|điều khoản|giá trị hợp đồng|bên mua|bên bán|"
    r"thanh toán|đặt cọc|bảo lãnh|phụ lục hợp đồng)",
    re.I,
)
SIG_BANGIAO = re.compile(
    r"(biên bản bàn giao|bbbg|nghiệm thu|bàn giao thiết bị|lắp đặt nghiệm thu)",
    re.I,
)
SIG_BAOTRI = re.compile(
    r"(bảo trì|bảo dưỡng|sửa chữa|nhật ký bảo trì|maintenance)",
    re.I,
)
SIG_PHAPLY = re.compile(
    r"(thẩm định|sở y tế|bhxh|cấp phép|giấy phép hoạt động)",
    re.I,
)

# Pattern tên file
FN_KIEMDINH = re.compile(r"^056-|01\.\d{2}[HP]-|GCN|KIEM.?DINH|HIEU.?CHUAN", re.I)
FN_HOPDONG = re.compile(r"\bH[DĐ]\b|HOP.?DONG|HDMB|HDKT|HD-|HĐ-|NT\s|NGHIEM.?THU", re.I)
FN_BANGIAO = re.compile(r"^BBBG|BAN.?GIAO|BG_", re.I)


def read_head(p: Path, n: int = 4000) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")[:n]
    except OSError:
        return ""


def classify_signal(stem: str, head: str, body_sample: str) -> str:
    text = head + "\n" + body_sample[:3000]
    scores = Counter()

    if FN_KIEMDINH.search(stem):
        scores["03_KIEM_DINH"] += 3
    if FN_HOPDONG.search(stem):
        scores["01_MUA_SAM"] += 3
    if FN_BANGIAO.search(stem):
        scores["02_BAN_GIAO"] += 3

    if SIG_KIEMDINH.search(text):
        scores["03_KIEM_DINH"] += 2
    if SIG_HOPDONG.search(text):
        scores["01_MUA_SAM"] += 2
    if SIG_BANGIAO.search(text):
        scores["02_BAN_GIAO"] += 2
    if SIG_BAOTRI.search(text):
        scores["04_BAO_TRI"] += 1
        scores["05_SUA_CHUA"] += 1
    if SIG_PHAPLY.search(text):
        scores["06_PHAP_LY"] += 2

    if not scores:
        return "99_CHUA_PHAN_LOAI"
    return scores.most_common(1)[0][0]


def audit():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = [e for e in manifest["entries"] if e.get("lifecycle") == "03_KIEM_DINH"]

    stats = {
        "total_in_03": len(entries),
        "by_old_folder": Counter(),
        "by_doc_type": Counter(),
        "has_cert_no": 0,
        "has_stamp_no": 0,
        "has_calibration_date": 0,
        "has_hieu_chuan_doc_type": 0,
        "filename_056_pattern": 0,
        "likely_misclassified": [],
        "suggested_moves": Counter(),
    }

    for e in entries:
        old = e.get("old_path", "")
        top = old.split("/")[0] if "/" in old else old.split("\\")[0]
        stats["by_old_folder"][top] += 1

        p = KIEM_DIR / Path(e.get("new_path", "").replace("03_KIEM_DINH/", "")).name
        if not p.exists():
            p = KIEM_DIR / Path(old).name
        if not p.exists():
            continue

        head = read_head(p)
        body = read_head(p, 8000)[4000:]

        dt = RE_DOC_TYPE.search(head)
        doc_type = dt.group(1).strip().strip('"\'') if dt else None
        stats["by_doc_type"][doc_type or "(none)"] += 1

        if RE_CERT.search(head):
            stats["has_cert_no"] += 1
        if RE_STAMP.search(head):
            stats["has_stamp_no"] += 1
        if RE_CALIB.search(head):
            cal = RE_CALIB.search(head).group(1).strip().strip('"\'')
            if cal and cal not in ("", "-", "null", "None"):
                stats["has_calibration_date"] += 1
        if doc_type and doc_type.upper() in ("HIEU_CHUAN", "KIEM_DINH", "CALIBRATION"):
            stats["has_hieu_chuan_doc_type"] += 1
        if FN_KIEMDINH.search(p.stem):
            stats["filename_056_pattern"] += 1

        suggested = classify_signal(p.stem, head, body)
        if suggested != "03_KIEM_DINH":
            stats["suggested_moves"][suggested] += 1
            stats["likely_misclassified"].append({
                "file": p.name,
                "old_path": old,
                "doc_type": doc_type,
                "suggested": suggested,
                "has_cert_no": bool(RE_CERT.search(head)),
                "has_stamp_no": bool(RE_STAMP.search(head)),
            })

    # Chỉ giữ top 200 mẫu misclassified trong JSON
    stats["likely_misclassified"] = stats["likely_misclassified"][:200]
    stats["by_old_folder"] = dict(stats["by_old_folder"].most_common(30))
    stats["by_doc_type"] = dict(stats["by_doc_type"].most_common(20))
    stats["suggested_moves"] = dict(stats["suggested_moves"])

    true_kiemdinh = (
        stats["has_hieu_chuan_doc_type"]
        + stats["filename_056_pattern"]
        - min(stats["has_hieu_chuan_doc_type"], stats["filename_056_pattern"])  # overlap rough
    )

    lines = [
        "=" * 70,
        "AUDIT PHÂN LOẠI 03_KIEM_DINH",
        "=" * 70,
        f"Tổng file trong 03_KIEM_DINH: {stats['total_in_03']}",
        "",
        "=== Dấu hiệu THỰC SỰ là GCN kiểm định ===",
        f"  doc_type HIEU_CHUAN/KIEM_DINH:     {stats['has_hieu_chuan_doc_type']}",
        f"  Tên file pattern 056-/01.26H/P-:   {stats['filename_056_pattern']}",
        f"  Có cert_no:                        {stats['has_cert_no']}",
        f"  Có stamp_no:                       {stats['has_stamp_no']}",
        f"  Có calibration_date hợp lệ:        {stats['has_calibration_date']}",
        "",
        "=== Nguồn gốc (thư mục cũ trước restructure) ===",
    ]
    for k, v in sorted(stats["by_old_folder"].items(), key=lambda x: -x[1])[:15]:
        lines.append(f"  {k}: {v}")

    lines.extend(["", "=== doc_type trong frontmatter ==="])
    for k, v in sorted(stats["by_doc_type"].items(), key=lambda x: -x[1])[:10]:
        lines.append(f"  {k}: {v}")

    lines.extend([
        "",
        "=== PHÁT HIỆN: File có thể bị gán NHẦM vào kiểm định ===",
        f"  Tổng nghi ngờ misclassify: {sum(stats['suggested_moves'].values())}",
    ])
    for k, v in sorted(stats["suggested_moves"].items(), key=lambda x: -x[1]):
        lines.append(f"  -> nên chuyển sang {k}: {v}")

    lines.extend(["", "=== Mẫu 30 file nghi ngờ nhất (không phải kiểm định) ==="])
    samples = [x for x in stats["likely_misclassified"] if x["suggested"] == "01_MUA_SAM"][:15]
    samples += [x for x in stats["likely_misclassified"] if x["suggested"] == "02_BAN_GIAO"][:10]
    samples += [x for x in stats["likely_misclassified"] if x["suggested"] == "06_PHAP_LY"][:5]
    for s in samples[:30]:
        lines.append(f"  [{s['suggested']}] {s['file']}")
        lines.append(f"       old={s['old_path'][:80]}  doc_type={s['doc_type']}")

    lines.extend([
        "",
        "=== KẾT LUẬN ===",
        f"  GCN kiểm định thực (ước tính): ~{stats['has_hieu_chuan_doc_type']} (doc_type HIEU_CHUAN)",
        f"  File từ thư mục 2024/2025 (hỗn hợp HĐ+NT+BBBG): ~{stats['by_old_folder'].get('2024',0)+stats['by_old_folder'].get('2025',0)}",
        f"  Cần di chuyển lại: ~{sum(stats['suggested_moves'].values())} file",
    ])

    OUT_JSON.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    audit()

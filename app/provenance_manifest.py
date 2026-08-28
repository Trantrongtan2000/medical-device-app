"""Deterministic, side-effect-free provenance manifests for document evidence."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def build_document_manifest(
    file_path: str | Path,
    *,
    parser_engine: Optional[str] = None,
    ocr_engine: Optional[str] = None,
) -> dict[str, Any]:
    """Build a manifest without inventing evidence for missing files."""
    path = Path(file_path).expanduser()
    manifest: dict[str, Any] = {
        "manifest_version": 1,
        "path": str(path.resolve(strict=False)),
        "exists": False,
        "size_bytes": None,
        "mtime_ns": None,
        "mtime_utc": None,
        "sha256": None,
        "parser_engine": parser_engine,
        "ocr_engine": ocr_engine,
    }
    try:
        stat = path.stat()
    except (FileNotFoundError, OSError):
        return manifest
    if not path.is_file():
        return manifest

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    manifest.update(
        exists=True,
        size_bytes=stat.st_size,
        mtime_ns=stat.st_mtime_ns,
        mtime_utc=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        sha256=digest.hexdigest(),
    )
    return manifest


def write_document_manifest(manifest: dict[str, Any], output_path: str | Path) -> Path:
    """Write stable JSON (sorted keys, fixed indentation, trailing newline)."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return destination
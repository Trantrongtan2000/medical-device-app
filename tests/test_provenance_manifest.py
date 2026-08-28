from app.provenance_manifest import build_document_manifest, write_document_manifest


def test_manifest_hash_metadata_and_stable_json(tmp_path):
    source = tmp_path / "evidence.pdf"
    source.write_bytes(b"evidence-v1")
    manifest = build_document_manifest(source, parser_engine="pdf-parser-1", ocr_engine="mistral-ocr-test")
    assert manifest["exists"] is True
    assert manifest["size_bytes"] == len(b"evidence-v1")
    assert manifest["sha256"]
    output = write_document_manifest(manifest, tmp_path / "provenance" / "manifest.json")
    first = output.read_text(encoding="utf-8")
    write_document_manifest(manifest, output)
    assert output.read_text(encoding="utf-8") == first
    assert '"sha256"' in first


def test_missing_manifest_has_no_fake_hash(tmp_path):
    manifest = build_document_manifest(tmp_path / "missing.pdf", parser_engine="unknown")
    assert manifest["exists"] is False
    assert manifest["sha256"] is None
    assert manifest["size_bytes"] is None
    assert manifest["mtime_ns"] is None
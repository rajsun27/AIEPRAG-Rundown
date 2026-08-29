import json

from src.manifest import build_manifest, write_manifest


def test_build_manifest_shape():
    manifest = build_manifest(
        batch_id="batch-1",
        source_document={"id": "doc-1", "file_name": "f.pdf", "file_type": "pdf", "checksum": "sha256:abc"},
        artifacts=[
            {"artifact_id": "a-1", "chunk_id": "c-1", "artifact_type": "semantic_chunk", "text": "...", "metadata": {}}
        ],
    )

    assert manifest["batch_id"] == "batch-1"
    assert manifest["source_document"]["file_name"] == "f.pdf"
    assert len(manifest["artifacts"]) == 1
    assert "generated_at" in manifest


def test_write_manifest_json_round_trips(tmp_path):
    manifest = build_manifest(
        batch_id="batch-1",
        source_document={"id": "doc-1", "file_name": "f.pdf", "file_type": "pdf", "checksum": "sha256:abc"},
        artifacts=[
            {"artifact_id": "a-1", "chunk_id": "c-1", "artifact_type": "semantic_chunk", "text": "...", "metadata": {}}
        ],
    )
    output_path = tmp_path / "out" / "manifest.json"

    written_path = write_manifest(manifest, output_path)

    assert written_path == output_path
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["batch_id"] == "batch-1"
    assert loaded["artifacts"][0]["artifact_id"] == "a-1"


def test_write_manifest_unsupported_extension_raises(tmp_path):
    manifest = build_manifest("batch-1", {"id": "doc-1", "file_name": "f.pdf"}, [])
    try:
        write_manifest(manifest, tmp_path / "manifest.xyz")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "Unsupported manifest output format" in str(e)

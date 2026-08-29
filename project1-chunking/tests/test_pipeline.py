import json
from pathlib import Path

from src.lineage import LineageWriter
from src.pipeline import run_pipeline
from tests.fakes import FakeConnection, install_fake_chonkie, install_fake_docling, install_fake_ollama


def test_run_pipeline_txt_only_semantic_chunks(tmp_path, monkeypatch):
    install_fake_ollama(monkeypatch)
    install_fake_chonkie(
        monkeypatch,
        spans=[("Paragraph one.", 0, 14), ("Paragraph two.", 16, 30)],
    )

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "sample.txt").write_text("Paragraph one.\n\nParagraph two.", encoding="utf-8")
    output_dir = tmp_path / "output"

    writer = LineageWriter(FakeConnection())
    written = run_pipeline(str(input_dir), str(output_dir), "config/artifact_config.yaml", writer)

    assert len(written) == 1
    manifest = json.loads(Path(written[0]).read_text(encoding="utf-8"))
    assert manifest["source_document"]["file_name"] == "sample.txt"
    artifact_types = {a["artifact_type"] for a in manifest["artifacts"]}
    assert artifact_types == {"semantic_chunk"}  # txt config only enables semantic_chunk
    assert len(manifest["artifacts"]) == 2


def test_run_pipeline_pdf_generates_all_configured_artifacts(tmp_path, monkeypatch):
    install_fake_docling(monkeypatch, "# Doc\n\nParagraph one. Paragraph two.", num_pages=1)
    install_fake_chonkie(
        monkeypatch,
        spans=[("Paragraph one.", 0, 14), ("Paragraph two.", 15, 29)],
    )
    install_fake_ollama(monkeypatch, reply="Q: What?\nA: This.\n\n- A factoid.")

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "sample.pdf").write_bytes(b"dummy pdf bytes, docling is mocked")
    output_dir = tmp_path / "output"

    writer = LineageWriter(FakeConnection())
    written = run_pipeline(str(input_dir), str(output_dir), "config/artifact_config.yaml", writer)

    manifest = json.loads(Path(written[0]).read_text(encoding="utf-8"))
    artifact_types = {a["artifact_type"] for a in manifest["artifacts"]}
    # pdf config in artifact_config.yaml enables all artifact types
    assert "semantic_chunk" in artifact_types
    assert "contextual_chunk" in artifact_types
    assert "raptor_summary" in artifact_types
    assert "abstractive_summary" in artifact_types
    assert "qa_pair" in artifact_types
    assert "factoid" in artifact_types


def test_run_pipeline_processes_multiple_files(tmp_path, monkeypatch):
    install_fake_ollama(monkeypatch)
    install_fake_chonkie(monkeypatch, spans=[("Only chunk.", 0, 11)])

    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "a.txt").write_text("Only chunk.", encoding="utf-8")
    (input_dir / "b.txt").write_text("Only chunk.", encoding="utf-8")
    output_dir = tmp_path / "output"

    writer = LineageWriter(FakeConnection())
    written = run_pipeline(str(input_dir), str(output_dir), "config/artifact_config.yaml", writer)

    assert len(written) == 2

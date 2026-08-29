from src.lineage import LineageWriter
from tests.fakes import FakeConnection


def test_insert_source_document_returns_new_id():
    conn = FakeConnection()
    writer = LineageWriter(conn)

    doc_id = writer.insert_source_document("f.pdf", "/docs/f.pdf", "pdf", "sha256:abc")

    assert doc_id
    assert conn.committed == 1


def test_insert_source_document_dedupes_by_checksum():
    conn = FakeConnection()
    writer = LineageWriter(conn)

    first_id = writer.insert_source_document("f.pdf", "/docs/f.pdf", "pdf", "sha256:abc")
    second_id = writer.insert_source_document("f.pdf", "/docs/f.pdf", "pdf", "sha256:abc")

    assert first_id == second_id


def test_insert_chunk_links_to_source_document():
    conn = FakeConnection()
    writer = LineageWriter(conn)
    doc_id = writer.insert_source_document("f.pdf", "/docs/f.pdf", "pdf", "sha256:abc")

    chunk_id = writer.insert_chunk(doc_id, 0, "chunk text", 0, 10, token_count=3)

    assert chunk_id
    insert_query, params = conn.executed[-1]
    assert insert_query.startswith("INSERT INTO chunk")
    assert params[1] == doc_id


def test_insert_artifact_requires_chunk_or_document():
    conn = FakeConnection()
    writer = LineageWriter(conn)

    try:
        writer.insert_artifact("factoid", "text", "ollama:llama3.1")
        assert False, "expected ValueError"
    except ValueError as e:
        assert "chunk_id or a source_document_id" in str(e)


def test_insert_artifact_with_parent_for_raptor():
    conn = FakeConnection()
    writer = LineageWriter(conn)
    doc_id = writer.insert_source_document("f.pdf", "/docs/f.pdf", "pdf", "sha256:abc")
    chunk_id = writer.insert_chunk(doc_id, 0, "chunk text", 0, 10)
    child_artifact_id = writer.insert_artifact(
        "semantic_chunk", "chunk text", "chonkie", chunk_id=chunk_id
    )

    parent_id = writer.insert_artifact(
        "raptor_summary",
        "summary text",
        "ollama:llama3.1",
        source_document_id=doc_id,
        parent_artifact_id=child_artifact_id,
        metadata={"raptor_level": 1},
    )

    assert parent_id
    insert_query, params = conn.executed[-1]
    assert params[3] == child_artifact_id  # parent_artifact_id positional slot

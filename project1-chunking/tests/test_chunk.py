import sys
import types

from src.chunk import semantic_chunk


def _install_fake_chonkie(monkeypatch, spans):
    fake_chunks = [
        types.SimpleNamespace(
            text=text, start_index=start, end_index=end, token_count=(end - start) // 4
        )
        for text, start, end in spans
    ]

    class FakeSemanticChunker:
        def __init__(self, chunk_size=512):
            self.chunk_size = chunk_size

        def chunk(self, markdown):
            return fake_chunks

    fake_module = types.SimpleNamespace(SemanticChunker=FakeSemanticChunker)
    monkeypatch.setitem(sys.modules, "chonkie", fake_module)


def test_semantic_chunk_empty_markdown_returns_no_chunks():
    assert semantic_chunk("") == []
    assert semantic_chunk("   \n  ") == []


def test_semantic_chunk_returns_char_offsets(monkeypatch):
    markdown = "Paragraph one. Paragraph two."
    _install_fake_chonkie(
        monkeypatch,
        spans=[("Paragraph one.", 0, 14), ("Paragraph two.", 15, 29)],
    )

    chunks = semantic_chunk(markdown)

    assert len(chunks) == 2
    assert chunks[0]["text"] == "Paragraph one."
    assert chunks[0]["char_start"] == 0
    assert chunks[0]["char_end"] == 14
    assert chunks[1]["char_start"] == 15
    assert chunks[1]["char_end"] == 29


def test_semantic_chunk_boundaries_do_not_overlap(monkeypatch):
    _install_fake_chonkie(
        monkeypatch,
        spans=[("A", 0, 1), ("B", 1, 2), ("C", 2, 3)],
    )

    chunks = semantic_chunk("ABC")

    for prev, curr in zip(chunks, chunks[1:]):
        assert prev["char_end"] <= curr["char_start"]

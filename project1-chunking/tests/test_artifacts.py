import sys
import types

from src.artifacts import (
    generate_abstractive_summary,
    generate_contextual_chunk,
    generate_factoids,
    generate_qa_pairs,
    generate_raptor_summary,
)


def _install_fake_ollama(monkeypatch, reply: str):
    def fake_chat(model, messages):
        return {"message": {"content": reply}}

    fake_module = types.SimpleNamespace(chat=fake_chat)
    monkeypatch.setitem(sys.modules, "ollama", fake_module)


def test_generate_contextual_chunk(monkeypatch):
    _install_fake_ollama(monkeypatch, "Contextualized chunk text.")
    result = generate_contextual_chunk("chunk", "context")
    assert result.artifact_type == "contextual_chunk"
    assert result.text == "Contextualized chunk text."


def test_generate_abstractive_summary(monkeypatch):
    _install_fake_ollama(monkeypatch, "A concise summary.")
    result = generate_abstractive_summary("some long document text")
    assert result.artifact_type == "abstractive_summary"
    assert result.text == "A concise summary."


def test_generate_raptor_summary_includes_level_metadata(monkeypatch):
    _install_fake_ollama(monkeypatch, "Higher-level summary.")
    result = generate_raptor_summary(["child one", "child two"], level=2)
    assert result.artifact_type == "raptor_summary"
    assert result.metadata["raptor_level"] == 2


def test_generate_qa_pairs_parses_multiple_pairs(monkeypatch):
    _install_fake_ollama(
        monkeypatch,
        "Q: What is X?\nA: X is Y.\n\nQ: What is Z?\nA: Z is W.",
    )
    results = generate_qa_pairs("some chunk text")
    assert len(results) == 2
    assert results[0].metadata == {"question": "What is X?", "answer": "X is Y."}
    assert results[1].metadata == {"question": "What is Z?", "answer": "Z is W."}
    assert all(r.artifact_type == "qa_pair" for r in results)


def test_generate_qa_pairs_ignores_malformed_output(monkeypatch):
    _install_fake_ollama(monkeypatch, "This is not in the expected format.")
    results = generate_qa_pairs("some chunk text")
    assert results == []


def test_generate_factoids_parses_bullet_list(monkeypatch):
    _install_fake_ollama(monkeypatch, "- Fact one.\n- Fact two.\nNot a factoid line.")
    results = generate_factoids("some chunk text")
    assert [r.text for r in results] == ["Fact one.", "Fact two."]
    assert all(r.artifact_type == "factoid" for r in results)

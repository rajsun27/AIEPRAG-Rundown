import sys
import types

import pytest

from src.convert import ConversionError, convert_to_markdown

FIXTURES = "tests/fixtures"


def test_convert_txt_passthrough():
    result = convert_to_markdown(f"{FIXTURES}/sample.txt")
    assert "plain text sample document" in result["markdown"]
    assert result["page_count"] == 1


def test_convert_unsupported_type_raises(tmp_path):
    bad_file = tmp_path / "sample.xyz"
    bad_file.write_text("data")
    with pytest.raises(ConversionError, match="Unsupported file type"):
        convert_to_markdown(bad_file)


def _install_fake_docling(monkeypatch, markdown_text, num_pages):
    fake_document = types.SimpleNamespace(
        export_to_markdown=lambda: markdown_text, num_pages=num_pages
    )
    fake_result = types.SimpleNamespace(document=fake_document)

    class FakeDocumentConverter:
        def convert(self, path):
            return fake_result

    fake_module = types.SimpleNamespace(DocumentConverter=FakeDocumentConverter)
    monkeypatch.setitem(sys.modules, "docling.document_converter", fake_module)
    monkeypatch.setitem(sys.modules, "docling", types.SimpleNamespace())


def test_convert_html_uses_docling(monkeypatch):
    _install_fake_docling(monkeypatch, "# Sample HTML\n\nParagraph one.", num_pages=1)
    result = convert_to_markdown(f"{FIXTURES}/sample.html")
    assert result["markdown"].startswith("# Sample HTML")
    assert result["page_count"] == 1


def test_convert_pdf_preserves_page_count(monkeypatch):
    _install_fake_docling(monkeypatch, "# Page 1\n\n---\n\n# Page 2", num_pages=2)
    result = convert_to_markdown(f"{FIXTURES}/sample.pdf")
    assert result["page_count"] == 2
    assert "Page 2" in result["markdown"]

"""Converts raw documents (PDF/HTML/TXT/DOC) to Markdown via docling, preserving page markers."""
from pathlib import Path

SUPPORTED_TYPES = {"pdf", "html", "htm", "txt", "doc", "docx"}


class ConversionError(ValueError):
    pass


def convert_to_markdown(file_path: str | Path) -> dict:
    file_path = Path(file_path)
    ext = file_path.suffix.lower().lstrip(".")
    if ext not in SUPPORTED_TYPES:
        raise ConversionError(f"Unsupported file type: .{ext}")

    if ext == "txt":
        text = file_path.read_text(encoding="utf-8")
        return {"markdown": text, "page_count": 1}

    # heavy dependency, imported lazily so txt-only workflows/tests don't require it
    from docling.document_converter import DocumentConverter

    converter = DocumentConverter()
    result = converter.convert(str(file_path))
    markdown = result.document.export_to_markdown()
    page_count = getattr(result.document, "num_pages", None) or 1
    return {"markdown": markdown, "page_count": page_count}

"""Shared test doubles for Project 1: fake Postgres connection, fake docling/chonkie/ollama."""
import sys
import types


class FakeCursor:
    def __init__(self, conn):
        self.conn = conn
        self._last_result = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, query, params=()):
        self.conn.executed.append((query.strip(), params))
        query_upper = query.strip().upper()

        if query_upper.startswith("INSERT INTO SOURCE_DOCUMENT"):
            checksum = params[4]
            existing = self.conn.source_documents_by_checksum.get(checksum)
            if existing:
                self._last_result = None
            else:
                doc_id = params[0]
                self.conn.source_documents_by_checksum[checksum] = doc_id
                self._last_result = (doc_id,)
        elif query_upper.startswith("SELECT ID FROM SOURCE_DOCUMENT"):
            checksum = params[0]
            self._last_result = (self.conn.source_documents_by_checksum[checksum],)
        else:
            self._last_result = None

    def fetchone(self):
        return self._last_result


class FakeConnection:
    def __init__(self):
        self.executed = []
        self.committed = 0
        self.source_documents_by_checksum = {}

    def cursor(self):
        return FakeCursor(self)

    def commit(self):
        self.committed += 1


def install_fake_ollama(monkeypatch, reply: str = "mock ollama response"):
    def fake_chat(model, messages):
        return {"message": {"content": reply}}

    monkeypatch.setitem(sys.modules, "ollama", types.SimpleNamespace(chat=fake_chat))


def install_fake_chonkie(monkeypatch, spans):
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

    monkeypatch.setitem(sys.modules, "chonkie", types.SimpleNamespace(SemanticChunker=FakeSemanticChunker))


def install_fake_docling(monkeypatch, markdown_text, num_pages=1):
    fake_document = types.SimpleNamespace(
        export_to_markdown=lambda: markdown_text, num_pages=num_pages
    )
    fake_result = types.SimpleNamespace(document=fake_document)

    class FakeDocumentConverter:
        def convert(self, path):
            return fake_result

    monkeypatch.setitem(sys.modules, "docling.document_converter",
                         types.SimpleNamespace(DocumentConverter=FakeDocumentConverter))
    monkeypatch.setitem(sys.modules, "docling", types.SimpleNamespace())

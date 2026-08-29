"""Splits Markdown into semantic chunks via chonkie, tracking char offsets for lineage."""


def semantic_chunk(markdown: str, chunk_size: int = 512) -> list[dict]:
    if not markdown.strip():
        return []

    # heavy dependency, imported lazily so it's mockable in unit tests
    from chonkie import SemanticChunker

    chunker = SemanticChunker(chunk_size=chunk_size)
    chunks = chunker.chunk(markdown)
    return [
        {
            "text": c.text,
            "char_start": c.start_index,
            "char_end": c.end_index,
            "token_count": c.token_count,
        }
        for c in chunks
    ]

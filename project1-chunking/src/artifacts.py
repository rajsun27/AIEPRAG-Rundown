"""Generates derivative artifacts (contextual chunks, summaries, RAPTOR, QA pairs, factoids)
via prompts to a local Ollama model."""
from dataclasses import dataclass, field


@dataclass
class ArtifactResult:
    artifact_type: str
    text: str
    metadata: dict = field(default_factory=dict)


def _call_ollama(prompt: str, model: str) -> str:
    from ollama import chat  # lazy import, heavy dependency

    response = chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


def generate_contextual_chunk(
    chunk_text: str, context_window: str, model: str = "llama3.1"
) -> ArtifactResult:
    prompt = (
        "Rewrite the following chunk so it includes necessary surrounding context, "
        "without changing its meaning.\n\n"
        f"Context:\n{context_window}\n\nChunk:\n{chunk_text}"
    )
    return ArtifactResult("contextual_chunk", _call_ollama(prompt, model))


def generate_abstractive_summary(text_to_summarize: str, model: str = "llama3.1") -> ArtifactResult:
    prompt = f"Write a concise abstractive summary of the following text:\n\n{text_to_summarize}"
    return ArtifactResult("abstractive_summary", _call_ollama(prompt, model))


def generate_raptor_summary(
    child_texts: list[str], level: int, model: str = "llama3.1"
) -> ArtifactResult:
    prompt = "Summarize the following related passages into a single higher-level summary:\n\n" + (
        "\n\n".join(child_texts)
    )
    return ArtifactResult(
        "raptor_summary", _call_ollama(prompt, model), {"raptor_level": level}
    )


def generate_qa_pairs(
    chunk_text: str, model: str = "llama3.1", num_pairs: int = 3
) -> list[ArtifactResult]:
    prompt = (
        f"Generate {num_pairs} question-answer pairs strictly grounded in the following text. "
        "Format each pair as 'Q: ...' then 'A: ...' on the next line, separated by blank lines.\n\n"
        + chunk_text
    )
    raw = _call_ollama(prompt, model)
    return [
        ArtifactResult("qa_pair", f"Q: {q}\nA: {a}", {"question": q, "answer": a})
        for q, a in _parse_qa_pairs(raw)
    ]


def _parse_qa_pairs(raw: str) -> list[tuple[str, str]]:
    pairs = []
    question = None
    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("Q:"):
            question = line[2:].strip()
        elif line.startswith("A:") and question is not None:
            pairs.append((question, line[2:].strip()))
            question = None
    return pairs


def generate_factoids(chunk_text: str, model: str = "llama3.1") -> list[ArtifactResult]:
    prompt = (
        "Extract a list of atomic factual statements (factoids) from the following text, "
        "one per line, prefixed with '- '.\n\n" + chunk_text
    )
    raw = _call_ollama(prompt, model)
    factoids = [line.strip()[2:].strip() for line in raw.splitlines() if line.strip().startswith("- ")]
    return [ArtifactResult("factoid", f) for f in factoids]

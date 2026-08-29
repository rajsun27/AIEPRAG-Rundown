"""Wires conversion -> chunking -> derivative artifacts -> lineage -> manifest into one pipeline."""
import hashlib
import uuid
from pathlib import Path

from src.artifacts import (
    generate_abstractive_summary,
    generate_contextual_chunk,
    generate_factoids,
    generate_qa_pairs,
    generate_raptor_summary,
)
from src.chunk import semantic_chunk
from src.config import load_artifact_config, resolve_artifacts_for_doc_type
from src.convert import convert_to_markdown
from src.lineage import LineageWriter
from src.manifest import build_manifest, write_manifest

GENERATED_BY_CHONKIE = "chonkie"
GENERATED_BY_OLLAMA = "ollama:llama3.1"


def _checksum(file_path: Path) -> str:
    return "sha256:" + hashlib.sha256(file_path.read_bytes()).hexdigest()


def process_document(file_path, config: dict, writer: LineageWriter) -> dict:
    file_path = Path(file_path)
    doc_type = file_path.suffix.lower().lstrip(".")
    toggles = resolve_artifacts_for_doc_type(config, doc_type)

    conversion = convert_to_markdown(file_path)
    checksum = _checksum(file_path)
    doc_id = writer.insert_source_document(
        file_path.name, str(file_path), doc_type, checksum, conversion["page_count"]
    )

    artifacts_manifest = []
    chunks = []

    if toggles.get("semantic_chunk"):
        chunks = semantic_chunk(conversion["markdown"])
        for idx, chunk_data in enumerate(chunks):
            chunk_id = writer.insert_chunk(
                doc_id, idx, chunk_data["text"], chunk_data["char_start"],
                chunk_data["char_end"], chunk_data.get("token_count"),
            )
            artifact_id = writer.insert_artifact(
                "semantic_chunk", chunk_data["text"], GENERATED_BY_CHONKIE, chunk_id=chunk_id
            )
            artifacts_manifest.append(
                {"artifact_id": artifact_id, "chunk_id": chunk_id, "artifact_type": "semantic_chunk",
                 "text": chunk_data["text"], "metadata": {}}
            )

            if toggles.get("contextual_chunk"):
                context_parts = []
                if idx > 0:
                    context_parts.append(chunks[idx - 1]["text"])
                if idx < len(chunks) - 1:
                    context_parts.append(chunks[idx + 1]["text"])
                contextual = generate_contextual_chunk(chunk_data["text"], "\n".join(context_parts))
                contextual_id = writer.insert_artifact(
                    "contextual_chunk", contextual.text, GENERATED_BY_OLLAMA, chunk_id=chunk_id
                )
                artifacts_manifest.append(
                    {"artifact_id": contextual_id, "chunk_id": chunk_id, "artifact_type": "contextual_chunk",
                     "text": contextual.text, "metadata": {}}
                )

            if toggles.get("qa_pair"):
                for qa in generate_qa_pairs(chunk_data["text"]):
                    qa_id = writer.insert_artifact(
                        "qa_pair", qa.text, GENERATED_BY_OLLAMA, chunk_id=chunk_id, metadata=qa.metadata
                    )
                    artifacts_manifest.append(
                        {"artifact_id": qa_id, "chunk_id": chunk_id, "artifact_type": "qa_pair",
                         "text": qa.text, "metadata": qa.metadata}
                    )

            if toggles.get("factoid"):
                for factoid in generate_factoids(chunk_data["text"]):
                    factoid_id = writer.insert_artifact(
                        "factoid", factoid.text, GENERATED_BY_OLLAMA, chunk_id=chunk_id
                    )
                    artifacts_manifest.append(
                        {"artifact_id": factoid_id, "chunk_id": chunk_id, "artifact_type": "factoid",
                         "text": factoid.text, "metadata": {}}
                    )

        if toggles.get("raptor_summary") and chunks:
            raptor = generate_raptor_summary([c["text"] for c in chunks], level=1)
            raptor_id = writer.insert_artifact(
                "raptor_summary", raptor.text, GENERATED_BY_OLLAMA,
                source_document_id=doc_id, metadata=raptor.metadata,
            )
            artifacts_manifest.append(
                {"artifact_id": raptor_id, "chunk_id": None, "artifact_type": "raptor_summary",
                 "text": raptor.text, "metadata": raptor.metadata}
            )

    if toggles.get("abstractive_summary"):
        summary = generate_abstractive_summary(conversion["markdown"])
        summary_id = writer.insert_artifact(
            "abstractive_summary", summary.text, GENERATED_BY_OLLAMA, source_document_id=doc_id
        )
        artifacts_manifest.append(
            {"artifact_id": summary_id, "chunk_id": None, "artifact_type": "abstractive_summary",
             "text": summary.text, "metadata": {}}
        )

    return {
        "source_document": {
            "id": doc_id, "file_name": file_path.name, "file_type": doc_type, "checksum": checksum,
        },
        "artifacts": artifacts_manifest,
    }


def run_pipeline(input_dir, output_manifest_dir, config_path, writer: LineageWriter) -> list[str]:
    config = load_artifact_config(config_path)
    input_dir = Path(input_dir)
    written_paths = []

    for file_path in sorted(p for p in input_dir.iterdir() if p.is_file()):
        result = process_document(file_path, config, writer)
        manifest = build_manifest(
            batch_id=str(uuid.uuid4()),
            source_document=result["source_document"],
            artifacts=result["artifacts"],
        )
        out_path = Path(output_manifest_dir) / f"{file_path.stem}.manifest.json"
        write_manifest(manifest, out_path)
        written_paths.append(str(out_path))

    return written_paths

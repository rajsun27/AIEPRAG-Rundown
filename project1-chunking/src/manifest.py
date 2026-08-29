"""Emits the Project 1 -> Project 2 handoff manifest (JSON or parquet) per SPEC.md Section 9.3."""
import json
from datetime import datetime, timezone
from pathlib import Path


def build_manifest(batch_id: str, source_document: dict, artifacts: list[dict]) -> dict:
    return {
        "batch_id": batch_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_document": source_document,
        "artifacts": artifacts,
    }


def write_manifest(manifest: dict, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.suffix == ".json":
        output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return output_path

    if output_path.suffix == ".parquet":
        import pandas as pd  # lazy import, heavy dependency

        rows = [
            {
                "batch_id": manifest["batch_id"],
                "generated_at": manifest["generated_at"],
                "source_document_id": manifest["source_document"]["id"],
                "source_document_file_name": manifest["source_document"]["file_name"],
                "artifact_id": artifact["artifact_id"],
                "chunk_id": artifact.get("chunk_id"),
                "artifact_type": artifact["artifact_type"],
                "text": artifact["text"],
                "metadata": json.dumps(artifact.get("metadata", {})),
            }
            for artifact in manifest["artifacts"]
        ]
        pd.DataFrame(rows).to_parquet(output_path, index=False)
        return output_path

    raise ValueError(f"Unsupported manifest output format: {output_path.suffix}")

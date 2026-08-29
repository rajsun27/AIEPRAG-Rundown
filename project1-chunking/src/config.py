"""Loads and validates artifact_config.yaml, resolving per-document-type artifact toggles."""
from pathlib import Path

import yaml

VALID_ARTIFACT_TYPES = {
    "semantic_chunk",
    "contextual_chunk",
    "abstractive_summary",
    "raptor_summary",
    "qa_pair",
    "factoid",
}


class ArtifactConfigError(ValueError):
    pass


def load_artifact_config(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise ArtifactConfigError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    if "default" not in raw:
        raise ArtifactConfigError("artifact_config.yaml must define a 'default' section")

    _validate_toggle_block(raw["default"], "default")
    for doc_type, toggles in raw.get("document_types", {}).items():
        _validate_toggle_block(toggles, doc_type)

    return raw


def _validate_toggle_block(block: dict, name: str) -> None:
    if not isinstance(block, dict):
        raise ArtifactConfigError(f"Section '{name}' must be a mapping of artifact_type -> bool")
    unknown = set(block) - VALID_ARTIFACT_TYPES
    if unknown:
        raise ArtifactConfigError(f"Unknown artifact type(s) in '{name}': {sorted(unknown)}")
    for artifact_type, enabled in block.items():
        if not isinstance(enabled, bool):
            raise ArtifactConfigError(
                f"'{name}.{artifact_type}' must be a boolean, got {type(enabled).__name__}"
            )


def resolve_artifacts_for_doc_type(config: dict, doc_type: str) -> dict:
    merged = dict(config["default"])
    merged.update(config.get("document_types", {}).get(doc_type, {}))
    return merged

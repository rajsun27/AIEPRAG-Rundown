import pytest

from src.config import (
    ArtifactConfigError,
    load_artifact_config,
    resolve_artifacts_for_doc_type,
)

VALID_CONFIG_PATH = "config/artifact_config.yaml"


def test_load_valid_config():
    config = load_artifact_config(VALID_CONFIG_PATH)
    assert "default" in config
    assert config["default"]["semantic_chunk"] is True


def test_resolve_artifacts_merges_default_and_doc_type():
    config = load_artifact_config(VALID_CONFIG_PATH)
    resolved = resolve_artifacts_for_doc_type(config, "pdf")
    assert resolved["semantic_chunk"] is True
    assert resolved["raptor_summary"] is True

    resolved_txt = resolve_artifacts_for_doc_type(config, "txt")
    assert resolved_txt["semantic_chunk"] is True
    assert resolved_txt["raptor_summary"] is False  # falls back to default


def test_missing_file_raises():
    with pytest.raises(ArtifactConfigError):
        load_artifact_config("config/does_not_exist.yaml")


def test_missing_default_section_raises(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("document_types:\n  pdf:\n    semantic_chunk: true\n")
    with pytest.raises(ArtifactConfigError, match="default"):
        load_artifact_config(bad_file)


def test_unknown_artifact_type_raises(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("default:\n  not_a_real_type: true\n")
    with pytest.raises(ArtifactConfigError, match="Unknown artifact type"):
        load_artifact_config(bad_file)


def test_non_boolean_toggle_raises(tmp_path):
    bad_file = tmp_path / "bad.yaml"
    bad_file.write_text("default:\n  semantic_chunk: \"yes\"\n")
    with pytest.raises(ArtifactConfigError, match="must be a boolean"):
        load_artifact_config(bad_file)

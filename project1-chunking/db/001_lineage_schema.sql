-- PostgreSQL lineage schema (Section 9.1 of SPEC.md) — source of truth for lineage tracking.
CREATE TYPE artifact_type AS ENUM (
    'semantic_chunk', 'contextual_chunk', 'abstractive_summary',
    'raptor_summary', 'qa_pair', 'factoid'
);

CREATE TABLE source_document (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name            TEXT NOT NULL,
    file_path            TEXT NOT NULL,
    file_type            TEXT NOT NULL,
    checksum             TEXT NOT NULL UNIQUE,
    page_count           INT,
    converted_markdown_path TEXT,
    status                TEXT NOT NULL DEFAULT 'pending',
    ingested_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    converted_at          TIMESTAMPTZ
);

CREATE TABLE chunk (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_document_id   UUID NOT NULL REFERENCES source_document(id) ON DELETE CASCADE,
    chunk_index          INT NOT NULL,
    text                 TEXT NOT NULL,
    char_start           INT NOT NULL,
    char_end             INT NOT NULL,
    token_count          INT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (source_document_id, chunk_index)
);

CREATE TABLE artifact (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id             UUID REFERENCES chunk(id) ON DELETE CASCADE,
    source_document_id   UUID REFERENCES source_document(id) ON DELETE CASCADE,
    parent_artifact_id   UUID REFERENCES artifact(id) ON DELETE CASCADE,
    artifact_type        artifact_type NOT NULL,
    text                 TEXT NOT NULL,
    metadata             JSONB NOT NULL DEFAULT '{}',
    generated_by_model   TEXT NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (chunk_id IS NOT NULL OR source_document_id IS NOT NULL)
);

CREATE TABLE vector_record (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artifact_id          UUID NOT NULL REFERENCES artifact(id) ON DELETE CASCADE,
    vector_backend       TEXT NOT NULL,
    external_vector_id   TEXT,
    embedding_model       TEXT NOT NULL,
    embedding_dims        INT NOT NULL,
    embedding             VECTOR(768),
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (artifact_id, vector_backend)
);

CREATE INDEX idx_chunk_source_document ON chunk(source_document_id);
CREATE INDEX idx_artifact_chunk ON artifact(chunk_id);
CREATE INDEX idx_artifact_type ON artifact(artifact_type);
CREATE INDEX idx_vector_record_artifact ON vector_record(artifact_id);

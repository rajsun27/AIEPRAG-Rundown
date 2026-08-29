# Project 1 — Chunking & Derivative Artifacts Checklist

Scope reference: [../SPEC.md](../SPEC.md) Sections 5, 9.1, 9.3, 12.

> **Gating rule:** each numbered step below must have its tests written and passing before starting
> the next step. Do not proceed while a step's "Tests" checkbox is unchecked.

## Step 1 — Setup
- [ ] Create `project1-chunking/` folder structure per Section 4 layout
- [ ] Add `Dockerfile` and `requirements.txt`/`pyproject.toml`
- [ ] Add `config/artifact_config.yaml` (per-doc-type artifact toggles)
- [ ] **Tests:** config loader unit test (valid/invalid `artifact_config.yaml`) passes
- [ ] **Gate:** ✅ tests pass before moving to Step 2

## Step 2 — Conversion & chunking
- [ ] Integrate docling: PDF → Markdown
- [ ] Integrate docling: HTML → Markdown
- [ ] Integrate docling: TXT/DOC → Markdown
- [ ] Preserve page/section markers for long multi-page documents
- [ ] Integrate chonkie semantic chunking on converted Markdown
- [ ] **Tests:** unit tests for docling conversion output shape (per file type) and chonkie chunk
      boundaries against fixture docs in `tests/fixtures/`
- [ ] **Gate:** ✅ tests pass before moving to Step 3

## Step 3 — Derivative artifacts (Ollama-driven, each config-toggleable)
- [ ] Contextual chunks (chunk + surrounding context window)
- [ ] Abstractive summary (per-document/section)
- [ ] RAPTOR recursive summary tree (`parent_artifact_id` linkage)
- [ ] QA pair generation per chunk
- [ ] Factoid extraction per chunk
- [ ] **Tests:** unit tests for each artifact's prompt-building logic against a mocked Ollama
      client (canned responses), one test per artifact type
- [ ] **Gate:** ✅ tests pass before moving to Step 4

## Step 4 — Lineage & output
- [ ] Apply Postgres DDL (Section 9.1): `source_document`, `chunk`, `artifact`, `vector_record`
- [ ] Write `source_document` row on ingest (checksum dedup check)
- [ ] Write `chunk` rows with char offsets/token counts
- [ ] Write `artifact` rows for every generated artifact type
- [ ] Emit manifest file (JSON/parquet) per Section 9.3 schema
- [ ] **Tests:** unit tests for lineage row construction; integration test writing to a throwaway
      Postgres and asserting rows/manifest match expectations
- [ ] **Gate:** ✅ tests pass before moving to Step 5

## Step 5 — Full pipeline integration
- [ ] Wire Steps 2–4 into a single runnable pipeline (CLI entrypoint)
- [ ] **Tests:** end-to-end integration test running the full pipeline on 2–3 sample docs
      (pdf/html/txt) against a throwaway Postgres, asserting lineage rows + manifest contents
- [ ] **Gate:** ✅ tests pass before marking Project 1 done

## Done criteria
- [ ] Can run standalone via CLI on a folder of sample docs
- [ ] Produces valid manifest consumable by Project 2
- [ ] All step-level tests above are green (full suite passes)

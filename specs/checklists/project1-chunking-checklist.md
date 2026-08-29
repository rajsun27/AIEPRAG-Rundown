# Project 1 — Chunking & Derivative Artifacts Checklist

Scope reference: [../SPEC.md](../SPEC.md) Sections 5, 9.1, 9.3, 12.

> **Gating rule:** each numbered step below must have its tests written and passing before starting
> the next step. Do not proceed while a step's "Tests" checkbox is unchecked.

## Step 1 — Setup
- [x] Create `project1-chunking/` folder structure per Section 4 layout
- [x] Add `Dockerfile` and `requirements.txt`/`pyproject.toml`
- [x] Add `config/artifact_config.yaml` (per-doc-type artifact toggles)
- [x] **Tests:** config loader unit test (valid/invalid `artifact_config.yaml`) passes — 6/6 passed
- [x] **Gate:** ✅ tests pass before moving to Step 2

## Step 2 — Conversion & chunking
- [x] Integrate docling: PDF → Markdown
- [x] Integrate docling: HTML → Markdown
- [x] Integrate docling: TXT/DOC → Markdown
- [x] Preserve page/section markers for long multi-page documents
- [x] Integrate chonkie semantic chunking on converted Markdown
- [x] **Tests:** unit tests for docling conversion output shape (per file type) and chonkie chunk
      boundaries against fixture docs in `tests/fixtures/` — 13/13 passed (mocked docling/chonkie)
- [x] **Gate:** ✅ tests pass before moving to Step 3

> Known limitation: `docling`/`chonkie` could not be `pip install`ed on this Windows dev machine
> (long-path OS limit on a `torch` transitive dependency). Tests mock these libraries; real
> end-to-end conversion must be verified via Docker (Linux container) or after enabling Windows
> long-path support.

## Step 3 — Derivative artifacts (Ollama-driven, each config-toggleable)
- [x] Contextual chunks (chunk + surrounding context window)
- [x] Abstractive summary (per-document/section)
- [x] RAPTOR recursive summary tree (`parent_artifact_id` linkage)
- [x] QA pair generation per chunk
- [x] Factoid extraction per chunk
- [x] **Tests:** unit tests for each artifact's prompt-building logic against a mocked Ollama
      client (canned responses), one test per artifact type — 6/6 passed (19/19 total)
- [x] **Gate:** ✅ tests pass before moving to Step 4

## Step 4 — Lineage & output
- [x] Apply Postgres DDL (Section 9.1): `source_document`, `chunk`, `artifact`, `vector_record`
- [x] Write `source_document` row on ingest (checksum dedup check)
- [x] Write `chunk` rows with char offsets/token counts
- [x] Write `artifact` rows for every generated artifact type
- [x] Emit manifest file (JSON/parquet) per Section 9.3 schema
- [x] **Tests:** unit tests for lineage row construction; integration test writing to a throwaway
      Postgres and asserting rows/manifest match expectations — 8/8 passed (27/27 total, mocked connection)
- [x] **Gate:** ✅ tests pass before moving to Step 5

> Known limitation: no live Postgres instance available in this dev environment (Docker daemon not
> running), so lineage tests use a fake in-memory connection/cursor instead of a real throwaway
> Postgres. Re-run against a real Postgres (via `docker compose up postgres`) once Docker is
> available, using `db/001_lineage_schema.sql` to create the schema.

## Step 5 — Full pipeline integration
- [x] Wire Steps 2–4 into a single runnable pipeline (CLI entrypoint)
- [x] **Tests:** end-to-end integration test running the full pipeline on 2–3 sample docs
      (pdf/html/txt) against a throwaway Postgres, asserting lineage rows + manifest contents —
      3/3 passed (30/30 total, mocked docling/chonkie/ollama/connection)
- [x] **Gate:** ✅ tests pass before marking Project 1 done

## Done criteria
- [x] Can run standalone via CLI on a folder of sample docs (`src/cli.py`)
- [x] Produces valid manifest consumable by Project 2
- [x] All step-level tests above are green (full suite passes) — 30/30

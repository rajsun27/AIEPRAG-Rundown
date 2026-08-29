# Project 2 — Loader Checklist

Scope reference: [../SPEC.md](../SPEC.md) Sections 6, 9.3, 12.

> **Gating rule:** each numbered step below must have its tests written and passing before starting
> the next step. Do not proceed while a step's "Tests" checkbox is unchecked.

## Step 1 — Setup
- [ ] Create `project2-loader/` folder structure per Section 4 layout
- [ ] Add `Dockerfile` and `requirements.txt`/`pyproject.toml`
- [ ] Add config for `MODEL_PROVIDER=ollama|openai` selection
- [ ] **Tests:** config/provider-selection unit test passes
- [ ] **Gate:** ✅ tests pass before moving to Step 2

## Step 2 — Manifest ingestion
- [ ] Manifest reader for JSON variant (Section 9.3)
- [ ] Manifest reader for parquet variant
- [ ] Resolve artifact records that need embedding
- [ ] **Tests:** unit tests for manifest parsing (both variants) against fixture manifests
- [ ] **Gate:** ✅ tests pass before moving to Step 3

## Step 3 — Embedding
- [ ] Ollama embedding client (e.g. `nomic-embed-text`)
- [ ] OpenAI embedding client (e.g. `text-embedding-3-small`)
- [ ] Provider selection resolved from config, no code change to switch
- [ ] **Tests:** unit tests for each embedding client against a mocked provider; test that
      switching config swaps provider with no code change
- [ ] **Gate:** ✅ tests pass before moving to Step 4

## Step 4 — API integration
- [ ] `api_client` module calling Project 3 CRUD endpoints
- [ ] Pass lineage IDs so Project 3 can populate `vector_record.external_vector_id`
- [ ] Idempotency: reprocessing a manifest does not create duplicate vectors
- [ ] **Tests:** unit test for idempotency-key logic; integration test loading a sample manifest
      and asserting correct CRUD calls made to a mocked Project 3 API (`httpx` mock transport)
- [ ] **Gate:** ✅ tests pass before marking Project 2 done

## Done criteria
- [ ] Can run standalone against a sample manifest + a running/mocked Project 3
- [ ] Switching embedding provider requires only a config change
- [ ] All step-level tests above are green (full suite passes)

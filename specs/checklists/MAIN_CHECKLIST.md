# Enterprise RAG — Main Progress Checklist

Tracks overall delivery progress across all 4 projects. See per-project checklists in this same
folder for detailed task breakdowns. Source of truth for scope: [../SPEC.md](../SPEC.md).

> **Gating rule:** every step in every per-project checklist must have its tests written and
> passing before the next step starts. Milestones below should only be checked off once the
> corresponding project checklist's step-level tests are all green.

## Milestones

- [ ] M0 — Spec finalized and approved (Sections 1–14 reviewed)
- [ ] M1 — Shared infrastructure up (`docker-compose.yml`: postgres+pgvector, qdrant, ollama)
- [ ] M2 — Postgres lineage schema created (Section 9.1 DDL applied via migration)
- [ ] M3 — Project 1 (Chunking) MVP: docling + chonkie working end-to-end on sample docs
- [ ] M4 — Project 1 derivative artifacts (contextual, RAPTOR, summary, QA, factoids) working
- [ ] M5 — Project 3 (Vector API) MVP: CRUD + search against Postgres backend
- [ ] M6 — Project 3 Qdrant adapter working, backend switch verified via config only
- [ ] M7 — Project 2 (Loader): manifest → embeddings → Project 3, idempotent reprocessing verified
- [ ] M8 — Project 4 (RAG Search): search + LLM answer synthesis with citations, both providers
- [ ] M9 — Automated test suites green for all 4 projects (Section 12)
- [ ] M10 — Cross-project end-to-end smoke test passing (Section 13)
- [ ] M11 — `docker-compose up` brings up full stack from clean checkout

## Per-project status

| Project | Status | Checklist |
|---|---|---|
| Project 1 — Chunking | Not started | [project1-chunking-checklist.md](project1-chunking-checklist.md) |
| Project 2 — Loader | Not started | [project2-loader-checklist.md](project2-loader-checklist.md) |
| Project 3 — Vector API | Not started | [project3-vector-api-checklist.md](project3-vector-api-checklist.md) |
| Project 4 — RAG Search | Not started | [project4-rag-search-checklist.md](project4-rag-search-checklist.md) |

## Open items carried from spec (Section 14)

- [ ] Finalize embedding model names/dimensions per provider
- [ ] Finalize RAPTOR clustering parameters
- [ ] Define retry/backoff policy for Ollama calls
- [ ] Write detailed Project 3 API request/response schema doc
- [ ] Confirm long-document page/section boundary handling through docling → chonkie

# Project 4 — RAG Search (Streamlit) Checklist

Scope reference: [../SPEC.md](../SPEC.md) Sections 8, 12.

> **Gating rule:** each numbered step below must have its tests written and passing before starting
> the next step. Do not proceed while a step's "Tests" checkbox is unchecked.

## Step 1 — Setup
- [ ] Create `project4-rag-search/` folder structure per Section 4 layout
- [ ] Add `Dockerfile` and `requirements.txt`/`pyproject.toml`
- [ ] Add config for `MODEL_PROVIDER=ollama|openai` selection (generation model)
- [ ] **Tests:** config/provider-selection unit test passes
- [ ] **Gate:** ✅ tests pass before moving to Step 2

## Step 2 — Retrieval
- [ ] `retrieval` module calling Project 3 `/search` endpoint
- [ ] Support artifact_type filters and top-k parameter from UI
- [ ] **Tests:** unit tests for retrieval request building against a stubbed Project 3 API
- [ ] **Gate:** ✅ tests pass before moving to Step 3

## Step 3 — Generation
- [ ] Ollama chat client for answer synthesis
- [ ] OpenAI chat client for answer synthesis
- [ ] Prompt template combining retrieved chunks + query
- [ ] Citation extraction linking answer back to source documents
- [ ] **Tests:** unit tests for retrieval-to-prompt formatting and citation extraction against
      mocked OpenAI/Ollama chat clients
- [ ] **Gate:** ✅ tests pass before moving to Step 4

## Step 4 — UI
- [ ] Search box + submit
- [ ] Answer display with inline/linked citations
- [ ] Optional: show raw retrieved chunks for transparency
- [ ] Provider/backend indicator (which LLM/vector backend is active)
- [ ] **Tests:** end-to-end integration test running a query against a stubbed Project 3 API and
      mocked LLM, asserting the rendered answer includes expected citations
- [ ] **Gate:** ✅ tests pass before marking Project 4 done

## Done criteria
- [ ] Can run standalone against a mocked/stubbed Project 3 + LLM
- [ ] Switching LLM provider requires only a config change
- [ ] All step-level tests above are green (full suite passes)

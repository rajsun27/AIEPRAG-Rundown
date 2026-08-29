# Project 3 — Vector CRUD API Checklist

Scope reference: [../SPEC.md](../SPEC.md) Sections 7, 9.1, 9.2, 9.4, 12.

> **Gating rule:** each numbered step below must have its tests written and passing before starting
> the next step. Do not proceed while a step's "Tests" checkbox is unchecked.

## Step 1 — Setup
- [ ] Create `project3-vector-api/` folder structure per Section 4 layout
- [ ] Add `Dockerfile` and `requirements.txt`/`pyproject.toml`
- [ ] FastAPI app scaffold, no SQLAlchemy dependency anywhere
- [ ] **Tests:** app boots and health-check endpoint test passes
- [ ] **Gate:** ✅ tests pass before moving to Step 2

## Step 2 — Data access adapters
- [ ] Postgres adapter using raw SQL (`psycopg`/`asyncpg`) against Section 9.1 DDL
- [ ] Qdrant adapter using `qdrant-client` against Section 9.2 collection schema
- [ ] Repository/adapter pattern so routers are backend-agnostic
- [ ] `VECTOR_BACKEND=postgres|qdrant` config switch, no code change to switch
- [ ] **Tests:** unit tests for adapter selection logic and SQL-building helpers; integration
      tests for each adapter against an ephemeral test Postgres and test Qdrant instance
- [ ] **Gate:** ✅ tests pass before moving to Step 3

## Step 3 — Endpoints
- [ ] `POST/GET/PUT/DELETE /documents`
- [ ] `POST/GET/PUT/DELETE /chunks`
- [ ] `POST/GET/PUT/DELETE /artifacts`
- [ ] `POST /vectors` (upsert vector + lineage link)
- [ ] `DELETE /vectors/{id}`
- [ ] `POST /search` (top-k, filterable by artifact_type/doc metadata) per Section 9.4 shape
- [ ] Pydantic request/response models for all endpoints
- [ ] **Tests:** Pydantic schema validation unit tests; FastAPI `TestClient` integration tests per
      endpoint against both backends, seeded with fixture data
- [ ] **Gate:** ✅ tests pass before marking Project 3 done

## Done criteria
- [ ] Same test suite passes against both backends
- [ ] `docker-compose up` brings up this service correctly
- [ ] All step-level tests above are green (full suite passes)

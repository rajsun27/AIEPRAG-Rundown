# Development Machine Setup Guide

Steps to get the Enterprise RAG monorepo running locally. Reference design: [SPEC.md](SPEC.md).

## 1. Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Git | any recent | clone/manage the repo |
| Docker Desktop (or Docker Engine + Compose) | latest | run Postgres, Qdrant, Ollama, Project 3/4 containers |
| Python | 3.11+ | run Project 1/2 locally outside Docker, run tests |
| Ollama | latest | serve local LLM/embedding models |

Optional (only if you plan to use OpenAI as a provider):
- An OpenAI API key.

## 2. Clone the repository

```powershell
git clone <repo-url>
cd AI_Scratch_1
```

## 3. Environment configuration

Copy the example env file and fill in values:

```powershell
Copy-Item .env.example .env
```

Key variables in `.env`:

```dotenv
# --- Postgres ---
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag
POSTGRES_USER=rag
POSTGRES_PASSWORD=changeme

# --- Vector backend switch (Project 3) ---
VECTOR_BACKEND=postgres          # postgres | qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# --- Model provider switch (Project 2 embeddings, Project 4 generation) ---
MODEL_PROVIDER=ollama            # ollama | openai
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_CHAT_MODEL=llama3.1

OPENAI_API_KEY=                  # only required if MODEL_PROVIDER=openai
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

# --- Project 3 API location (used by Project 2 and Project 4) ---
VECTOR_API_BASE_URL=http://localhost:8000
```

## 4. Start shared infrastructure

```powershell
docker compose up -d postgres qdrant ollama
```

Verify containers are healthy:

```powershell
docker compose ps
```

## 5. Pull local Ollama models

```powershell
ollama pull llama3.1
ollama pull nomic-embed-text
# optional alternates referenced in the spec
ollama pull gemma2
ollama pull qwen2.5
```

## 6. Apply the Postgres lineage schema

Run the DDL from [SPEC.md](SPEC.md) Section 9.1 against the running Postgres instance:

```powershell
docker compose exec -T postgres psql -U rag -d rag -f /docker-entrypoint-initdb.d/001_lineage_schema.sql
```

(Place the DDL file at `project3-vector-api/db/001_lineage_schema.sql` and mount it into the
Postgres container's init directory in `docker-compose.yml`, or apply it manually with `psql` if
you are not using an init-mount.)

## 7. Set up each project locally (for development outside Docker)

Repeat for each of `project1-chunking`, `project2-loader`, `project3-vector-api`,
`project4-rag-search`:

```powershell
cd project1-chunking
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

## 8. Run Project 3 (Vector API) locally

```powershell
cd project3-vector-api
uvicorn src.main:app --reload --port 8000
```

## 9. Run Project 4 (Streamlit RAG Search) locally

```powershell
cd project4-rag-search
streamlit run src/ui/app.py
```

## 10. Run Project 1 (Chunking) against sample docs

```powershell
cd project1-chunking
python -m src.cli --input ./samples --output ./out/manifest.json
```

## 11. Run Project 2 (Loader) against the manifest

```powershell
cd project2-loader
python -m src.cli --manifest ../project1-chunking/out/manifest.json
```

## 12. Run tests

Each project has its own suite; run from that project's folder:

```powershell
cd project1-chunking
pytest

cd ..\project3-vector-api
pytest
```

Or bring up the full stack (including test profile services) and run the cross-project smoke test:

```powershell
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d
pytest tests/e2e
```

## 13. Common troubleshooting

| Symptom | Likely cause |
|---|---|
| Project 3 fails to connect to Postgres | `.env` DB host/port wrong, or container not healthy yet |
| Ollama calls time out | model not pulled yet (`ollama pull <model>`), or `OLLAMA_HOST` wrong |
| Qdrant adapter tests fail | `VECTOR_BACKEND` set to `postgres` while tests expect `qdrant`, or Qdrant container not running |
| Embeddings dimension mismatch error | `embedding_dims`/pgvector column width doesn't match the configured model's output size |

## 14. Next steps

Once local setup is verified, track implementation progress using
[checklists/MAIN_CHECKLIST.md](checklists/MAIN_CHECKLIST.md) and the per-project checklists in
that same folder.

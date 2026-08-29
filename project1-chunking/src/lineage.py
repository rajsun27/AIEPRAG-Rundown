"""Writes source_document/chunk/artifact lineage rows to Postgres (raw SQL, no ORM)."""
import os
import uuid
from dataclasses import dataclass
from typing import Optional


def connect_from_env():
    """Builds a psycopg connection from POSTGRES_* env vars (used outside of tests)."""
    import psycopg  # lazy import, heavy dependency

    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


@dataclass
class LineageWriter:
    conn: object  # any psycopg-like connection; injected for testability

    def insert_source_document(
        self,
        file_name: str,
        file_path: str,
        file_type: str,
        checksum: str,
        page_count: Optional[int] = None,
    ) -> str:
        doc_id = str(uuid.uuid4())
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO source_document
                    (id, file_name, file_path, file_type, checksum, page_count, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'converted')
                ON CONFLICT (checksum) DO NOTHING
                RETURNING id
                """,
                (doc_id, file_name, file_path, file_type, checksum, page_count),
            )
            row = cur.fetchone()
            if row is None:
                cur.execute(
                    "SELECT id FROM source_document WHERE checksum = %s", (checksum,)
                )
                row = cur.fetchone()
        self.conn.commit()
        return row[0]

    def insert_chunk(
        self,
        source_document_id: str,
        chunk_index: int,
        text: str,
        char_start: int,
        char_end: int,
        token_count: Optional[int] = None,
    ) -> str:
        chunk_id = str(uuid.uuid4())
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chunk
                    (id, source_document_id, chunk_index, text, char_start, char_end, token_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    chunk_id,
                    source_document_id,
                    chunk_index,
                    text,
                    char_start,
                    char_end,
                    token_count,
                ),
            )
        self.conn.commit()
        return chunk_id

    def insert_artifact(
        self,
        artifact_type: str,
        text: str,
        generated_by_model: str,
        chunk_id: Optional[str] = None,
        source_document_id: Optional[str] = None,
        parent_artifact_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        if chunk_id is None and source_document_id is None:
            raise ValueError("artifact must attach to a chunk_id or a source_document_id")

        artifact_id = str(uuid.uuid4())
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO artifact
                    (id, chunk_id, source_document_id, parent_artifact_id, artifact_type,
                     text, metadata, generated_by_model)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    artifact_id,
                    chunk_id,
                    source_document_id,
                    parent_artifact_id,
                    artifact_type,
                    text,
                    metadata or {},
                    generated_by_model,
                ),
            )
        self.conn.commit()
        return artifact_id

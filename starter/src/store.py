"""Store and search vectors using PostgreSQL + pgvector."""
import json
from typing import Any
import psycopg
from .models import Chunk


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int = 1536) -> None:
        self.database_url = database_url
        self.dimensions = dimensions

    def get_connection(self):
        return psycopg.connect(self.database_url)

    def create_schema(self) -> None:
        """Tạo bảng chunks và bật extension pgvector."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS chunks (
                        id TEXT PRIMARY KEY,
                        strategy TEXT NOT NULL,
                        document_id TEXT NOT NULL,
                        source TEXT NOT NULL,
                        page INT NOT NULL,
                        text TEXT NOT NULL,
                        metadata JSONB NOT NULL,
                        embedding vector({self.dimensions}) NOT NULL
                    );
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_strat ON chunks(strategy);")
            conn.commit()

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Nạp dữ liệu Idempotent: xóa chunk cũ của strategy trước khi insert."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM chunks WHERE strategy = %s;", (strategy,))
                for chunk, vec in zip(chunks, vectors):
                    vec_str = "[" + ",".join(str(x) for x in vec) + "]"
                    cur.execute("""
                        INSERT INTO chunks (id, strategy, document_id, source, page, text, metadata, embedding)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector);
                    """, (
                        chunk.chunk_id,
                        strategy,
                        chunk.document_id,
                        chunk.source,
                        chunk.page,
                        chunk.text,
                        json.dumps(chunk.metadata),
                        vec_str
                    ))
            conn.commit()
        print(f"[Store] Đã lưu {len(chunks)} chunks cho chiến lược '{strategy}'")

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Tìm kiếm Cosine Similarity kèm metadata filtering."""
        vec_str = "[" + ",".join(str(x) for x in query_vector) + "]"
        sql = f"""
            SELECT id, document_id, source, page, text, metadata,
                   1 - (embedding <=> %s::vector) AS score
            FROM chunks
            WHERE strategy = %s
        """
        params: list[Any] = [vec_str, strategy]

        if filters:
            for k, v in filters.items():
                sql += f" AND metadata->>%s = %s"
                params.extend([k, str(v)])

        sql += " ORDER BY embedding <=> %s::vector LIMIT %s;"
        params.extend([vec_str, top_k])

        results = []
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                for row in cur.fetchall():
                    results.append({
                        "chunk_id": row[0],
                        "document_id": row[1],
                        "source": row[2],
                        "page": row[3],
                        "text": row[4],
                        "metadata": row[5] if isinstance(row[5], dict) else json.loads(row[5]),
                        "score": float(row[6])
                    })
        return results
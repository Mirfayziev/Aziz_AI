import os
import json
import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.services.openai_client import openai_client


DEFAULT_DB_PATH = os.getenv("AZIZAI_DB_PATH", "data/azizai.db")
EMBED_MODEL = os.getenv("AZIZAI_EMBED_MODEL", "text-embedding-3-small")


def _ensure_dir_for_db(db_path: str) -> None:
    folder = os.path.dirname(db_path)
    if folder:
        os.makedirs(folder, exist_ok=True)


def _connect(db_path: str) -> sqlite3.Connection:
    _ensure_dir_for_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def _serialize_vec(vec: List[float]) -> bytes:
    # compact JSON bytes (simple, dependency-free)
    return json.dumps(vec, separators=(",", ":")).encode("utf-8")


def _deserialize_vec(b: bytes) -> List[float]:
    return json.loads(b.decode("utf-8"))


def _cosine(a: List[float], b: List[float]) -> float:
    # safe cosine similarity
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na <= 0.0 or nb <= 0.0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


@dataclass
class VectorMemoryItem:
    id: str
    user_id: str
    text: str
    meta: Dict[str, Any]
    created_at: str
    score: float = 0.0


class VectorMemory:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = _connect(self.db_path)
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS vector_memory (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    text TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    meta TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vm_user ON vector_memory(user_id);")
            conn.commit()
        finally:
            conn.close()

    async def _embed(self, text: str) -> List[float]:
        # OpenAI embeddings
        resp = await openai_client.embeddings.create(
            model=EMBED_MODEL,
            input=text
        )
        return resp.data[0].embedding

    async def add(
        self,
        user_id: str,
        text: str,
        meta: Optional[Dict[str, Any]] = None,
        id_: Optional[str] = None,
    ) -> str:
        if not text or not text.strip():
            return ""

        meta = meta or {}
        created_at = datetime.utcnow().isoformat()
        if not id_:
            # deterministic-ish id
            base = f"{user_id}|{created_at}|{text[:64]}"
            id_ = str(abs(hash(base)))

        emb = await self._embed(text)
        emb_b = _serialize_vec(emb)
        meta_s = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))

        conn = _connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO vector_memory (id, user_id, text, embedding, meta, created_at)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (id_, user_id, text, emb_b, meta_s, created_at),
            )
            conn.commit()
        finally:
            conn.close()

        return id_

    async def search(
        self,
        user_id: str,
        query: str,
        top_k: int = 6,
        min_score: float = 0.35,
        limit_scan: int = 400,
    ) -> List[VectorMemoryItem]:
        if not query or not query.strip():
            return []

        q_emb = await self._embed(query)

        conn = _connect(self.db_path)
        rows: List[Tuple[str, str, str, bytes, str, str]] = []
        try:
            cur = conn.execute(
                """
                SELECT id, user_id, text, embedding, meta, created_at
                FROM vector_memory
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?;
                """,
                (user_id, limit_scan),
            )
            rows = cur.fetchall()
        finally:
            conn.close()

        scored: List[VectorMemoryItem] = []
        for rid, ruser, rtext, remb, rmeta, rcreated in rows:
            try:
                vec = _deserialize_vec(remb)
                score = _cosine(q_emb, vec)
                if score >= min_score:
                    scored.append(
                        VectorMemoryItem(
                            id=rid,
                            user_id=ruser,
                            text=rtext,
                            meta=json.loads(rmeta),
                            created_at=rcreated,
                            score=score,
                        )
                    )
            except Exception:
                continue

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]


vector_memory = VectorMemory()

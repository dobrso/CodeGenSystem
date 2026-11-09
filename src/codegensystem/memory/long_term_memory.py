import json
import math
import sqlite3
import time
import uuid
from pathlib import Path

import httpx

from utils.settings import Settings


MEMORY_DIR = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)
DB_PATH =  f"{MEMORY_DIR}/memory.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn

def init_memory_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id              TEXT PRIMARY KEY,
                timestamp       REAL,
                request_text    TEXT,
                arch_plan       TEXT,   -- JSON
                router_decision TEXT,
                review_verdict  TEXT,
                embedding       TEXT,   -- JSON list[float]
                access_count    INTEGER DEFAULT 0
            )
        """)

def embed(text):
    response = httpx.post(
        f"{Settings.OLLAMA_BASE_URL}/api/embeddings",
        json={"model": Settings.EMBEDDING_MODEL, "prompt": text},
        timeout=Settings.TIMEOUT,
    )
    response.raise_for_status()

    return response.json()["embedding"]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0

    return dot / (na * nb)

def persist_memory(state):
    architect = state["architect_response"]
    plan_text = " ".join(architect.plan) + " " + " ".join(architect.acceptance_criteria)

    with connect() as conn:
        conn.execute(
            "INSERT INTO memories VALUES (?,?,?,?,?,?,?,?)",
            (
                str(uuid.uuid4()),
                time.time(),
                state["input"],
                json.dumps(architect.plan, ensure_ascii=False),
                state["router_response"],
                state["reviewer_response"].verdict,
                json.dumps(embed(plan_text)),
                0,
            ),
        )

def recall_memories(query):
    q = embed(query)
    now = time.time()

    with connect() as conn:
        rows = conn.execute("SELECT * FROM memories").fetchall()

        scored = []
        for r in rows:
            sim = cosine(q, json.loads(r["embedding"]))
            age_days = (now - r["timestamp"]) / 86400.0
            fresh = 0.5 ** (age_days / 30.0)
            scored.append((sim * fresh, r))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [x for x in scored[:Settings.TOP_K] if x[0] >= Settings.MIN_SCORE]

        ids = [r["id"] for _, r in top]
        if ids:
            conn.executemany(
                "UPDATE memories SET access_count = access_count + 1 WHERE id = ?",
                [(i,) for i in ids],
            )

    return [
        {
            "score": score,
            "request": r["request_text"],
            "plan": json.loads(r["arch_plan"]),
            "verdict": r["review_verdict"],
        }
        for score, r in top
    ]
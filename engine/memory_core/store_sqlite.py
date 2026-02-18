"""
store_sqlite.py — SQLite storage backend for session memory.

Manages the memory.db database in .ai_runtime/session/.
Handles schema creation, message/fact/summary CRUD, and purge.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Fact, Message, Summary

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    namespace TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    ts TEXT NOT NULL,
    metadata_json TEXT
);

CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    namespace TEXT NOT NULL,
    fact_text TEXT NOT NULL,
    ts TEXT NOT NULL,
    importance INTEGER DEFAULT 5,
    tags_json TEXT,
    supersedes_id INTEGER
);

CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    namespace TEXT NOT NULL,
    summary_text TEXT NOT NULL,
    ts TEXT NOT NULL,
    scope TEXT DEFAULT 'rolling'
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    type TEXT NOT NULL,
    payload_json TEXT
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_messages_session_ns ON messages(session_id, namespace);
CREATE INDEX IF NOT EXISTS idx_messages_ts ON messages(ts);
CREATE INDEX IF NOT EXISTS idx_facts_session_ns ON facts(session_id, namespace);
CREATE INDEX IF NOT EXISTS idx_summaries_session_ns ON summaries(session_id, namespace);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_db_path(project_root: Path, db_path: Path | str | None = None) -> Path:
    """Resolve the memory database path."""
    if db_path:
        return Path(db_path)
    return project_root / ".ai_runtime" / "session" / "memory.db"


def connect(db_path: Path) -> sqlite3.Connection:
    """Open or create the memory database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def detect_fts5(conn: sqlite3.Connection) -> bool:
    """Check if FTS5 is available in this SQLite build."""
    try:
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS _fts5_test USING fts5(x)")
        conn.execute("DROP TABLE IF EXISTS _fts5_test")
        return True
    except sqlite3.OperationalError:
        return False


def ensure_fts(conn: sqlite3.Connection) -> bool:
    """Create FTS5 virtual tables if supported. Returns True if FTS5 is active."""
    if not detect_fts5(conn):
        return False

    fts_sql = """
    CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts
        USING fts5(content, content=messages, content_rowid=id);

    CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts
        USING fts5(fact_text, content=facts, content_rowid=id);
    """
    conn.executescript(fts_sql)
    conn.commit()

    # Create triggers to keep FTS in sync
    trigger_sql = """
    CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
        INSERT INTO messages_fts(rowid, content) VALUES (new.id, new.content);
    END;

    CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
        INSERT INTO messages_fts(messages_fts, rowid, content) VALUES('delete', old.id, old.content);
    END;

    CREATE TRIGGER IF NOT EXISTS facts_ai AFTER INSERT ON facts BEGIN
        INSERT INTO facts_fts(rowid, fact_text) VALUES (new.id, new.fact_text);
    END;

    CREATE TRIGGER IF NOT EXISTS facts_ad AFTER DELETE ON facts BEGIN
        INSERT INTO facts_fts(facts_fts, rowid, fact_text) VALUES('delete', old.id, old.fact_text);
    END;
    """
    conn.executescript(trigger_sql)
    conn.commit()
    return True


# ── Messages ──

def insert_message(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    role: str,
    content: str,
    metadata: dict[str, Any] | None = None,
) -> int:
    """Insert a message and return its row id."""
    cur = conn.execute(
        "INSERT INTO messages (session_id, namespace, role, content, ts, metadata_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, namespace, role, content, _now(),
         json.dumps(metadata) if metadata else None),
    )
    conn.commit()
    return cur.lastrowid  # type: ignore[return-value]


def get_recent_messages(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    limit: int = 50,
) -> list[Message]:
    """Get the most recent messages, ordered oldest-first."""
    rows = conn.execute(
        "SELECT * FROM messages WHERE session_id = ? AND namespace = ? "
        "ORDER BY id DESC LIMIT ?",
        (session_id, namespace, limit),
    ).fetchall()

    return [_row_to_message(r) for r in reversed(rows)]


def get_message_count(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
) -> int:
    """Count messages in a session/namespace."""
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM messages WHERE session_id = ? AND namespace = ?",
        (session_id, namespace),
    ).fetchone()
    return row["cnt"]


# ── Facts ──

def insert_fact(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    fact_text: str,
    importance: int = 5,
    tags: list[str] | None = None,
    supersedes_id: int | None = None,
) -> int:
    """Insert a fact and return its row id."""
    cur = conn.execute(
        "INSERT INTO facts (session_id, namespace, fact_text, ts, importance, tags_json, supersedes_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (session_id, namespace, fact_text, _now(), importance,
         json.dumps(tags) if tags else None, supersedes_id),
    )
    conn.commit()
    return cur.lastrowid  # type: ignore[return-value]


def get_facts(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    limit: int = 100,
) -> list[Fact]:
    """Get facts ordered by importance (descending), then recency."""
    rows = conn.execute(
        "SELECT * FROM facts WHERE session_id = ? AND namespace = ? "
        "AND supersedes_id IS NULL "
        "ORDER BY importance DESC, id DESC LIMIT ?",
        (session_id, namespace, limit),
    ).fetchall()
    return [_row_to_fact(r) for r in rows]


def get_fact_count(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
) -> int:
    """Count active (non-superseded) facts."""
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM facts "
        "WHERE session_id = ? AND namespace = ? AND supersedes_id IS NULL",
        (session_id, namespace),
    ).fetchone()
    return row["cnt"]


def delete_superseded_facts(conn: sqlite3.Connection, session_id: str, namespace: str) -> int:
    """Remove facts that have been superseded. Returns count deleted."""
    cur = conn.execute(
        "DELETE FROM facts WHERE session_id = ? AND namespace = ? AND supersedes_id IS NOT NULL",
        (session_id, namespace),
    )
    conn.commit()
    return cur.rowcount


# ── Summaries ──

def upsert_summary(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    summary_text: str,
    scope: str = "rolling",
) -> int:
    """Insert or replace the summary for a session/namespace/scope."""
    # Check for existing
    existing = conn.execute(
        "SELECT id FROM summaries WHERE session_id = ? AND namespace = ? AND scope = ?",
        (session_id, namespace, scope),
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE summaries SET summary_text = ?, ts = ? WHERE id = ?",
            (summary_text, _now(), existing["id"]),
        )
        conn.commit()
        return existing["id"]
    else:
        cur = conn.execute(
            "INSERT INTO summaries (session_id, namespace, summary_text, ts, scope) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, namespace, summary_text, _now(), scope),
        )
        conn.commit()
        return cur.lastrowid  # type: ignore[return-value]


def get_summary(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    scope: str = "rolling",
) -> Summary | None:
    """Get the latest summary for a session/namespace/scope."""
    row = conn.execute(
        "SELECT * FROM summaries WHERE session_id = ? AND namespace = ? AND scope = ? "
        "ORDER BY id DESC LIMIT 1",
        (session_id, namespace, scope),
    ).fetchone()
    return _row_to_summary(row) if row else None


# ── Events ──

def add_event(conn: sqlite3.Connection, event_type: str, payload: dict | None = None):
    """Log an internal memory event."""
    conn.execute(
        "INSERT INTO events (ts, type, payload_json) VALUES (?, ?, ?)",
        (_now(), event_type, json.dumps(payload) if payload else None),
    )
    conn.commit()


# ── Meta ──

def get_meta(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else None


def set_meta(conn: sqlite3.Connection, key: str, value: str):
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)", (key, value))
    conn.commit()


# ── Purge ──

def purge_messages(
    conn: sqlite3.Connection,
    namespace: str | None = None,
    older_than_iso: str | None = None,
) -> int:
    """Delete messages matching criteria. Returns count deleted."""
    conditions = []
    params: list[str] = []

    if namespace:
        conditions.append("namespace = ?")
        params.append(namespace)
    if older_than_iso:
        conditions.append("ts < ?")
        params.append(older_than_iso)

    where = " AND ".join(conditions) if conditions else "1=1"
    cur = conn.execute(f"DELETE FROM messages WHERE {where}", params)
    conn.commit()
    return cur.rowcount


def purge_facts(
    conn: sqlite3.Connection,
    namespace: str | None = None,
    older_than_iso: str | None = None,
) -> int:
    """Delete facts matching criteria. Returns count deleted."""
    conditions = []
    params: list[str] = []

    if namespace:
        conditions.append("namespace = ?")
        params.append(namespace)
    if older_than_iso:
        conditions.append("ts < ?")
        params.append(older_than_iso)

    where = " AND ".join(conditions) if conditions else "1=1"
    cur = conn.execute(f"DELETE FROM facts WHERE {where}", params)
    conn.commit()
    return cur.rowcount


def purge_summaries(
    conn: sqlite3.Connection,
    namespace: str | None = None,
) -> int:
    """Delete summaries matching criteria."""
    if namespace:
        cur = conn.execute("DELETE FROM summaries WHERE namespace = ?", (namespace,))
    else:
        cur = conn.execute("DELETE FROM summaries")
    conn.commit()
    return cur.rowcount


# ── Row converters ──

def _row_to_message(row: sqlite3.Row) -> Message:
    meta = None
    if row["metadata_json"]:
        try:
            meta = json.loads(row["metadata_json"])
        except (json.JSONDecodeError, TypeError):
            pass
    return Message(
        id=row["id"],
        session_id=row["session_id"],
        namespace=row["namespace"],
        role=row["role"],
        content=row["content"],
        ts=row["ts"],
        metadata=meta,
    )


def _row_to_fact(row: sqlite3.Row) -> Fact:
    tags = []
    if row["tags_json"]:
        try:
            tags = json.loads(row["tags_json"])
        except (json.JSONDecodeError, TypeError):
            pass
    return Fact(
        id=row["id"],
        session_id=row["session_id"],
        namespace=row["namespace"],
        fact_text=row["fact_text"],
        ts=row["ts"],
        importance=row["importance"],
        tags=tags,
        supersedes_id=row["supersedes_id"],
    )


def _row_to_summary(row: sqlite3.Row) -> Summary:
    return Summary(
        id=row["id"],
        session_id=row["session_id"],
        namespace=row["namespace"],
        summary_text=row["summary_text"],
        ts=row["ts"],
        scope=row["scope"],
    )

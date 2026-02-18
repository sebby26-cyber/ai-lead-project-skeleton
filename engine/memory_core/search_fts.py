"""
search_fts.py — Full-text search with FTS5 and LIKE fallback.

Provides unified search interface regardless of FTS5 availability.
"""

from __future__ import annotations

import sqlite3

from .models import Fact, Message
from .store_sqlite import _row_to_fact, _row_to_message


def search_messages(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    query: str,
    limit: int = 20,
    use_fts: bool = True,
) -> list[Message]:
    """Search messages by content. Uses FTS5 if available, falls back to LIKE."""
    if use_fts and _has_fts_table(conn, "messages_fts"):
        return _fts_search_messages(conn, session_id, namespace, query, limit)
    return _like_search_messages(conn, session_id, namespace, query, limit)


def search_facts(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    query: str,
    limit: int = 20,
    use_fts: bool = True,
) -> list[Fact]:
    """Search facts by text. Uses FTS5 if available, falls back to LIKE."""
    if use_fts and _has_fts_table(conn, "facts_fts"):
        return _fts_search_facts(conn, session_id, namespace, query, limit)
    return _like_search_facts(conn, session_id, namespace, query, limit)


# ── FTS5 search ──

def _fts_search_messages(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    query: str,
    limit: int,
) -> list[Message]:
    """Search messages using FTS5."""
    # Escape FTS5 special characters
    safe_query = _escape_fts_query(query)
    rows = conn.execute(
        "SELECT m.* FROM messages m "
        "JOIN messages_fts fts ON m.id = fts.rowid "
        "WHERE fts.content MATCH ? AND m.session_id = ? AND m.namespace = ? "
        "ORDER BY fts.rank LIMIT ?",
        (safe_query, session_id, namespace, limit),
    ).fetchall()
    return [_row_to_message(r) for r in rows]


def _fts_search_facts(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    query: str,
    limit: int,
) -> list[Fact]:
    """Search facts using FTS5."""
    safe_query = _escape_fts_query(query)
    rows = conn.execute(
        "SELECT f.* FROM facts f "
        "JOIN facts_fts fts ON f.id = fts.rowid "
        "WHERE fts.fact_text MATCH ? AND f.session_id = ? AND f.namespace = ? "
        "AND f.supersedes_id IS NULL "
        "ORDER BY fts.rank LIMIT ?",
        (safe_query, session_id, namespace, limit),
    ).fetchall()
    return [_row_to_fact(r) for r in rows]


# ── LIKE fallback ──

def _like_search_messages(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    query: str,
    limit: int,
) -> list[Message]:
    """Search messages using LIKE (fallback when FTS5 unavailable)."""
    pattern = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM messages "
        "WHERE session_id = ? AND namespace = ? AND content LIKE ? "
        "ORDER BY id DESC LIMIT ?",
        (session_id, namespace, pattern, limit),
    ).fetchall()
    return [_row_to_message(r) for r in rows]


def _like_search_facts(
    conn: sqlite3.Connection,
    session_id: str,
    namespace: str,
    query: str,
    limit: int,
) -> list[Fact]:
    """Search facts using LIKE (fallback when FTS5 unavailable)."""
    pattern = f"%{query}%"
    rows = conn.execute(
        "SELECT * FROM facts "
        "WHERE session_id = ? AND namespace = ? AND fact_text LIKE ? "
        "AND supersedes_id IS NULL "
        "ORDER BY importance DESC, id DESC LIMIT ?",
        (session_id, namespace, pattern, limit),
    ).fetchall()
    return [_row_to_fact(r) for r in rows]


# ── Helpers ──

def _has_fts_table(conn: sqlite3.Connection, table_name: str) -> bool:
    """Check if an FTS virtual table exists."""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    ).fetchone()
    return row is not None


def _escape_fts_query(query: str) -> str:
    """Escape special FTS5 characters and wrap terms for prefix matching."""
    # Remove FTS5 operators that could cause syntax errors
    cleaned = query.replace('"', "").replace("*", "").replace("(", "").replace(")", "")
    cleaned = cleaned.replace("AND", "").replace("OR", "").replace("NOT", "")
    terms = cleaned.split()
    if not terms:
        return '""'
    # Quote each term for exact matching
    return " ".join(f'"{t}"' for t in terms if t.strip())

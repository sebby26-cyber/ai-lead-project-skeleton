"""
ai_db.py — SQLite schema, ingest, and query helpers.

The local DB is a derived cache. Canonical state lives in .ai/state/*.yaml.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    actor TEXT NOT NULL,
    type TEXT NOT NULL,
    payload_json TEXT
);

CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    title TEXT,
    department TEXT,
    provider TEXT,
    model TEXT,
    reports_to TEXT,
    authority TEXT
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    owner_role TEXT,
    requires_approval_json TEXT,
    updated_ts TEXT
);

CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    approval_type TEXT,
    status TEXT,
    approved_by TEXT,
    ts TEXT
);

CREATE TABLE IF NOT EXISTS snapshots (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def get_db_path(runtime_dir: Path) -> Path:
    return runtime_dir / "ai.db"


def create_db(runtime_dir: Path) -> sqlite3.Connection:
    """Create the SQLite database and schema."""
    db_path = get_db_path(runtime_dir)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def connect_db(runtime_dir: Path) -> sqlite3.Connection:
    """Connect to an existing DB, or create if missing."""
    db_path = get_db_path(runtime_dir)
    if not db_path.exists():
        return create_db(runtime_dir)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def ingest_team(conn: sqlite3.Connection, team_data: dict):
    """Ingest team.yaml data into the workers table."""
    conn.execute("DELETE FROM workers")
    orch = team_data.get("orchestrator", {})
    conn.execute(
        "INSERT OR REPLACE INTO workers (id, role_id, title, department, provider, model, reports_to, authority) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            orch.get("role_id", "orchestrator"),
            orch.get("role_id", "orchestrator"),
            orch.get("title", "Orchestrator"),
            "orchestration",
            None,
            None,
            None,
            orch.get("authority", "write"),
        ),
    )
    for role in team_data.get("roles", []):
        for worker in role.get("workers", []):
            conn.execute(
                "INSERT OR REPLACE INTO workers (id, role_id, title, department, provider, model, reports_to, authority) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    worker.get("id", role["role_id"]),
                    role["role_id"],
                    role.get("title", ""),
                    role.get("department", ""),
                    worker.get("provider", ""),
                    worker.get("model", ""),
                    role.get("reports_to", ""),
                    role.get("authority", "read"),
                ),
            )
        if not role.get("workers"):
            conn.execute(
                "INSERT OR REPLACE INTO workers (id, role_id, title, department, provider, model, reports_to, authority) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    role["role_id"],
                    role["role_id"],
                    role.get("title", ""),
                    role.get("department", ""),
                    None,
                    None,
                    role.get("reports_to", ""),
                    role.get("authority", "read"),
                ),
            )
    conn.commit()


def ingest_board(conn: sqlite3.Connection, board_data: dict):
    """Ingest board.yaml data into the tasks table."""
    conn.execute("DELETE FROM tasks")
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    for task in board_data.get("tasks", []):
        approvals = task.get("requires_approval", [])
        conn.execute(
            "INSERT OR REPLACE INTO tasks (id, title, status, owner_role, requires_approval_json, updated_ts) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                task["id"],
                task["title"],
                task["status"],
                task.get("owner_role", ""),
                json.dumps(approvals),
                now,
            ),
        )
    conn.commit()


def ingest_approvals(conn: sqlite3.Connection, approvals_data: dict):
    """Ingest approvals.yaml approval_log into the approvals table."""
    conn.execute("DELETE FROM approvals")
    for entry in approvals_data.get("approval_log", []):
        conn.execute(
            "INSERT INTO approvals (task_id, approval_type, status, approved_by, ts) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                entry.get("task_id", ""),
                entry.get("approval_type", entry.get("trigger_id", "")),
                entry.get("status", "pending"),
                entry.get("approved_by", ""),
                entry.get("timestamp", ""),
            ),
        )
    conn.commit()


def set_snapshot(conn: sqlite3.Connection, key: str, value: str):
    conn.execute(
        "INSERT OR REPLACE INTO snapshots (key, value) VALUES (?, ?)", (key, value)
    )
    conn.commit()


def get_snapshot(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute(
        "SELECT value FROM snapshots WHERE key = ?", (key,)
    ).fetchone()
    return row["value"] if row else None


def add_event(conn: sqlite3.Connection, actor: str, event_type: str, payload: dict | None = None):
    from datetime import datetime, timezone

    conn.execute(
        "INSERT INTO events (ts, actor, type, payload_json) VALUES (?, ?, ?, ?)",
        (
            datetime.now(timezone.utc).isoformat(),
            actor,
            event_type,
            json.dumps(payload) if payload else None,
        ),
    )
    conn.commit()


def export_events(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT ts, actor, type, payload_json FROM events ORDER BY id").fetchall()
    result = []
    for r in rows:
        entry = {"ts": r["ts"], "actor": r["actor"], "type": r["type"]}
        if r["payload_json"]:
            entry["payload"] = json.loads(r["payload_json"])
        result.append(entry)
    return result


def export_derived(conn: sqlite3.Connection) -> dict:
    workers = [dict(r) for r in conn.execute("SELECT * FROM workers").fetchall()]
    tasks = [dict(r) for r in conn.execute("SELECT * FROM tasks").fetchall()]
    approvals = [dict(r) for r in conn.execute("SELECT * FROM approvals").fetchall()]
    return {"workers": workers, "tasks": tasks, "approvals": approvals}


def import_events(conn: sqlite3.Connection, events: list[dict]):
    for ev in events:
        payload = ev.get("payload")
        conn.execute(
            "INSERT INTO events (ts, actor, type, payload_json) VALUES (?, ?, ?, ?)",
            (
                ev["ts"],
                ev["actor"],
                ev["type"],
                json.dumps(payload) if payload else None,
            ),
        )
    conn.commit()


def get_task_counts(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
    ).fetchall()
    return {r["status"]: r["cnt"] for r in rows}


def get_pending_approvals(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM approvals WHERE status = 'pending'"
    ).fetchall()
    return [dict(r) for r in rows]


def get_active_tasks(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM tasks WHERE status = 'in_progress'"
    ).fetchall()
    return [dict(r) for r in rows]

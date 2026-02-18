"""
packs.py — Memory pack export/import for session memory.

Exports messages, facts, and summaries as portable packs.
Imports are append-safe and never modify .ai/state/*.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def export_pack(
    conn: sqlite3.Connection,
    out_path: str | Path,
    namespaces: list[str] | None = None,
) -> str:
    """Export session memory as a portable pack.

    Args:
        conn: Database connection.
        out_path: Output path (directory or .zip).
        namespaces: Optional filter. None = export all.

    Returns:
        Path to the created pack.
    """
    out = Path(out_path)
    is_zip = out.suffix == ".zip"

    if is_zip:
        pack_dir = out.parent / f"_pack_staging_{out.stem}"
    else:
        pack_dir = out

    pack_dir.mkdir(parents=True, exist_ok=True)

    ns_filter = ""
    ns_params: list[str] = []
    if namespaces:
        placeholders = ",".join("?" for _ in namespaces)
        ns_filter = f" WHERE namespace IN ({placeholders})"
        ns_params = list(namespaces)

    checksums: dict[str, str] = {}

    # Messages
    _export_jsonl(
        conn, pack_dir / "messages.jsonl",
        f"SELECT * FROM messages{ns_filter} ORDER BY id",
        ns_params, checksums,
    )

    # Facts
    _export_jsonl(
        conn, pack_dir / "facts.jsonl",
        f"SELECT * FROM facts{ns_filter} ORDER BY id",
        ns_params, checksums,
    )

    # Summaries
    _export_jsonl(
        conn, pack_dir / "summaries.jsonl",
        f"SELECT * FROM summaries{ns_filter} ORDER BY id",
        ns_params, checksums,
    )

    # Events (optional, always export all)
    event_count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    if event_count > 0:
        _export_jsonl(
            conn, pack_dir / "events.jsonl",
            "SELECT * FROM events ORDER BY id",
            [], checksums,
        )

    # Manifest
    manifest = {
        "version": "1.0",
        "type": "session_memory",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "namespaces": namespaces or "all",
        "counts": {
            "messages": _count(conn, "messages", ns_filter, ns_params),
            "facts": _count(conn, "facts", ns_filter, ns_params),
            "summaries": _count(conn, "summaries", ns_filter, ns_params),
        },
    }
    manifest_path = pack_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    checksums["manifest.json"] = _sha256_file(manifest_path)

    # Checksums
    (pack_dir / "checksums.json").write_text(json.dumps(checksums, indent=2))

    if is_zip:
        with zipfile.ZipFile(str(out), "w", zipfile.ZIP_DEFLATED) as zf:
            for fpath in pack_dir.rglob("*"):
                if fpath.is_file():
                    zf.write(str(fpath), fpath.relative_to(pack_dir))
        shutil.rmtree(str(pack_dir))
        return str(out)

    return str(pack_dir)


def import_pack(
    conn: sqlite3.Connection,
    pack_path: str | Path,
) -> dict[str, int]:
    """Import a session memory pack. Append-safe.

    Args:
        conn: Database connection.
        pack_path: Path to pack directory or .zip.

    Returns:
        Dict of counts imported per table.
    """
    path = Path(pack_path).resolve()
    cleanup_dir: Path | None = None

    # Handle zip
    if path.suffix == ".zip" and path.is_file():
        extract_dir = path.parent / f"_import_tmp_{path.stem}"
        if extract_dir.exists():
            shutil.rmtree(str(extract_dir))
        extract_dir.mkdir(parents=True)
        with zipfile.ZipFile(str(path), "r") as zf:
            zf.extractall(str(extract_dir))
        path = extract_dir
        cleanup_dir = extract_dir

    if not path.is_dir():
        raise FileNotFoundError(f"Not a valid memory pack: {pack_path}")

    manifest_path = path / "manifest.json"
    if not manifest_path.exists():
        raise ValueError("No manifest.json found in memory pack.")

    manifest = json.loads(manifest_path.read_text())
    if manifest.get("version") != "1.0":
        raise ValueError(f"Unsupported pack version: {manifest.get('version')}")

    # Validate checksums
    checksums_path = path / "checksums.json"
    if checksums_path.exists():
        checksums = json.loads(checksums_path.read_text())
        for filename, expected_hash in checksums.items():
            fpath = path / filename
            if fpath.exists() and _sha256_file(fpath) != expected_hash:
                raise ValueError(f"Checksum mismatch for {filename}")

    counts: dict[str, int] = {}

    # Import messages
    counts["messages"] = _import_jsonl(
        conn, path / "messages.jsonl",
        "INSERT INTO messages (session_id, namespace, role, content, ts, metadata_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ["session_id", "namespace", "role", "content", "ts", "metadata_json"],
    )

    # Import facts
    counts["facts"] = _import_jsonl(
        conn, path / "facts.jsonl",
        "INSERT INTO facts (session_id, namespace, fact_text, ts, importance, tags_json, supersedes_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        ["session_id", "namespace", "fact_text", "ts", "importance", "tags_json", "supersedes_id"],
    )

    # Import summaries
    counts["summaries"] = _import_jsonl(
        conn, path / "summaries.jsonl",
        "INSERT INTO summaries (session_id, namespace, summary_text, ts, scope) "
        "VALUES (?, ?, ?, ?, ?)",
        ["session_id", "namespace", "summary_text", "ts", "scope"],
    )

    # Import events (optional)
    events_path = path / "events.jsonl"
    if events_path.exists():
        counts["events"] = _import_jsonl(
            conn, events_path,
            "INSERT INTO events (ts, type, payload_json) VALUES (?, ?, ?)",
            ["ts", "type", "payload_json"],
        )

    conn.commit()

    if cleanup_dir and cleanup_dir.exists():
        shutil.rmtree(str(cleanup_dir))

    return counts


# ── Helpers ──

def _export_jsonl(
    conn: sqlite3.Connection,
    out_file: Path,
    query: str,
    params: list[str],
    checksums: dict[str, str],
):
    """Export query results as JSONL."""
    rows = conn.execute(query, params).fetchall()
    with open(out_file, "w") as f:
        for row in rows:
            f.write(json.dumps(dict(row)) + "\n")
    checksums[out_file.name] = _sha256_file(out_file)


def _import_jsonl(
    conn: sqlite3.Connection,
    jsonl_path: Path,
    insert_sql: str,
    fields: list[str],
) -> int:
    """Import JSONL records into a table. Returns count imported."""
    if not jsonl_path.exists():
        return 0

    count = 0
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            values = tuple(record.get(field) for field in fields)
            conn.execute(insert_sql, values)
            count += 1
    conn.commit()
    return count


def _count(conn: sqlite3.Connection, table: str, where: str, params: list[str]) -> int:
    """Count rows in a table with optional filter."""
    row = conn.execute(f"SELECT COUNT(*) FROM {table}{where}", params).fetchone()
    return row[0]


def _sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

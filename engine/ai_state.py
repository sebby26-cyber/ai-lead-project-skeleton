"""
ai_state.py — State load/save and reconciliation.

Loads canonical YAML, computes hashes, reconciles with SQLite cache.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

from . import ai_db


def _load_yaml(path: Path) -> dict:
    text = path.read_text()
    if yaml:
        return yaml.safe_load(text) or {}
    raise ImportError("PyYAML is required. Install it: pip install pyyaml")


def _save_yaml(path: Path, data: dict):
    if yaml:
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
    else:
        raise ImportError("PyYAML is required. Install it: pip install pyyaml")


def compute_canonical_hash(ai_dir: Path) -> str:
    """Compute a hash of all canonical YAML files to detect changes."""
    state_dir = ai_dir / "state"
    h = hashlib.sha256()
    for name in sorted(["team.yaml", "board.yaml", "approvals.yaml", "commands.yaml"]):
        fpath = state_dir / name
        if fpath.exists():
            h.update(fpath.read_bytes())
    return h.hexdigest()


def load_canonical(ai_dir: Path) -> dict:
    """Load all canonical YAML state files into a single dict."""
    state_dir = ai_dir / "state"
    return {
        "team": _load_yaml(state_dir / "team.yaml"),
        "board": _load_yaml(state_dir / "board.yaml"),
        "approvals": _load_yaml(state_dir / "approvals.yaml"),
        "commands": _load_yaml(state_dir / "commands.yaml"),
    }


def save_canonical(ai_dir: Path, state: dict):
    """Save state dict back to canonical YAML files."""
    state_dir = ai_dir / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    if "team" in state:
        _save_yaml(state_dir / "team.yaml", state["team"])
    if "board" in state:
        _save_yaml(state_dir / "board.yaml", state["board"])
    if "approvals" in state:
        _save_yaml(state_dir / "approvals.yaml", state["approvals"])
    if "commands" in state:
        _save_yaml(state_dir / "commands.yaml", state["commands"])


def reconcile(ai_dir: Path, runtime_dir: Path) -> bool:
    """Reconcile canonical YAML with SQLite DB.

    Returns True if DB was updated, False if already in sync.
    """
    conn = ai_db.connect_db(runtime_dir)
    current_hash = compute_canonical_hash(ai_dir)
    stored_hash = ai_db.get_snapshot(conn, "canonical_hash")

    if stored_hash == current_hash:
        conn.close()
        return False

    # Canonical changed (or first run) — re-ingest
    state = load_canonical(ai_dir)
    ai_db.ingest_team(conn, state["team"])
    ai_db.ingest_board(conn, state["board"])
    ai_db.ingest_approvals(conn, state["approvals"])

    from datetime import datetime, timezone

    ai_db.set_snapshot(conn, "canonical_hash", current_hash)
    ai_db.set_snapshot(conn, "last_ingested_ts", datetime.now(timezone.utc).isoformat())
    ai_db.add_event(conn, "system", "reconcile", {"hash": current_hash})

    conn.close()
    return True


def render_status(ai_dir: Path, runtime_dir: Path) -> str:
    """Render a terminal-friendly status report and update STATUS.md."""
    state = load_canonical(ai_dir)
    board = state["board"]
    team = state["team"]
    approvals = state["approvals"]

    columns = board.get("columns", [])
    tasks = board.get("tasks", [])

    # Count tasks per column
    counts = {col: 0 for col in columns}
    for task in tasks:
        s = task.get("status", "backlog")
        if s in counts:
            counts[s] += 1

    total = len(tasks)
    done = counts.get("done", 0)
    pct = int((done / total * 100)) if total > 0 else 0

    # Progress bar
    bar_width = 20
    filled = int(bar_width * pct / 100)
    bar = "#" * filled + "." * (bar_width - filled)

    # Active tasks
    active = [t for t in tasks if t.get("status") == "in_progress"]

    # Blockers (tasks blocked by approvals)
    pending_approvals = approvals.get("approval_log", [])
    pending = [a for a in pending_approvals if a.get("status") == "pending"]

    # Build report
    lines = []
    lines.append("=" * 50)
    lines.append("  PROJECT STATUS")
    lines.append("=" * 50)

    # Phase
    if total == 0:
        phase = "Initialization"
    elif done == total:
        phase = "Complete"
    elif any(t.get("status") == "in_progress" for t in tasks):
        phase = "Active Development"
    else:
        phase = "Planning"
    lines.append(f"  Phase: {phase}")
    lines.append("")

    # Tasks by column
    lines.append("  Tasks:")
    max_col_len = max((len(c) for c in columns), default=10)
    max_count = max(counts.values()) if counts else 1
    for col in columns:
        cnt = counts[col]
        bar_len = int(5 * cnt / max_count) if max_count > 0 else 0
        bar_str = "#" * bar_len + "." * (5 - bar_len)
        lines.append(f"    {col:<{max_col_len}}  {bar_str}  {cnt}")
    lines.append("")

    # Progress
    lines.append(f"  Progress: [{bar}] {pct}%")
    lines.append("")

    # Active tasks
    if active:
        lines.append("  Active Tasks:")
        for t in active:
            owner = t.get("owner_role", "unassigned")
            lines.append(f"    - {t['id']}: {t['title']} ({owner})")
        lines.append("")

    # Blockers
    if pending:
        lines.append("  Pending Approvals:")
        for a in pending:
            lines.append(f"    - {a.get('trigger_id', 'unknown')} on {a.get('task_id', '?')}")
    else:
        lines.append("  Blockers: None")
        lines.append("  Pending Approvals: None")
    lines.append("")
    lines.append("=" * 50)

    report = "\n".join(lines)

    # Also write STATUS.md
    _write_status_md(ai_dir, phase, columns, counts, total, done, pct, active, pending)

    return report


def _write_status_md(ai_dir, phase, columns, counts, total, done, pct, active, pending):
    from datetime import datetime, timezone

    bar_width = 20
    filled = int(bar_width * pct / 100)
    bar_md = "#" * filled + "." * (bar_width - filled)

    lines = ["# Project Status", ""]
    lines.append("> Auto-generated by `ai status`. Do not edit manually.")
    lines.append("")
    lines.append(f"## Phase\n{phase}")
    lines.append("")
    lines.append("## Task Summary")
    lines.append("| Column | Count |")
    lines.append("|--------|-------|")
    for col in columns:
        lines.append(f"| {col} | {counts.get(col, 0)} |")
    lines.append("")
    lines.append(f"## Progress\n[{bar_md}] {pct}%")
    lines.append("")

    if active:
        lines.append("## Active Tasks")
        for t in active:
            lines.append(f"- **{t['id']}**: {t['title']} (owner: {t.get('owner_role', 'unassigned')})")
        lines.append("")

    if pending:
        lines.append("## Pending Approvals")
        for a in pending:
            lines.append(f"- {a.get('trigger_id', 'unknown')} on {a.get('task_id', '?')}")
    else:
        lines.append("## Blockers\nNone")
        lines.append("")
        lines.append("## Pending Approvals\nNone")
    lines.append("")
    lines.append("## Recent Decisions\nSee DECISIONS.md")
    lines.append("")
    lines.append(f"---\n*Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")

    # Preserve Legacy Snapshot section if it exists in the current STATUS.md
    status_path = ai_dir / "STATUS.md"
    legacy_section = ""
    if status_path.exists():
        existing = status_path.read_text()
        marker = "## Legacy Status Snapshot"
        idx = existing.find(marker)
        if idx >= 0:
            legacy_section = "\n\n" + existing[idx:]

    (ai_dir / "STATUS.md").write_text("\n".join(lines) + legacy_section + "\n")

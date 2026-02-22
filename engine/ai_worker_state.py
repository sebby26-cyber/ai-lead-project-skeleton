"""
ai_worker_state.py — Canonical worker state management.

Manages durable, portable worker state in .ai/workers/ (committed to git).
This enables workers to resume on any machine without .ai_runtime/.

Storage layout:
  .ai/workers/roster.yaml          — Worker roster (id, role, provider, status)
  .ai/workers/assignments.yaml     — Worker → ticket ID mappings
  .ai/workers/checkpoints/<id>/    — Markdown checkpoints per worker
  .ai/workers/summaries/<id>.md    — Latest state summary per worker
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _yaml_dump(data: dict) -> str:
    if yaml:
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    raise ImportError("PyYAML is required. Install it: pip install pyyaml")


def ensure_workers_dir(project_root: Path) -> Path:
    """Create .ai/workers/ directory structure if missing. Returns workers dir."""
    workers_dir = project_root / ".ai" / "workers"
    for subdir in ["checkpoints", "summaries"]:
        (workers_dir / subdir).mkdir(parents=True, exist_ok=True)
    return workers_dir


def write_roster(project_root: Path, workers_list: list[dict]) -> Path:
    """Write roster.yaml from a list of worker dicts.

    Each dict should have: worker_id, role, provider, model, status, last_checkpoint_id.
    """
    workers_dir = ensure_workers_dir(project_root)
    roster_path = workers_dir / "roster.yaml"

    entries = []
    for w in workers_list:
        entries.append({
            "worker_id": w.get("worker_id", ""),
            "role": w.get("role", ""),
            "provider": w.get("provider", ""),
            "model": w.get("model", ""),
            "status": w.get("status", "ready"),
            "last_checkpoint_id": w.get("last_checkpoint_id"),
        })

    roster_path.write_text(_yaml_dump({"workers": entries}))
    return roster_path


def load_roster(project_root: Path) -> list[dict]:
    """Load committed roster. Returns list of worker dicts."""
    roster_path = project_root / ".ai" / "workers" / "roster.yaml"
    if not roster_path.exists() or yaml is None:
        return []
    try:
        data = yaml.safe_load(roster_path.read_text()) or {}
        return data.get("workers", [])
    except Exception:
        return []


def write_canonical_checkpoint(
    project_root: Path,
    worker_id: str,
    data: dict,
) -> str:
    """Write a Markdown checkpoint to .ai/workers/checkpoints/<worker_id>/<id>.md.

    Args:
        data: Dict with optional keys: completed, pending, files_changed,
              decisions, resume_instructions, progress_summary, next_steps,
              role, provider, timestamp.

    Returns checkpoint_id.
    """
    now = datetime.now(timezone.utc)
    checkpoint_id = now.strftime("%Y%m%d_%H%M%S")

    cp_dir = ensure_workers_dir(project_root) / "checkpoints" / worker_id
    cp_dir.mkdir(parents=True, exist_ok=True)

    role = data.get("role", "")
    provider = data.get("provider", "")
    timestamp = data.get("timestamp", now.isoformat())

    lines = [
        f"# Checkpoint: {checkpoint_id}",
        f"Worker: {worker_id} | Role: {role} | Provider: {provider}",
        f"Timestamp: {timestamp}",
        "",
    ]

    # Completed
    completed = data.get("completed", [])
    if completed:
        lines.append("## Completed")
        for item in completed:
            lines.append(f"- {item}")
        lines.append("")

    # Pending
    pending = data.get("pending", [])
    if pending:
        lines.append("## Pending")
        for item in pending:
            lines.append(f"- {item}")
        lines.append("")

    # Files changed
    files_changed = data.get("files_changed", [])
    if files_changed:
        lines.append("## Files Changed")
        for item in files_changed:
            lines.append(f"- {item}")
        lines.append("")

    # Decisions
    decisions = data.get("decisions", [])
    if decisions:
        lines.append("## Decisions")
        for item in decisions:
            lines.append(f"- {item}")
        lines.append("")

    # Progress summary (fallback from existing checkpoint format)
    progress = data.get("progress_summary", "")
    if progress and not completed:
        lines.append("## Progress")
        lines.append(progress)
        lines.append("")

    # Resume instructions / next steps
    resume = data.get("resume_instructions", data.get("next_steps", ""))
    if resume:
        lines.append("## Resume Instructions")
        lines.append(resume)
        lines.append("")

    cp_path = cp_dir / f"{checkpoint_id}.md"
    cp_path.write_text("\n".join(lines))

    # Update roster with checkpoint ref
    _update_roster_checkpoint(project_root, worker_id, checkpoint_id)

    return checkpoint_id


def _update_roster_checkpoint(
    project_root: Path, worker_id: str, checkpoint_id: str
) -> None:
    """Update last_checkpoint_id in roster.yaml for a worker."""
    roster_path = project_root / ".ai" / "workers" / "roster.yaml"
    if not roster_path.exists() or yaml is None:
        return
    try:
        data = yaml.safe_load(roster_path.read_text()) or {}
        for w in data.get("workers", []):
            if w.get("worker_id") == worker_id:
                w["last_checkpoint_id"] = checkpoint_id
                break
        roster_path.write_text(_yaml_dump(data))
    except Exception:
        pass


def load_latest_canonical_checkpoint(
    project_root: Path, worker_id: str
) -> dict | None:
    """Load the most recent canonical checkpoint for a worker.

    Returns dict with keys: checkpoint_id, worker_id, role, provider,
    timestamp, progress_summary, next_steps (parsed from markdown).
    Returns None if no checkpoint found.
    """
    cp_dir = project_root / ".ai" / "workers" / "checkpoints" / worker_id
    if not cp_dir.is_dir():
        return None

    files = sorted(cp_dir.glob("*.md"), reverse=True)
    if not files:
        return None

    return _parse_checkpoint_md(files[0])


def _parse_checkpoint_md(path: Path) -> dict:
    """Parse a markdown checkpoint file into a dict."""
    text = path.read_text()
    result: dict = {
        "checkpoint_id": path.stem,
        "source": "canonical",
    }

    # Parse header line: "Worker: X | Role: Y | Provider: Z"
    header_match = re.search(r"Worker:\s*(\S+)\s*\|\s*Role:\s*(\S+)\s*\|\s*Provider:\s*(\S+)", text)
    if header_match:
        result["worker_id"] = header_match.group(1)
        result["role"] = header_match.group(2)
        result["provider"] = header_match.group(3)

    # Parse timestamp
    ts_match = re.search(r"Timestamp:\s*(.+)", text)
    if ts_match:
        result["timestamp"] = ts_match.group(1).strip()

    # Parse sections
    sections = _extract_sections(text)
    if "Completed" in sections:
        result["completed"] = _parse_bullet_list(sections["Completed"])
    if "Pending" in sections:
        result["pending"] = _parse_bullet_list(sections["Pending"])
    if "Files Changed" in sections:
        result["files_changed"] = _parse_bullet_list(sections["Files Changed"])
    if "Decisions" in sections:
        result["decisions"] = _parse_bullet_list(sections["Decisions"])
    if "Progress" in sections:
        result["progress_summary"] = sections["Progress"].strip()
    if "Resume Instructions" in sections:
        result["next_steps"] = sections["Resume Instructions"].strip()

    return result


def _extract_sections(text: str) -> dict[str, str]:
    """Extract ## sections from markdown text."""
    sections: dict[str, str] = {}
    current_section = None
    current_content: list[str] = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_content)
            current_section = line[3:].strip()
            current_content = []
        elif current_section is not None:
            current_content.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_content)

    return sections


def _parse_bullet_list(text: str) -> list[str]:
    """Parse markdown bullet list into list of strings."""
    items = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:])
    return items


def write_summary(project_root: Path, worker_id: str, data: dict) -> Path:
    """Write or update a worker summary file.

    Args:
        data: Dict with keys: role, title, provider, model, status,
              last_checkpoint_id, responsibilities, open_tickets, latest_progress.
    """
    summaries_dir = ensure_workers_dir(project_root) / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    title = data.get("title", data.get("role", worker_id))
    provider = data.get("provider", "?")
    model = data.get("model", "?")
    status = data.get("status", "ready")
    last_cp = data.get("last_checkpoint_id", "none")

    lines = [
        f"# Worker: {worker_id}",
        f"Role: {title} | Provider: {provider} | Model: {model}",
        f"Status: {status}",
        f"Last Checkpoint: {last_cp}",
        "",
    ]

    responsibilities = data.get("responsibilities", [])
    if responsibilities:
        lines.append("## Current Responsibilities")
        for r in responsibilities:
            lines.append(f"- {r}")
        lines.append("")

    tickets = data.get("open_tickets", [])
    if tickets:
        lines.append("## Open Tickets")
        for t in tickets:
            lines.append(f"- {t}")
        lines.append("")
    else:
        lines.append("## Open Tickets")
        lines.append("- (awaiting assignment)")
        lines.append("")

    progress = data.get("latest_progress", "")
    if progress:
        lines.append("## Latest Progress")
        lines.append(progress)
        lines.append("")

    summary_path = summaries_dir / f"{worker_id}.md"
    summary_path.write_text("\n".join(lines))
    return summary_path


def load_summary(project_root: Path, worker_id: str) -> str | None:
    """Load a worker summary as raw markdown. Returns None if not found."""
    summary_path = project_root / ".ai" / "workers" / "summaries" / f"{worker_id}.md"
    if not summary_path.exists():
        return None
    return summary_path.read_text()


def sync_from_runtime(project_root: Path) -> str:
    """Sync runtime worker state to canonical.

    Reads .ai_runtime/workers/registry.json and writes:
    - .ai/workers/roster.yaml
    - .ai/workers/summaries/<worker_id>.md for each worker
    """
    import json

    registry_path = project_root / ".ai_runtime" / "workers" / "registry.json"
    if not registry_path.exists():
        return "No runtime worker registry found."

    try:
        registry = json.loads(registry_path.read_text())
    except Exception:
        return "Failed to read runtime worker registry."

    workers = registry.get("workers", [])
    if not workers:
        return "No workers in runtime registry."

    # Write roster
    write_roster(project_root, workers)

    # Write summaries
    for w in workers:
        worker_id = w.get("worker_id", "")
        if not worker_id:
            continue
        write_summary(project_root, worker_id, {
            "role": w.get("role", ""),
            "provider": w.get("provider", ""),
            "model": w.get("model", ""),
            "status": w.get("status", "ready"),
            "last_checkpoint_id": w.get("last_checkpoint_id"),
        })

    return f"Synced {len(workers)} worker(s) to canonical state."

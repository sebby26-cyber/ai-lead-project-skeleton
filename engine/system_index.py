"""
system_index.py — System layer index builder and lookup.

Scans the skeleton submodule (read-only) to build a cached index of
available commands, key files, and capabilities. The index is stored at
``.ai_runtime/system_index.json`` and refreshed when the submodule HEAD
changes. No writes are made to the submodule.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _get_submodule_head(skeleton_dir: Path) -> str:
    """Return the current HEAD commit of the skeleton submodule."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(skeleton_dir),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _scan_key_files(skeleton_dir: Path) -> list[dict]:
    """Scan the skeleton for key documentation and config files."""
    entries: list[dict] = []

    known_files = [
        ("templates/.ai/AGENTS.md", "Operator protocol — startup, commands, rules"),
        ("templates/.ai/core/AUTHORITY_MODEL.md", "Authority model — single-writer architecture"),
        ("templates/.ai/core/WORKER_EXECUTION_RULES.md", "Worker execution rules — read-only boundaries"),
        ("templates/.ai/core/STATUS_REPORT_PROTOCOL.md", "Status report protocol"),
        ("templates/.ai/prompts/orchestrator_system.md", "Orchestrator system prompt"),
        ("templates/.ai/state/commands.yaml", "Command registry with aliases"),
        ("engine/README.md", "Engine internals and module map"),
        ("README.md", "Project overview and onboarding"),
    ]

    for rel_path, description in known_files:
        full = skeleton_dir / rel_path
        if full.exists():
            entries.append({"path": rel_path, "description": description})

    return entries


def _scan_commands(skeleton_dir: Path) -> list[dict]:
    """Extract command definitions from the template commands.yaml."""
    commands_path = skeleton_dir / "templates" / ".ai" / "state" / "commands.yaml"
    if not commands_path.exists() or yaml is None:
        return []

    try:
        data = yaml.safe_load(commands_path.read_text()) or {}
    except Exception:
        return []

    result = []
    for cmd in data.get("commands", []):
        result.append({
            "name": cmd.get("name", ""),
            "description": cmd.get("description", ""),
            "aliases": cmd.get("aliases", []),
        })
    return result


def _scan_engine_modules(skeleton_dir: Path) -> list[dict]:
    """List engine Python modules and their docstrings."""
    engine_dir = skeleton_dir / "engine"
    modules: list[dict] = []

    if not engine_dir.is_dir():
        return modules

    for py_file in sorted(engine_dir.glob("*.py")):
        if py_file.name.startswith("__"):
            continue
        # Extract first docstring line
        desc = ""
        try:
            text = py_file.read_text()
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    # Single-line docstring
                    content = stripped.strip("\"'").strip()
                    if content:
                        desc = content.split("—")[-1].strip() if "—" in content else content
                    break
        except Exception:
            pass
        modules.append({"name": py_file.name, "description": desc})

    return modules


def build_system_index(skeleton_dir: Path, runtime_dir: Path) -> dict:
    """Build the system index from the skeleton submodule.

    Writes the index to ``.ai_runtime/system_index.json``.
    Returns the index dict.
    """
    head = _get_submodule_head(skeleton_dir)

    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skeleton_head": head,
        "skeleton_path": str(skeleton_dir),
        "key_files": _scan_key_files(skeleton_dir),
        "commands": _scan_commands(skeleton_dir),
        "engine_modules": _scan_engine_modules(skeleton_dir),
    }

    runtime_dir.mkdir(parents=True, exist_ok=True)
    index_path = runtime_dir / "system_index.json"
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    return index


def load_system_index(runtime_dir: Path) -> dict | None:
    """Load the cached system index, or None if it doesn't exist."""
    index_path = runtime_dir / "system_index.json"
    if not index_path.exists():
        return None
    try:
        return json.loads(index_path.read_text())
    except Exception:
        return None


def needs_refresh(skeleton_dir: Path, runtime_dir: Path) -> bool:
    """Check if the system index needs rebuilding (submodule HEAD changed)."""
    cached = load_system_index(runtime_dir)
    if cached is None:
        return True
    current_head = _get_submodule_head(skeleton_dir)
    return cached.get("skeleton_head") != current_head


def ensure_system_index(skeleton_dir: Path, runtime_dir: Path) -> dict:
    """Build or refresh the system index as needed. Returns the index."""
    if needs_refresh(skeleton_dir, runtime_dir):
        return build_system_index(skeleton_dir, runtime_dir)
    return load_system_index(runtime_dir) or build_system_index(skeleton_dir, runtime_dir)


def lookup_command(index: dict, query: str) -> dict | None:
    """Look up a command by name or alias in the index.

    Returns the command dict if found, None otherwise.
    """
    query_lower = query.lower().strip().lstrip("/")
    for cmd in index.get("commands", []):
        if cmd["name"].lower() == query_lower:
            return cmd
        for alias in cmd.get("aliases", []):
            if alias.lower().strip().lstrip("/") == query_lower:
                return cmd
    return None


def lookup_capability(index: dict, query: str) -> str:
    """Answer a capability question using the system index.

    Returns a deterministic answer based on indexed data.
    """
    query_lower = query.lower()

    # Check commands first
    cmd = lookup_command(index, query)
    if cmd:
        aliases = ", ".join(cmd.get("aliases", [])[:3])
        return f"Yes. Command: {cmd['name']} — {cmd['description']}. Aliases: {aliases}"

    # Search command descriptions
    for cmd in index.get("commands", []):
        if query_lower in cmd.get("description", "").lower():
            return f"Related command: {cmd['name']} — {cmd['description']}"

    # Search key files
    for f in index.get("key_files", []):
        if query_lower in f.get("description", "").lower():
            return f"See: {f['path']} — {f['description']}"

    # Search engine modules
    for mod in index.get("engine_modules", []):
        if query_lower in mod.get("description", "").lower():
            return f"Engine module: {mod['name']} — {mod['description']}"

    return (
        f"Not found in the system layer. '{query}' is not a known command or feature. "
        "Use /help to see available capabilities, or propose this as a new feature."
    )

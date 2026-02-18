"""
ai_run.py — Orchestrator loop runner and command dispatcher.

Routes CLI commands to their handlers. Also provides the `ai run` loop.
"""

from __future__ import annotations

from pathlib import Path

from . import ai_db, ai_git, ai_init, ai_memory, ai_state, ai_validate


def find_schemas_dir() -> Path:
    """Find the schemas directory in the skeleton repo."""
    return ai_init.find_skeleton_dir() / "schemas"


def handle_status(project_root: Path, **kwargs) -> str:
    ai_dir = project_root / ".ai"
    runtime_dir = project_root / ".ai_runtime"
    ai_state.reconcile(ai_dir, runtime_dir)
    return ai_state.render_status(ai_dir, runtime_dir)


def handle_export_memory(project_root: Path, out: str | None = None, **kwargs) -> str:
    ai_dir = project_root / ".ai"
    runtime_dir = project_root / ".ai_runtime"
    skeleton_dir = ai_init.find_skeleton_dir()
    version = ai_git.get_skeleton_version(skeleton_dir)
    path = ai_memory.export_memory(ai_dir, runtime_dir, version, out)
    return f"Memory pack exported to: {path}"


def handle_import_memory(project_root: Path, in_path: str = "", **kwargs) -> str:
    if not in_path:
        return "Error: --in <path> is required for import-memory."
    ai_dir = project_root / ".ai"
    runtime_dir = project_root / ".ai_runtime"
    return ai_memory.import_memory(ai_dir, runtime_dir, in_path)


def handle_rehydrate_db(project_root: Path, **kwargs) -> str:
    ai_dir = project_root / ".ai"
    runtime_dir = project_root / ".ai_runtime"

    # Delete existing DB and rebuild
    db_path = ai_db.get_db_path(runtime_dir)
    if db_path.exists():
        db_path.unlink()

    ai_db.create_db(runtime_dir)
    updated = ai_state.reconcile(ai_dir, runtime_dir)
    return "Database rehydrated from canonical YAML state."


def handle_validate(project_root: Path, **kwargs) -> str:
    ai_dir = project_root / ".ai"
    schemas_dir = find_schemas_dir()
    results = ai_validate.validate_all(ai_dir, schemas_dir)

    lines = []
    all_valid = True
    for filename, errors in results.items():
        if errors:
            all_valid = False
            lines.append(f"  FAIL  {filename}")
            for err in errors:
                lines.append(f"        {err}")
        else:
            lines.append(f"  OK    {filename}")

    header = "Validation: ALL PASSED" if all_valid else "Validation: ERRORS FOUND"
    return header + "\n" + "\n".join(lines)


def handle_migrate(project_root: Path, **kwargs) -> str:
    """Non-destructive template migration.

    Copies new/missing template files from the skeleton into .ai/.
    Never overwrites existing files (especially STATUS.md, DECISIONS.md, state/*).
    """
    skeleton_dir = ai_init.find_skeleton_dir()
    ai_dir = project_root / ".ai"

    ai_init.copy_templates(skeleton_dir, project_root)

    # Re-stamp metadata with current skeleton version
    meta = ai_init.stamp_metadata(project_root, skeleton_dir)

    lines = [
        "Migration complete (non-destructive).",
        f"  Skeleton version: {meta.get('skeleton_version', 'unknown')}",
        "  New template files added (if any were missing).",
        "  Existing files were NOT overwritten.",
        "  Run 'ai validate' to check schema compliance.",
    ]
    return "\n".join(lines)


def handle_session_memory_export(
    project_root: Path,
    out: str | None = None,
    namespaces: str | None = None,
    **kwargs,
) -> str:
    """Export session memory pack."""
    from .memory_core.api import SessionMemory

    mem = SessionMemory(project_root)
    try:
        ns_list = namespaces.split(",") if namespaces else None
        out_path = out or str(project_root / ".ai_runtime" / "session" / "memory_export")
        result_path = mem.export_pack(out_path, ns_list)
        return f"Session memory exported to: {result_path}"
    finally:
        mem.close()


def handle_session_memory_import(
    project_root: Path,
    in_path: str = "",
    **kwargs,
) -> str:
    """Import session memory pack."""
    if not in_path:
        return "Error: --in <path> is required."

    from .memory_core.api import SessionMemory

    mem = SessionMemory(project_root)
    try:
        counts = mem.import_pack(in_path)
        parts = [f"{k}: {v}" for k, v in counts.items() if v > 0]
        return f"Session memory imported. {', '.join(parts)}."
    except (FileNotFoundError, ValueError) as e:
        return f"Error: {e}"
    finally:
        mem.close()


def handle_session_memory_purge(
    project_root: Path,
    namespace: str | None = None,
    days: str | None = None,
    **kwargs,
) -> str:
    """Purge session memory."""
    from .memory_core.api import SessionMemory

    mem = SessionMemory(project_root)
    try:
        days_int = int(days) if days else None
        counts = mem.purge(namespace=namespace, older_than_days=days_int)
        parts = [f"{k}: {v}" for k, v in counts.items()]
        return f"Session memory purged. {', '.join(parts)}."
    finally:
        mem.close()


def handle_git_sync(project_root: Path, message: str | None = None, **kwargs) -> str:
    # First render status to update STATUS.md
    ai_dir = project_root / ".ai"
    runtime_dir = project_root / ".ai_runtime"
    ai_state.reconcile(ai_dir, runtime_dir)
    ai_state.render_status(ai_dir, runtime_dir)

    success, msg = ai_git.git_sync(project_root, message)
    return msg


# Command registry: maps handler names to functions
HANDLERS = {
    "handle_status": handle_status,
    "handle_export_memory": handle_export_memory,
    "handle_import_memory": handle_import_memory,
    "handle_rehydrate_db": handle_rehydrate_db,
    "handle_validate": handle_validate,
    "handle_git_sync": handle_git_sync,
    "handle_migrate": handle_migrate,
}


def load_command_registry(project_root: Path) -> dict:
    """Load commands.yaml and build a lookup: alias -> handler_name."""
    try:
        import yaml
    except ImportError:
        return {}

    commands_path = project_root / ".ai" / "state" / "commands.yaml"
    if not commands_path.exists():
        return {}

    data = yaml.safe_load(commands_path.read_text()) or {}
    registry = {}
    for cmd in data.get("commands", []):
        handler = cmd.get("handler", "")
        for alias in [cmd.get("name", "")] + cmd.get("aliases", []):
            if alias:
                registry[alias.lower().strip().lstrip("/")] = handler
    return registry


def dispatch_command(project_root: Path, command: str, **kwargs) -> str:
    """Dispatch a command string to its handler."""
    registry = load_command_registry(project_root)
    normalized = command.lower().strip().lstrip("/")

    handler_name = registry.get(normalized)
    if not handler_name:
        return f"Unknown command: '{command}'. Run 'ai --help' for available commands."

    handler = HANDLERS.get(handler_name)
    if not handler:
        return f"Handler '{handler_name}' not implemented."

    return handler(project_root, **kwargs)


def run_loop(project_root: Path):
    """Interactive orchestrator loop (v1: simple command REPL)."""
    ai_dir = project_root / ".ai"
    runtime_dir = project_root / ".ai_runtime"

    # Ensure state is reconciled
    ai_state.reconcile(ai_dir, runtime_dir)

    print("AI Orchestrator running. Type commands or 'quit' to exit.")
    print("Available: status, export-memory, import-memory, rehydrate-db, validate, git-sync")
    print()

    while True:
        try:
            cmd = input("ai> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not cmd:
            continue
        if cmd.lower() in ("quit", "exit", "q"):
            print("Exiting.")
            break

        # Parse simple args
        parts = cmd.split()
        command = parts[0]
        kwargs = {}

        # Parse --key value pairs
        i = 1
        while i < len(parts):
            if parts[i].startswith("--"):
                key = parts[i][2:].replace("-", "_")
                if i + 1 < len(parts) and not parts[i + 1].startswith("--"):
                    kwargs[key] = parts[i + 1]
                    i += 2
                else:
                    kwargs[key] = True
                    i += 1
            else:
                i += 1

        result = dispatch_command(project_root, command, **kwargs)
        print(result)
        print()

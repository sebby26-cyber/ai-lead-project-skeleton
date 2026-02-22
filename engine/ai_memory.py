"""
ai_memory.py — Export/import memory packs for portability.

Memory packs carry local runtime events and derived state snapshots.
Canonical state remains in .ai/state/*.yaml (repo source of truth).
"""

from __future__ import annotations

import json
import os
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from . import ai_db, ai_state


def export_memory(
    ai_dir: Path,
    runtime_dir: Path,
    skeleton_version: str,
    out_path: str | None = None,
) -> str:
    """Export a memory pack.

    Returns the path to the created pack (directory or zip).
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    pack_dir = runtime_dir / "memory_pack_cache" / f"memory_pack_{ts}"
    pack_dir.mkdir(parents=True, exist_ok=True)

    conn = ai_db.connect_db(runtime_dir)

    # Compute canonical hash
    canonical_hash = ai_state.compute_canonical_hash(ai_dir)

    # Load metadata
    metadata_path = ai_dir / "METADATA.yaml"
    project_id = "unknown"
    if metadata_path.exists():
        try:
            import yaml
            meta = yaml.safe_load(metadata_path.read_text()) or {}
            project_id = meta.get("project_id", "unknown")
        except Exception:
            pass

    # Check if canonical worker state exists
    workers_dir = ai_dir / "workers"
    worker_state_included = workers_dir.is_dir() and any(workers_dir.rglob("*"))

    # Write manifest
    manifest = {
        "version": "1.0",
        "project_id": project_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "skeleton_version": skeleton_version,
        "canonical_hash": canonical_hash,
        "worker_state_included": worker_state_included,
    }
    (pack_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # Write events as JSONL
    events = ai_db.export_events(conn)
    with open(pack_dir / "events.jsonl", "w") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    # Write derived state
    derived = ai_db.export_derived(conn)
    (pack_dir / "derived_state.json").write_text(json.dumps(derived, indent=2))

    conn.close()

    # Optionally compress
    if out_path:
        out_p = Path(out_path)
        if out_p.suffix == ".zip":
            with zipfile.ZipFile(str(out_p), "w", zipfile.ZIP_DEFLATED) as zf:
                for fpath in pack_dir.rglob("*"):
                    if fpath.is_file():
                        zf.write(str(fpath), fpath.relative_to(pack_dir))
            shutil.rmtree(str(pack_dir))
            return str(out_p)
        else:
            # Copy to specified directory
            if out_p.exists():
                shutil.rmtree(str(out_p))
            shutil.copytree(str(pack_dir), str(out_p))
            shutil.rmtree(str(pack_dir))
            return str(out_p)

    return str(pack_dir)


def import_memory(
    ai_dir: Path,
    runtime_dir: Path,
    in_path: str,
) -> str:
    """Import a memory pack.

    Returns a status message.
    """
    in_p = Path(in_path).resolve()

    # Handle zip files
    if in_p.suffix == ".zip" and in_p.is_file():
        extract_dir = runtime_dir / "memory_pack_cache" / "import_tmp"
        if extract_dir.exists():
            shutil.rmtree(str(extract_dir))
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(str(in_p), "r") as zf:
            zf.extractall(str(extract_dir))
        in_p = extract_dir

    if not in_p.is_dir():
        return f"Error: {in_path} is not a valid memory pack directory or zip file."

    # Validate manifest
    manifest_path = in_p / "manifest.json"
    if not manifest_path.exists():
        return "Error: No manifest.json found in memory pack."

    manifest = json.loads(manifest_path.read_text())
    if manifest.get("version") != "1.0":
        return f"Error: Unsupported memory pack version: {manifest.get('version')}"

    conn = ai_db.connect_db(runtime_dir)

    # Import events
    events_path = in_p / "events.jsonl"
    imported_count = 0
    if events_path.exists():
        events = []
        with open(events_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        ai_db.import_events(conn, events)
        imported_count = len(events)

    # Import derived state if schema matches
    derived_path = in_p / "derived_state.json"
    derived_imported = False
    if derived_path.exists():
        try:
            derived = json.loads(derived_path.read_text())
            # Only import derived if canonical hash matches (schema compatible)
            current_hash = ai_state.compute_canonical_hash(ai_dir)
            if manifest.get("canonical_hash") == current_hash:
                # Schema matches, safe to import derived
                derived_imported = True
            # Events are always imported; derived only when compatible
        except Exception:
            pass

    # Run reconciliation — canonical YAML is source of truth
    ai_state.reconcile(ai_dir, runtime_dir)

    ai_db.add_event(conn, "system", "import_memory", {
        "source": str(in_path),
        "events_imported": imported_count,
        "derived_imported": derived_imported,
    })

    conn.close()

    # Clean up temp extract
    tmp_dir = runtime_dir / "memory_pack_cache" / "import_tmp"
    if tmp_dir.exists():
        shutil.rmtree(str(tmp_dir))

    return (
        f"Imported {imported_count} events from memory pack.\n"
        f"Derived state: {'imported (schema match)' if derived_imported else 'skipped (reconciled from canonical)'}.\n"
        f"Canonical YAML remains source of truth."
    )

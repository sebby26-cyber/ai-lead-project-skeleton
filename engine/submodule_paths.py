"""Canonical/legacy Scaffold AI submodule path helpers."""

from __future__ import annotations

from pathlib import Path

CANONICAL_SUBMODULE_PATH = "scaffold/scaffold-ai"
LEGACY_SUBMODULE_PATH = "vendor/scaffold-ai"

SUBMODULE_POLICY_SUMMARY = (
    "vendor/ is reserved for package managers (for example Go vendoring). "
    "Scaffold/system submodules must use a non-package-manager directory such as "
    f"'{CANONICAL_SUBMODULE_PATH}'."
)


def detect_submodule_layout(project_root: Path) -> dict[str, bool]:
    """Inspect known legacy/canonical submodule locations in a project."""
    return {
        "legacy_exists": (project_root / LEGACY_SUBMODULE_PATH).exists(),
        "canonical_exists": (project_root / CANONICAL_SUBMODULE_PATH).exists(),
    }


def relpath_from_project(project_root: Path, path: Path) -> str | None:
    """Return *path* relative to *project_root*, if possible."""
    try:
        return str(path.resolve().relative_to(project_root.resolve()))
    except ValueError:
        return None


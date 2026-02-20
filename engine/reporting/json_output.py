"""
json_output.py — JSON output for ProjectReport.

The JSON representation IS the report model. Terminal output derives from it.
"""

from __future__ import annotations

import json

from .model import ProjectReport


def render_json(report: ProjectReport, indent: int = 2) -> str:
    """Serialize a ProjectReport to JSON string."""
    return json.dumps(report.to_dict(), indent=indent, ensure_ascii=False)

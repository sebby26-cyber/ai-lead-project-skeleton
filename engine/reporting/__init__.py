"""
reporting — PM-grade project reporting module.

Owns: report model, builder, terminal renderer, JSON output.
"""

from .model import ProjectReport, ReportTask, ReportMilestone, ReportDecision
from .builder import generate_report
from .renderer import render_terminal
from .json_output import render_json

__all__ = [
    "ProjectReport",
    "ReportTask",
    "ReportMilestone",
    "ReportDecision",
    "generate_report",
    "render_terminal",
    "render_json",
]

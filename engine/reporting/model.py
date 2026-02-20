"""
model.py — Canonical report data model (JSON-serializable).

This is the single source of truth for report structure.
Terminal and JSON renderers both consume this model.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ReportTask:
    id: str
    title: str
    status: str  # backlog | ready | in_progress | review | done
    progress: Optional[int] = None  # 0-100, nullable
    priority: Optional[str] = None  # high | medium | low, nullable
    owner: Optional[str] = None  # explicit name or None → "Unassigned"
    owner_role: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    blocker_reason: Optional[str] = None
    requires_approval: list[str] = field(default_factory=list)
    last_update: Optional[str] = None
    artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        if d["owner"] is None:
            d["owner"] = "Unassigned"
        return d


@dataclass
class ReportMilestone:
    id: str
    title: str
    status: str  # done | in_progress | pending
    target_date: Optional[str] = None
    completion_date: Optional[str] = None
    tasks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReportDecision:
    date: str
    title: str
    detail: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReportApproval:
    trigger_id: str
    description: str
    task_id: Optional[str] = None
    status: str = "pending"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DataHealth:
    missing_owners: int = 0
    stale_tasks: int = 0
    tasks_without_priority: int = 0
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProjectReport:
    generated_at: str
    project_name: str
    current_phase: str
    overall_progress: int  # 0-100

    summary: list[str] = field(default_factory=list)
    milestones: list[ReportMilestone] = field(default_factory=list)
    tasks: list[ReportTask] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    decisions_recent: list[ReportDecision] = field(default_factory=list)
    approvals_pending: list[ReportApproval] = field(default_factory=list)
    recent_activity: list[str] = field(default_factory=list)
    assignments: dict[str, list[str]] = field(default_factory=dict)
    next_actions: list[str] = field(default_factory=list)
    data_health: DataHealth = field(default_factory=DataHealth)

    # Counts by status for quick access
    task_counts: dict[str, int] = field(default_factory=dict)
    columns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "generated_at": self.generated_at,
            "project_name": self.project_name,
            "current_phase": self.current_phase,
            "overall_progress": self.overall_progress,
            "summary": self.summary,
            "milestones": [m.to_dict() for m in self.milestones],
            "tasks": [t.to_dict() for t in self.tasks],
            "blockers": self.blockers,
            "risks": self.risks,
            "decisions_recent": [d.to_dict() for d in self.decisions_recent],
            "approvals_pending": [a.to_dict() for a in self.approvals_pending],
            "recent_activity": self.recent_activity,
            "assignments": self.assignments,
            "next_actions": self.next_actions,
            "data_health": self.data_health.to_dict(),
            "task_counts": self.task_counts,
            "columns": self.columns,
        }

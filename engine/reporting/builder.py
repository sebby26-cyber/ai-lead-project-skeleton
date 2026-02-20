"""
builder.py — Report builder. Aggregates project state into a ProjectReport.

Accepts an adapter dict that maps project-specific state into the
canonical format. The builder never reads files directly — the adapter
provides all data.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .model import (
    DataHealth,
    ProjectReport,
    ReportApproval,
    ReportDecision,
    ReportMilestone,
    ReportTask,
)


def generate_report(adapter_data: dict) -> ProjectReport:
    """Build a ProjectReport from adapter-provided data.

    adapter_data keys:
        project_name: str
        board: dict (columns, tasks)
        team: dict (orchestrator, roles)
        approvals: dict (triggers, approval_log)
        decisions_text: str (raw DECISIONS.md content)
        metadata: dict (project_id, skeleton_version, etc.)
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    project_name = adapter_data.get("project_name", "Unknown Project")

    # --- Tasks ---
    board = adapter_data.get("board", {})
    columns = board.get("columns", ["backlog", "ready", "in_progress", "review", "done"])
    raw_tasks = board.get("tasks", [])

    tasks: list[ReportTask] = []
    for t in raw_tasks:
        tasks.append(ReportTask(
            id=t.get("id", "?"),
            title=t.get("title", "Untitled"),
            status=t.get("status", "backlog"),
            progress=t.get("progress"),
            priority=t.get("priority"),
            owner=t.get("owner"),
            owner_role=t.get("owner_role"),
            dependencies=t.get("dependencies", []),
            blocker_reason=t.get("blocker_reason"),
            requires_approval=t.get("requires_approval", []),
            last_update=t.get("last_update"),
            artifacts=t.get("artifacts", []),
        ))

    # --- Counts ---
    task_counts = {col: 0 for col in columns}
    for t in tasks:
        if t.status in task_counts:
            task_counts[t.status] += 1

    total = len(tasks)
    done_count = task_counts.get("done", 0)
    overall_progress = int(done_count / total * 100) if total > 0 else 0

    # --- Phase ---
    if total == 0:
        phase = "Initialization"
    elif done_count == total:
        phase = "Complete"
    elif any(t.status == "in_progress" for t in tasks):
        phase = "Active Development"
    elif any(t.status == "ready" for t in tasks):
        phase = "Planning"
    else:
        phase = "Backlog"

    # --- Summary bullets ---
    summary = []
    summary.append(f"{done_count}/{total} tasks completed ({overall_progress}%)")
    in_progress = task_counts.get("in_progress", 0)
    ready = task_counts.get("ready", 0)
    backlog = task_counts.get("backlog", 0)
    if in_progress > 0:
        summary.append(f"{in_progress} task(s) in progress")
    if ready > 0:
        summary.append(f"{ready} task(s) ready to start")
    if backlog > 0:
        summary.append(f"{backlog} task(s) in backlog")

    # --- Assignments ---
    team = adapter_data.get("team", {})
    assignments: dict[str, list[str]] = {}

    # Map owner_role → task IDs
    for t in tasks:
        if t.status == "done":
            continue
        role = t.owner_role or t.owner
        if role:
            assignments.setdefault(role, []).append(t.id)
        else:
            assignments.setdefault("Unassigned", []).append(t.id)

    # --- Blockers ---
    blockers = []
    for t in tasks:
        if t.blocker_reason:
            blockers.append(f"{t.id}: {t.blocker_reason}")
        if t.requires_approval and t.status not in ("done",):
            blockers.append(f"{t.id}: requires approval ({', '.join(t.requires_approval)})")

    # --- Approvals ---
    approvals_data = adapter_data.get("approvals", {})
    approval_log = approvals_data.get("approval_log", [])
    pending_approvals = [
        ReportApproval(
            trigger_id=a.get("trigger_id", "unknown"),
            description=a.get("description", ""),
            task_id=a.get("task_id"),
            status=a.get("status", "pending"),
        )
        for a in approval_log
        if a.get("status") == "pending"
    ]

    # --- Decisions ---
    decisions_text = adapter_data.get("decisions_text", "")
    decisions_recent = _parse_decisions(decisions_text)

    # --- Milestones (derived from done phases) ---
    milestones = _derive_milestones(tasks)

    # --- Next actions ---
    next_actions = []
    ready_tasks = [t for t in tasks if t.status == "ready"]
    for t in sorted(ready_tasks, key=lambda x: (x.priority != "high", x.id)):
        next_actions.append(f"[{t.id}] {t.title}")
    if not next_actions:
        backlog_tasks = [t for t in tasks if t.status == "backlog"]
        for t in sorted(backlog_tasks, key=lambda x: (x.priority != "high", x.id))[:3]:
            next_actions.append(f"[{t.id}] {t.title} (needs triage)")

    # --- Data health ---
    data_health = DataHealth()
    warnings = []
    no_owner = [t for t in tasks if t.status != "done" and not t.owner and not t.owner_role]
    data_health.missing_owners = len(no_owner)
    if no_owner:
        warnings.append(f"{len(no_owner)} active task(s) have no owner assigned")

    no_priority = [t for t in tasks if t.status != "done" and not t.priority]
    data_health.tasks_without_priority = len(no_priority)
    if no_priority:
        warnings.append(f"{len(no_priority)} active task(s) have no priority set")

    no_update = [t for t in tasks if t.status == "in_progress" and not t.last_update]
    data_health.stale_tasks = len(no_update)
    if no_update:
        warnings.append(f"{len(no_update)} in-progress task(s) have no last_update timestamp")

    data_health.warnings = warnings

    # --- Risks ---
    risks = []
    if data_health.missing_owners > 0:
        risks.append("Some tasks have no assigned owner")
    high_backlog = [t for t in tasks if t.status == "backlog" and t.priority == "high"]
    if len(high_backlog) > 3:
        risks.append(f"{len(high_backlog)} high-priority tasks still in backlog")

    return ProjectReport(
        generated_at=now,
        project_name=project_name,
        current_phase=phase,
        overall_progress=overall_progress,
        summary=summary,
        milestones=milestones,
        tasks=tasks,
        blockers=blockers,
        risks=risks,
        decisions_recent=decisions_recent,
        approvals_pending=pending_approvals,
        recent_activity=[],
        assignments=assignments,
        next_actions=next_actions,
        data_health=data_health,
        task_counts=task_counts,
        columns=columns,
    )


def _parse_decisions(text: str) -> list[ReportDecision]:
    """Parse recent decisions from DECISIONS.md content."""
    if not text:
        return []

    decisions = []
    # Match ## YYYY-MM-DD: Title patterns
    pattern = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2}):\s*(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))

    for i, match in enumerate(matches):
        date = match.group(1)
        title = match.group(2).strip()

        # Extract detail: text between this heading and the next
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        detail = text[start:end].strip()

        # Trim to first few lines
        detail_lines = detail.split("\n")
        if len(detail_lines) > 5:
            detail = "\n".join(detail_lines[:5]) + "\n  ..."

        decisions.append(ReportDecision(date=date, title=title, detail=detail))

    # Return most recent 5
    return decisions[-5:]


def _derive_milestones(tasks: list[ReportTask]) -> list[ReportMilestone]:
    """Derive milestones from phase-level tasks (PHASE-* prefixed)."""
    milestones = []
    for t in tasks:
        if t.id.startswith("PHASE-") or t.id.startswith("V2-"):
            status = "done" if t.status == "done" else "in_progress" if t.status == "in_progress" else "pending"
            milestones.append(ReportMilestone(
                id=t.id,
                title=t.title,
                status=status,
                tasks=[t.id],
            ))
    return milestones

"""
renderer.py — Terminal renderer for ProjectReport.

Produces clean, aligned, PM-grade terminal output.
All rendering derives from the report model (which is JSON-serializable).
"""

from __future__ import annotations

from .model import ProjectReport


def render_terminal(report: ProjectReport) -> str:
    """Render a ProjectReport as terminal-friendly text."""
    W = 72
    lines: list[str] = []

    # ── Header ──
    lines.append("=" * W)
    lines.append(_center("PROJECT STATUS REPORT", W))
    lines.append("=" * W)
    lines.append(f"  Project:   {report.project_name}")
    lines.append(f"  Phase:     {report.current_phase}")
    lines.append(f"  Generated: {report.generated_at}")
    lines.append("")

    # ── Executive Summary ──
    lines.append(_section("Executive Summary"))
    for bullet in report.summary:
        lines.append(f"  - {bullet}")
    lines.append("")

    # ── Progress Overview ──
    lines.append(_section("Progress Overview"))
    bar = _progress_bar(report.overall_progress, width=30)
    lines.append(f"  {bar}  {report.overall_progress}%")
    lines.append("")

    # Status counts table
    if report.task_counts:
        lines.append("  Status        Count")
        lines.append("  " + "-" * 24)
        for col in report.columns:
            cnt = report.task_counts.get(col, 0)
            label = col.replace("_", " ").title()
            lines.append(f"  {label:<14} {cnt:>5}")
        lines.append("")

    # ── Milestones ──
    if report.milestones:
        lines.append(_section("Milestones"))
        for m in report.milestones:
            marker = _status_marker(m.status)
            lines.append(f"  {marker} {m.id}: {m.title}")
        lines.append("")

    # ── Task Snapshot ──
    lines.append(_section("Task Snapshot"))

    # Active / in-progress
    active = [t for t in report.tasks if t.status == "in_progress"]
    if active:
        lines.append("  IN PROGRESS:")
        for t in active:
            owner = t.owner or t.owner_role or "Unassigned"
            lines.append(f"    [{t.id}] {t.title}")
            lines.append(f"           owner: {owner}  priority: {t.priority or '-'}")
        lines.append("")

    # Ready
    ready = [t for t in report.tasks if t.status == "ready"]
    if ready:
        lines.append("  READY:")
        for t in ready:
            owner = t.owner or t.owner_role or "Unassigned"
            pri = t.priority or "-"
            lines.append(f"    [{t.id}] {t.title}")
            lines.append(f"           owner: {owner}  priority: {pri}")
        lines.append("")

    # Backlog
    backlog = [t for t in report.tasks if t.status == "backlog"]
    if backlog:
        lines.append("  BACKLOG:")
        for t in backlog:
            owner = t.owner or t.owner_role or "Unassigned"
            pri = t.priority or "-"
            lines.append(f"    [{t.id}] {t.title}")
            lines.append(f"           owner: {owner}  priority: {pri}")
        lines.append("")

    # Review
    review = [t for t in report.tasks if t.status == "review"]
    if review:
        lines.append("  IN REVIEW:")
        for t in review:
            owner = t.owner or t.owner_role or "Unassigned"
            lines.append(f"    [{t.id}] {t.title}")
            lines.append(f"           owner: {owner}  priority: {t.priority or '-'}")
        lines.append("")

    # Blocked
    blocked = [t for t in report.tasks if t.blocker_reason]
    if blocked:
        lines.append("  BLOCKED:")
        for t in blocked:
            lines.append(f"    [{t.id}] {t.title}")
            lines.append(f"           reason: {t.blocker_reason}")
        lines.append("")

    # Done (compact)
    done = [t for t in report.tasks if t.status == "done"]
    if done:
        lines.append(f"  COMPLETED ({len(done)}):")
        for t in done:
            lines.append(f"    [x] {t.id}: {t.title}")
        lines.append("")

    # ── Assignments ──
    lines.append(_section("Assignments"))
    if report.assignments:
        for role, task_ids in report.assignments.items():
            lines.append(f"  {role}:")
            for tid in task_ids:
                lines.append(f"    - {tid}")
    else:
        lines.append("  No assignments configured")
    lines.append("")

    # ── Blockers & Risks ──
    lines.append(_section("Blockers & Risks"))
    if report.blockers:
        lines.append("  Blockers:")
        for b in report.blockers:
            lines.append(f"    - {b}")
    else:
        lines.append("  Blockers: None")
    lines.append("")
    if report.risks:
        lines.append("  Risks:")
        for r in report.risks:
            lines.append(f"    - {r}")
    else:
        lines.append("  Risks: None")
    lines.append("")

    # ── Decisions & Approvals ──
    lines.append(_section("Recent Decisions"))
    if report.decisions_recent:
        for d in report.decisions_recent:
            lines.append(f"  [{d.date}] {d.title}")
            for detail_line in d.detail.split("\n")[:3]:
                if detail_line.strip():
                    lines.append(f"    {detail_line.strip()}")
    else:
        lines.append("  No recent decisions recorded")
    lines.append("")

    if report.approvals_pending:
        lines.append("  Pending Approvals:")
        for a in report.approvals_pending:
            target = f" on {a.task_id}" if a.task_id else ""
            lines.append(f"    - {a.trigger_id}{target}: {a.description}")
    else:
        lines.append("  Pending Approvals: None")
    lines.append("")

    # ── Next Actions ──
    lines.append(_section("Next Actions"))
    if report.next_actions:
        for i, action in enumerate(report.next_actions, 1):
            lines.append(f"  {i}. {action}")
    else:
        lines.append("  No pending actions")
    lines.append("")

    # ── Data Health ──
    if report.data_health.warnings:
        lines.append(_section("Data Health"))
        for w in report.data_health.warnings:
            lines.append(f"  ! {w}")
        lines.append("")

    lines.append("=" * W)

    return "\n".join(lines)


def _center(text: str, width: int) -> str:
    pad = (width - len(text)) // 2
    return " " * pad + text


def _section(title: str) -> str:
    return f"  --- {title} ---"


def _progress_bar(pct: int, width: int = 30) -> str:
    filled = int(width * pct / 100)
    return "[" + "#" * filled + "." * (width - filled) + "]"


def _status_marker(status: str) -> str:
    if status == "done":
        return "[x]"
    elif status == "in_progress":
        return "[~]"
    else:
        return "[ ]"

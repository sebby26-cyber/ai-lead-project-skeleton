# Context Persistence System

**Purpose:** Ensure project state survives context loss and agent replacement
**Enforces:** Canonical state files, append-only logs, resume-ready structure

---

## Core Principle

**Context must persist across:**

1. Agent replacement (lead handoff)
2. Session termination
3. Context window exhaustion
4. Days/weeks between work sessions
5. Multiple worker deployments

**Mechanism:** Canonical state files in repository

---

## Three Canonical Files

### STATUS.md

**Role:** Single source of truth for current project state

**Contains:**

- Current phase and milestone
- Active deliverables
- Prioritized TODO list
- Phase plan with acceptance criteria
- Worker roster (who's working on what)
- Progress metrics
- Resume checklist for handoff
- Completion checklists (v1/v2/etc)

**Update frequency:** After every deliverable completion, phase transition, or worker deployment

**Persistence guarantee:** New lead reads this FIRST

---

### DECISIONS.md

**Role:** Append-only log of architectural decisions

**Contains:**

- Timestamped decision entries
- Context for each decision (why needed)
- Alternatives considered
- Consequences and trade-offs
- Phase transitions
- Breaking changes

**Update frequency:** When any architectural decision is made

**Persistence guarantee:** Never delete entries, only append

---

### AGENTS.md

**Role:** Process guardrails and orchestration rules

**Contains:**

- Lead conductor protocol
- Worker orchestration rules
- Status report format specification
- Approval gate requirements
- Worker pool configuration
- Non-overlapping execution policy

**Update frequency:** When orchestration rules change (rare)

**Persistence guarantee:** Defines invariant behavior across sessions

---

## File Format Specifications

### STATUS.md Structure

```markdown
# Project Status

**Last Updated:** [YYYY-MM-DD HH:MM]
**Lead Agent:** [Agent ID]
**Phase:** Phase N - [Name]
**Milestone:** [Name] ([X]% complete)

---

## Current Deliverable

[Name of active deliverable]
**Status:** IN PROGRESS / NEXT
**Owner:** Lead / Worker-N

---

## Phase Plan

### Phase 0: Foundation
[Phase details, acceptance criteria, deliverables]

### Phase 1: Core Implementation
[Phase details, acceptance criteria, deliverables]

[... all phases ...]

---

## Progress

**Overall:** [X]% ([M]/[N] milestones complete)
**Current Phase:** [X]% ([M]/[N] deliverables complete)
**Tests:** [X]/[Y] passing ([Z]%)

---

## TODO (Prioritized)

### P0 (Critical)
- [ ] Next immediate action
- [ ] Another critical item

### P1 (High Priority)
- [ ] Important but not blocking
- [ ] Secondary priority

### P2 (Nice to Have)
- [ ] Future improvements

---

## Worker Roster

**Active Workers:**
- Codex-Worker-1: [Task] (Scope: files/modules)
- Claude-Worker-2: [Task] (Scope: design/planning)

**Recent Completions:**
- Codex-Worker-3: [Task] (COMPLETE, integrated 2026-02-15)

---

## Resume Checklist

**For new lead agent:**

1. Read STATUS.md (this file)
2. Read DECISIONS.md (recent entries, last 7 days)
3. Check .taskers/runs/ (active worker outputs)
4. Run smoke tests (verify current state)
5. Pick next P0 from TODO above
6. Update STATUS.md after any change
7. Re-run tests before commit

**Target:** Operational in <15 minutes

---

## Acceptance Checklists

### v1 Done Criteria
- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
[... all v1 criteria ...]

### v2 Phase-Entry Checklist
- [ ] Entry criterion 1
- [ ] Entry criterion 2
[... all v2 entry criteria ...]

---

**Status File End**
```

---

### DECISIONS.md Structure

```markdown
# Architectural Decision Log

**Project:** [Project Name]
**Started:** [YYYY-MM-DD]

---

## 2026-02-16: Decision Title

**Context:** [Why this decision was needed]

**Decision:** [What was decided]

**Alternatives Considered:**
1. Alternative A - Rejected because [reason]
2. Alternative B - Rejected because [reason]

**Consequences:**
- Positive: [Benefits]
- Negative: [Trade-offs or costs]
- Neutral: [Other impacts]

**Status:** Accepted
**Supersedes:** [Previous decision number, if any]

---

## 2026-02-15: Another Decision

[Same format as above]

---

[... append-only, newest at top ...]

---

**Decision Log End**
```

---

### AGENTS.md Structure

```markdown
# Agent Orchestration Protocol

**Last Updated:** [YYYY-MM-DD]
**Version:** 1.0

---

## Lead Conductor Role

[Lead agent responsibilities, constraints, authority]

---

## Worker Orchestration

**Pool Configuration:**
- Maximum workers: 15
  - Codex: 5 workers
  - Claude: 5 workers
  - Gemini: 5 workers (optional, disabled by default)

**Worker Constraints:**
- Read-only repository access
- Scoped tickets only
- No overlapping file ownership
- Report findings, do not commit

---

## Status Report Protocol

[7-section format specification]

---

## Approval Gates

[When user approval required]

---

**Agents File End**
```

---

## Runtime State Storage

### .taskers/ Directory

**Purpose:** Worker execution state (git-ignored)

**Structure:**

```
.taskers/
├── tickets/               # Runtime worker tickets
│   ├── Codex-Worker-1.md
│   ├── Claude-Worker-1.md
│   └── ...
├── runs/                  # Execution outputs
│   ├── 20260216_142834/   # Timestamped run
│   │   ├── Codex-Worker-1.txt
│   │   ├── Claude-Worker-2.txt
│   │   └── ...
│   └── 20260215_093021/   # Previous run
└── [legacy logs]          # Historical execution logs
```

**Persistence:**

- Tickets: Current worker assignments
- Runs: Historical execution outputs
- Git-ignored (not committed)
- Preserved locally for session continuity

---

### Worker Ticket Templates

**Purpose:** Committed ticket templates for reproducibility

**Location:** `docs/worker-ticket-templates/`

**Structure:**

```
docs/worker-ticket-templates/
├── README.md              # Template usage instructions
├── codex-1.md             # Codex worker 1 template
├── codex-2.md             # Codex worker 2 template
├── ...
├── claude-1.md            # Claude worker 1 template
├── claude-2.md            # Claude worker 2 template
└── ...
```

**Persistence:** Committed to git, version controlled

**Usage:** Copy templates to .taskers/tickets/ before worker launch

---

## Resume Protocol

### For New Lead Agent

**Step 1: Read Canonical Files**

```bash
# Read in this order:
1. STATUS.md        # Current state
2. DECISIONS.md     # Recent decisions (last 7 days)
3. AGENTS.md        # Process rules
```

**Time:** 10 minutes

---

**Step 2: Verify State**

```bash
# Check active workers
ls -la .taskers/runs/$(ls -t .taskers/runs/ | head -1)/

# Run smoke tests
make smoke-test

# Check git status
git status
```

**Time:** 3 minutes

---

**Step 3: Resume Execution**

1. Read next P0 from STATUS.md TODO section
2. Continue from current deliverable
3. Update STATUS.md after any change
4. Re-run tests before commit

**Time:** 2 minutes

**Total handoff time:** <15 minutes

---

### For Context Window Compression

**When context fills up:**

1. Generate status report
2. Update STATUS.md with current state
3. Log recent decisions in DECISIONS.md
4. Commit changes
5. New session reads canonical files
6. Resumes from current state

**State preserved in files, not in memory.**

---

## State Synchronization

### After Every Deliverable

**Lead must:**

1. Update STATUS.md:
   - Mark deliverable complete
   - Update progress percentages
   - Move TODO items
2. Update DECISIONS.md (if architectural change)
3. Commit both files
4. Run tests

**Example commit:**

```
Deliverable complete: Integration tests

- All integration tests passing (32/32)
- Updated STATUS.md (Phase 2 now 75% complete)
- Logged test framework decision in DECISIONS.md

Tests: 184/184 passing
```

---

### After Phase Transition

**Lead must:**

1. Update STATUS.md:
   - Mark phase complete
   - Advance to next phase
   - Update milestone progress
2. Log transition in DECISIONS.md
3. Generate status report
4. Request approval (if required)
5. Commit updates

---

### After Worker Integration

**Lead must:**

1. Update STATUS.md:
   - Move worker from "Active" to "Recent Completions"
   - Note integration decision (accepted/rejected/partial)
2. Log significant decisions in DECISIONS.md
3. Update TODO if new work discovered
4. Commit updates

---

## Persistence Guarantees

### What Persists

✅ **Current project state** (STATUS.md)
✅ **Architectural decisions** (DECISIONS.md)
✅ **Process rules** (AGENTS.md)
✅ **Phase plan** (in STATUS.md)
✅ **Acceptance criteria** (in STATUS.md)
✅ **Worker tickets** (templates committed)
✅ **Execution history** (.taskers/runs/)
✅ **Git commits** (code + canonical files)

---

### What Does NOT Persist

❌ Agent memory (context window)
❌ Active worker processes (terminate between sessions)
❌ Uncommitted code changes
❌ Unlogged decisions
❌ Verbal agreements (must be in DECISIONS.md)
❌ Assumptions not written down

**Rule:** If it's not in a canonical file, it doesn't exist.

---

## Anti-Patterns

### Avoid These

❌ **Verbal-only decisions** - Must log in DECISIONS.md
❌ **Stale STATUS.md** - Must update after every deliverable
❌ **Missing resume checklist** - New lead can't resume
❌ **No TODO prioritization** - Unclear what to do next
❌ **Uncommitted state** - Changes not persisted
❌ **Incomplete decision logs** - Missing context or rationale
❌ **Vague current deliverable** - Can't resume work

---

## Handoff Testing

**Test handoff protocol:**

1. Generate status report
2. Simulate new lead:
   - Read STATUS.md only
   - Can you determine next action?
   - Can you continue work without questions?
3. If NO, STATUS.md is insufficient
4. If YES, handoff will succeed

**Quality check:**

```markdown
## Handoff Quality Checklist

- [ ] STATUS.md has current deliverable
- [ ] Next P0 is clear and actionable
- [ ] Active workers listed with scopes
- [ ] Progress percentages calculated
- [ ] Resume checklist present
- [ ] Phase plan exists
- [ ] Acceptance criteria defined
- [ ] Tests status shown
```

---

## Recovery Scenarios

### Scenario 1: Lead Agent Replaced

**Problem:** Current lead agent unavailable, new lead assigned

**Recovery:**

1. New lead reads STATUS.md (10 min)
2. New lead reads DECISIONS.md recent entries (5 min)
3. New lead runs smoke tests (2 min)
4. New lead picks next P0 from TODO
5. New lead continues work

**Total time:** <20 minutes
**Data loss:** None (all in canonical files)

---

### Scenario 2: Context Window Full

**Problem:** Agent approaching context limit

**Recovery:**

1. Agent updates STATUS.md with current state
2. Agent logs recent decisions in DECISIONS.md
3. Agent commits updates
4. Agent regenerates (new context window)
5. Agent reads canonical files
6. Agent resumes from current deliverable

**Total time:** <5 minutes
**Data loss:** None (persisted before regeneration)

---

### Scenario 3: Multi-Day Gap

**Problem:** No work for 1 week, resuming project

**Recovery:**

1. Agent reads STATUS.md (refreshes current state)
2. Agent reads DECISIONS.md (last 7 days of decisions)
3. Agent checks .taskers/runs/ (any stale workers)
4. Agent runs smoke tests (verify nothing broken)
5. Agent picks next P0
6. Agent continues work

**Total time:** <15 minutes
**Data loss:** None (all preserved in files)

---

### Scenario 4: Worker Outputs Lost

**Problem:** .taskers/ directory deleted (git-ignored)

**Recovery:**

1. Worker outputs are in .taskers/runs/ (git-ignored, OK to lose)
2. Worker tickets can be regenerated from templates
3. STATUS.md shows which workers were active
4. If integration already done, no recovery needed
5. If integration not done, re-launch workers from templates

**Impact:** Low (outputs are temporary, integration is persisted)

---

## State File Maintenance

### STATUS.md Maintenance

**Keep fresh:**

- Update after every deliverable (mandatory)
- Update after phase transition (mandatory)
- Update when workers deployed/completed (mandatory)
- Update TODO when priorities change

**Keep concise:**

- Archive completed phases (move to docs/history/)
- Keep current phase + next phase only
- Prune old TODO items (move to backlog)

---

### DECISIONS.md Maintenance

**Keep append-only:**

- Never delete entries
- Never edit past entries (except typos)
- Add new entries at top (reverse chronological)
- Use "Supersedes" to mark replacements

**When to archive:**

- If >100 decisions, move old entries to docs/decisions/YYYY.md
- Keep recent 50 decisions in main file
- Link to archives in header

---

### AGENTS.md Maintenance

**Keep stable:**

- Rarely changes (process invariants)
- Version bumps when changing orchestration rules
- Document changes in DECISIONS.md when updated

---

## Example: Complete State Persistence

### Initial Setup

```bash
# Create canonical files
touch STATUS.md DECISIONS.md AGENTS.md

# Initialize STATUS.md
cat > STATUS.md <<EOF
# Project Status

**Last Updated:** 2026-02-16 09:00
**Lead Agent:** Agent-ABC123
**Phase:** Phase 0 - Foundation
**Milestone:** Foundation Complete (0% complete)

## Resume Checklist
1. Read STATUS.md
2. Read DECISIONS.md
3. Run smoke tests
4. Pick next P0
5. Continue work

## TODO
### P0
- [ ] Create Makefile
- [ ] Setup test framework

EOF

# Commit
git add STATUS.md DECISIONS.md AGENTS.md
git commit -m "Initialize canonical state files"
```

---

### After Deliverable

```bash
# Update STATUS.md (mark deliverable complete)
# Update DECISIONS.md (log decision)
# Commit

git add STATUS.md DECISIONS.md
git commit -m "Deliverable complete: Makefile"
```

---

### Before Handoff

```bash
# Generate status report
# Verify STATUS.md has resume checklist
# Verify next P0 is clear
# Commit any uncommitted changes
# Handoff ready
```

---

### New Lead Resumes

```bash
# Read canonical files
cat STATUS.md         # Current state
tail -20 DECISIONS.md # Recent decisions
cat AGENTS.md         # Process rules

# Verify state
make smoke-test
git status

# Continue
# Pick next P0 from STATUS.md TODO
# Start work
```

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo STATUS.md, DECISIONS.md, AGENTS.md patterns
**Last Updated:** 2026-02-16

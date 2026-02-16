# Status Report Protocol

**Purpose:** Generate transfer-safe status reports for handoff and visibility
**Enforces:** Fixed format, objective data, resume-ready structure

---

## Report Purpose

**Status report must enable:**

1. **User visibility** - Quick understanding of project state
2. **Lead handoff** - New lead can resume in <15 minutes
3. **Milestone tracking** - Progress measurement
4. **Blocker identification** - What's preventing progress
5. **Decision support** - What needs approval

**Critical requirement:** Report must be self-contained and actionable.

---

## Fixed 7-Section Format

**Every status report has exactly these sections in this order:**

1. Current State
2. Progress
3. Active Work
4. Recent Completions
5. Next Steps
6. Blockers (if any)
7. Approval Requests (if any)

**Do not add, remove, or reorder sections.**

---

## Section 1: Current State

**Purpose:** Snapshot of where project is right now

**Format:**

```markdown
## Current State

**Phase:** Phase N - [Phase Name]
**Milestone:** [Milestone Name] ([X]% complete)
**Deliverable:** [Current deliverable name] (IN PROGRESS / NEXT / COMPLETE)
**Overall Progress:** [X]% ([M]/[N] milestones complete)
```

**Example:**

```markdown
## Current State

**Phase:** Phase 2 - MVP Implementation
**Milestone:** MVP Functional (65% complete)
**Deliverable:** Integration Tests (IN PROGRESS)
**Overall Progress:** 40% (2/5 milestones complete)
```

**Requirements:**

- All percentages calculated from objective data
- Phase and milestone from STATUS.md
- Current deliverable is what lead is working on NOW

---

## Section 2: Progress

**Purpose:** Detailed breakdown of completion metrics

**Format:**

```markdown
## Progress

**Milestones:**
- [x] Foundation Complete (Phase 0) ✓
- [x] Authentication Complete (Phase 1) ✓
- [ ] MVP Functional (Phase 2) - 65%
- [ ] Enhanced Features (Phase 3) - 0%
- [ ] v1 Release (Phase 4) - 0%

**Current Phase Deliverables:**
- [x] Core API implementation ✓
- [x] Business logic ✓
- [ ] Integration tests (IN PROGRESS)
- [ ] Performance tuning (NEXT)

**Test Status:**
- Unit: 147/147 passing (100%)
- Integration: 28/32 passing (87%)
- Smoke: 3/5 passing (60%)
- Overall: 178/184 (96.7%)
```

**Requirements:**

- List ALL milestones with completion status
- Show current phase deliverables
- Include test metrics (exact counts, not "most")
- Calculate percentages from real data

**Progress calculation:**

```
Overall = (Completed Milestones / Total Milestones) * 100
Phase = (Completed Deliverables / Total Deliverables) * 100
Tests = (Passing Tests / Total Tests) * 100
```

---

## Section 3: Active Work

**Purpose:** What is happening right now

**Format:**

```markdown
## Active Work

**Lead:**
- Implementing integration test suite (internal/tests/integration/)
- Current focus: API endpoint tests

**Workers:**
- Codex-Worker-1: Writing unit tests for planner module
  - Scope: internal/planner/*_test.go
  - Status: 60% complete
  - Output: .taskers/runs/20260216_142834/Codex-Worker-1.txt

- Claude-Worker-2: Performance analysis for governor
  - Scope: internal/governor/ analysis
  - Status: COMPLETE (awaiting integration)
  - Output: .taskers/runs/20260216_142834/Claude-Worker-2.txt

**Next P0:** Complete integration tests, then performance tuning
```

**Requirements:**

- State what lead is actively coding
- List ALL active workers
- Include worker scope and status
- Identify next P0 item clearly

---

## Section 4: Recent Completions

**Purpose:** What was accomplished since last report

**Format:**

```markdown
## Recent Completions

**Since last report (2026-02-15):**

1. ✓ Deliverable: Business Logic
   - Implemented core algorithm in internal/core/
   - All unit tests passing (42/42)
   - Logged in DECISIONS.md (2026-02-15)

2. ✓ Deliverable: API Endpoint Refactoring
   - Unified error handling across endpoints
   - Integration tests updated
   - Performance improved (P95: 320ms → 180ms)

3. ✓ Worker Integration: Codex-Worker-3 proposals
   - Reviewed authentication refactoring proposal
   - Integrated 80% of suggestions
   - Rejected 20% due to scope concerns

**Commits:** 7 commits since last report
**Tests Added:** 23 new tests
**Documentation:** API.md updated with new endpoints
```

**Requirements:**

- List deliverables completed
- Include worker integrations
- Show metrics (commits, tests, etc.)
- Date last report for context

---

## Section 5: Next Steps

**Purpose:** What will happen next (prioritized)

**Format:**

```markdown
## Next Steps

**Immediate (Today):**
1. Complete integration test suite
   - Finish API endpoint tests (3 remaining)
   - Run full suite and verify 100% passing
   - Update STATUS.md

**This Phase (Next 2-3 days):**
2. Performance tuning deliverable
   - Profile critical paths
   - Optimize governor token issuance
   - Target: P95 <150ms (currently 180ms)

3. Integration test fixes
   - Debug 4 failing integration tests
   - Fix root cause in planner routing

**Next Phase (Phase 3):**
4. Enhanced features implementation
   - Waiting for Phase 2 approval
   - Tickets prepared in .taskers/tickets/

**Approval Gates:**
- Phase 2 acceptance (after performance tuning)
```

**Requirements:**

- Prioritize P0, P1, P2
- Group by timeframe (immediate, this phase, next phase)
- Note dependencies
- Flag approval gates

---

## Section 6: Blockers

**Purpose:** What is preventing progress (if anything)

**Format:**

```markdown
## Blockers

**None currently.**
```

OR

```markdown
## Blockers

1. **Integration Test Failures (High Priority)**
   - 4/32 integration tests failing in planner module
   - Root cause: Router heuristic edge case
   - Impact: Cannot advance to performance tuning
   - Mitigation: Debugging now, fix expected today

2. **External Dependency (Medium Priority)**
   - OAuth provider sandbox intermittently unavailable
   - Impact: Cannot run full auth integration tests
   - Mitigation: Using mock provider for now
   - Resolution: Waiting for provider support ticket #12345

3. **Approval Pending (Low Priority)**
   - Phase 2 → Phase 3 transition requires user approval
   - Impact: Cannot deploy Phase 3 workers yet
   - Next: Will request approval after performance tuning
```

**Requirements:**

- List each blocker separately
- Include priority (High/Medium/Low)
- State impact clearly
- Provide mitigation or resolution plan
- If no blockers, explicitly state "None currently"

---

## Section 7: Approval Requests

**Purpose:** What needs user decision

**Format:**

```markdown
## Approval Requests

**None pending.**
```

OR

```markdown
## Approval Requests

1. **Phase 2 Acceptance**
   - Request: Approve Phase 2 completion and advance to Phase 3
   - Reason: All acceptance criteria met
   - Evidence:
     - All deliverables complete (4/4)
     - Tests passing (184/184, 100%)
     - Performance within SLA (P95: 145ms < 150ms target)
   - Next: Deploy Phase 3 workers upon approval

2. **Architecture Decision: Caching Strategy**
   - Request: Approve Redis for caching vs in-memory
   - Reason: In-memory insufficient for multi-instance deployment
   - Alternatives:
     - Redis (recommended): Centralized, persistent
     - Memcached: Faster but no persistence
     - In-memory: Simple but single-instance only
   - Impact: Affects Phase 3 deliverable scope
   - Decision needed by: 2026-02-18 (Phase 3 start)
```

**Requirements:**

- Each request separately numbered
- Clear ask ("approve X")
- Provide evidence/rationale
- State alternatives considered
- Note urgency if time-sensitive
- If no approvals needed, state "None pending"

---

## Status Report Template

```markdown
# Project Status Report

**Generated:** [YYYY-MM-DD HH:MM]
**Report For:** [Project Name]
**Lead Agent:** [Agent ID or name]

---

## Current State

**Phase:** Phase N - [Phase Name]
**Milestone:** [Milestone Name] ([X]% complete)
**Deliverable:** [Current deliverable] (STATUS)
**Overall Progress:** [X]% ([M]/[N] milestones complete)

---

## Progress

**Milestones:**
- [x] Milestone 1 ✓
- [ ] Milestone 2 - [X]%
- [ ] Milestone 3 - 0%

**Current Phase Deliverables:**
- [x] Deliverable A ✓
- [ ] Deliverable B (IN PROGRESS)
- [ ] Deliverable C (NEXT)

**Test Status:**
- Unit: X/X passing (100%)
- Integration: X/X passing (100%)
- Smoke: X/X passing (100%)
- Overall: X/X (100%)

---

## Active Work

**Lead:**
- [Current focus]

**Workers:**
- Worker-1: [Task] (Status)
- Worker-2: [Task] (Status)

**Next P0:** [Next priority item]

---

## Recent Completions

**Since last report ([DATE]):**

1. ✓ Deliverable: [Name]
   - [Details]

2. ✓ Integration: [Worker proposals]
   - [Details]

**Metrics:**
- Commits: N
- Tests Added: N
- Documentation: [Updates]

---

## Next Steps

**Immediate:**
1. [Next action]

**This Phase:**
2. [Upcoming work]

**Next Phase:**
3. [Future work]

---

## Blockers

**None currently.**

OR

1. **Blocker Name (Priority)**
   - Root cause: [Description]
   - Impact: [Effect on progress]
   - Mitigation: [How addressing]

---

## Approval Requests

**None pending.**

OR

1. **Request Name**
   - Request: [Clear ask]
   - Evidence: [Supporting data]
   - Decision needed by: [Date]

---

**Report End**
```

---

## Report Triggers

**Generate status report when:**

1. User requests via `/status` command
2. Milestone completed
3. Phase completed
4. Major blocker encountered
5. Approval needed
6. Lead handoff imminent
7. Weekly update (for long projects)

**Minimum frequency:** Once per phase
**Maximum frequency:** On demand

---

## Transfer-Safe Requirements

**Report must enable new lead to:**

1. Understand current state in <5 minutes
2. Identify next action immediately
3. Know what workers are active
4. See recent progress
5. Understand blockers
6. Resume work without asking questions

**Test:** Could a fresh lead read this report and continue work?

---

## Calculation Rules

### Progress Percentages

**Overall project:**

```
Overall = (Completed Milestones / Total Milestones) * 100
```

**Current milestone:**

```
Milestone = (Met Acceptance Criteria / Total Criteria) * 100
```

**Current phase:**

```
Phase = (Completed Deliverables / Total Deliverables) * 100
```

**Test pass rate:**

```
Tests = (Passing Tests / Total Tests) * 100
```

**Always round to whole numbers.**

---

### Completion Status

**Deliverable status:**

- `COMPLETE` - All criteria met, integrated, tests passing
- `IN PROGRESS` - Currently being worked on
- `NEXT` - Queued for immediate work
- `PLANNED` - Scheduled for later
- `BLOCKED` - Cannot proceed due to blocker

**Milestone status:**

- `COMPLETE` (with ✓) - All acceptance criteria met, approved
- `IN PROGRESS` (with %) - Some criteria met, work ongoing
- `PLANNED` (0%) - Not started yet
- `BLOCKED` - Cannot proceed

---

## Handoff Protocol

**When generating report for handoff:**

1. Include full context (no assumptions)
2. List ALL active workers
3. Identify exact next action
4. Note any in-flight decisions
5. Provide resume checklist

**Handoff section (add to report):**

```markdown
## Resume Checklist for New Lead

1. Read STATUS.md (project state)
2. Read DECISIONS.md (recent entries, last 7 days)
3. Check .taskers/runs/ (active workers)
4. Run smoke tests (verify current state)
5. Pick next P0: [Exact next action]
6. Continue from [Current deliverable]
```

**Target:** New lead operational in <15 minutes from reading report.

---

## Example: Complete Status Report

```markdown
# Project Status Report

**Generated:** 2026-02-16 14:30
**Report For:** KROV CLI Tool
**Lead Agent:** Agent-A79B837

---

## Current State

**Phase:** Phase 2 - MVP Implementation
**Milestone:** MVP Functional (65% complete)
**Deliverable:** Integration Tests (IN PROGRESS)
**Overall Progress:** 40% (2/5 milestones complete)

---

## Progress

**Milestones:**
- [x] Foundation Complete (Phase 0) ✓
- [x] Authentication Complete (Phase 1) ✓
- [ ] MVP Functional (Phase 2) - 65%
- [ ] Enhanced Features (Phase 3) - 0%
- [ ] v1 Release (Phase 4) - 0%

**Current Phase Deliverables:**
- [x] Core API implementation ✓
- [x] Business logic ✓
- [ ] Integration tests (IN PROGRESS)
- [ ] Performance tuning (NEXT)

**Test Status:**
- Unit: 147/147 passing (100%)
- Integration: 28/32 passing (87%)
- Smoke: 3/5 passing (60%)
- Overall: 178/184 (96.7%)

---

## Active Work

**Lead:**
- Implementing integration test suite
- Current focus: API endpoint tests (3/8 complete)
- Files: internal/tests/integration/api_test.go

**Workers:**
- Codex-Worker-1: Planner module unit tests
  - Scope: internal/planner/*_test.go
  - Status: 80% complete
  - Output: .taskers/runs/20260216_142834/Codex-Worker-1.txt

**Next P0:** Complete integration tests, debug 4 failures

---

## Recent Completions

**Since last report (2026-02-15):**

1. ✓ Deliverable: Business Logic
   - Core algorithm in internal/core/
   - Unit tests: 42/42 passing
   - Logged: DECISIONS.md (2026-02-15)

2. ✓ Deliverable: API Refactoring
   - Unified error handling
   - Performance: P95 320ms → 180ms

**Metrics:**
- Commits: 7
- Tests Added: 23
- Documentation: API.md updated

---

## Next Steps

**Immediate:**
1. Complete integration tests (3 remaining)
2. Debug 4 failing tests (planner module)
3. Run full suite, verify 100% passing

**This Phase:**
4. Performance tuning deliverable
   - Target: P95 <150ms (current: 180ms)
5. Smoke test fixes (2 scenarios)

**Next Phase:**
6. Phase 3 workers deployment (pending approval)

---

## Blockers

1. **Integration Test Failures (High Priority)**
   - Root cause: Router heuristic edge case
   - Impact: Delays performance tuning
   - Mitigation: Debugging now, fix today

---

## Approval Requests

1. **Phase 2 Acceptance**
   - Request: Approve Phase 2 completion
   - Evidence: 3/4 deliverables done, 96.7% tests passing
   - Decision needed by: 2026-02-17 (before Phase 3)

---

**Report End**
```

---

## Anti-Patterns

**Avoid these:**

❌ Vague status ("making progress")
❌ Missing sections
❌ Subjective percentages (guessing)
❌ No next steps
❌ Hiding blockers
❌ Unclear approval requests
❌ No test metrics

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo AGENTS.md status protocol
**Last Updated:** 2026-02-16

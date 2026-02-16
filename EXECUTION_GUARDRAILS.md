# Execution Guardrails

**Purpose:** Prevent common failure modes in AI-led project execution
**Enforces:** Safety constraints, anti-patterns, quality gates

---

## Core Guardrails

### Guardrail 1: No Code Before Plan

**Rule:** Never write code before granular plan exists

**Enforcement:**

```markdown
BEFORE writing any code:
- [ ] Blueprint exists and is complete
- [ ] Granular plan exists in STATUS.md
- [ ] Phases defined with acceptance criteria
- [ ] Deliverables identified
- [ ] User approved plan

ONLY THEN: Begin implementation
```

**Violation symptoms:**

- No STATUS.md phase plan
- Unclear deliverables
- No acceptance criteria
- User hasn't approved scope

**Recovery:**

1. Stop coding immediately
2. Document current work (WIP commit)
3. Create granular plan
4. Get user approval
5. Resume coding

---

### Guardrail 2: No Phase Skip

**Rule:** Must complete Phase N before starting Phase N+1

**Enforcement:**

```markdown
BEFORE advancing to next phase:
- [ ] All deliverables in current phase complete
- [ ] All acceptance criteria met
- [ ] Tests passing (100%)
- [ ] Documentation updated
- [ ] User approval obtained (if major milestone)

ONLY THEN: Advance to next phase
```

**Violation symptoms:**

- Incomplete deliverables in current phase
- Skipping to "more interesting" work
- Unmet acceptance criteria
- Tests failing

**Recovery:**

1. Return to incomplete phase
2. Complete all deliverables
3. Verify acceptance criteria
4. Get approval
5. Then advance

---

### Guardrail 3: Test Before Commit

**Rule:** Never commit code without passing tests

**Enforcement:**

```markdown
BEFORE every commit:
- [ ] Run full test suite
- [ ] All tests passing (100%)
- [ ] No test skips or ignores (unless documented)
- [ ] Coverage maintained or improved

ONLY THEN: Commit
```

**Violation symptoms:**

- Failing tests in CI
- "Will fix tests later" mentality
- Test failures ignored

**Recovery:**

1. Do not commit
2. Fix failing tests
3. Re-run test suite
4. Only commit when green

**Exception:** WIP commits (clearly marked, not for merge)

---

### Guardrail 4: Non-Overlapping Worker Scope

**Rule:** No two workers can modify same files

**Enforcement:**

```markdown
BEFORE launching workers:
- [ ] Each worker has explicit file scope
- [ ] No file appears in multiple worker tickets
- [ ] Feature boundaries non-overlapping
- [ ] Integration plan exists for lead

ONLY THEN: Launch workers
```

**Violation symptoms:**

- Two workers proposing changes to same file
- Merge conflicts in worker outputs
- Unclear integration approach

**Recovery:**

1. Halt overlapping workers
2. Revise ticket scopes
3. Re-launch with corrected boundaries

---

### Guardrail 5: Approval Gates Enforced

**Rule:** User approval required for major decisions

**Enforcement:**

```markdown
REQUIRE approval for:
- [ ] Initial execution plan
- [ ] Phase transitions (major milestones)
- [ ] Architecture changes (breaking, significant)
- [ ] Technology stack changes
- [ ] Scope changes

WAIT for explicit "yes" before proceeding
```

**Violation symptoms:**

- Advancing phases without approval
- Making breaking changes without consent
- Assuming user agreement

**Recovery:**

1. Stop execution
2. Document what was done
3. Request retroactive approval
4. Rollback if not approved

---

### Guardrail 6: Context Persistence

**Rule:** All state must persist in canonical files

**Enforcement:**

```markdown
AFTER any state change:
- [ ] STATUS.md updated
- [ ] DECISIONS.md logged (if architectural)
- [ ] Changes committed to git

IF NOT: State will be lost on context refresh
```

**Violation symptoms:**

- "I thought we decided X" (not in DECISIONS.md)
- Lost progress after agent restart
- New lead can't resume

**Recovery:**

1. Reconstruct state from git history
2. Update canonical files
3. Commit immediately

---

### Guardrail 7: Worker Read-Only Policy

**Rule:** Workers cannot commit, only lead integrates

**Enforcement:**

```markdown
WORKERS:
- [ ] Read-only repository access
- [ ] Output proposals to .taskers/runs/
- [ ] Never commit directly
- [ ] Never modify STATUS.md/DECISIONS.md

LEAD:
- [ ] Only agent with write access
- [ ] Reviews all worker proposals
- [ ] Makes integration decisions
- [ ] Commits integrated work
```

**Violation symptoms:**

- Workers committing code
- Workers modifying canonical files
- Unreviewed worker changes in repo

**Recovery:**

1. Revert worker commits
2. Review changes manually
3. Lead re-commits after review

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Scope Creep

**Problem:** Adding features not in plan or blueprint

**Symptoms:**

- "While I'm here, let me also..."
- Features not in phase plan
- Deliverables expanding mid-execution

**Prevention:**

- Stick to plan rigidly
- If new work needed, revise plan first
- Get approval for scope changes

**Example:**

❌ BAD: "Implementing auth provider, also added rate limiting"
✅ GOOD: "Implementing auth provider per deliverable spec"

---

### Anti-Pattern 2: AI Chaos (Uncontrolled Workers)

**Problem:** Launching workers without scoped tickets

**Symptoms:**

- Workers proposing conflicting changes
- Unclear integration path
- Overlapping work
- "Swarm" behavior

**Prevention:**

- Never launch workers without explicit tickets
- Always define scope boundaries
- Verify non-overlapping before launch
- Limit pool size (15 max by default)

**Example:**

❌ BAD: "Launch 20 workers to speed up work"
✅ GOOD: "Launch 3 workers with explicit, non-overlapping scopes"

---

### Anti-Pattern 3: Documentation Drift

**Problem:** Code changes but docs don't update

**Symptoms:**

- README shows old features
- API docs out of sync with endpoints
- STATUS.md shows stale state
- DECISIONS.md missing recent decisions

**Prevention:**

- Update docs in same commit as code
- Use pre-commit checklist
- Verify doc sync before handoff

**Example:**

❌ BAD: Commit code only, docs "TODO"
✅ GOOD: Commit code + STATUS.md + DECISIONS.md + API docs together

---

### Anti-Pattern 4: Test Neglect

**Problem:** Committing code without tests

**Symptoms:**

- Coverage dropping
- No tests for new features
- "Will add tests later"
- Integration tests missing

**Prevention:**

- Tests are part of deliverable (not afterthought)
- Test before commit (always)
- Coverage gate (>80% target)

**Example:**

❌ BAD: Implement feature, commit, "add tests later"
✅ GOOD: Implement feature + tests, verify passing, then commit

---

### Anti-Pattern 5: Premature Optimization

**Problem:** Optimizing before baseline functionality works

**Symptoms:**

- Focusing on performance before correctness
- Complex architecture for simple problem
- Over-engineering

**Prevention:**

- Implement correct solution first
- Measure performance second
- Optimize only if needed (based on metrics)

**Example:**

❌ BAD: Phase 0, implementing distributed caching
✅ GOOD: Phase 0 foundation, Phase 3 performance optimization

---

### Anti-Pattern 6: Silent Failures

**Problem:** Ignoring test failures or blockers

**Symptoms:**

- CI red but committing anyway
- Integration tests failing, advancing phase
- Blockers not documented

**Prevention:**

- All tests must pass before commit
- Document blockers immediately
- Never advance with failing criteria

**Example:**

❌ BAD: "4 tests failing, but most work, so phase complete"
✅ GOOD: "4 tests failing, blocked on bug fix, cannot advance"

---

### Anti-Pattern 7: Handoff Unpreparedness

**Problem:** Lead handoff without preparation

**Symptoms:**

- Uncommitted changes
- Stale STATUS.md
- No next P0 identified
- New lead can't resume

**Prevention:**

- Always prepare for handoff
- Update canonical files
- Commit all work
- Clear next action

**Example:**

❌ BAD: "Context lost, new lead starts over"
✅ GOOD: "New lead reads STATUS.md, resumes in 10 minutes"

---

## Quality Gates

### Gate 1: Plan Approval

**When:** After plan generation, before implementation

**Criteria:**

- [ ] Blueprint complete
- [ ] Phases defined with acceptance criteria
- [ ] Deliverables identified
- [ ] User reviewed and approved

**If fails:** Revise plan until approved

---

### Gate 2: Deliverable Completion

**When:** After deliverable work, before marking complete

**Criteria:**

- [ ] Implementation complete per spec
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] STATUS.md updated

**If fails:** Continue work until criteria met

---

### Gate 3: Phase Acceptance

**When:** After all deliverables in phase, before advancing

**Criteria:**

- [ ] All deliverables complete
- [ ] All acceptance criteria met
- [ ] Full test suite passing
- [ ] User approval obtained (if major)

**If fails:** Remediate until all criteria met

---

### Gate 4: Pre-Commit

**When:** Before every commit

**Criteria:**

- [ ] Tests passing (100%)
- [ ] STATUS.md updated (if state changed)
- [ ] DECISIONS.md logged (if architectural)
- [ ] Commit message clear

**If fails:** Do not commit, fix issues first

---

### Gate 5: Pre-Handoff

**When:** Before lead agent handoff

**Criteria:**

- [ ] All changes committed
- [ ] STATUS.md current
- [ ] DECISIONS.md current
- [ ] Tests passing
- [ ] Next P0 identified

**If fails:** Prepare properly before handoff

---

## Safety Mechanisms

### Mechanism 1: Worker Pool Limit

**Purpose:** Prevent swarm behavior

**Limit:** 15 workers maximum (configurable)

- Codex: 5 max
- Claude: 5 max
- Gemini: 5 max (optional, disabled by default)

**Enforcement:**

- Scripts enforce limit
- User override available (dangerous mode)
- Lead must justify >15 workers

---

### Mechanism 2: Read-Only Workers

**Purpose:** Prevent unreviewed changes

**Enforcement:**

- Workers have no commit access
- Output to .taskers/runs/ only
- Lead reviews all proposals
- Lead makes integration decisions

---

### Mechanism 3: Resume Checklist

**Purpose:** Enable handoff in <15 minutes

**Enforcement:**

- Always present in STATUS.md
- Standard 7-step checklist
- Tested with every handoff
- Updated if handoff fails

---

### Mechanism 4: Append-Only Decision Log

**Purpose:** Preserve architectural history

**Enforcement:**

- DECISIONS.md is append-only
- Never delete entries
- Use "Supersedes" for changes
- Timestamp all entries

---

### Mechanism 5: Test Gates

**Purpose:** Prevent broken code in repo

**Enforcement:**

- Pre-commit: tests must pass
- Pre-phase-advance: full suite must pass
- CI gates (if configured)
- Coverage minimum (>80% target)

---

## Violation Recovery

### If Plan Skipped

**Violation:** Started coding without granular plan

**Recovery:**

1. Stop coding
2. Commit WIP (if substantial work done)
3. Create plan in STATUS.md
4. Get user approval
5. Resume from plan

---

### If Tests Failing

**Violation:** Committed with failing tests

**Recovery:**

1. Revert commit (if just committed)
2. Fix tests immediately
3. Re-run test suite
4. Commit fix

---

### If Scope Overlap

**Violation:** Launched workers with overlapping scope

**Recovery:**

1. Halt all overlapping workers
2. Review worker tickets
3. Revise scopes to non-overlapping
4. Re-launch with corrected scopes

---

### If Documentation Drift

**Violation:** Code and docs out of sync

**Recovery:**

1. Review recent code changes
2. Update all affected docs (README, API, STATUS.md)
3. Commit doc updates
4. Establish doc update discipline

---

### If Approval Skipped

**Violation:** Advanced phase without approval

**Recovery:**

1. Stop work
2. Document current state
3. Request retroactive approval
4. If not approved, rollback and remediate

---

## Checklist for Guardrail Compliance

### Daily Startup

```markdown
- [ ] Read STATUS.md (current state)
- [ ] Verify on correct phase
- [ ] Check active workers (no overlaps)
- [ ] Confirm next P0 is clear
```

---

### Before Worker Launch

```markdown
- [ ] Tickets have explicit scope
- [ ] No file overlaps between workers
- [ ] Pool size within limits (15 max)
- [ ] Integration plan exists
```

---

### Before Commit

```markdown
- [ ] Tests passing (100%)
- [ ] STATUS.md updated
- [ ] DECISIONS.md logged (if needed)
- [ ] Documentation synced
- [ ] Commit message clear
```

---

### Before Phase Advance

```markdown
- [ ] All deliverables complete
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] User approval obtained
```

---

### Before Handoff

```markdown
- [ ] All work committed
- [ ] STATUS.md current
- [ ] DECISIONS.md current
- [ ] Tests passing
- [ ] Next P0 clear
- [ ] Resume checklist present
```

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo AGENTS.md, execution patterns, safety mechanisms
**Last Updated:** 2026-02-16

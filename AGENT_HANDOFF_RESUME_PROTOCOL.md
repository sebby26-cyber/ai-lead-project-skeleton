# Agent Handoff Resume Protocol

**Purpose:** Enable lead agent replacement in <15 minutes
**Enforces:** Standard resume procedure, zero knowledge loss

---

## Protocol Overview

**Goal:** New lead agent can resume project execution without:

- Re-discovering project state
- Asking user questions
- Repeating completed work
- Breaking context or losing decisions

**Target:** <15 minute handoff time
**Mechanism:** Canonical state files + resume checklist

---

## Handoff Trigger Scenarios

### Scenario 1: Planned Handoff

**Context:** Current lead completing session, new lead taking over

**Trigger:**
- Current lead finishing work
- End of work session
- User requests lead change

**Preparation required:** Yes (current lead prepares)

---

### Scenario 2: Emergency Handoff

**Context:** Current lead unavailable (crash, context loss, etc.)

**Trigger:**
- Agent error or failure
- Context window exhausted
- Unexpected termination

**Preparation required:** No (rely on last committed state)

---

### Scenario 3: Multi-Day Resume

**Context:** Project paused for extended period

**Trigger:**
- Days/weeks gap between sessions
- User returning to project

**Preparation required:** No (canonical files persist)

---

## Outgoing Lead Responsibilities

### Preparation Checklist

**Before handoff, current lead must:**

```markdown
## Handoff Preparation

- [ ] All work committed (no uncommitted changes)
- [ ] STATUS.md updated with current state
- [ ] DECISIONS.md logged (recent architectural decisions)
- [ ] Tests passing (run smoke tests)
- [ ] Worker status documented (active workers listed)
- [ ] Next P0 identified clearly in TODO
- [ ] Resume checklist present in STATUS.md
- [ ] Status report generated (optional but recommended)
```

**Time required:** 10 minutes

---

### STATUS.md Update

**Ensure STATUS.md contains:**

1. **Current state:**
   - Phase and milestone
   - Active deliverable
   - Progress percentages

2. **Active work:**
   - What lead was working on
   - Worker roster (who's active)
   - In-flight tasks

3. **Next steps:**
   - Prioritized TODO (P0, P1, P2)
   - Clear next action
   - Dependencies or blockers

4. **Resume checklist:**
   - Standard 7-step checklist
   - Any handoff-specific notes

---

### DECISIONS.md Update

**Log any recent decisions:**

```markdown
## 2026-02-16: [Decision Title]

**Context:** [Why decision was made]
**Decision:** [What was decided]
**Alternatives:** [What was rejected]
**Consequences:** [Impact on project]
```

**Include:**

- Last 7 days of architectural decisions
- Any in-flight decisions (not yet finalized)
- Phase transition decisions

---

### Worker Management

**Handle active workers:**

1. **If workers running:**
   - Wait for completion OR
   - Document current status in STATUS.md
   - Note which workers are mid-execution

2. **If workers complete:**
   - Integrate outputs OR
   - Document integration decision in STATUS.md
   - Move to "Recent Completions" section

3. **If workers blocked:**
   - Document blocker in STATUS.md
   - Provide context for resolution

---

### Commit Final State

**Final commit before handoff:**

```bash
# Ensure STATUS.md and DECISIONS.md current
git add STATUS.md DECISIONS.md
git commit -m "Handoff preparation: [current deliverable]

- Current phase: Phase N
- Active deliverable: [name]
- Next P0: [action]
- Tests: [X]/[Y] passing

Ready for lead handoff."

# Verify clean state
git status  # Should show no uncommitted changes
```

---

### Optional: Generate Status Report

**If time permits (recommended):**

1. Generate full status report (7-section format)
2. Save to docs/status/YYYY-MM-DD.md
3. Include in handoff
4. Provides comprehensive snapshot

---

## Incoming Lead Responsibilities

### Resume Checklist (Standard)

**New lead executes this checklist in order:**

```markdown
## Resume Checklist

1. **Read STATUS.md** (5 minutes)
   - Current phase and deliverable
   - Active workers
   - Next P0 item
   - Progress metrics

2. **Read DECISIONS.md** (3 minutes)
   - Recent entries (last 7 days)
   - Understand recent architectural decisions
   - Note any in-flight decisions

3. **Check active workers** (2 minutes)
   - List .taskers/runs/ directory
   - Read recent worker outputs
   - Determine if integration needed

4. **Run smoke tests** (3 minutes)
   - Verify current state is functional
   - Ensure tests pass as documented
   - Identify any regressions

5. **Confirm git status** (1 minute)
   - Check for uncommitted changes
   - Verify on correct branch
   - Ensure remote sync (if applicable)

6. **Pick next P0** (1 minute)
   - Read TODO section in STATUS.md
   - Identify top priority item
   - Understand dependencies

7. **Continue execution** (start work)
   - Begin working on next P0
   - Update STATUS.md after changes
   - Run tests before commits
```

**Total time:** <15 minutes
**Output:** Lead fully operational, ready to continue work

---

### Step-by-Step Execution

#### Step 1: Read STATUS.md

**What to extract:**

```markdown
**Current state:**
- Phase: [Which phase are we in?]
- Milestone: [Current milestone and % complete]
- Deliverable: [What deliverable is active?]

**Active work:**
- Lead: [What was previous lead working on?]
- Workers: [Which workers are active?]

**Next steps:**
- P0: [What is the next critical action?]
- Blockers: [Anything preventing progress?]

**Progress:**
- Overall: [X]%
- Phase: [Y]%
- Tests: [Z]/[W] passing
```

**Time:** 5 minutes

**Questions answered:**

- Where is the project right now?
- What was being worked on?
- What needs to happen next?
- Are there any blockers?

---

#### Step 2: Read DECISIONS.md

**What to extract:**

```markdown
**Recent decisions (last 7 days):**
1. Decision: [Topic]
   - What was decided
   - Why (context)
   - Alternatives rejected

2. Decision: [Topic]
   - What was decided
   - Why (context)
   - Alternatives rejected

[... up to ~10 most recent ...]
```

**Time:** 3 minutes

**Questions answered:**

- What architectural decisions were made recently?
- Why were they made?
- What alternatives were considered?

**Note:** Don't read entire log, focus on recent entries (top 10-20)

---

#### Step 3: Check Active Workers

**Commands:**

```bash
# Find latest run directory
LATEST_RUN=$(ls -t .taskers/runs/ | head -1)

# List worker outputs
ls -la .taskers/runs/$LATEST_RUN/

# Read worker outputs
cat .taskers/runs/$LATEST_RUN/Codex-Worker-1.txt
cat .taskers/runs/$LATEST_RUN/Claude-Worker-2.txt
```

**What to determine:**

- Are workers still running?
- Have workers completed?
- Do outputs need integration?
- Are workers blocked?

**Action:**

- If complete: Review proposals, make integration decision
- If running: Monitor status, wait for completion
- If blocked: Read blocker, determine resolution

**Time:** 2 minutes

---

#### Step 4: Run Smoke Tests

**Commands:**

```bash
# Run smoke test suite
make smoke-test

# OR specific smoke tests
./scripts/smoke_test.sh

# Verify output
echo $?  # Should be 0 (success)
```

**Expected:**

- Tests pass as documented in STATUS.md
- No regressions from last session
- System functional

**If tests fail:**

- Check if blocker documented in STATUS.md
- Determine if failure is expected
- Debug if unexpected regression

**Time:** 3 minutes

---

#### Step 5: Confirm Git Status

**Commands:**

```bash
# Check git status
git status

# Verify on correct branch
git branch --show-current

# Check for uncommitted changes
git diff

# Check remote sync (if applicable)
git fetch
git status
```

**Expected:**

- No uncommitted changes (clean working tree)
- On correct branch (usually main/master)
- Synced with remote (if applicable)

**If issues:**

- Uncommitted changes: Review, commit if valid, or stash
- Wrong branch: Checkout correct branch
- Out of sync: Pull remote changes

**Time:** 1 minute

---

#### Step 6: Pick Next P0

**From STATUS.md TODO section:**

```markdown
## TODO (Prioritized)

### P0 (Critical)
- [ ] Complete integration tests (← THIS IS NEXT)
- [ ] Debug failing tests

### P1 (High Priority)
- [ ] Performance tuning
```

**Action:**

- Read top P0 item
- Understand scope and deliverable
- Check dependencies or blockers
- Prepare to start work

**Time:** 1 minute

---

#### Step 7: Continue Execution

**Start work:**

1. Begin working on identified P0
2. Follow normal execution workflow
3. Update STATUS.md after any change
4. Run tests before commits
5. Log decisions in DECISIONS.md

**Handoff complete.** Lead is now fully operational.

---

## Verification

### Handoff Quality Test

**Question for new lead:**

> "Can you continue work without asking the user any questions?"

**If YES:** Handoff succeeded
**If NO:** STATUS.md or DECISIONS.md incomplete

---

### Required Information

**New lead must know:**

✅ Current phase and milestone
✅ Active deliverable
✅ Next action (P0 item)
✅ Active workers (if any)
✅ Recent decisions (last 7 days)
✅ Test status
✅ Blockers (if any)

**If any missing:** Handoff preparation was incomplete

---

## Handoff Failure Modes

### Failure 1: Vague Next Action

**Problem:** STATUS.md TODO says "Continue work"

**Impact:** New lead doesn't know what to do

**Fix:** Current lead must specify exact next action

**Example:**

❌ BAD: "Continue work on tests"
✅ GOOD: "Complete integration tests (3 remaining: API endpoints, auth flow, error handling)"

---

### Failure 2: Uncommitted Changes

**Problem:** Outgoing lead left uncommitted work

**Impact:** New lead doesn't know if changes are valid

**Fix:** Current lead must commit before handoff

**Recovery:**

```bash
# New lead reviews uncommitted changes
git diff

# Decide: commit, stash, or discard
git add . && git commit -m "WIP: [description]"
# OR
git stash
```

---

### Failure 3: Missing Worker Context

**Problem:** STATUS.md says "Workers running" but no details

**Impact:** New lead doesn't know worker scopes or status

**Fix:** Current lead must document:

```markdown
## Active Workers

- Codex-Worker-1: Integration tests for planner module
  - Scope: internal/planner/*_test.go
  - Status: 60% complete (estimate)
  - Output: .taskers/runs/20260216_142834/Codex-Worker-1.txt
  - Next: Review output when complete
```

---

### Failure 4: Stale DECISIONS.md

**Problem:** No recent decision entries, but major changes made

**Impact:** New lead doesn't understand recent architecture changes

**Fix:** Current lead must log decisions before handoff

**Recovery:**

```bash
# New lead reviews recent commits
git log --oneline -10

# Infers decisions from commit messages
# Documents in DECISIONS.md retroactively
```

---

## Emergency Handoff (No Preparation)

**Scenario:** Current lead unavailable, no handoff preparation

**Recovery procedure:**

1. **Read STATUS.md** (may be stale)
   - Use last committed version
   - Understand last known state

2. **Review recent commits**
   ```bash
   git log --oneline -20
   git show HEAD
   ```
   - Determine what was worked on recently
   - Identify current deliverable

3. **Check for uncommitted changes**
   ```bash
   git status
   git diff
   ```
   - Review any uncommitted work
   - Decide: commit, stash, or discard

4. **Run tests**
   ```bash
   make test
   ```
   - Verify current state
   - Identify any breakage

5. **Reconstruct context**
   - Read DECISIONS.md (recent entries)
   - Read blueprint/plan documents
   - Infer next action from STATUS.md + commits

6. **Update STATUS.md**
   - Document current state (as reconstructed)
   - Set next P0 based on inference
   - Mark any uncertainty

7. **Continue work**
   - Proceed with best understanding
   - Ask user if critical ambiguities exist

**Time:** 20-30 minutes (longer than planned handoff)
**Risk:** May miss context without preparation

---

## Multi-Day Resume

**Scenario:** Project paused for days/weeks

**Resume procedure (same as standard handoff):**

1. Read STATUS.md (refresh context)
2. Read DECISIONS.md (last 7-14 days, depending on gap)
3. Check for stale workers (likely none)
4. Run smoke tests (verify nothing broken)
5. Check git status (ensure clean)
6. Pick next P0
7. Continue work

**Additional considerations:**

- Check for dependency updates (npm, go mod, etc.)
- Review any external changes (APIs, third-party libraries)
- Verify tests still pass after time gap

**Time:** <20 minutes

---

## Handoff Best Practices

### For Outgoing Lead

✅ **Always commit before handoff**
✅ **Update STATUS.md completely**
✅ **Log recent decisions**
✅ **Identify clear next P0**
✅ **Document worker status**
✅ **Run tests (ensure green)**
✅ **Generate status report (if time)**

❌ **Don't leave uncommitted changes**
❌ **Don't assume verbal context persists**
❌ **Don't skip decision logging**
❌ **Don't leave vague TODO items**

---

### For Incoming Lead

✅ **Follow resume checklist exactly**
✅ **Read canonical files first (not code)**
✅ **Verify with tests**
✅ **Update STATUS.md after any work**
✅ **Ask user only if critical ambiguity**

❌ **Don't skip resume checklist**
❌ **Don't assume prior knowledge**
❌ **Don't restart from scratch**
❌ **Don't ignore canonical files**

---

## Checklist Templates

### Outgoing Lead Handoff Checklist

```markdown
## Handoff Preparation Checklist

- [ ] All changes committed (git status clean)
- [ ] STATUS.md updated with current state
- [ ] DECISIONS.md logged (recent decisions)
- [ ] Active workers documented (status, scope, output)
- [ ] Next P0 identified and clear
- [ ] Tests passing (smoke tests run)
- [ ] Resume checklist present in STATUS.md
- [ ] Blockers documented (if any)
- [ ] Approval requests noted (if any)

**Handoff ready:** Yes / No
```

---

### Incoming Lead Resume Checklist

```markdown
## Resume Checklist

- [ ] Read STATUS.md (current state, next P0)
- [ ] Read DECISIONS.md (last 7 days)
- [ ] Check active workers (.taskers/runs/)
- [ ] Run smoke tests (verify state)
- [ ] Confirm git status (clean, correct branch)
- [ ] Identify next P0 (from STATUS.md TODO)
- [ ] Continue execution (start work)

**Resume complete:** Yes / No
**Time taken:** [X] minutes
```

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo STATUS.md resume checklist
**Last Updated:** 2026-02-16

# Project Execution Lifecycle

**Purpose:** Define the complete flow from concept to delivery
**Enforces:** Blueprint → Plan → Phase → Deliverable → Approval progression

---

## Lifecycle Overview

```
Concept/Blueprint
    ↓
Granular Plan Generation
    ↓
User Approval Gate
    ↓
Phase Execution (iterative)
    ↓
Deliverable Completion
    ↓
Phase Acceptance Gate
    ↓
Next Phase or Project Complete
```

**No shortcuts.** Each stage has specific outputs and approval gates.

---

## Stage 1: Blueprint Definition

**Input:** User requirements, vision document, or concept description

**Process:**

1. User creates `docs/blueprint/IMPLEMENTATION_INSTRUCTIONS.md`
2. Blueprint contains:
   - Project vision and goals
   - High-level architecture
   - Major features/capabilities
   - Success criteria
   - Non-functional requirements

**Output:** Authoritative blueprint document

**Lead agent actions:**

- Read and internalize blueprint
- Ask clarifying questions if ambiguous
- Do NOT proceed to planning until blueprint is clear

**Approval:** Blueprint must be explicit and complete before next stage

**Example blueprint structure:**

```markdown
# Project Implementation Blueprint

## Vision
[What we're building and why]

## Architecture
[High-level system design]

## Core Features
1. Feature A
2. Feature B
3. Feature C

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints
[Technical, resource, or timeline constraints]

## Non-Negotiables
[Hard requirements that cannot be compromised]
```

---

## Stage 2: Granular Plan Generation

**Input:** Approved blueprint

**Process:**

1. Lead reads blueprint completely
2. Lead breaks project into **phases**
3. Each phase broken into **deliverables**
4. Each deliverable broken into **tasks**
5. Tasks assigned to **workers** (if parallelizable)

**Output:** Granular execution plan in `STATUS.md`

**Plan requirements:**

- **Phases** must have acceptance criteria
- **Deliverables** must be verifiable
- **Tasks** must be scoped and bounded
- **Dependencies** must be explicit
- **Testing** must be defined per phase

**Lead agent actions:**

1. Analyze blueprint complexity
2. Identify natural phase boundaries
3. Define phase acceptance criteria
4. Break phases into deliverables
5. Estimate effort (optional)
6. Identify parallelization opportunities
7. Create worker ticket stubs
8. Document plan in `STATUS.md`

**Plan format:**

```markdown
# Phase Plan

## Phase 0: Foundation
**Goal:** Repository structure and workflow setup
**Acceptance Criteria:**
- [ ] Build system operational
- [ ] Test harness functional
- [ ] CI/CD pipeline configured

**Deliverables:**
1. Build system (Makefile, scripts)
2. Test framework
3. CI configuration

## Phase 1: Core Feature A
**Goal:** Implement Feature A from blueprint
**Acceptance Criteria:**
- [ ] API contract implemented
- [ ] Unit tests passing
- [ ] Integration tests passing

**Deliverables:**
1. API interface
2. Core logic
3. Test suite

[... more phases ...]
```

**Approval:** User must approve plan before any implementation begins

---

## Stage 3: User Approval Gate

**Trigger:** Lead completes granular plan

**Process:**

1. Lead presents plan to user
2. User reviews:
   - Phase breakdown
   - Acceptance criteria
   - Deliverables
   - Timeline estimate (if provided)
3. User either:
   - **Approves:** Proceed to execution
   - **Requests changes:** Revise plan
   - **Rejects:** Return to blueprint

**Approval format:**

- User explicitly says "approved" or "proceed"
- Lead logs approval in `DECISIONS.md`
- Plan frozen in `STATUS.md`

**Lead actions:**

- Do NOT begin implementation until explicit approval
- Answer user questions about plan
- Revise if requested
- Log approval decision

**Example approval log:**

```markdown
## 2026-02-16: Execution Plan Approved

**Context:** User reviewed Phase 0-5 execution plan
**Decision:** Approved to proceed with Phase 0
**Alternatives Considered:** None
**Consequences:** Begin foundation work
```

---

## Stage 4: Phase Execution

**Input:** Approved phase from plan

**Process:** Iterative deliverable completion

### Phase Startup

1. Lead reads phase acceptance criteria
2. Lead identifies first deliverable
3. Lead breaks deliverable into tasks
4. Lead generates worker tickets (if parallel work)
5. Lead updates `STATUS.md` with current phase

### Deliverable Execution Loop

**For each deliverable in phase:**

1. **Task decomposition** (if needed)
   - Identify parallelizable work
   - Create worker tickets
   - Define scope boundaries

2. **Worker deployment** (if parallel)
   - Launch workers via orchestration script
   - Monitor worker progress
   - Collect worker outputs

3. **Integration**
   - Review worker proposals
   - Make integration decisions
   - Implement changes
   - Resolve conflicts

4. **Testing**
   - Run unit tests
   - Run integration tests
   - Run smoke tests (if applicable)
   - Verify acceptance criteria

5. **Documentation**
   - Update `STATUS.md` (mark deliverable complete)
   - Log decisions in `DECISIONS.md`
   - Update README or API docs
   - Commit with clear message

6. **Next deliverable**
   - Move to next item in phase
   - Repeat until phase complete

### Phase Completion

1. Verify all deliverables complete
2. Run full test suite
3. Check all acceptance criteria met
4. Generate status report
5. Request user approval for phase (if major milestone)

**Lead maintains `STATUS.md` throughout:**

```markdown
## Current Phase: Phase 1 - Core Feature A

### Deliverables
- [x] API interface - COMPLETE
- [x] Core logic - COMPLETE
- [ ] Test suite - IN PROGRESS

### Active Workers
- Codex-Worker-1: Writing unit tests for API
- Claude-Worker-2: Designing integration test strategy

### Next P0
Complete test suite implementation
```

---

## Stage 5: Phase Acceptance Gate

**Trigger:** All deliverables in phase complete

**Process:**

1. Lead verifies acceptance criteria
2. Lead runs smoke tests
3. Lead generates status report
4. Lead requests phase approval from user
5. User reviews and approves/rejects

**Approval requirements:**

- All acceptance criteria met
- Tests passing
- Documentation updated
- `STATUS.md` reflects completion

**Lead actions:**

- Do NOT advance to next phase without approval
- Present evidence of acceptance criteria
- Document approval in `DECISIONS.md`

**Example:**

```markdown
## Phase 1 Acceptance

**Acceptance Criteria:**
- [x] API contract implemented ✓
- [x] Unit tests passing (47/47) ✓
- [x] Integration tests passing (12/12) ✓

**Test Results:**
- Unit: 47 passed, 0 failed
- Integration: 12 passed, 0 failed
- Smoke: 3 scenarios passed

**Request:** Phase 1 acceptance for advancement to Phase 2
```

**User approval:** Explicit "approved" before proceeding

---

## Stage 6: Phase Iteration or Completion

**After phase approval:**

### If more phases remain:

1. Lead advances to next phase
2. Lead updates `STATUS.md` current phase
3. Lead reads next phase acceptance criteria
4. Return to Stage 4 (Phase Execution)

### If all phases complete:

1. Lead verifies project acceptance criteria (from blueprint)
2. Lead runs final smoke tests
3. Lead generates final status report
4. Lead requests project completion approval

**Project completion checklist:**

- [ ] All phases complete
- [ ] All acceptance criteria met
- [ ] Full test suite passing
- [ ] Documentation complete
- [ ] README updated with release notes
- [ ] `STATUS.md` marked complete
- [ ] `DECISIONS.md` finalized
- [ ] No uncommitted changes
- [ ] CI/CD green

---

## Lifecycle Invariants

**These rules NEVER change:**

1. **No code before plan** - Blueprint → Plan → Approval → Code
2. **No phase skip** - Must complete Phase N before Phase N+1
3. **Approval gates enforced** - User approval required at gates
4. **Testing mandatory** - Tests run before phase acceptance
5. **State persisted** - `STATUS.md` updated at every deliverable
6. **Decisions logged** - Architectural changes recorded

---

## Resume Protocol

**If lead agent changes mid-lifecycle:**

1. New lead reads `STATUS.md`
2. Identifies current phase and deliverable
3. Reviews recent `DECISIONS.md` entries
4. Checks active workers (if any)
5. Continues from current deliverable

**Resume checklist in `STATUS.md`:**

```markdown
## Resume Checklist

1. Read STATUS.md (current phase/deliverable)
2. Read DECISIONS.md (recent architectural decisions)
3. Check .taskers/runs/ (active workers)
4. Run smoke tests (verify current state)
5. Pick next P0 from TODO
6. Continue execution
```

**Target:** New lead operational in <15 minutes

---

## Parallel Execution

**When workers can parallelize:**

1. Lead identifies independent deliverables
2. Lead creates scoped tickets for each worker
3. Lead verifies no overlap
4. Lead launches workers simultaneously
5. Lead monitors all workers
6. Lead integrates when all complete

**Example:**

```
Phase 2: Multi-module implementation

Deliverable A: Module X (Codex-Worker-1)
Deliverable B: Module Y (Codex-Worker-2)
Deliverable C: Module Z (Claude-Worker-1)

[All three execute in parallel]

Lead integrates all three when complete
```

**Constraint:** No two workers touch same files

---

## Emergency Procedures

### Blueprint Ambiguity Discovered

1. Halt execution
2. Document ambiguity
3. Ask user for clarification
4. Update blueprint
5. Revise plan if needed
6. Resume execution

### Phase Acceptance Failure

1. Identify failing criteria
2. Create remediation tasks
3. Execute fixes
4. Re-test
5. Re-request approval

### Worker Scope Overlap

1. Halt overlapping workers
2. Revise tickets
3. Re-launch with corrected scope
4. Continue execution

### Test Failures

1. Do NOT commit
2. Debug failures
3. Fix root cause
4. Re-run tests
5. Only proceed when green

---

## Lifecycle Metrics

**Measure progress by:**

- Phases completed / Total phases
- Deliverables completed / Total deliverables
- Acceptance criteria met / Total criteria
- Test pass rate
- Time per phase (optional)

**Status report includes:**

```markdown
## Progress

**Overall:** 60% (3/5 phases complete)
**Current Phase:** Phase 4 - TUI Implementation (80% complete)
**Deliverables:** 14/18 complete
**Tests:** 156/156 passing (100%)
```

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo STATUS.md, phase execution patterns
**Last Updated:** 2026-02-16

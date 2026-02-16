# Blueprint to Plan Process

**Purpose:** Convert high-level blueprint into actionable granular plan
**Enforces:** Structured decomposition, phase boundaries, acceptance criteria

---

## Process Overview

**Input:** Approved blueprint document
**Output:** Granular execution plan with phases, deliverables, tasks

**Lead agent responsibility:** Transform blueprint vision into execution roadmap

---

## Step 1: Blueprint Analysis

### Read Completely

**First action:** Read entire blueprint without interruption

**Extract:**

1. **Core vision** - What problem are we solving?
2. **Major features** - What are the main capabilities?
3. **Success criteria** - How do we know when we're done?
4. **Constraints** - What are the limits (technical, timeline, resources)?
5. **Non-negotiables** - What must be preserved?

### Identify Ambiguities

**Look for:**

- Vague requirements ("should be fast", "user-friendly")
- Undefined terms or concepts
- Missing specifications
- Conflicting requirements
- Unclear dependencies

**Action:** If found, halt and ask user for clarification BEFORE planning

**Example:**

```markdown
## Blueprint Clarification Needed

**Ambiguity:** Blueprint states "real-time sync" but doesn't define latency target
**Question:** What is acceptable sync latency? <100ms, <1s, <5s?
**Impact:** Affects architecture choice (WebSocket vs polling)

[WAIT for user response]
```

---

## Step 2: Phase Boundary Identification

### Natural Breakpoints

**Identify phases based on:**

1. **Dependency layers** - Foundation → Core → Features → Polish
2. **Architectural boundaries** - Backend → API → Frontend
3. **Risk mitigation** - Proof of concept → MVP → Full implementation
4. **User value** - Minimum viable → Enhanced → Complete
5. **Testing milestones** - Unit → Integration → End-to-end

### Phase Characteristics

**Good phase:**

✅ Has clear entry/exit criteria
✅ Delivers standalone value
✅ Can be tested independently
✅ Has manageable scope (1-2 weeks for AI)
✅ Has minimal external dependencies

**Bad phase:**

❌ Too large (>1 month)
❌ No clear completion criteria
❌ Cannot be tested until next phase
❌ Tightly coupled to other phases

### Phase Template

```markdown
## Phase N: [Name]

**Goal:** [One sentence describing phase outcome]

**Entry Criteria:**
- [ ] Prerequisite 1 from previous phase
- [ ] Prerequisite 2

**Acceptance Criteria:**
- [ ] Deliverable criterion 1
- [ ] Deliverable criterion 2
- [ ] Test criterion

**Exit Criteria:**
- [ ] All acceptance criteria met
- [ ] Tests passing
- [ ] Documentation updated
```

---

## Step 3: Deliverable Decomposition

### For Each Phase

**Break into deliverables:**

1. **Deliverable** = Completable unit of work with verifiable output
2. Each deliverable has:
   - Clear scope
   - Test strategy
   - Documentation requirement
   - Integration point

### Deliverable Sizing

**Optimal deliverable:**

- Completable in 1-3 days
- Produces testable artifact
- Can be integrated independently
- Has clear definition of done

**Too large:** >1 week → Break into sub-deliverables
**Too small:** <4 hours → Combine with related work

### Deliverable Template

```markdown
### Deliverable: [Name]

**Scope:** [What files/modules/features]
**Output:** [What artifact is produced]
**Testing:** [How to verify correctness]
**Dependencies:** [What must exist first]
**Integration:** [How this connects to system]

**Definition of Done:**
- [ ] Implementation complete
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed (if applicable)
```

---

## Step 4: Task Identification

### For Each Deliverable

**Identify atomic tasks:**

1. **Task** = Single-agent work unit
2. Tasks can be:
   - Sequential (must happen in order)
   - Parallel (can happen simultaneously)

### Task Scoping

**Good task:**

✅ Assigned to one worker or lead
✅ Has explicit file/module scope
✅ Completable in <1 day
✅ Has clear success criteria
✅ Non-overlapping with other tasks

**Bad task:**

❌ Requires multiple agents to coordinate
❌ Vague scope ("improve performance")
❌ Takes >1 week
❌ No measurable completion
❌ Overlaps with other tasks

### Parallelization Analysis

**Identify parallel tasks:**

- No shared file dependencies
- Independent features
- Different modules
- Read-only analysis tasks

**Assign to workers:**

- Codex workers → Code implementation tasks
- Claude workers → Design/planning tasks
- Lead → Integration and cross-cutting tasks

---

## Step 5: Acceptance Criteria Definition

### Per-Phase Criteria

**Format:**

```markdown
## Phase N Acceptance Criteria

**Functional:**
- [ ] Feature X works as specified in blueprint
- [ ] API contract matches specification
- [ ] Edge cases handled correctly

**Testing:**
- [ ] Unit test coverage >80%
- [ ] Integration tests passing
- [ ] Smoke tests passing

**Documentation:**
- [ ] API documentation updated
- [ ] README reflects new features
- [ ] Decision log current

**Quality:**
- [ ] No regression in existing tests
- [ ] Performance within acceptable range
- [ ] Code follows project conventions
```

**Must be:**

- Objective (not "good enough")
- Measurable (test pass rates, coverage)
- Verifiable (can run test to confirm)
- Comprehensive (covers functional + non-functional)

---

## Step 6: Dependency Mapping

### Identify Dependencies

**Between phases:**

```
Phase 0 (Foundation)
  ↓
Phase 1 (Core API) - depends on Phase 0
  ↓
Phase 2 (Features) - depends on Phase 1
  ↓
Phase 3 (Polish) - depends on Phase 2
```

**Between deliverables:**

```
Deliverable A: Database schema
  ↓
Deliverable B: Data access layer (depends on A)
  ↓
Deliverable C: Business logic (depends on B)
```

**Between tasks:**

```
Task 1: Design interface (Claude-Worker-1)
  ↓
Task 2: Implement interface (Codex-Worker-1, depends on Task 1)
  ↓
Task 3: Write tests (Codex-Worker-2, depends on Task 2)
```

### Document Dependencies

```markdown
## Dependency Graph

Phase 0 → Phase 1 → Phase 2 → Phase 3
         ↓
      Optional: Phase 1.5 (if needed)

**Critical Path:**
- Phase 0 deliverable A blocks all of Phase 1
- Phase 1 deliverable C blocks Phase 2 deliverable A
```

---

## Step 7: Risk Identification

### Analyze Plan Risks

**Look for:**

1. **Technical risks** - Unproven technology, complex integration
2. **Dependency risks** - External APIs, third-party libraries
3. **Scope risks** - Ambiguous requirements, feature creep
4. **Resource risks** - Complexity exceeds AI capability

### Mitigation Strategies

**For each risk:**

```markdown
## Risk: [Description]

**Likelihood:** High/Medium/Low
**Impact:** High/Medium/Low
**Mitigation:** [How we reduce risk]
**Contingency:** [What we do if risk materializes]
```

**Example:**

```markdown
## Risk: External API availability

**Likelihood:** Medium
**Impact:** High (blocks Phase 2)
**Mitigation:** Implement mock API in Phase 0 for testing
**Contingency:** Fallback to local data source
```

---

## Step 8: Plan Documentation

### Output Format

**Location:** `STATUS.md`

**Structure:**

```markdown
# Project Status

## Current Phase
[Active phase with current deliverable]

## Phase Plan

### Phase 0: Foundation
[Phase details, acceptance criteria, deliverables]

### Phase 1: Core Implementation
[Phase details, acceptance criteria, deliverables]

[... all phases ...]

## Progress Tracking
[Current completion metrics]

## TODO (Prioritized)
[Next items to work on]

## Worker Roster
[Active workers and their tickets]
```

### Plan Review Checklist

Before presenting plan to user:

- [ ] All blueprint features covered
- [ ] Phases have acceptance criteria
- [ ] Deliverables are sized appropriately
- [ ] Dependencies are explicit
- [ ] Parallel work opportunities identified
- [ ] Testing strategy defined per phase
- [ ] Risks identified and mitigated
- [ ] Resume checklist included

---

## Step 9: User Approval

### Present Plan

**Format:**

```markdown
# Execution Plan for [Project]

## Overview
- Total Phases: N
- Estimated Deliverables: M
- Parallel Work: K workers max

## Phase Breakdown
[Summary of each phase]

## Critical Path
[Key dependencies]

## Risks
[Major risks and mitigations]

## Next Steps
Upon approval:
1. Begin Phase 0
2. Deploy workers for [specific tasks]
3. Target Phase 0 completion: [timeline]
```

### Approval Gate

**Lead actions:**

1. Present plan clearly
2. Answer user questions
3. **WAIT for explicit approval**
4. Do NOT begin implementation
5. Log approval in `DECISIONS.md`

**User responses:**

- **"Approved"** → Proceed to execution
- **"Revise [X]"** → Update plan and re-present
- **"Clarify [Y]"** → Provide more detail
- **"Rejected"** → Return to blueprint

---

## Step 10: Plan Maintenance

### During Execution

**Plan is living document:**

- Update when deliverables complete
- Revise if scope changes
- Add phases if needed
- Mark acceptance criteria as met

### Plan Revision Triggers

**When to revise plan:**

1. Blueprint changes (user adds/removes features)
2. Unforeseen technical constraints discovered
3. Dependencies change
4. Phase acceptance reveals gaps

**Revision process:**

1. Identify what changed
2. Update affected phases
3. Re-check dependencies
4. **Request approval** for significant changes
5. Log revision in `DECISIONS.md`

---

## Planning Anti-Patterns

### Avoid These

❌ **Planning paralysis** - Don't over-plan; start with Phase 0
❌ **Vague phases** - "Implement features" is not a phase
❌ **No acceptance criteria** - Can't verify completion
❌ **Too granular** - Don't plan every line of code
❌ **Too vague** - Don't have one giant "implementation" phase
❌ **Ignoring dependencies** - Parallel work must be truly independent
❌ **No testing strategy** - Tests are part of plan, not afterthought

---

## Blueprint Patterns

### Pattern: Layered Architecture

**Blueprint mentions:** Backend, API, Frontend

**Plan structure:**

- Phase 0: Repository setup
- Phase 1: Backend core
- Phase 2: API layer
- Phase 3: Frontend
- Phase 4: Integration & Polish

### Pattern: Feature Iteration

**Blueprint mentions:** MVP + Enhanced features

**Plan structure:**

- Phase 0: Foundation
- Phase 1: MVP (minimal feature set)
- Phase 2: Enhanced features (batch 1)
- Phase 3: Enhanced features (batch 2)
- Phase 4: Polish & Release

### Pattern: Proof of Concept

**Blueprint mentions:** High technical risk

**Plan structure:**

- Phase 0: Proof of concept (de-risk core assumption)
- Phase 1: MVP (if POC succeeds)
- Phase 2: Full implementation
- Phase 3: Production hardening

---

## Example: Complete Blueprint-to-Plan

### Input Blueprint

```markdown
# Chat Application Blueprint

## Vision
Real-time chat with AI assistance

## Features
1. User authentication
2. Real-time messaging
3. AI-powered message suggestions
4. Message history

## Success Criteria
- Users can send/receive messages <1s latency
- AI suggestions appear within 2s
- 99.9% uptime

## Constraints
- Use existing auth provider
- SQLite for local storage
```

### Output Plan

```markdown
# Chat Application Execution Plan

## Phase 0: Foundation (1 week)
**Goal:** Repository, build, and test infrastructure

**Acceptance Criteria:**
- [ ] Build system functional
- [ ] Test framework configured
- [ ] CI pipeline running

**Deliverables:**
1. Repository structure
2. Build scripts (Makefile)
3. Test harness
4. CI configuration

## Phase 1: Authentication (1 week)
**Goal:** User auth via existing provider

**Acceptance Criteria:**
- [ ] Users can sign up/login
- [ ] Tokens validated correctly
- [ ] Session management works

**Deliverables:**
1. Auth provider integration
2. Token validation
3. Session middleware
4. Auth tests

## Phase 2: Real-Time Messaging (2 weeks)
**Goal:** Core chat functionality

**Acceptance Criteria:**
- [ ] Messages sent/received <1s
- [ ] WebSocket connection stable
- [ ] Message persistence working

**Deliverables:**
1. WebSocket server
2. Message protocol
3. SQLite message store
4. Client-server sync
5. Integration tests

## Phase 3: AI Suggestions (2 weeks)
**Goal:** AI-powered message assistance

**Acceptance Criteria:**
- [ ] Suggestions appear <2s
- [ ] Suggestions contextually relevant
- [ ] Fallback if AI unavailable

**Deliverables:**
1. AI provider integration
2. Context extraction
3. Suggestion UI
4. Caching layer
5. AI tests (with mocks)

## Phase 4: Polish & Release (1 week)
**Goal:** Production readiness

**Acceptance Criteria:**
- [ ] 99.9% uptime in stress test
- [ ] All edge cases handled
- [ ] Documentation complete

**Deliverables:**
1. Error handling hardening
2. Performance optimization
3. Release documentation
4. Smoke tests
```

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo blueprint patterns, phase planning
**Last Updated:** 2026-02-16

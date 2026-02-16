# Worker Ticket Template

**Purpose:** Standard format for worker task tickets
**Usage:** Copy and customize for each worker deployment

---

## Template

```markdown
# {Worker-Type}-Worker-{N}

**Assigned:** {YYYY-MM-DD}
**Phase:** Phase {N} - {Phase Name}
**Deliverable:** {Deliverable Name}
**Owner:** {Worker-Type}-Worker-{N}

---

## Task

{One or two sentence description of what this worker needs to do}

---

## Scope

### Files Included (You CAN modify/analyze)

- {path/to/file1.go}
- {path/to/file2.go}
- {path/to/file3.go}

### Files Excluded (Do NOT touch)

- {path/to/other/file.go}
- {shared/infrastructure/}
- {any files assigned to other workers}

### Boundaries

**Included:**
- {Specific feature or module}
- {Specific functionality}

**Excluded:**
- {Features outside scope}
- {Shared infrastructure (lead's job)}

---

## Success Criteria

- [ ] {Criterion 1: specific, measurable}
- [ ] {Criterion 2: specific, measurable}
- [ ] {Criterion 3: specific, measurable}
- [ ] Tests written and passing (>{X}% coverage)
- [ ] Documentation updated (code comments, API docs if applicable)

---

## Context

### From Blueprint

{Relevant excerpt from blueprint/plan that provides background}

### Related Work

- {Other deliverables this depends on}
- {Other workers this relates to (but does not overlap)}

### Acceptance Criteria (Phase Level)

{Relevant phase acceptance criteria this task contributes to}

---

## Constraints

### You MUST

- ✅ Stay within scope boundaries
- ✅ Analyze and propose only (read-only)
- ✅ Report findings to lead
- ✅ Consider edge cases
- ✅ Suggest tests

### You MUST NOT

- ❌ Modify files outside scope
- ❌ Commit code directly
- ❌ Change STATUS.md or DECISIONS.md
- ❌ Launch other workers
- ❌ Assume integration approach

---

## Dependencies

**Blocked By:**
{List of tasks that must complete before this one can start}
- {Task/Worker ID}: {Brief description}

**Blocks:**
{List of tasks that cannot start until this one completes}
- {Task/Worker ID}: {Brief description}

**Parallel With:**
{List of tasks that can run simultaneously}
- {Task/Worker ID}: {Brief description}

---

## Output Format

**Location:** `.taskers/runs/{timestamp}/{Worker-Type}-Worker-{N}.txt`

**Required Sections:**

### 1. Task Summary
{What you were asked to do}

### 2. Analysis
{What you found, discovered, or understood}

### 3. Proposal
{What you recommend}

#### Affected Files
- {path/to/file1.go}
- {path/to/file2.go}

#### Implementation Sketch
```{language}
// Code or pseudocode showing proposed implementation
```

#### Testing Strategy
{How lead should verify this works}
- Unit tests: {what to test}
- Integration tests: {what to test}
- Edge cases: {what to cover}

#### Integration Notes
{What lead needs to know to integrate this}
- {Integration point 1}
- {Integration point 2}

### 4. Risks & Alternatives
**Risks:**
- {Risk 1 and mitigation}
- {Risk 2 and mitigation}

**Alternatives Considered:**
- {Alternative A}: {Why rejected}
- {Alternative B}: {Why rejected}

### 5. Status
{COMPLETE | BLOCKED | NEEDS_CLARIFICATION}

**If BLOCKED:**
- Blocker: {What's blocking you}
- Attempted: {What you tried}
- Needs: {What would unblock you}

**If NEEDS_CLARIFICATION:**
- Question: {What's unclear}
- Context: {Why you're asking}
- Impact: {How this affects your work}

---

## Questions for Lead

{Any questions you have about scope, requirements, or integration}

1. {Question 1}
2. {Question 2}

---

## Notes

{Any additional context, observations, or concerns}

---

**Worker Instructions End**
```

---

## Customization Guide

### For Codex Workers (Code Implementation)

**Specialize for:**

- Code implementation tasks
- Bug analysis and fixes
- Refactoring proposals
- Test implementation

**Example scope:**

```markdown
## Task
Implement token validation logic in internal/auth/validator.go

## Scope
### Files Included
- internal/auth/validator.go (create)
- internal/auth/types.go (read)
- tests/auth/validator_test.go (create)

### Boundaries
**Included:**
- JWT token parsing
- Signature validation
- Expiration checking
- Unit tests

**Excluded:**
- OAuth provider integration (different worker)
- Session management (different deliverable)
```

---

### For Claude Workers (Design/Planning)

**Specialize for:**

- Architecture design
- API contract design
- Implementation planning
- Documentation writing

**Example scope:**

```markdown
## Task
Design API contract for skill execution interface

## Scope
### Files Included
- Design document (create): docs/design/skill-execution-api.md

### Boundaries
**Included:**
- Interface definition
- Request/response formats
- Error handling strategy
- Integration points

**Excluded:**
- Implementation (Codex worker's job)
- Existing API changes (lead's job)
```

---

### For Gemini Workers (Supplemental Analysis)

**Specialize for:**

- Cross-validation
- Alternative approaches
- Edge case discovery
- Performance analysis

**Example scope:**

```markdown
## Task
Validate Codex-Worker-1 refactoring proposal for correctness

## Scope
### Files Included
- Review Codex-Worker-1 output
- Review internal/planner/ (read-only)

### Boundaries
**Included:**
- Validate correctness of proposal
- Identify edge cases not considered
- Propose alternatives if issues found

**Excluded:**
- Making final integration decision (lead's job)
- Implementing different approach (outside scope)
```

---

## Example: Complete Codex Worker Ticket

```markdown
# Codex-Worker-1

**Assigned:** 2026-02-16
**Phase:** Phase 2 - MVP Implementation
**Deliverable:** Integration Tests
**Owner:** Codex-Worker-1

---

## Task

Implement integration tests for the planner module's auto-routing functionality.

---

## Scope

### Files Included

- internal/tests/integration/planner_test.go (create)
- internal/planner/router.go (read)
- internal/planner/service.go (read)

### Files Excluded

- internal/governor/ (different module, different worker)
- internal/runner/ (different module)
- Any files in internal/tui/ (different deliverable)

### Boundaries

**Included:**
- Integration tests for planner routing heuristics
- Test cases: basic routing, fallback routing, edge cases
- Table-driven test structure
- Mock external dependencies (governor, runner)

**Excluded:**
- Unit tests (already complete)
- End-to-end tests (lead's job)
- Changes to planner implementation (read-only analysis)

---

## Success Criteria

- [ ] 8-10 integration tests implemented
- [ ] All routing scenarios covered (basic, fallback, edge)
- [ ] Tests passing (100%)
- [ ] Coverage for router.go >90%
- [ ] Code comments for complex test cases
- [ ] README updated with test instructions

---

## Context

### From Blueprint

Phase 2 requires comprehensive integration testing to ensure planner
auto-routing works correctly across different skill types and scenarios.
Critical for MVP functionality.

### Related Work

- Unit tests: Already complete (Codex-Worker-2, integrated)
- Planner implementation: Complete (Phase 1)

### Acceptance Criteria (Phase 2)

- All integration tests passing (100%)
- Test coverage >80% for all modules

---

## Constraints

### You MUST

- ✅ Stay within planner module scope
- ✅ Create integration tests only (no implementation changes)
- ✅ Use table-driven test pattern (project convention)
- ✅ Mock external dependencies
- ✅ Include edge case coverage

### You MUST NOT

- ❌ Modify planner implementation (read-only)
- ❌ Create tests for governor or runner modules (different workers)
- ❌ Commit directly (output proposal only)
- ❌ Assume integration approach

---

## Dependencies

**Blocked By:**
- None (planner implementation complete)

**Blocks:**
- None (can proceed in parallel with other work)

**Parallel With:**
- Claude-Worker-2: Performance analysis (independent)

---

## Output Format

**Location:** `.taskers/runs/20260216_142834/Codex-Worker-1.txt`

**Required Sections:**

### 1. Task Summary
Implement integration tests for planner auto-routing

### 2. Analysis
{Your analysis of router.go and routing logic}

### 3. Proposal

#### Affected Files
- internal/tests/integration/planner_test.go (create)

#### Implementation Sketch
```go
// Table-driven integration tests for router
func TestPlannerRouting(t *testing.T) {
    tests := []struct{
        name string
        input SkillRequest
        want RoutingDecision
    }{
        // Test cases here
    }
    // ...
}
```

#### Testing Strategy
- Run via: `go test -v internal/tests/integration/`
- Expected: All tests pass
- Coverage: `go test -cover` should show >90% for router.go

#### Integration Notes
- Tests are self-contained
- No changes to existing code
- Can integrate immediately

### 4. Risks & Alternatives
{Your risk analysis}

### 5. Status
COMPLETE

---

## Questions for Lead

None

---

## Notes

None

---

**Worker Instructions End**
```

---

## Ticket Preparation Workflow

### Step 1: Identify Work Unit

**From deliverable:** "Integration Tests"

**Break into tasks:**

- Task 1: Planner integration tests (Codex-Worker-1)
- Task 2: Governor integration tests (Codex-Worker-2)
- Task 3: Runner integration tests (Codex-Worker-3)

---

### Step 2: Define Scope

**For each task:**

- List specific files included
- List files excluded
- Define functional boundaries
- Verify non-overlapping with other tasks

---

### Step 3: Set Success Criteria

**Make criteria:**

- Specific (exact test count or coverage %)
- Measurable (can verify objectively)
- Achievable (within worker capability)
- Relevant (contributes to deliverable)

---

### Step 4: Document Dependencies

**Identify:**

- What must complete first? (blocking)
- What can run in parallel? (independent)
- What is blocked by this? (downstream)

---

### Step 5: Customize Template

**Copy template:**

```bash
cp docs/worker-ticket-templates/codex-1.md .taskers/tickets/Codex-Worker-1.md
```

**Fill in:**

- Task description
- Scope (files, boundaries)
- Success criteria
- Context from blueprint
- Dependencies
- Constraints

---

### Step 6: Verify

**Before launching worker:**

- [ ] Scope is clear and explicit
- [ ] No overlap with other workers
- [ ] Success criteria measurable
- [ ] Dependencies documented
- [ ] Output format specified

---

## Worker Ticket Directory Structure

### Committed Templates

```
docs/worker-ticket-templates/
├── README.md              # Template usage instructions
├── codex-1.md             # Codex worker 1 template
├── codex-2.md
├── codex-3.md
├── codex-4.md
├── codex-5.md
├── claude-1.md            # Claude worker 1 template
├── claude-2.md
├── claude-3.md
├── claude-4.md
├── claude-5.md
├── gemini-1.md            # Gemini worker 1 template (optional)
├── gemini-2.md
├── gemini-3.md
├── gemini-4.md
└── gemini-5.md
```

**Purpose:** Version-controlled templates for reproducibility

---

### Runtime Tickets

```
.taskers/tickets/
├── Codex-Worker-1.md      # Active ticket (customized)
├── Codex-Worker-2.md
├── Claude-Worker-1.md
└── ...
```

**Purpose:** Git-ignored, runtime-customized tickets

**Workflow:**

1. Copy template from `docs/worker-ticket-templates/` to `.taskers/tickets/`
2. Customize for specific task
3. Launch worker with customized ticket
4. Worker reads ticket from `.taskers/tickets/`

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo worker ticket templates
**Last Updated:** 2026-02-16

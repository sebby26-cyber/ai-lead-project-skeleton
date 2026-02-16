# Granular Task Decomposition

**Purpose:** Break deliverables into worker-assignable tasks
**Enforces:** Scoped, non-overlapping, parallelizable work units

---

## Decomposition Principles

### What Is a Task?

**Task** = Smallest assignable unit of work with clear scope and output

**Characteristics:**

- Completable by single worker in <1 day
- Has explicit file/module boundaries
- Produces verifiable artifact
- Can be tested independently
- Non-overlapping with other tasks

---

## Decomposition Process

### Step 1: Analyze Deliverable

**For deliverable:** "Implement user authentication"

**Ask:**

1. What files/modules are involved?
2. What are the logical sub-components?
3. What can be parallelized?
4. What dependencies exist?
5. How will this be tested?

**Output:** List of logical components

```
Components:
- Auth provider interface
- Token validation
- Session middleware
- Database schema
- API endpoints
- Tests
```

---

### Step 2: Identify Work Units

**For each component:**

**Ask:**

- Can this be done by one worker?
- Does this overlap with other components?
- Is scope clear and bounded?
- Can output be verified?

**Classification:**

- **Sequential work** - Must happen in order
- **Parallel work** - Can happen simultaneously
- **Integration work** - Lead must handle

**Example:**

```
Sequential:
1. Design auth interface (Claude-Worker-1)
   ↓
2. Implement interface (Codex-Worker-1, depends on #1)

Parallel (can happen simultaneously):
3. Design database schema (Claude-Worker-2)
4. Design API endpoints (Claude-Worker-3)

Integration (lead only):
5. Integrate all components
6. End-to-end testing
```

---

### Step 3: Define Task Scope

**For each task, specify:**

#### 1. Files Involved

```markdown
**Scope:**
- internal/auth/provider.go (read/write)
- internal/auth/types.go (read)
- tests/auth_test.go (write)
```

**Rule:** If two tasks touch same file, they are NOT parallel

#### 2. Boundaries

```markdown
**Included:**
- OAuth provider integration
- Token refresh logic

**Excluded:**
- Session storage (different task)
- User profile management (different deliverable)
```

#### 3. Success Criteria

```markdown
**Definition of Done:**
- [ ] Provider interface implemented
- [ ] Token validation working
- [ ] Unit tests passing (>80% coverage)
- [ ] Documentation updated
```

---

### Step 4: Assign Worker Type

**Match task to worker specialty:**

| Task Type | Worker Type | Rationale |
|-----------|-------------|-----------|
| Code implementation | Codex | Code generation strength |
| API design | Claude | Design/architecture |
| Test strategy | Claude | Planning/analysis |
| Bug analysis | Codex | Code understanding |
| Documentation | Claude | Writing/explanation |
| Refactoring | Codex | Code transformation |

**Lead tasks:**

- Integration across components
- Cross-cutting changes
- Test execution and verification
- Merge conflict resolution

---

### Step 5: Create Worker Tickets

**Template:**

```markdown
# {Worker-Type}-Worker-{N}

## Task
[One sentence task description]

## Scope

### Files Included
- path/to/file1.go
- path/to/file2.go

### Files Excluded (Do Not Touch)
- path/to/other/file.go
- shared/infrastructure/

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Tests written and passing

## Context
[Relevant background from blueprint/plan]

## Constraints
- Read-only repository access
- Do not modify files outside scope
- Report findings only, do not commit

## Dependencies
[Tasks that must complete first, if any]

## Output Format
- Analysis document with findings
- Code proposals with rationale
- Test strategy
```

**Save to:** `.taskers/tickets/{Worker-Type}-Worker-{N}.md`

---

## Decomposition Patterns

### Pattern 1: Layer-Based Decomposition

**Deliverable:** "Implement data access layer"

**Tasks:**

1. Database schema design (Claude-Worker-1)
2. Migration scripts (Codex-Worker-1, depends on #1)
3. Repository interface design (Claude-Worker-2, parallel with #1)
4. Repository implementation (Codex-Worker-2, depends on #3)
5. Data access tests (Codex-Worker-3, depends on #4)

**Lead:** Integration + end-to-end tests

---

### Pattern 2: Feature-Based Decomposition

**Deliverable:** "Multi-feature module"

**Tasks:**

1. Feature A implementation (Codex-Worker-1)
2. Feature B implementation (Codex-Worker-2, parallel with #1)
3. Feature C implementation (Codex-Worker-3, parallel with #1, #2)
4. Integration tests (Lead)

**Constraint:** Features A, B, C must not share files

---

### Pattern 3: Design-First Decomposition

**Deliverable:** "Complex system component"

**Tasks:**

1. Architecture design (Claude-Worker-1)
2. Interface definition (Claude-Worker-2, depends on #1)
3. Implementation (Codex-Worker-1, depends on #2)
4. Testing strategy (Claude-Worker-3, parallel with #3)
5. Test implementation (Codex-Worker-2, depends on #3, #4)

**Lead:** Review design, integrate implementation

---

### Pattern 4: Refactoring Decomposition

**Deliverable:** "Refactor module X"

**Tasks:**

1. Analyze current implementation (Codex-Worker-1)
2. Propose refactoring approach (Claude-Worker-1, depends on #1)
3. Extract component A (Codex-Worker-2, depends on #2)
4. Extract component B (Codex-Worker-3, depends on #2, parallel with #3)
5. Update tests (Codex-Worker-4, depends on #3, #4)

**Lead:** Approve refactoring approach, integrate changes

---

## Scope Boundary Enforcement

### File-Level Boundaries

**Rule:** One file = one worker (or lead)

**Example:**

```
✅ GOOD:
- Codex-Worker-1: internal/auth/provider.go
- Codex-Worker-2: internal/auth/session.go
- Lead: internal/auth/integration.go

❌ BAD (overlap):
- Codex-Worker-1: internal/auth/provider.go
- Codex-Worker-2: internal/auth/provider.go (CONFLICT!)
```

---

### Feature-Level Boundaries

**Rule:** Non-overlapping functional scope

**Example:**

```
✅ GOOD:
- Codex-Worker-1: User registration feature
- Codex-Worker-2: Password reset feature
- Codex-Worker-3: Email verification feature

❌ BAD (overlap):
- Codex-Worker-1: User management (too broad)
- Codex-Worker-2: User authentication (overlap with #1)
```

---

### Module-Level Boundaries

**Rule:** Clear module ownership

**Example:**

```
✅ GOOD:
- Codex-Worker-1: internal/planner/ (entire module)
- Codex-Worker-2: internal/governor/ (entire module)
- Codex-Worker-3: internal/runner/ (entire module)

✅ ALSO GOOD (sub-module):
- Codex-Worker-1: internal/planner/router.go
- Codex-Worker-2: internal/planner/service.go
(Different files in same module, no overlap)
```

---

## Task Sizing Guidelines

### Right-Sized Task

**Characteristics:**

- 4-8 hours of focused work
- Single clear objective
- Measurable completion
- Testable output

**Example:**

```markdown
Task: Implement token validation

**Scope:**
- internal/auth/validator.go (200 LOC)
- Parse JWT tokens
- Validate signatures
- Check expiration

**Output:**
- validator.go implementation
- Unit tests (>80% coverage)
- Documentation comments

**Estimate:** 6 hours
```

---

### Too Large (needs decomposition)

**Signs:**

- >1 day of work
- Multiple sub-objectives
- Affects >3 files
- Unclear completion

**Example:**

```markdown
❌ Task: Implement complete auth system

This is TOO LARGE. Should be:
✅ Task 1: Implement provider interface
✅ Task 2: Implement token validation
✅ Task 3: Implement session management
✅ Task 4: Implement middleware
```

---

### Too Small (should combine)

**Signs:**

- <2 hours of work
- Single function
- No independent value

**Example:**

```markdown
❌ Task: Write helper function formatToken()

This is TOO SMALL. Combine with:
✅ Task: Implement token utilities (includes formatToken, parseToken, validateToken)
```

---

## Dependency Management

### Explicit Dependencies

**Document in ticket:**

```markdown
## Dependencies

**Blocks:**
- Codex-Worker-2 (needs interface definition from this task)
- Codex-Worker-3 (needs schema from this task)

**Blocked By:**
- Claude-Worker-1 (need design approval first)

**Parallel With:**
- Claude-Worker-2 (independent API design)
```

---

### Sequential vs Parallel

**Sequential (must be ordered):**

```
Task A: Design interface
  ↓
Task B: Implement interface (depends on A)
  ↓
Task C: Test implementation (depends on B)
```

**Parallel (can run simultaneously):**

```
Task A: Module X implementation
Task B: Module Y implementation (independent)
Task C: Module Z implementation (independent)
```

---

## Verification Strategy

### Task Completion Checklist

**For each task:**

```markdown
- [ ] Scope boundaries respected
- [ ] All files within scope modified
- [ ] No files outside scope touched
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Worker reported findings
- [ ] Lead reviewed output
```

---

### Integration Verification

**After all tasks in deliverable complete:**

```markdown
- [ ] All worker outputs collected
- [ ] Conflicts resolved
- [ ] Integration performed by lead
- [ ] Full test suite passing
- [ ] Deliverable acceptance criteria met
```

---

## Anti-Patterns

### Avoid These

❌ **Vague scope** - "Improve auth module"
❌ **Overlapping tasks** - Two workers modifying same file
❌ **No success criteria** - Can't verify completion
❌ **Missing dependencies** - Launch dependent task before prerequisite
❌ **Too granular** - One function per task
❌ **Too coarse** - Entire subsystem per task
❌ **Ambiguous boundaries** - "And related files"

---

## Example: Complete Decomposition

### Deliverable

"Implement TUI status display"

---

### Analysis

**Components:**
- State management
- Rendering logic
- User input handling
- Status data fetching

**Files:**
- internal/tui/app.go (state)
- internal/tui/render.go (display)
- internal/tui/input.go (keyboard)
- internal/tui/status.go (data)

---

### Task Breakdown

#### Task 1: Design TUI state machine

**Worker:** Claude-Worker-1
**Type:** Design

```markdown
## Task
Design state machine for TUI application state

## Scope
- Design document (no code)
- State transitions
- Event handling model

## Output
- State diagram
- Transition table
- Event handler specifications

## Dependencies
None (can start immediately)
```

---

#### Task 2: Implement state management

**Worker:** Codex-Worker-1
**Type:** Implementation

```markdown
## Task
Implement TUI state management in app.go

## Scope
### Files
- internal/tui/app.go (write)
- internal/tui/types.go (write)

## Success Criteria
- [ ] AppState struct implemented
- [ ] State transitions working
- [ ] Unit tests passing (>80% coverage)

## Dependencies
- Claude-Worker-1 (need state design first)
```

---

#### Task 3: Implement rendering logic

**Worker:** Codex-Worker-2
**Type:** Implementation

```markdown
## Task
Implement TUI rendering in render.go

## Scope
### Files
- internal/tui/render.go (write)

### Boundaries
- Only rendering logic
- Do NOT implement state management (Codex-Worker-1)
- Do NOT implement input handling (Codex-Worker-3)

## Success Criteria
- [ ] Render functions implemented
- [ ] Display tests passing

## Dependencies
- Codex-Worker-1 (need AppState definition)

## Parallel With
- Codex-Worker-3 (input handling)
```

---

#### Task 4: Implement input handling

**Worker:** Codex-Worker-3
**Type:** Implementation

```markdown
## Task
Implement keyboard input handling in input.go

## Scope
### Files
- internal/tui/input.go (write)

## Success Criteria
- [ ] Keyboard handlers implemented
- [ ] Event dispatch working
- [ ] Input tests passing

## Dependencies
- Codex-Worker-1 (need AppState definition)

## Parallel With
- Codex-Worker-2 (rendering)
```

---

#### Task 5: Integration & Testing

**Owner:** Lead
**Type:** Integration

```markdown
## Task
Integrate all TUI components and run end-to-end tests

## Scope
- All internal/tui/* files
- Integration test suite

## Success Criteria
- [ ] All components integrated
- [ ] No merge conflicts
- [ ] Full TUI functional
- [ ] E2E tests passing

## Dependencies
- Codex-Worker-1, 2, 3 (all implementation tasks)
```

---

## Decomposition Checklist

**Before launching workers:**

- [ ] All tasks have explicit scope
- [ ] No file overlaps between tasks
- [ ] Dependencies documented
- [ ] Success criteria defined
- [ ] Worker types assigned
- [ ] Tickets created
- [ ] Integration plan exists

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo worker orchestration patterns
**Last Updated:** 2026-02-16

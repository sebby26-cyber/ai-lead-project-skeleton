# Repository Synchronization and Logging

**Purpose:** Keep repository state synchronized with execution reality
**Enforces:** Documentation updates, decision logging, commit discipline

---

## Core Principle

**Repository must reflect true project state at all times:**

1. **Code** = Implementation
2. **Tests** = Verification
3. **Documentation** = Current state and decisions
4. **Canonical files** = Execution progress

**Never:** Let docs diverge from code, or let code diverge from plan

---

## Synchronization Points

### After Every Deliverable

**When deliverable completes:**

1. **Update STATUS.md:**
   - Mark deliverable complete
   - Update progress percentages
   - Move TODO items
   - Update worker roster if applicable

2. **Update DECISIONS.md (if architectural):**
   - Log any architectural decisions made
   - Document alternatives considered
   - Note consequences

3. **Update documentation:**
   - README if user-facing features added
   - API.md if API contracts changed
   - Architecture docs if structure changed

4. **Commit everything:**
   ```bash
   git add STATUS.md DECISIONS.md [other docs] [code] [tests]
   git commit -m "Deliverable complete: [name]

   - [Brief description of what was delivered]
   - STATUS.md updated (Phase N now X% complete)
   - [Decision logged in DECISIONS.md] (if applicable)
   - Tests: [X]/[Y] passing"
   ```

---

### After Phase Transition

**When phase completes:**

1. **Update STATUS.md:**
   - Mark phase complete
   - Advance current phase indicator
   - Update milestone progress
   - Archive completed phase details (optional)

2. **Log transition in DECISIONS.md:**
   ```markdown
   ## YYYY-MM-DD: Phase N Complete

   **Context:** All Phase N acceptance criteria met
   **Decision:** Approved to advance to Phase N+1
   **Deliverables:** [List of completed deliverables]
   **Tests:** [Test status]
   **Next:** Begin Phase N+1
   ```

3. **Update README:**
   - Note major milestone achieved
   - Update features list if applicable
   - Update status badge (if used)

4. **Commit phase transition:**
   ```bash
   git add STATUS.md DECISIONS.md README.md
   git commit -m "Phase N complete, advancing to Phase N+1

   - All Phase N acceptance criteria met
   - Tests: [X]/[Y] passing
   - Next: Phase N+1 [name]"
   ```

---

### After Worker Integration

**When worker output integrated:**

1. **Update STATUS.md:**
   - Move worker from "Active" to "Recent Completions"
   - Note integration decision (accepted/rejected/partial)
   - Update deliverable status if affected

2. **Log decision in DECISIONS.md (if significant):**
   ```markdown
   ## YYYY-MM-DD: Worker Proposal Integration

   **Context:** Codex-Worker-1 proposed [change]
   **Decision:** Accepted with modifications
   **Rationale:** [Why accepted, what modified]
   **Consequences:** [Impact on system]
   ```

3. **Commit integration:**
   ```bash
   git add [integrated code] STATUS.md DECISIONS.md
   git commit -m "Integrate Codex-Worker-1 proposal: [topic]

   - [Brief description of integration]
   - Accepted: [what was accepted]
   - Modified: [what was changed]
   - Tests: [X]/[Y] passing"
   ```

---

### Before Commits (Always)

**Pre-commit checklist:**

```markdown
- [ ] Tests run and passing
- [ ] STATUS.md updated (if deliverable/phase change)
- [ ] DECISIONS.md logged (if architectural decision)
- [ ] Documentation synced (README, API docs)
- [ ] Code follows project conventions
- [ ] Commit message is clear and descriptive
```

**Never commit without:**

- Running tests
- Updating canonical files (if state changed)
- Clear commit message

---

## Decision Logging

### When to Log

**Log in DECISIONS.md when:**

1. **Architectural decisions:**
   - Technology choices (libraries, frameworks)
   - Design patterns adopted
   - Module structure changes
   - API contract changes

2. **Behavior changes:**
   - Breaking changes to existing features
   - Algorithm changes
   - Performance trade-offs
   - Security decisions

3. **Process changes:**
   - Worker pool size changes
   - Phase plan revisions
   - Approval gate additions

4. **Phase transitions:**
   - Phase completions
   - Milestone achievements
   - Major approvals

**Do NOT log:**

- Minor bug fixes (unless architecturally significant)
- Documentation typos
- Test additions (unless new strategy)
- Trivial refactoring

---

### Decision Entry Format

**Standard format:**

```markdown
## YYYY-MM-DD: [Decision Title]

**Context:**
[Why was this decision needed? What problem or requirement drove it?]

**Decision:**
[What was decided? Be explicit and actionable.]

**Alternatives Considered:**
1. [Alternative A] - Rejected because [reason]
2. [Alternative B] - Rejected because [reason]
3. [Alternative C] - Rejected because [reason]

**Consequences:**
- **Positive:** [Benefits of this decision]
- **Negative:** [Trade-offs or costs]
- **Neutral:** [Other impacts]

**Status:** Accepted | Proposed | Rejected | Superseded
**Supersedes:** [Previous decision ID, if replacing an old decision]
**References:** [Links to issues, docs, or discussions]
```

---

### Example Decision Log

```markdown
## 2026-02-16: Adopt Redis for Session Caching

**Context:**
In-memory session storage works for single-instance deployment but fails
in multi-instance scenarios. Phase 3 requires horizontal scaling capability.

**Decision:**
Use Redis for centralized session storage.

**Alternatives Considered:**
1. In-memory (current) - Rejected: doesn't support multi-instance
2. Memcached - Rejected: no persistence, sessions lost on restart
3. PostgreSQL sessions table - Rejected: overkill, adds DB load
4. Redis - **Accepted**: fast, persistent, multi-instance support

**Consequences:**
- **Positive:**
  - Enables horizontal scaling
  - Session persistence across restarts
  - Fast access (<5ms P95)
- **Negative:**
  - New dependency (Redis server required)
  - Slightly more complex deployment
  - Network hop for session access
- **Neutral:**
  - Configuration needed for Redis connection

**Status:** Accepted
**Supersedes:** N/A
**References:** Phase 3 scaling requirements (STATUS.md)
```

---

## Commit Discipline

### Commit Message Format

**Standard format:**

```
[One-line summary of change]

- [Bullet point detail 1]
- [Bullet point detail 2]
- [Documentation/status updates]
- Tests: [test status]
```

**Examples:**

```
Deliverable complete: OAuth provider integration

- Implemented OAuth flow in internal/auth/oauth.go
- Token validation working (all 47 tests passing)
- STATUS.md updated (Phase 1 now 50% complete)
- Decision logged: chose OAuth 2.0 over SAML
- Tests: 55/55 passing (100%)
```

```
Integrate Codex-Worker-2 refactoring proposal

- Refactored planner module per worker proposal
- Accepted: extract router to separate file
- Modified: kept heuristics in main service (scope concern)
- STATUS.md updated (worker moved to Recent Completions)
- Tests: 147/147 passing
```

```
Phase 1 complete: Authentication

- All Phase 1 acceptance criteria met
- OAuth, token validation, session management functional
- Tests: 55/55 passing (100%)
- STATUS.md updated (Phase 1 complete, advancing to Phase 2)
- DECISIONS.md: Phase 1 completion logged
```

---

### Commit Frequency

**When to commit:**

✅ **After deliverable completion** (mandatory)
✅ **After worker integration** (mandatory)
✅ **After phase transition** (mandatory)
✅ **After significant refactoring** (if tests pass)
✅ **End of work session** (if in middle of work, use WIP commit)

❌ **Do NOT commit:**
- Broken code (tests failing)
- Incomplete deliverables (unless WIP commit)
- Without updating STATUS.md (if state changed)

**WIP (Work In Progress) commits:**

```
WIP: Integration tests (3/8 complete)

- Implemented API endpoint tests
- 3 tests passing, 5 remaining
- STATUS.md NOT updated (deliverable not complete)
- Will complete tomorrow

DO NOT MERGE
```

---

### Commit Atomicity

**One commit should:**

- Complete one deliverable OR
- Integrate one worker output OR
- Make one architectural change

**One commit should NOT:**

- Mix multiple deliverables
- Include unrelated changes
- Span multiple phases

**Example of good atomicity:**

```
✅ GOOD:
Commit 1: Deliverable: OAuth provider
Commit 2: Deliverable: Token validation
Commit 3: Deliverable: Session middleware

❌ BAD:
Commit 1: OAuth + Token + Session + some refactoring + docs update
```

---

## Documentation Synchronization

### README.md

**Update when:**

- New user-facing features added
- Installation/setup changes
- Major milestones achieved
- API usage changes

**Keep current:**

- Feature list
- Installation instructions
- Quick start guide
- Status badges (if used)

---

### API.md (or equivalent)

**Update when:**

- API endpoints added/changed/removed
- Request/response formats change
- Authentication changes
- Error codes change

**Keep current:**

- Endpoint list
- Request/response examples
- Authentication requirements
- Error handling

---

### Architecture Documentation

**Update when:**

- Module structure changes
- Dependencies added/removed
- Design patterns adopted
- System boundaries change

**Keep current:**

- System architecture diagram (if exists)
- Module descriptions
- Dependency graph
- Design decision rationale

---

## Test Synchronization

### Test Suite Maintenance

**After code changes:**

1. Add tests for new functionality
2. Update tests for changed functionality
3. Remove tests for deleted functionality
4. Verify all tests pass

**Test commit discipline:**

```
Add integration tests for planner module

- 8 new integration tests for router
- Tests cover: basic routing, fallback, edge cases
- All tests passing (147/147 unit, 32/32 integration)
- STATUS.md: Integration tests deliverable 80% complete
```

---

### Test Status Tracking

**In STATUS.md:**

```markdown
## Test Status

**Unit Tests:** 147/147 passing (100%)
**Integration Tests:** 32/32 passing (100%)
**Smoke Tests:** 5/5 passing (100%)
**Overall:** 184/184 passing (100%)

**Coverage:** 87% (target: >80%)
```

**Update after:**

- New tests added
- Tests pass/fail state changes
- Coverage changes

---

## Execution Logging

### Worker Execution Logs

**Location:** `.taskers/runs/[timestamp]/`

**Contents:**

- Worker output files (per worker)
- Execution logs
- Proposals and analysis

**Retention:**

- Keep last 10 runs
- Archive older runs (optional)
- Git-ignored (not committed)

**Usage:**

- Review worker proposals
- Debug worker failures
- Track execution history

---

### Audit Trail

**Track in DECISIONS.md:**

- What workers were deployed
- What proposals were integrated
- What architectural decisions made
- What phases completed

**Track in git log:**

- When deliverables completed
- When tests added
- When refactoring done
- When features added

---

## Anti-Patterns

### Avoid These

❌ **Documentation drift:**
- Code changes but docs don't update
- STATUS.md shows old state
- API docs out of sync with endpoints

❌ **Uncommitted state:**
- Changes in working directory not committed
- Lead handoff with uncommitted work
- Tests passing locally but not in repo

❌ **Decision amnesia:**
- Architectural changes not logged
- Worker integrations not documented
- Phase transitions not recorded

❌ **Test lag:**
- Code committed without tests
- Tests failing but commit anyway
- Coverage dropping without notice

❌ **Vague commits:**
- "Fixed stuff"
- "WIP"
- "Updates"

---

## Synchronization Checklist

### After Every Change

```markdown
- [ ] Code changes complete
- [ ] Tests added/updated
- [ ] Tests passing (100%)
- [ ] STATUS.md updated (if state changed)
- [ ] DECISIONS.md logged (if architectural)
- [ ] Documentation synced (README, API docs)
- [ ] Commit message clear and descriptive
- [ ] Git commit executed
```

---

### Before Phase Transition

```markdown
- [ ] All deliverables complete
- [ ] All tests passing
- [ ] STATUS.md reflects completion
- [ ] DECISIONS.md logs phase transition
- [ ] README updated with milestone
- [ ] Approval obtained (if required)
- [ ] Phase transition committed
```

---

### Before Handoff

```markdown
- [ ] All changes committed
- [ ] STATUS.md current
- [ ] DECISIONS.md current
- [ ] Tests passing
- [ ] No uncommitted changes (git status clean)
- [ ] Worker status documented
- [ ] Next P0 identified
```

---

## Example: Complete Sync Workflow

### Scenario: Complete Integration Tests Deliverable

**Step 1: Implement**

```bash
# Write integration tests
vim internal/tests/integration/api_test.go

# Run tests
make test
# Output: 184/184 passing
```

---

**Step 2: Update STATUS.md**

```markdown
## Current Phase Deliverables

- [x] Core API implementation ✓
- [x] Business logic ✓
- [x] Integration tests ✓ (just completed)
- [ ] Performance tuning (NEXT)

## Progress

**Current Phase:** 75% (3/4 deliverables complete)
**Tests:** 184/184 passing (100%)
```

---

**Step 3: Log Decision (if applicable)**

```markdown
## 2026-02-16: Integration Test Strategy

**Context:** Need comprehensive integration testing for API layer
**Decision:** Use table-driven tests with parallel execution
**Alternatives:**
1. Sequential tests - Rejected: too slow
2. Mock-based - Rejected: want real integration
**Consequences:**
- Fast test suite (<10s for 32 tests)
- High confidence in API correctness
```

---

**Step 4: Commit**

```bash
git add internal/tests/integration/ STATUS.md DECISIONS.md
git commit -m "Deliverable complete: Integration tests

- 32 integration tests for API layer
- All tests passing (184/184, 100%)
- Table-driven with parallel execution
- STATUS.md updated (Phase 2 now 75% complete)
- DECISIONS.md: Integration test strategy logged
- Tests: 184/184 passing"
```

---

**Step 5: Verify Sync**

```bash
# Verify clean state
git status
# Output: nothing to commit, working tree clean

# Verify tests still pass
make test
# Output: 184/184 passing

# Repository is now synced with reality
```

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo commit workflow, DECISIONS.md patterns
**Last Updated:** 2026-02-16

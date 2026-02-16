# Milestone and Deliverable System

**Purpose:** Track measurable progress and completion
**Enforces:** Objective criteria, verifiable outputs, phase gates

---

## Definitions

### Milestone

**Milestone** = Major project checkpoint with significant value delivery

**Characteristics:**

- Represents substantial progress (phase completion)
- Has clear acceptance criteria
- Requires user approval to pass
- Measurable and verifiable
- Typically aligned with phase boundaries

**Examples:**

- "MVP functional and tested"
- "API layer complete"
- "v1 release candidate ready"

---

### Deliverable

**Deliverable** = Concrete work output within a phase

**Characteristics:**

- Completable in 1-3 days
- Produces testable artifact
- Has definition of done
- Contributes to milestone
- Can be integrated independently

**Examples:**

- "Auth provider implementation"
- "Database migration scripts"
- "Unit test suite"

---

### Task

**Task** = Atomic work unit assigned to worker

**Characteristics:**

- Completable in <1 day
- Single worker scope
- Clear file/module boundaries
- Verifiable output

**Examples:**

- "Implement token validator"
- "Design API interface"
- "Write integration tests"

---

## Hierarchy

```
Project
  ├─ Milestone 1 (Phase 0 complete)
  │    ├─ Deliverable 1.1 (Build system)
  │    │    ├─ Task 1.1.1 (Makefile)
  │    │    └─ Task 1.1.2 (Scripts)
  │    ├─ Deliverable 1.2 (Test framework)
  │    └─ Deliverable 1.3 (CI pipeline)
  │
  ├─ Milestone 2 (Phase 1 complete)
  │    ├─ Deliverable 2.1 (Core API)
  │    └─ Deliverable 2.2 (API tests)
  │
  └─ Milestone 3 (v1 complete)
```

---

## Milestone Definition

### Milestone Template

```markdown
## Milestone: [Name]

**Goal:** [One sentence outcome]
**Phase:** Phase N
**Target:** [Optional date/timeline]

**Acceptance Criteria:**
- [ ] Functional criterion 1
- [ ] Functional criterion 2
- [ ] Testing criterion
- [ ] Documentation criterion
- [ ] Quality criterion

**Deliverables:**
1. Deliverable A
2. Deliverable B
3. Deliverable C

**Value Delivered:**
[What user/stakeholder can do after this milestone]

**Approval Required:** Yes/No
```

---

### Example Milestones

#### Milestone: Foundation Complete

```markdown
## Milestone: Foundation Complete

**Goal:** Repository, build, and test infrastructure operational
**Phase:** Phase 0
**Target:** Week 1

**Acceptance Criteria:**
- [ ] Build system runs successfully (make build, make test)
- [ ] Unit test framework configured
- [ ] CI pipeline green on main branch
- [ ] Code coverage reporting enabled
- [ ] Documentation structure established

**Deliverables:**
1. Makefile with build/test/clean targets
2. Test framework (testing package, mocks)
3. GitHub Actions CI workflow
4. README with build instructions

**Value Delivered:**
Developers can build, test, and verify code changes

**Approval Required:** No (foundation work)
```

---

#### Milestone: MVP Functional

```markdown
## Milestone: MVP Functional

**Goal:** Minimum viable product with core features working
**Phase:** Phase 2
**Target:** Week 4

**Acceptance Criteria:**
- [ ] All MVP features implemented per blueprint
- [ ] End-to-end workflow functional
- [ ] API contract stable (no breaking changes expected)
- [ ] Integration tests passing (100%)
- [ ] Performance acceptable (<500ms P95 latency)
- [ ] Security audit passed (no critical issues)

**Deliverables:**
1. Core feature implementations
2. API endpoints
3. Integration test suite
4. Performance benchmarks
5. Security review report

**Value Delivered:**
Users can perform core workflows end-to-end

**Approval Required:** YES (major milestone)
```

---

## Deliverable Definition

### Deliverable Template

```markdown
### Deliverable: [Name]

**Phase:** Phase N
**Owner:** Lead/Worker

**Scope:**
[What files/modules/features]

**Output:**
[What artifact is produced]

**Success Criteria:**
- [ ] Implementation complete
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed

**Testing:**
[How to verify]

**Dependencies:**
[What must exist first]

**Contributes To:**
[Which milestone this supports]
```

---

### Example Deliverables

#### Deliverable: Auth Provider Integration

```markdown
### Deliverable: Auth Provider Integration

**Phase:** Phase 1
**Owner:** Codex-Worker-1

**Scope:**
- internal/auth/provider.go
- internal/auth/oauth.go
- internal/auth/types.go
- tests/auth/provider_test.go

**Output:**
- OAuth provider interface implemented
- Token validation working
- Session creation functional

**Success Criteria:**
- [ ] Provider interface fully implemented
- [ ] OAuth flow working (login/logout/refresh)
- [ ] Token validation passing all test cases
- [ ] Unit test coverage >85%
- [ ] Integration test with mock provider passing
- [ ] API documentation updated

**Testing:**
- Unit tests: TestProviderInterface, TestTokenValidation
- Integration test: TestOAuthFlow
- Manual test: Login via OAuth provider

**Dependencies:**
- Phase 0 complete (test framework exists)
- OAuth credentials configured

**Contributes To:**
Milestone: Authentication Complete
```

---

## Progress Tracking

### In STATUS.md

**Format:**

```markdown
## Progress

**Overall:** 45% (2/5 milestones complete)

**Current Milestone:** MVP Functional (65% complete)
  - [x] Deliverable 1: Core API (COMPLETE)
  - [x] Deliverable 2: Business Logic (COMPLETE)
  - [ ] Deliverable 3: Integration Tests (IN PROGRESS)
  - [ ] Deliverable 4: Performance Tuning (NEXT)

**Phase:** Phase 2 - MVP Implementation

**Milestones:**
  - [x] Foundation Complete (Phase 0)
  - [x] Authentication Complete (Phase 1)
  - [ ] MVP Functional (Phase 2) - IN PROGRESS
  - [ ] Enhanced Features (Phase 3) - PLANNED
  - [ ] v1 Release (Phase 4) - PLANNED
```

---

### Calculation Method

**Overall progress:**

```
Overall = (Completed Milestones / Total Milestones) * 100
```

**Phase progress:**

```
Phase = (Completed Deliverables / Total Deliverables in Phase) * 100
```

**Milestone progress:**

```
Milestone = (Met Acceptance Criteria / Total Acceptance Criteria) * 100
```

---

## Acceptance Criteria

### Writing Good Criteria

**GOOD criteria (objective, measurable):**

✅ "Unit test coverage >80%"
✅ "API response time <200ms P95"
✅ "All integration tests passing (15/15)"
✅ "Zero critical security vulnerabilities"
✅ "Documentation includes API examples"

**BAD criteria (subjective, vague):**

❌ "Code quality is good"
❌ "Performance is acceptable"
❌ "Most tests passing"
❌ "Documentation is complete"

---

### Criteria Categories

#### Functional Criteria

```markdown
**Functional:**
- [ ] Feature X works as specified in blueprint
- [ ] API contract matches specification
- [ ] Edge cases handled (null inputs, empty lists, etc.)
- [ ] Error messages are user-friendly
```

#### Testing Criteria

```markdown
**Testing:**
- [ ] Unit test coverage >80%
- [ ] Integration tests passing (100%)
- [ ] Smoke tests passing (all scenarios)
- [ ] Performance tests meet SLA (<500ms P95)
- [ ] Security tests passing (OWASP top 10)
```

#### Documentation Criteria

```markdown
**Documentation:**
- [ ] API documentation generated and reviewed
- [ ] README updated with new features
- [ ] Architecture decision logged in DECISIONS.md
- [ ] Code comments for complex logic
```

#### Quality Criteria

```markdown
**Quality:**
- [ ] No regression in existing tests
- [ ] Code follows project conventions
- [ ] No new linter warnings
- [ ] Dependencies updated (no security alerts)
```

---

## Verification Process

### Deliverable Verification

**When deliverable marked complete:**

1. Lead reads deliverable success criteria
2. Lead runs tests specified in deliverable
3. Lead checks all criteria met
4. Lead updates STATUS.md
5. Lead commits with clear message

**Checklist:**

```markdown
## Deliverable Verification: [Name]

- [ ] All success criteria met
- [ ] Tests run and passing
- [ ] Output artifact exists
- [ ] Documentation updated
- [ ] STATUS.md updated
- [ ] DECISIONS.md logged (if architectural)
```

---

### Milestone Verification

**When milestone claimed complete:**

1. Lead reads milestone acceptance criteria
2. Lead runs full test suite
3. Lead verifies all deliverables complete
4. Lead generates status report
5. Lead requests user approval (if required)

**Checklist:**

```markdown
## Milestone Verification: [Name]

- [ ] All deliverables complete
- [ ] All acceptance criteria met
- [ ] Full test suite passing
- [ ] Smoke tests passing
- [ ] Documentation current
- [ ] Performance acceptable
- [ ] Security review passed (if required)
- [ ] User approval obtained (if required)
```

---

## Status Reporting

### Milestone Status Report

**Format:**

```markdown
# Milestone Status: [Name]

## Summary
- Status: IN PROGRESS / COMPLETE / BLOCKED
- Progress: 65%
- Phase: Phase 2

## Acceptance Criteria
- [x] Criterion 1 ✓
- [x] Criterion 2 ✓
- [ ] Criterion 3 (IN PROGRESS)
- [ ] Criterion 4 (NEXT)

## Deliverables
- [x] Deliverable A (COMPLETE)
- [x] Deliverable B (COMPLETE)
- [ ] Deliverable C (IN PROGRESS)

## Test Status
- Unit: 147/147 passing (100%)
- Integration: 28/32 passing (87%)
- Smoke: 3/5 passing (60%)

## Blockers
[None / List of blockers]

## Next Steps
1. Complete Deliverable C
2. Fix failing integration tests
3. Run smoke tests
4. Request approval
```

---

## Approval Gates

### When Approval Required

**Require user approval for:**

1. Major milestones (MVP, v1, v2)
2. Phase transitions
3. Breaking changes
4. Architecture decisions
5. Technology changes

**Do NOT require approval for:**

- Foundation work (Phase 0)
- Bug fixes within scope
- Test improvements
- Documentation updates

---

### Approval Process

**Lead actions:**

1. Verify milestone acceptance criteria met
2. Generate milestone status report
3. Present to user with evidence
4. **WAIT for explicit approval**
5. Log approval in DECISIONS.md
6. Advance to next milestone/phase

**User response:**

- "Approved" → Proceed
- "Conditional approval (fix X first)" → Address and re-request
- "Rejected (reason)" → Remediate and re-present

---

### Approval Log Format

```markdown
## 2026-02-16: Milestone "MVP Functional" Approved

**Context:** Phase 2 complete, all acceptance criteria met
**Evidence:**
- All deliverables complete (4/4)
- Tests passing (175/175 unit, 32/32 integration)
- Performance within SLA (P95: 180ms < 500ms target)
- Security audit: 0 critical, 2 low (acceptable)

**Decision:** Approved to advance to Phase 3
**Next Milestone:** Enhanced Features
```

---

## Tracking Tools

### STATUS.md Structure

```markdown
# Project Status

## Current State
- Phase: Phase 2 - MVP Implementation
- Milestone: MVP Functional (65% complete)
- Deliverable: Integration Tests (IN PROGRESS)

## Milestones
- [x] Foundation Complete (Phase 0)
- [x] Authentication Complete (Phase 1)
- [ ] MVP Functional (Phase 2) - 65%
- [ ] Enhanced Features (Phase 3) - 0%
- [ ] v1 Release (Phase 4) - 0%

## Phase 2 Deliverables
- [x] Core API implementation
- [x] Business logic
- [ ] Integration tests (IN PROGRESS)
- [ ] Performance tuning (NEXT)

## Test Status
- Unit: 147/147 (100%)
- Integration: 28/32 (87%)
- Smoke: 3/5 (60%)

## Active Workers
- Codex-Worker-1: Writing integration tests
- Claude-Worker-2: Performance analysis

## Next P0
Complete integration test suite
```

---

### DECISIONS.md Tracking

**Log milestone completions:**

```markdown
## 2026-02-10: Foundation Milestone Complete

**Context:** Phase 0 complete
**Deliverables:**
- Build system (Makefile)
- Test framework (testing package)
- CI pipeline (GitHub Actions)

**Acceptance:**
- All tests passing
- CI green on main
- Documentation updated

**Next:** Begin Phase 1 (Authentication)
```

---

## Anti-Patterns

### Avoid These

❌ **Vague milestones** - "Make progress on features"
❌ **Unmeasurable criteria** - "Code quality is good"
❌ **No approval gates** - Advancing phases without user consent
❌ **Scope creep** - Adding deliverables mid-phase without plan revision
❌ **False completion** - Marking done without verification
❌ **Skipping tests** - Advancing without running test suite
❌ **Documentation lag** - Not updating STATUS.md after completion

---

## Example: Complete Milestone Lifecycle

### 1. Milestone Definition

```markdown
## Milestone: Authentication Complete

**Goal:** User authentication functional
**Phase:** Phase 1
**Target:** Week 2

**Acceptance Criteria:**
- [ ] Users can sign up/login via OAuth
- [ ] Token validation working
- [ ] Session management functional
- [ ] Auth tests passing (100%)
- [ ] API docs updated

**Deliverables:**
1. OAuth provider integration
2. Token validation
3. Session middleware
4. Auth test suite
```

---

### 2. Execution

- Lead breaks into deliverables
- Lead creates worker tickets
- Workers execute tasks
- Lead integrates outputs
- Tests run after each deliverable

---

### 3. Progress Updates

**After Deliverable 1 complete:**

```markdown
## Milestone: Authentication Complete (25% complete)

**Deliverables:**
- [x] OAuth provider integration (COMPLETE)
- [ ] Token validation (NEXT)
- [ ] Session middleware (PLANNED)
- [ ] Auth test suite (PLANNED)
```

**After Deliverable 2 complete:**

```markdown
## Milestone: Authentication Complete (50% complete)

**Deliverables:**
- [x] OAuth provider integration (COMPLETE)
- [x] Token validation (COMPLETE)
- [ ] Session middleware (IN PROGRESS)
- [ ] Auth test suite (PLANNED)
```

---

### 4. Verification

**When all deliverables done:**

```markdown
## Milestone Verification: Authentication Complete

**Acceptance Criteria:**
- [x] Users can sign up/login via OAuth ✓
- [x] Token validation working ✓
- [x] Session management functional ✓
- [x] Auth tests passing (47/47) 100% ✓
- [x] API docs updated ✓

**Test Results:**
- Unit: 47/47 passing
- Integration: 8/8 passing
- Smoke: OAuth flow tested manually

**Status:** COMPLETE
```

---

### 5. Approval (if required)

```markdown
# Milestone Complete: Authentication

All acceptance criteria met. Request approval to advance to Phase 2.

**Evidence:**
- OAuth flow functional (tested)
- All tests passing (55/55)
- Documentation updated
```

**User:** "Approved"

---

### 6. Log and Advance

```markdown
## 2026-02-14: Authentication Milestone Complete

**Context:** Phase 1 complete, all acceptance criteria met
**Decision:** Approved to advance to Phase 2 (MVP Implementation)
**Deliverables:** 4/4 complete
**Tests:** 55/55 passing
```

**STATUS.md updated:**

```markdown
## Milestones
- [x] Foundation Complete (Phase 0)
- [x] Authentication Complete (Phase 1) ✓
- [ ] MVP Functional (Phase 2) - 0%
```

---

## Version

**Model Version:** 1.0
**Extracted From:** krov/repo STATUS.md milestone tracking
**Last Updated:** 2026-02-16

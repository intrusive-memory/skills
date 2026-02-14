# Sprint Supervisor

Orchestrate multi-agent sprint execution with automatic verification, retry logic, and state management.

## Overview

The Sprint Supervisor is an agentic orchestrator that breaks down complex projects into atomic sprints and dispatches background agents to execute them in parallel. It manages state, handles failures with automatic retry, and enforces dependency constraints.

**Key Features**:
- **Pre-execution pipeline**: Analyze requirements, generate execution plans, validate quality
- **Parallel execution**: Run independent work units simultaneously
- **Automatic verification**: Validate sprint completion via git state, exit criteria, and agent output
- **Fault tolerance**: Automatic retry with exponential backoff, graceful degradation
- **State persistence**: Crash-safe state management across invocations

---

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    REQUIREMENTS DOCUMENT                     │
│                  (PRD, SPEC, README, etc.)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │  /sprint-supervisor │
                  │      breakdown      │
                  └──────────┬──────────┘
                            │
                            │ Generates
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      EXECUTION_PLAN.md                       │
│  • Work units (packages/components/phases)                   │
│  • Sprints (3-7 atomic tasks each)                          │
│  • Dependencies (layers, prerequisites)                      │
│  • Entry/Exit criteria (machine-verifiable)                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │  /sprint-supervisor │
                  │       analyze       │◄─────┐
                  └──────────┬──────────┘      │
                            │                  │
                            │ Orchestrates     │
                            ▼                  │
        ┌───────────────────────────────────┐ │
        │                                   │ │
        │  Pass 1: Completeness Check       │ │
        │  • Point A → Point B coverage     │ │
        │  • Open questions detection       │ │
        │  • Gap analysis                   │ │
        │                                   │ │
        └───────────────┬───────────────────┘ │
                        │                      │
                        ▼                      │
        ┌───────────────────────────────────┐ │
        │                                   │ │
        │  Pass 2: Atomicity & Testability  │ │
        │  (delegates to evaluate)          │ │
        │  • Sprint sizing check            │ │
        │  • Verification criteria          │ │
        │  • Context budget fit             │ │
        │                                   │ │
        └───────────────┬───────────────────┘ │
                        │                      │
                        ▼                      │
        ┌───────────────────────────────────┐ │
        │                                   │ │
        │  Pass 3: Priority & Parallelism   │ │
        │  (delegates to prioritize)        │ │
        │  • Dependency graph               │ │
        │  • Priority scoring               │ │
        │  • Parallelization opportunities  │ │
        │                                   │ │
        └───────────────┬───────────────────┘ │
                        │                      │
                        ▼                      │
        ┌───────────────────────────────────┐ │
        │     ANALYSIS_REPORT.md            │ │
        │  • Diagnostic findings            │ │
        │  • Critical/recommended/optional  │ │
        │  • Auto-fix recommendations       │ │
        └───────────────┬───────────────────┘ │
                        │                      │
              ┌─────────┴─────────┐            │
              ▼                   ▼            │
    ┌─────────────────┐ ┌─────────────────┐   │
    │  /sprint-super- │ │  /sprint-super- │   │
    │    visor        │ │    visor        │   │
    │    evaluate     │ │    prioritize   │   │
    │                 │ │                 │   │
    │  Auto-fix       │ │  Auto-reorder   │   │
    │  atomicity/     │ │  sprints by     │   │
    │  testability    │ │  priority       │   │
    └────────┬────────┘ └────────┬────────┘   │
             │                   │             │
             └─────────┬─────────┘             │
                       │                       │
                       │ Optional fixes        │
                       │ modify plan ──────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              EXECUTION_PLAN.md (validated)                   │
│  • Atomic sprints (right-sized for context budget)          │
│  • Machine-verifiable exit criteria                         │
│  • Optimal execution order (priority-based)                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │  /sprint-supervisor │
              │        start        │
              └──────────┬──────────┘
                        │
                        │ Initializes
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   SUPERVISOR_STATE.md                        │
│  • Work unit states (NOT_STARTED → RUNNING → COMPLETED)    │
│  • Sprint states (PENDING → DISPATCHED → RUNNING)          │
│  • Active agents table (task IDs, output files)            │
│  • Attempt counters (for retry logic)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Event Loop
                        ▼
        ┌───────────────────────────────────┐
        │                                   │
        │  1. Dispatch background agents    │
        │     (parallel for independent     │
        │      work units)                  │
        │                                   │
        │  2. Poll for completion           │
        │     (non-blocking TaskOutput)     │
        │                                   │
        │  3. Verify sprint outcome         │
        │     • Git commits                 │
        │     • Exit criteria commands      │
        │     • Agent output signals        │
        │                                   │
        │  4. Handle results                │
        │     • SUCCESS → next sprint       │
        │     • PARTIAL → continuation      │
        │     • FAILURE → retry (backoff)   │
        │     • FATAL → BLOCKED (manual)    │
        │                                   │
        │  5. Update state                  │
        │     (SUPERVISOR_STATE.md)         │
        │                                   │
        │  6. Check dependency gates        │
        │     (unlock new work units)       │
        │                                   │
        └───────────────┬───────────────────┘
                        │
                        │ Repeat until
                        ▼
        ┌───────────────────────────────────┐
        │   All work units COMPLETED        │
        │        — or —                     │
        │   All active work units BLOCKED   │
        └───────────────────────────────────┘
```

---

## Commands

### Pre-execution Commands

| Command | Purpose | Input | Output |
|---------|---------|-------|--------|
| `breakdown` | Generate execution plan from requirements | Requirements doc | EXECUTION_PLAN.md |
| `analyze` | Three-pass comprehensive analysis | EXECUTION_PLAN.md | ANALYSIS_REPORT.md |
| `evaluate` | Auto-fix atomicity/testability issues | EXECUTION_PLAN.md | EXECUTION_PLAN.md (modified) |
| `prioritize` | Auto-reorder sprints by priority | EXECUTION_PLAN.md | EXECUTION_PLAN.md (modified) |

### Execution Commands

| Command | Purpose | State Required |
|---------|---------|----------------|
| `start` | Begin execution from scratch | EXECUTION_PLAN.md |
| `resume` | Continue after stop/failure | SUPERVISOR_STATE.md |
| `status` | Report current progress | SUPERVISOR_STATE.md |
| `stop` | Graceful shutdown (drain → wait → kill) | SUPERVISOR_STATE.md |
| `killall` | Emergency stop (immediate termination) | SUPERVISOR_STATE.md |

---

## Execution Plan Format

The Sprint Supervisor uses dynamic plan detection — it adapts to various formats. However, the recommended structure includes:

### Minimal Plan Structure

```markdown
# EXECUTION_PLAN.md — Project Name

## Work Units

| Work Unit | Directory | Sprints | Layer | Dependencies |
|-----------|-----------|---------|-------|-------------|
| Core      | src/core  | 3       | 1     | none        |
| API       | src/api   | 2       | 2     | Core        |

## Sprints

### Sprint 1: Foundation Types

**Entry criteria**:
- [ ] First sprint — no prerequisites

**Tasks**:
1. Create User model in `src/core/models/User.swift`
2. Create Session protocol in `src/core/protocols/Session.swift`
3. Add unit tests for User model

**Exit criteria**:
- [ ] Files exist: `User.swift`, `Session.swift`, `UserTests.swift`
- [ ] Build passes: `swift build`
- [ ] Tests pass: `swift test`

### Sprint 2: Authentication Service

**Entry criteria**:
- [ ] Sprint 1 complete (types exist)

**Tasks**:
1. Implement AuthService in `src/core/services/AuthService.swift`
2. Implement credential validation
3. Add auth tests

**Exit criteria**:
- [ ] File exists: `AuthService.swift`
- [ ] Build passes: `swift build`
- [ ] All tests pass: `swift test`

### Sprint 3: API Endpoints

**Entry criteria**:
- [ ] Sprint 2 complete (auth service exists)

**Tasks**:
1. Create login endpoint in `src/api/routes/auth.swift`
2. Create logout endpoint
3. Add integration tests

**Exit criteria**:
- [ ] File exists: `auth.swift`
- [ ] Server starts: `swift run`
- [ ] Integration tests pass: `swift test --filter APITests`

## Summary

| Metric | Value |
|--------|-------|
| Work units | 2 |
| Total sprints | 3 |
| Dependency structure | layers |
```

### Detection Heuristics

The supervisor detects plan structure using these patterns:

#### Work Units

1. **Table with columns**: `Work Unit`, `Package`, `Component`, `Module` → each row is a work unit
2. **Section headers**: Multiple `## <Name>` sections with sprint definitions → each section is a work unit
3. **Single project**: No multi-unit structure detected → entire plan is one work unit

#### Sprints

1. **Sprint headers**: `## Sprint N:` or `### Sprint N:` → each header is a sprint
2. **Sprint table**: Columns like `Sprint`, `Name`, `Description` → each row is a sprint
3. **Compound sprints**: `Sprint 2a`, `Sprint 2b` → sequential sub-sprints

#### Dependencies

1. **Layer column**: Work units with `Layer` values → higher layers wait for lower layers
2. **Dependencies column**: Explicit `depends on` or `requires` → cross-unit dependencies
3. **Entry criteria**: References to prior sprints → sequential dependencies

#### Entry/Exit Criteria

1. **Checklist items**: `- [ ]` under "Entry Criteria" or "Exit Criteria" headings
2. **Fenced code blocks**: Shell commands to execute for verification
3. **Assertions**: Boolean checks on state

### Task Types

The supervisor classifies sprints by task type to determine dispatch and verification strategy:

| Type | Indicators | Verification Strategy |
|------|-----------|----------------------|
| `code` | "Write", "Create", "Implement", "Build", "Fix" + code artifacts | Git commit + build/test pass |
| `command` | "Run", "Execute", "Deploy", explicit shell commands | Command output matches expected |
| `background` | "Start", "Kick off", "nohup", estimated duration > 1hr | Process confirmed running |
| `deferred` | "Wait for", "Monitor", external dependency | Poll verification until success |
| `manual` | "Listen", "Visit", "Check browser", human judgment | Report findings, user confirms |

### Best Practices

**Atomic sprints**:
- 3-7 tasks per sprint (not too narrow, not too broad)
- Single concern (one subsystem or feature)
- Clear artifact (named, specific outputs)
- Bounded scope (fits within context budget, default 50 turns)

**Machine-verifiable exit criteria**:
- At least one command-based check (`swift build`, `swift test`, `test -f path`)
- Avoid vague language ("works correctly" → "tests pass: `swift test`")
- Cover all tasks (every task has corresponding exit criterion)

**Dependency clarity**:
- Explicit entry criteria referencing prior sprint outputs
- Layer-based grouping for cross-unit dependencies
- Foundation work in early sprints (types, interfaces, shared utilities)

**Priority-optimized order**:
- High-risk sprints early (new technology, external APIs)
- Foundation sprints before dependent sprints
- Bottleneck sprints as early as dependencies allow

---

## Usage Examples

### Generate plan from requirements

```bash
/sprint-supervisor breakdown /path/to/PRD.md
```

**Output**: `EXECUTION_PLAN.md` with work units, sprints, entry/exit criteria

### Analyze plan quality

```bash
/sprint-supervisor analyze
```

**Output**: `ANALYSIS_REPORT.md` with three-pass diagnostic:
- Pass 1: Completeness (Point A → Point B coverage, gaps, open questions)
- Pass 2: Atomicity & Testability (sprint sizing, verification criteria)
- Pass 3: Priority & Parallelism (dependency graph, execution order)

### Auto-fix quality issues

```bash
# Fix atomicity/testability issues (split oversized sprints, add exit criteria)
/sprint-supervisor evaluate

# Reorder sprints by priority (foundation-first, risk-early, bottleneck-early)
/sprint-supervisor prioritize
```

### Execute the plan

```bash
# Start from scratch
/sprint-supervisor start

# Check status (non-blocking)
/sprint-supervisor status

# Graceful shutdown (drain → wait → kill)
/sprint-supervisor stop

# Resume after stop or failure
/sprint-supervisor resume

# Emergency stop (immediate kill all agents)
/sprint-supervisor killall
```

### Typical workflow

```bash
# 1. Generate plan
/sprint-supervisor breakdown requirements.md

# 2. Analyze quality
/sprint-supervisor analyze

# 3. Auto-fix issues (optional)
/sprint-supervisor evaluate
/sprint-supervisor prioritize

# 4. Re-analyze to verify (optional)
/sprint-supervisor analyze

# 5. Execute
/sprint-supervisor start

# 6. Monitor (in another session)
watch -n 5 '/sprint-supervisor status'

# 7. If issues arise
/sprint-supervisor stop      # graceful shutdown
# ... fix issues manually ...
/sprint-supervisor resume    # continue execution
```

---

## State Machine

### Work Unit States

```
NOT_STARTED ──(start)──► RUNNING ──(all sprints done)──► COMPLETED
                           │
                           ├──(stop)──► STOPPING ──(agents finish)──► STOPPED
                           │
                           ├──(sprint FATAL)──► BLOCKED
                           │
                           └──(killall)──► KILLED

STOPPED ──(resume)──► RUNNING
BLOCKED ──(resume)──► RUNNING
KILLED ──(resume)──► RUNNING
```

### Sprint States

```
PENDING ──(dispatch)──► DISPATCHED ──(agent starts)──► RUNNING
                                                          │
                          ┌───────────────────────────────┤
                          │                               │
                          ▼                               ▼
                      COMPLETED                       PARTIAL
                                                          │
                                                          └──(continuation)──► DISPATCHED

RUNNING ──(failure)──► BACKOFF ──(retry)──► DISPATCHED
                         │
                         └──(max retries)──► FATAL
```

---

## Verification Cascade

When a sprint agent completes, the supervisor determines the outcome using these sources (in order):

1. **Agent output**: Explicit success/failure/partial signals
2. **Git state**: New commits, uncommitted changes
3. **Progress files**: PROGRESS.md, TODO.md status markers
4. **Exit criteria commands**: Execute and check return codes
5. **Task-type-specific checks**: Based on sprint classification

**Verdict**:
- SUCCESS: Any source shows definitive success, no contradictions → sprint COMPLETED
- PARTIAL: Progress made but work remains → sprint PARTIAL (continuation)
- FAILURE: No progress, agent exited → sprint BACKOFF (retry)
- FATAL: Max retries exhausted → sprint FATAL, work unit BLOCKED

---

## Error Recovery

All recovery follows the state machine — no ad-hoc fixes:

| Scenario | State Transition | Action |
|----------|------------------|--------|
| Sprint succeeds | RUNNING → COMPLETED | Dispatch next sprint (if any) |
| Sprint partial | RUNNING → PARTIAL | Dispatch continuation with remaining work |
| Sprint fails | RUNNING → BACKOFF | Increment attempt, dispatch retry with failure context |
| Max retries hit | BACKOFF → FATAL | Work unit → BLOCKED, report to user |
| Context exhaustion | RUNNING → PARTIAL or BACKOFF | Verify progress, dispatch continuation or retry |
| Agent unresponsive | (after 10 empty polls) → BACKOFF | Terminate agent, increment attempt |
| Deferred wait | (poll until condition met) → COMPLETED | Do not increment attempt (waiting ≠ failure) |

---

## Files Generated

| File | Created By | Purpose |
|------|-----------|---------|
| `EXECUTION_PLAN.md` | `breakdown` | Work units, sprints, entry/exit criteria |
| `ANALYSIS_REPORT.md` | `analyze` | Three-pass diagnostic report |
| `SUPERVISOR_STATE.md` | `start` | Persistent state (work unit/sprint states, active agents, attempt counters) |

---

## Configuration

### Context Budget

Default: 50 turns per sprint agent

Set with `--max-turns=N` flag:

```bash
/sprint-supervisor analyze --max-turns=100
/sprint-supervisor evaluate --max-turns=100
```

Calibration: ~15-20 productive actions per 50 turns (rest is overhead)

### Max Retries

Default: 3 attempts per sprint

Configured in `SUPERVISOR_STATE.md`:

```markdown
## Configuration
- max_retries: 3
```

### Polling Cadence

- Poll interval: Non-blocking checks with `timeout: 5000ms`
- Unresponsive threshold: 10 consecutive empty polls → terminate agent
- Deferred wait threshold: 20 unsuccessful polls → report to user

---

## Advanced Features

### Parallel Execution

Work units in the same layer with no shared dependencies execute in parallel:

```markdown
| Work Unit | Layer | Dependencies |
|-----------|-------|-------------|
| Core      | 1     | none        |
| Utils     | 1     | none        |  ← Both execute in parallel
| API       | 2     | Core        |
```

### Compound Sprints

Sequential sub-sprints for complex work:

```markdown
### Sprint 2a: API Client
...

### Sprint 2b: API Integration
**Entry criteria**:
- [ ] Sprint 2a complete
...
```

Sprint 2a must complete before 2b starts.

### Background Tasks

Sprints that launch long-running processes:

```markdown
**Exit criteria**:
- [ ] Process is running: `pgrep -f "server.py"`
```

Sprint completes once process starts — does not wait for process to finish.

### Deferred Tasks

Sprints waiting on external conditions:

```markdown
**Exit criteria**:
- [ ] Deployment succeeded: `curl https://api.example.com/health`
```

Supervisor polls verification command until success — does not fail after retries.

---

## Troubleshooting

### Plan won't parse

- Ensure work units have distinct names
- Verify sprint numbering (1, 2, 3 or 1a, 1b, 2a)
- Check entry/exit criteria formatting (`- [ ]` checkboxes)

### Sprint keeps failing

- Check `SUPERVISOR_STATE.md` Decisions Log for failure details
- Review agent output files (paths in Active Agents table)
- Verify entry criteria are met before sprint starts
- Ensure exit criteria are achievable (not too strict)

### Work unit stuck in BLOCKED

- Sprint hit FATAL after max retries
- Manual intervention needed
- Fix underlying issue, then run `/sprint-supervisor resume`

### Execution too slow

- Check if work units are serialized unnecessarily (layer structure)
- Review `ANALYSIS_REPORT.md` Pass 3 for parallelization opportunities
- Run `/sprint-supervisor prioritize` to optimize order

### Context exhaustion

- Sprints are too large (too many tasks/files)
- Run `/sprint-supervisor analyze` to identify oversized sprints
- Run `/sprint-supervisor evaluate` to auto-split oversized sprints
- Or increase context budget: `--max-turns=100`

---

## Architecture

The Sprint Supervisor is a **state machine orchestrator**, not a code generator:

**What it does**:
- Parse execution plans (any markdown format)
- Dispatch background agents (one per sprint)
- Poll for completion (non-blocking)
- Verify outcomes (git state, exit criteria, agent output)
- Manage state transitions (deterministic state machine)
- Handle errors (retry with backoff, escalate to FATAL)

**What it doesn't do**:
- Write production code (agents do this)
- Write tests (agents do this)
- Override dependencies (enforces plan constraints)
- Skip verification (always validates sprint completion)
- Modify execution plan during execution (plan is immutable during `start`/`resume`)

**Design principles**:
- **Event-at-a-time processing**: Handle one completion event, update state, dispatch next
- **State transitions drive dispatch**: Reactive, not imperative (sprint enters PENDING → gets dispatched)
- **Write state before dispatching**: Crash-safe (state never lost)
- **Verification cascade**: Multiple sources of truth (agent output, git, files, commands)
- **Graceful degradation**: PARTIAL → continuation, FAILURE → retry, FATAL → BLOCKED

---

## License

Part of the Anthropic Claude Code package collection.

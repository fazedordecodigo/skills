# Canonical MCP Debugging Framework

Systematic debugging and automation workflow for Serena with n8n-mcp and other tools.

## Operating Doctrine

| Rule | Practice |
|------|----------|
| Tools-first | Use MCP tools for file/code/workflow state. No manual guessing. |
| No "done" without proof | Done = validation passed + artifacts updated + checkpoint announced |
| Explicit source of truth | Pick ONE: scripts/contract, live system, DB schema. Don't blend. |
| Prevent amnesia | Every phase produces files + memory entries |
| Dry-run before mutation | validateOnly + atomic first for any changes |
| Failures drive next steps | Capture fail state, then fix. No summaries. |

## Artifact System

All artifacts in `<PROJECT_ROOT>/_CLAUDE_INPUT/`:

| Artifact | File | Purpose |
|----------|------|---------|
| Working set manifest | `RepoMap.md` | What's staged, what's missing |
| Source-of-truth contract | `BEHAVIOR_CONTRACT.md` | Exact expected behavior/output |
| Snapshot (before) | `<SYSTEM>_SNAPSHOT_BEFORE.json` | Proof of starting state |
| Parity grid | `PARITY_GRID.md` | Rule-by-rule mismatch map |
| Update plan (dry-run) | `<SYSTEM>_UPDATE_PLAN.json` | Atomic ops for validation |
| Snapshot (after) | `<SYSTEM>_SNAPSHOT_AFTER.json` | Proof of end state |
| Report | `PARITY_REPORT.md` | Changes + rule satisfied |
| Fail capture | `ERROR_<SYSTEM>.json` | Exact error payload |

**Serena Memories:**
- `BEHAVIOR_CONTRACT` - Strict rules: schema, blocks, null rules
- `PARITY_FINAL` - Final proof criteria + re-validation method

## Canonical Workflow Phases

### Phase A: Reset & Lock

1. Force tools-first mode
2. Lock project path via `activate_project`
3. Confirm working set exists via `list_dir`
4. Announce checkpoint

### Phase B: Behavior Contract

1. Read scripts/docs defining expected behavior
2. Use `search_for_pattern` for key terms
3. Create `BEHAVIOR_CONTRACT.md` via `create_text_file`
4. Save condensed rules via `write_memory`

### Phase C: Mutation Strategy

| Condition | Strategy |
|-----------|----------|
| Live edits reliable | Live-edit (preferred) |
| Read-only or flaky | File-first export/edit/import |

### Phase D: Snapshot → Parity Grid

1. Snapshot current state
2. Build `PARITY_GRID.md` mapping:
   - Contract requirement
   - Current state (node + json path)
   - Match (Y/N)
   - Exact fix needed
   - Required operations

### Phase E: Update Plan (Dry-Run)

1. Convert parity fixes to atomic operations
2. Set `validateOnly: true`, `atomic: true`
3. Execute dry-run
4. If fail: capture error, correct plan, repeat
5. Proceed only when dry-run passes

### Phase F: Apply + Validate

1. Apply with `validateOnly: false`, `atomic: true`
2. Run validation
3. Capture after-snapshot
4. Update parity grid with actual results

### Phase G: Memory Hardening

1. Update contract/grid with actual truth
2. Write/overwrite memory with final state
3. Include: source locations, validation method, final rules

### Phase H: Failure Patterns

| Failure Type | Response |
|--------------|----------|
| Schema mismatch | Pull DB schema → map fields → update mapping |
| Format errors | Audit executions → enforce conversion rules → re-run |
| Provider issues | Locate config nodes → update endpoints → prove before/after |

## Prompt Templates

### SESSION BOOTSTRAP
```
RULES:
- No apologies, no explanations, no commentary unless requested
- No claims without tool-verified evidence
- Use Serena tools whenever possible

PHASE 0 - SERENA LOCK-ON
1) get_current_config
2) activate_project "<PROJECT_PATH>" (if not active)
3) check_onboarding_performed
   - if NOT onboarded: run onboarding, then list_memories
4) list_memories
5) read_memory for relevant memories

OUTPUT: Active project path, Onboarding status, Memories read (names only)
```

### INPUT TRIAGE + CONTRACT
```
PHASE 1 - TRIAGE + BEHAVIOR CONTRACT

1) list_dir "_CLAUDE_INPUT" (recursive)
2) read_file "_CLAUDE_INPUT/RepoMap.md"
3) read_file primary implementation files
4) Build BEHAVIOR_CONTRACT.md with:
   - Required inputs
   - Required outputs
   - Invariants
   - Validation procedure
5) create_text_file "_CLAUDE_INPUT/BEHAVIOR_CONTRACT.md"
6) write_memory "BEHAVIOR_CONTRACT"

OUTPUT: Files read, Contract location, Validation checklist
```

### EXECUTION LOOP
```
PHASE 2 - EXECUTE IN LOOPS

Loop rules:
- Before edits: think_about_collected_information
- Before done: think_about_whether_you_are_done
- If drift: think_about_task_adherence

For each fix:
A) Acquire: search_for_pattern / read_file / symbol tools
B) Plan: ChangePlan table (target, change, reason, validation)
C) Apply: Serena line/symbol editing tools
D) Validate: Run system validation
E) Persist: summarize_changes, write_memory

OUTPUT: ChangePlan table, Edits performed, Validation results, Memory names
```

### HARD RESET (Rogue Recovery)
```
STOP. You are off-task.

1) think_about_task_adherence
2) read_memory "BEHAVIOR_CONTRACT"
3) Re-state current objective in 1 sentence
4) Next 3 tool-bound actions only

OUTPUT: Objective sentence, Next 3 actions
```

## Definition of "Done"

| Criteria | Required Proof |
|----------|----------------|
| System validates | Validation tool pass |
| No runtime errors | Successful execution |
| Contract aligned | `BEHAVIOR_CONTRACT.md` matches final state |
| Parity grid closed | All Match=Y (or explicitly accepted deltas) |
| Memory updated | Final memory reflects reality |

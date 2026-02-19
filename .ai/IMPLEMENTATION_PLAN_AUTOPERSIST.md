# Implementation Plan: Automatic Persistence

> Status: **COMPLETE** — All items implemented and verified (18/18 self-check tests pass).

## What Exists (Final State)

### Memory Core (`engine/memory_core/`)
- **api.py** — Public `SessionMemory` class. Only file imported from outside the package.
- **store_sqlite.py** — SQLite backend with WAL mode, schema, message/fact/summary CRUD, purge, events, meta.
- **search_fts.py** — FTS5 search with automatic LIKE fallback.
- **policy.py** — Policy loader from YAML, per-namespace enforcement (persist mode, retention, roles, denylist).
- **redact.py** — Pattern-based redaction (API keys, bearer tokens, secrets). Built-in + user denylist.
- **packs.py** — Export/import memory packs (directory or zip, manifest + JSONL + checksums).
- **models.py** — Pure dataclasses: Message, Fact, Summary, NamespacePolicy, MemoryPolicy.
- **util.py** — Distillation prompt builders (strings only, no model calls).

### Auto-Persistence Hooks (`engine/ai_run.py`)
- **`run_loop()`** — Full orchestrator loop with automatic persistence:
  - Persists every user input and command response to session memory (orchestrator namespace)
  - Auto-imports from `.ai_runtime/import_inbox/` on startup
  - Auto-exports session memory pack to `.ai_runtime/memory_packs/` on graceful exit
  - Re-renders `STATUS.md` on exit
  - Checks distillation interval every N turns (signals orchestrator, no model calls)
  - Logs state-changing commands as canonical events

### Canonical Persistence
- **`ai git-sync`** — Commits only whitelisted `.ai/` paths, never `.ai_runtime/`
- **`STATUS.md`** — Auto-updated on status, git-sync, and run-loop exit
- **`DECISIONS.md`** — Append-only decision log
- **Reconciliation** — Canonical YAML ingested into SQLite; hash-based change detection

### Policy Template (`templates/.ai/state/memory_policy.yaml`)
- Per-namespace persist modes: `full`, `summary_only`, `distilled_only`, `none`
- `auto_export_on_exit: true`, `auto_import_inbox: true`
- Global + namespace denylist regex patterns
- Retention days, max messages, max facts, distillation interval, allowed roles

### CLI (`engine/ai`)
- `ai init`, `ai run`, `ai status`, `ai validate`, `ai git-sync`, `ai migrate`
- `ai export-memory`, `ai import-memory`, `ai rehydrate-db`
- `ai memory export/import/purge` (session memory advanced commands)

### Runtime Directories (`.ai_runtime/`)
- `session/` — memory.db (session memory SQLite)
- `import_inbox/` — Drop zone for auto-import on startup
- `memory_packs/` — Auto-exported packs on exit
- `logs/`, `memory_pack_cache/` — Working directories

## Self-Check Coverage (18 tests)

| # | Test | Status |
|---|------|--------|
| 1 | Project root detection | PASS |
| 2 | Init creates structure | PASS |
| 3 | DB creation + ingest | PASS |
| 4 | Export/import roundtrip | PASS |
| 5 | Git-sync whitelist | PASS |
| 6 | Schema validation | PASS |
| 7 | Status rendering | PASS |
| 8 | Init no-overwrite | PASS |
| 9 | Session memory DB init + CRUD | PASS |
| 10 | Session memory FTS fallback | PASS |
| 11 | Session memory redaction | PASS |
| 12 | Session memory pack roundtrip | PASS |
| 13 | Session memory policy enforcement | PASS |
| 14 | Auto-import from inbox | PASS |
| 15 | Auto-export pack | PASS |
| 16 | Distillation check | PASS |
| 17 | STATUS.md auto-update | PASS |
| 18 | Init creates autopersist dirs | PASS |

## Architecture Boundaries

- **memory_core/** is decoupled behind `SessionMemory` API — extractable to its own repo
- **No LLM calls** in memory_core — model-agnostic, returns plain `{role, content}` messages
- **No API keys required** — works with any model interface
- **Canonical state** (`.ai/`) is git-committed; runtime state (`.ai_runtime/`) is gitignored
- **Memory packs** are portable context accelerators, not committed by default

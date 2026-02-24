# Scaffold AI — Engine

The engine provides the CLI and runtime for Scaffold AI.

## Requirements

- Python 3.10+
- [PyYAML](https://pypi.org/project/PyYAML/) (`pip install pyyaml`)
- Git (for git-sync and version detection)
- SQLite3 (included in Python stdlib)

## Installation

This skeleton is designed to be used as a **git submodule** inside your project:

`vendor/` is reserved for package-manager outputs (for example Go vendoring). Use `scaffold/scaffold-ai` as the canonical system-layer submodule path.

```bash
# Add as submodule
git submodule add <skeleton-repo-url> scaffold/scaffold-ai

# Or clone directly for standalone use
git clone <skeleton-repo-url> scaffold/scaffold-ai
```

## Usage

All commands are run from your **project root**, not the skeleton directory:

```bash
# Initialize — creates .ai/ (canonical state) and .ai_runtime/ (local cache)
python scaffold/scaffold-ai/engine/ai init

# Check status
python scaffold/scaffold-ai/engine/ai status

# Start interactive orchestrator loop
python scaffold/scaffold-ai/engine/ai run

# Export memory pack for portability
python scaffold/scaffold-ai/engine/ai export-memory --out pack.zip

# Import memory pack on another machine
python scaffold/scaffold-ai/engine/ai import-memory --in pack.zip

# Rebuild local DB from canonical YAML (if DB is corrupted or missing)
python scaffold/scaffold-ai/engine/ai rehydrate-db

# Validate YAML files against schemas
python scaffold/scaffold-ai/engine/ai validate

# Commit only canonical state files to git
python scaffold/scaffold-ai/engine/ai git-sync
```

## Migrating Existing Repos (legacy `vendor/scaffold-ai`)

If an existing repo still uses `vendor/scaffold-ai`, the canonical path has moved to `scaffold/scaffold-ai` to avoid Go vendor collisions.

```bash
# Preview the migration (no changes)
ai init --migrate-submodule --dry-run

# Apply the migration (explicit + idempotent)
ai init --migrate-submodule

# Verify
ai validate
ai status
```

If the legacy submodule has local changes, preserve them first, then migrate manually:

```bash
git mv vendor/scaffold-ai scaffold/scaffold-ai
git submodule sync -- scaffold/scaffold-ai
python scaffold/scaffold-ai/engine/ai init
```

## Architecture

### Source of Truth
- `.ai/state/*.yaml` — canonical state (committed to repo)
- `.ai/STATUS.md`, `.ai/DECISIONS.md` — derived views (committed)
- `.ai/METADATA.yaml` — project metadata (committed)

### Local Runtime (gitignored)
- `.ai_runtime/ai.db` — SQLite derived cache
- `.ai_runtime/logs/` — runtime logs
- `.ai_runtime/session/` — session data
- `.ai_runtime/memory_pack_cache/` — exported packs

### Precedence
1. `.ai/state/*.yaml` ALWAYS wins
2. SQLite DB is rebuilt from canonical on conflict
3. Markdown outputs are regenerated from canonical/DB

### Single-Writer Policy
- Only the Orchestrator writes canonical state
- Workers are read-only to the repository
- Workers produce patchsets/artifacts, never direct edits

## Directory Layout

```
project-root/
├── scaffold/scaffold-ai/          # Scaffold AI (submodule)
│   ├── engine/
│   │   ├── ai                   # CLI entrypoint
│   │   ├── ai_init.py           # Initialization
│   │   ├── ai_run.py            # Command dispatcher
│   │   ├── ai_state.py          # State load/save/reconcile
│   │   ├── ai_db.py             # SQLite helpers
│   │   ├── ai_git.py            # Git sync
│   │   ├── ai_memory.py         # Export/import packs
│   │   ├── ai_validate.py       # Schema validation
│   │   └── self_check.py        # Sanity tests
│   ├── schemas/                 # JSON schemas
│   └── templates/.ai/           # Template files
├── .ai/                         # Canonical state (committed)
│   ├── state/
│   │   ├── team.yaml
│   │   ├── board.yaml
│   │   ├── approvals.yaml
│   │   └── commands.yaml
│   ├── core/                    # Policy docs
│   ├── prompts/                 # Orchestrator + role prompts
│   ├── STATUS.md
│   ├── DECISIONS.md
│   ├── RUNBOOK.md
│   └── METADATA.yaml
└── .ai_runtime/                 # Local cache (gitignored)
    ├── ai.db
    ├── logs/
    ├── session/
    └── memory_pack_cache/
```

## Self-Check

Run the built-in sanity tests:

```bash
python scaffold/scaffold-ai/engine/self_check.py
```

## Extending

### Adding New Commands
1. Add the command to `templates/.ai/state/commands.yaml`
2. Implement the handler function in `engine/ai_run.py`
3. Register it in the `HANDLERS` dict

### Adding New Roles
Edit `.ai/state/team.yaml` or use the onboarding flow during `ai init`.

### Custom Approval Triggers
Edit `.ai/state/approvals.yaml` to add new triggers with required approvals.

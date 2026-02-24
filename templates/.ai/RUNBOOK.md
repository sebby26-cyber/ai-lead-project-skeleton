# Scaffold AI Runbook

## Getting Started

1. Initialize the AI team: `ai init`
2. Check status: `ai status`
3. Run the orchestrator: `ai run`

## Commands Reference

| Command | Description |
|---------|-------------|
| `ai init` | Initialize `.ai/` and `.ai_runtime/` in the project |
| `ai run` | Start the orchestrator loop |
| `ai status` | Generate a status report |
| `ai export-memory [--out path]` | Export memory pack |
| `ai import-memory --in path` | Import memory pack |
| `ai rehydrate-db` | Rebuild DB from canonical YAML |
| `ai validate` | Validate YAML against schemas |
| `ai git-sync` | Commit canonical state files |

## Source of Truth

- **Canonical state**: `.ai/state/*.yaml` (committed to repo)
- **Local runtime**: `.ai_runtime/` (gitignored, never committed)
- **SQLite DB**: `.ai_runtime/ai.db` (derived cache, rebuildable)

If there is ever a conflict, canonical YAML always wins. The DB can be rebuilt at any time with `ai rehydrate-db`.

## Memory Pack

The memory pack (`ai export-memory`) is a portable snapshot of local runtime events and derived state. It is **not** a replacement for canonical state — it carries history and context.

To transfer context to another machine:
1. `ai export-memory --out pack.zip` on source
2. Copy `pack.zip` to destination
3. `ai import-memory --in pack.zip` on destination
4. Canonical `.ai/state/*.yaml` remains authoritative

## Single-Writer Policy

- Only the Orchestrator writes canonical state files.
- Workers are strictly read-only to the repository.
- Workers produce outputs as patchsets/artifacts under `.ai/runs/`.
- Workers never run `git commit` or `git push`.

## Submodule Usage

This skeleton is designed to be used as a git submodule:

```bash
git submodule add <repo-url> scaffold/scaffold-ai
python scaffold/scaffold-ai/engine/ai init
python scaffold/scaffold-ai/engine/ai status
```

`vendor/` is reserved for package-manager outputs (for example Go vendoring). Keep the Scaffold AI system layer under `scaffold/`, not `vendor/`.

## Migration (legacy `vendor/scaffold-ai`)

If your repo still uses the old legacy submodule path:

```bash
# Preview (no changes)
ai init --migrate-submodule --dry-run

# Apply (explicit, idempotent)
ai init --migrate-submodule

# Verify
ai validate
ai status
```

If the legacy submodule has local changes, automation will refuse to move it. In that case, preserve your changes first, then run:

```bash
git mv vendor/scaffold-ai scaffold/scaffold-ai
git submodule sync -- scaffold/scaffold-ai
ai init
ai validate
```

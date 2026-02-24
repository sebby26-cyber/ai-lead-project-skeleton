from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from engine import ai_init, ai_validate
from engine.submodule_paths import CANONICAL_SUBMODULE_PATH, LEGACY_SUBMODULE_PATH


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = REPO_ROOT / "engine" / "ai"


def _run_cli(*args: str) -> str:
    result = subprocess.run(
        [sys.executable, str(CLI_PATH), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


class SubmodulePathMigrationTests(unittest.TestCase):
    def test_cli_help_uses_canonical_submodule_examples(self) -> None:
        out = _run_cli("--help")
        self.assertIn(f"python {CANONICAL_SUBMODULE_PATH}/engine/ai init", out)
        self.assertIn(f"python {CANONICAL_SUBMODULE_PATH}/engine/ai status", out)

    def test_help_json_troubleshooting_uses_canonical_full_path(self) -> None:
        data = json.loads(_run_cli("help", "--json"))
        tips = data.get("troubleshooting", [])
        joined = "\n".join(tips)
        self.assertIn(f"python {CANONICAL_SUBMODULE_PATH}/engine/ai", joined)

    def test_validate_submodule_path_policy_flags_legacy_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".ai").mkdir()
            (root / ".ai" / "METADATA.yaml").write_text(
                f"submodule_path: {LEGACY_SUBMODULE_PATH}\n"
            )
            (root / ".gitmodules").write_text(
                f'[submodule "scaffold-ai"]\n\tpath = {LEGACY_SUBMODULE_PATH}\n'
            )
            (root / LEGACY_SUBMODULE_PATH).mkdir(parents=True)

            errors = ai_validate.validate_submodule_path_policy(root)

            self.assertTrue(errors)
            self.assertTrue(any(LEGACY_SUBMODULE_PATH in e for e in errors))
            self.assertTrue(any(CANONICAL_SUBMODULE_PATH in e for e in errors))

    def test_validate_submodule_path_policy_passes_canonical_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".ai").mkdir()
            (root / ".ai" / "METADATA.yaml").write_text(
                f"submodule_path: {CANONICAL_SUBMODULE_PATH}\n"
            )
            (root / ".gitmodules").write_text(
                f'[submodule "scaffold-ai"]\n\tpath = {CANONICAL_SUBMODULE_PATH}\n'
            )
            (root / CANONICAL_SUBMODULE_PATH).mkdir(parents=True)

            errors = ai_validate.validate_submodule_path_policy(root)
            self.assertEqual(errors, [])

    def test_migrate_legacy_submodule_dry_run_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / LEGACY_SUBMODULE_PATH).mkdir(parents=True)

            out = ai_init._migrate_legacy_submodule(root, dry_run=True)

            self.assertIn(LEGACY_SUBMODULE_PATH, out)
            self.assertIn(CANONICAL_SUBMODULE_PATH, out)
            self.assertIn("Dry-run only", out)

    def test_migrate_legacy_submodule_is_idempotent_when_already_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / CANONICAL_SUBMODULE_PATH).mkdir(parents=True)

            out = ai_init._migrate_legacy_submodule(root, dry_run=False)
            self.assertIn("already uses canonical path", out)


if __name__ == "__main__":
    unittest.main()

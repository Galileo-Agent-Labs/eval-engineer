#!/usr/bin/env python3
"""Installer checks for the Eval Engineer skill CLI."""

from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from eval_engineer_installer import cli  # noqa: E402


def run_cli(args: list[str]) -> int:
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        return cli.main(args)


class EvalEngineerInstallerTest(unittest.TestCase):
    def test_project_install_copies_codex_and_claude_skill_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "sample-project"
            project_dir.mkdir()

            result = run_cli(["install", "--project-dir", str(project_dir)])

            self.assertEqual(result, 0)
            for base in (project_dir / ".agents", project_dir / ".claude"):
                for skill_name in cli.SKILL_NAMES:
                    skill_dir = base / "skills" / skill_name
                    self.assertTrue((skill_dir / "SKILL.md").is_file(), skill_dir)
                self.assertTrue((base / "skills" / "eval-dataset" / "SKILL.md").is_file())
                core_dir = base / "skills" / "eval-engineer"
                self.assertTrue((core_dir / "references" / "tokenomics-rca.md").is_file())
                self.assertTrue((core_dir / "scripts" / "summarize_debug_packet.py").is_file())
                self.assertTrue((core_dir / "scripts" / "fetch_log_stream_packet.py").is_file())

    def test_log_stream_fetcher_is_a_required_core_script(self) -> None:
        self.assertIn("scripts/fetch_log_stream_packet.py", cli.CORE_REQUIRED_FILES)

    def test_project_install_scaffolds_galileo_workspace_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "sample-project"
            config_path = project_dir / ".galileo" / "config.yml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("agent_type: custom\n", encoding="utf-8")

            result = run_cli(["install", "--target", "codex", "--project-dir", str(project_dir)])

            self.assertEqual(result, 0)
            self.assertTrue((project_dir / ".galileo" / "current").is_dir())
            self.assertTrue((project_dir / ".galileo" / "eval-dataset").is_dir())
            self.assertTrue((project_dir / ".galileo" / "sessions").is_dir())
            self.assertTrue((project_dir / ".galileo" / "learnings.md").is_file())
            self.assertEqual(config_path.read_text(encoding="utf-8"), "agent_type: custom\n")

    def test_project_install_requires_force_for_existing_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "sample-project"
            project_dir.mkdir()

            first = run_cli(["install", "--target", "codex", "--project-dir", str(project_dir)])
            second = run_cli(["install", "--target", "codex", "--project-dir", str(project_dir)])

            self.assertEqual(first, 0)
            self.assertEqual(second, 1)

    def test_check_validates_installed_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "sample-project"
            project_dir.mkdir()

            install_result = run_cli(["install", "--target", "claude", "--project-dir", str(project_dir)])
            check_result = run_cli(["check", "--target", "claude", "--project-dir", str(project_dir)])

            self.assertEqual(install_result, 0)
            self.assertEqual(check_result, 0)

    def test_user_codex_install_uses_codex_home_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            codex_home = Path(tmpdir) / "codex-home"

            with patch.dict("os.environ", {"CODEX_HOME": str(codex_home)}):
                install_result = run_cli(["install", "--target", "codex", "--scope", "user"])
                check_result = run_cli(["check", "--target", "codex", "--scope", "user"])

            self.assertEqual(install_result, 0)
            self.assertEqual(check_result, 0)
            for skill_name in cli.SKILL_NAMES:
                skill_dir = codex_home / "skills" / skill_name
                self.assertTrue((skill_dir / "SKILL.md").is_file(), skill_dir)


if __name__ == "__main__":
    unittest.main()

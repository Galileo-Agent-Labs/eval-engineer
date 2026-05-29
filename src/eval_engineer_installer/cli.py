"""Install the Eval Engineer skill bundle into Codex and Claude Code projects."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Iterator, Sequence


SKILL_NAMES = (
    "eval-engineer",
    "eval-setup",
    "eval-fetch",
    "eval-dataset",
    "eval-measure",
    "eval-diagnose",
    "eval-cost",
    "eval-audit",
)
CORE_SKILL_NAME = "eval-engineer"
CORE_REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/metrics.md",
    "references/tokenomics-rca.md",
    "references/galileo-url-intake.md",
    "references/evidence-provenance.md",
    "references/eval-datasets.md",
    "scripts/summarize_debug_packet.py",
    "scripts/compare_tokenomics_packets.py",
    "scripts/parse_galileo_url.py",
    "scripts/fetch_log_stream_packet.py",
)
PROJECT_SCAFFOLD_DIRS = (
    ".galileo/current",
    ".galileo/eval-dataset",
    ".galileo/sessions",
)
PROJECT_SCAFFOLD_FILES = {
    ".galileo/config.yml": """# Eval Engineer project configuration.
# Fill this in as the app and Galileo evidence shape become clear.
agent_type: unknown
metrics: []
editable_files: []
blocked_files: []
verification_commands: []
evidence:
  baseline_packet: .galileo/current/debug-packet.json
  verification_packet: .galileo/current/verification-debug-packet.json
""",
    ".galileo/learnings.md": """# Eval Engineer Learnings

Capture durable RCA, measurement, and tokenomics patterns here. Keep
case-specific notes in `.galileo/current/` or dated reports.
""",
}


class InstallError(RuntimeError):
    """Raised when installation cannot proceed safely."""


@dataclass(frozen=True)
class Destination:
    agent: str
    scope: str
    skills_root: Path


def _repo_skills_source() -> Path | None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "skills"
        if all((candidate / skill_name / "SKILL.md").is_file() for skill_name in SKILL_NAMES):
            return candidate
    return None


@contextmanager
def _skills_source() -> Iterator[Path]:
    local_source = _repo_skills_source()
    if local_source is not None:
        yield local_source
        return

    bundled = resources.files("eval_engineer_installer").joinpath("bundled", "skills")
    with resources.as_file(bundled) as bundled_path:
        yield bundled_path


def _validate_skill_dir(path: Path, required_files: tuple[str, ...] = ("SKILL.md",)) -> None:
    missing = [relative for relative in required_files if not (path / relative).is_file()]
    if missing:
        formatted = ", ".join(missing)
        raise InstallError(f"{path} is missing required skill files: {formatted}")


def _validate_skills_root(path: Path) -> None:
    for skill_name in SKILL_NAMES:
        required = CORE_REQUIRED_FILES if skill_name == CORE_SKILL_NAME else ("SKILL.md",)
        _validate_skill_dir(path / skill_name, required)


def _selected_agents(target: str) -> list[str]:
    if target == "both":
        return ["codex", "claude"]
    return [target]


def _codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex")).expanduser()


def _destinations(target: str, scope: str, project_dir: Path) -> list[Destination]:
    project_dir = project_dir.expanduser().resolve()
    destinations: list[Destination] = []
    for agent in _selected_agents(target):
        if scope == "project":
            base = project_dir / (".agents" if agent == "codex" else ".claude") / "skills"
        elif agent == "codex":
            base = _codex_home() / "skills"
        else:
            base = Path.home() / ".claude" / "skills"
        destinations.append(Destination(agent=agent, scope=scope, skills_root=base))
    return destinations


def _copy_ignore(_directory: str, names: list[str]) -> set[str]:
    ignored = {".DS_Store", "__pycache__"}
    return {name for name in names if name in ignored or name.endswith(".pyc")}


def _remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _scaffold_project(project_dir: Path, dry_run: bool = False) -> None:
    project_dir = project_dir.expanduser().resolve()
    for relative in PROJECT_SCAFFOLD_DIRS:
        path = project_dir / relative
        if dry_run:
            print(f"would ensure directory: {path}")
        else:
            path.mkdir(parents=True, exist_ok=True)

    for relative, content in PROJECT_SCAFFOLD_FILES.items():
        path = project_dir / relative
        if dry_run:
            action = "keep existing" if path.exists() else "create"
            print(f"would {action} file: {path}")
            continue
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")


def install(args: argparse.Namespace) -> int:
    destinations = _destinations(args.target, args.scope, args.project_dir)
    with _skills_source() as source_root:
        _validate_skills_root(source_root)

        for destination in destinations:
            for skill_name in SKILL_NAMES:
                source = source_root / skill_name
                path = destination.skills_root / skill_name
                if args.dry_run:
                    print(f"would install {destination.agent} {destination.scope}: {path}")
                    continue

                if path.exists() or path.is_symlink():
                    if not args.force:
                        raise InstallError(
                            f"{path} already exists; rerun with --force to replace it"
                        )
                    _remove_existing(path)

                path.parent.mkdir(parents=True, exist_ok=True)
                if args.link:
                    if _repo_skills_source() is None:
                        raise InstallError("--link requires running from a source checkout")
                    path.symlink_to(source)
                else:
                    shutil.copytree(source, path, ignore=_copy_ignore)

                required = CORE_REQUIRED_FILES if skill_name == CORE_SKILL_NAME else ("SKILL.md",)
                _validate_skill_dir(path, required)
                print(f"installed {destination.agent} {destination.scope}: {path}")

        if args.scope == "project" and not args.no_scaffold:
            _scaffold_project(args.project_dir, dry_run=args.dry_run)
            if not args.dry_run:
                print(f"prepared project workspace: {args.project_dir.expanduser().resolve() / '.galileo'}")

    if not args.dry_run:
        print("restart Codex or Claude Code if the skills directory was not already watched")
    return 0


def check(args: argparse.Namespace) -> int:
    destinations = _destinations(args.target, args.scope, args.project_dir)
    for destination in destinations:
        for skill_name in SKILL_NAMES:
            path = destination.skills_root / skill_name
            required = CORE_REQUIRED_FILES if skill_name == CORE_SKILL_NAME else ("SKILL.md",)
            _validate_skill_dir(path, required)
            print(f"ok {destination.agent} {destination.scope}: {path}")
    if args.scope == "project":
        galileo_dir = args.project_dir.expanduser().resolve() / ".galileo"
        if galileo_dir.is_dir():
            print(f"ok project workspace: {galileo_dir}")
        else:
            print(f"warning: project workspace missing: {galileo_dir}", file=sys.stderr)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eval-engineer",
        description="Install the Eval Engineer Galileo skill for Codex and Claude Code.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install", help="install the skill")
    add_shared_arguments(install_parser)
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing installed skill directory",
    )
    install_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print destinations without writing files",
    )
    install_parser.add_argument(
        "--link",
        action="store_true",
        help="symlink from a local source checkout instead of copying files",
    )
    install_parser.add_argument(
        "--no-scaffold",
        action="store_true",
        help="do not create the minimal .galileo project workspace for project-scope installs",
    )
    install_parser.set_defaults(func=install)

    check_parser = subparsers.add_parser("check", help="validate an installed skill")
    add_shared_arguments(check_parser)
    check_parser.set_defaults(func=check)

    return parser


def add_shared_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--target",
        choices=("codex", "claude", "both"),
        default="both",
        help="which agent skill location to install into",
    )
    parser.add_argument(
        "--scope",
        choices=("project", "user"),
        default="project",
        help="install into the current project or the user's global skill folder",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="project root for project-scope installs",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except InstallError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

"""
Shared helpers for the repository test suite.

Public API: load_validator, isolated_root, write_file, and artifact builders used
by unit and integration tests.

Side effects: creates temporary directories and mutates the imported validator
module globals inside an isolated context manager. It never writes inside the
repository working tree.
"""
from __future__ import annotations

import contextlib
import importlib.util
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validation" / "validate_config.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLI_PACKAGE = REPO_ROOT / "packages" / "ote_cli"

if str(CLI_PACKAGE) not in sys.path:
    sys.path.insert(0, str(CLI_PACKAGE))

AGENT_ROLES = [
    "coordinator",
    "planner",
    "researcher",
    "architect",
    "backend-developer",
    "frontend-developer",
    "database-specialist",
    "code-reviewer",
    "test-engineer",
    "security-reviewer",
    "performance-analyst",
    "documentation-engineer",
]

GIT_DENY_RULES = [
    "git add*",
    "git stage*",
    "git commit*",
    "git -C * add*",
    "git -C * stage*",
    "git -C * commit*",
    "git -c * add*",
    "git -c * stage*",
    "git -c * commit*",
    "git stash*",
    "git reset*",
    "git checkout*",
    "git clean*",
]


def load_validator() -> ModuleType:
    """
    Import the repository validator as a fresh module instance.
    """
    spec = importlib.util.spec_from_file_location("ote_validate_config", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load validator from {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def isolated_root(validator: ModuleType) -> Iterator[Path]:
    """
    Point the validator at a temporary repository root and reset its state.
    """
    original_root = validator.ROOT
    with tempfile.TemporaryDirectory(prefix="ote-test-") as directory:
        root = Path(directory)
        validator.ROOT = root
        reset_state(validator)
        try:
            yield root
        finally:
            validator.ROOT = original_root
            reset_state(validator)


def reset_state(validator: ModuleType) -> None:
    """
    Clear accumulated errors, warnings, and counters.
    """
    validator.errors.clear()
    validator.warnings.clear()
    validator.checked = 0


def write_file(root: Path, relative: str, content: str) -> Path:
    """
    Write content under root, creating parent directories as needed.
    """
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def agent_text(role: str, *, mode: str = "subagent", description: str = "Test agent.", deny_git: bool = True) -> str:
    """
    Build a provenance-complete agent document for fixtures.
    """
    lines = [
        "---",
        "# Provenance",
        "# source: https://example.com/upstream",
        "# author: Fixture Author",
        "# author_url: https://example.com/author",
        "# upstream_path: agents/example.md",
        "# upstream_commit: 0000000000000000000000000000000000000000",
        "# retrieved: 2026-11-12",
        "# license: MIT",
        "# modified: fixture only",
        f"description: {description}",
        f"mode: {mode}",
        "permissions:",
        "  - action: edit",
        '    resource: "*"',
        "    effect: allow",
    ]
    if deny_git:
        for resource in GIT_DENY_RULES:
            lines.append("  - action: shell")
            lines.append(f'    resource: "{resource}"')
            lines.append("    effect: deny")
    lines.append("---")
    lines.append("")
    lines.append(f"# {role}")
    lines.append("")
    lines.append("Fixture body.")
    lines.append("")
    return "\n".join(lines)


def skill_text(name: str, *, description: str = "Fixture skill used by tests.") -> str:
    """
    Build a skill document with complete provenance metadata.
    """
    return "\n".join(
        [
            "---",
            f"name: {name}",
            f"description: {description}",
            "metadata:",
            '  author: "Fixture Author"',
            '  author_url: "https://example.com/author"',
            '  source: "https://example.com/upstream"',
            '  upstream_path: "skills/example/SKILL.md"',
            '  upstream_commit: "0000000000000000000000000000000000000000"',
            '  retrieved: "2026-11-12"',
            '  license: "MIT"',
            '  modified: "fixture only"',
            "---",
            "",
            f"# {name}",
            "",
            "Fixture body.",
            "",
        ]
    )


def command_text(agent: str, *, description: str = "Fixture command.") -> str:
    """
    Build a command document with complete provenance metadata.
    """
    return "\n".join(
        [
            "---",
            "# Provenance",
            "# source: https://example.com/upstream",
            "# author: Fixture Author",
            "# author_url: https://example.com/author",
            "# upstream_path: commands/example.md",
            "# upstream_commit: 0000000000000000000000000000000000000000",
            "# retrieved: 2026-11-12",
            "# license: MIT",
            "# modified: fixture only",
            f"description: {description}",
            f"agent: {agent}",
            "---",
            "",
            "Fixture body.",
            "",
        ]
    )


def registry_text(entries: list[tuple[str, str]]) -> str:
    """
    Build a provenance registry with local paths for the given id and path pairs.
    """
    lines = ["version: 1", 'updated: "2026-11-12"', "", "sources:", "  fixture:", '    repository: "https://example.com/upstream"', '    commit: "0000000000000000000000000000000000000000"', '    license: "MIT"', '    owner: "Fixture Author"', '    author: "Fixture Author"', '    author_url: "https://example.com/author"', "", "agents:"]
    for identifier, local in entries:
        lines.extend(
            [
                f"  - id: {identifier}",
                f'    local: "{local}"',
                "    source: fixture",
                '    upstream_path: "agents/example.md"',
                '    upstream_commit: "0000000000000000000000000000000000000000"',
                '    license: "MIT"',
                '    author: "Fixture Author"',
                '    author_url: "https://example.com/author"',
                '    retrieved: "2026-11-12"',
                '    modified: "fixture only"',
            ]
        )
    lines.append("")
    return "\n".join(lines)

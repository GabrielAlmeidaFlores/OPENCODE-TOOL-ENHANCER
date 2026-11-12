"""
Spec-driven development artifacts for ``ote spec``.

Public API: :func:`create`, :func:`list_specs`, :func:`plan`, and :func:`verify`.

Each spec lives under ``specs/<slug>/`` with four Markdown artifacts:
requirements, design, tasks, and evidence. Every task must reference an
acceptance criterion and every criterion must have evidence.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .paths import OteError

FILES = ("requirements.md", "design.md", "tasks.md", "evidence.md")
CRITERION = re.compile(r"^- \[[ xX]\] (AC-\d+):\s*(.+)$")
TASK = re.compile(r"^- \[[ xX]\] (T-\d+):\s*(.+?)\s*\(criterion:\s*(AC-\d+)\)\s*$")
EVIDENCE = re.compile(r"^- (AC-\d+):\s*(.+)$")


def slug(feature: str) -> str:
    """
    Convert a feature name into a directory-safe slug.
    """
    value = re.sub(r"[^a-z0-9]+", "-", feature.lower()).strip("-")
    if not value:
        raise OteError("feature name must contain letters or digits")
    return value[:60]


def _placeholders(text: str) -> bool:
    """
    Return True when a line still contains an angle-bracket placeholder.
    """
    return "<" in text and ">" in text


def create(root: Path, feature: str, criteria: list[str]) -> Path:
    """
    Create the four spec artifacts for a feature.
    """
    directory = root / "specs" / slug(feature)
    if directory.exists():
        raise OteError(f"spec already exists: {directory}")
    cleaned = [item.strip() for item in criteria if item.strip()]
    invalid = [item for item in cleaned if _placeholders(item)]
    if invalid:
        raise OteError("criteria must not contain angle-bracket placeholders")
    directory.mkdir(parents=True)
    if cleaned:
        criterion_lines = [f"- [ ] AC-{index}: {text}" for index, text in enumerate(cleaned, start=1)]
    else:
        criterion_lines = ["- [ ] AC-1: <describe observable behavior>"]
    (directory / "requirements.md").write_text(
        f"""# Requirements: {feature}

## Goals

Describe the outcome this change must produce.

## Acceptance Criteria

Every criterion is binary and testable.

{chr(10).join(criterion_lines)}

## Non-Goals

List what this change does not do.
""",
        encoding="utf-8",
    )
    (directory / "design.md").write_text(
        f"""# Design: {feature}

## Components

List the modules, interfaces, and data flow.

## Decisions

Record trade-offs and rejected alternatives.

## Risks

List failure modes and mitigations.
""",
        encoding="utf-8",
    )
    (directory / "tasks.md").write_text(
        f"""# Tasks: {feature}

Each task must name the criterion it satisfies.

- [ ] T-1: <describe the smallest verifiable task> (criterion: AC-1)
""",
        encoding="utf-8",
    )
    (directory / "evidence.md").write_text(
        f"""# Evidence: {feature}

Record the command and observed result for every criterion.

- AC-1: <command or artifact that proves the criterion>
""",
        encoding="utf-8",
    )
    return directory


def list_specs(root: Path) -> list[dict[str, Any]]:
    """
    Return the spec directories and whether the four artifacts exist.
    """
    directory = root / "specs"
    if not directory.is_dir():
        return []
    results = []
    for path in sorted(item for item in directory.iterdir() if item.is_dir()):
        missing = [name for name in FILES if not (path / name).is_file()]
        results.append(
            {
                "name": path.name,
                "path": str(path),
                "complete": not missing,
                "missing": missing,
            }
        )
    return results


def _read(path: Path) -> str:
    """
    Read an artifact, failing with a clear message when it is absent.
    """
    if not path.is_file():
        raise OteError(f"missing spec artifact: {path}")
    return path.read_text(encoding="utf-8")


def _criteria(text: str) -> dict[str, str]:
    """
    Parse acceptance criteria, rejecting placeholders and duplicates.
    """
    results: dict[str, str] = {}
    for line in text.splitlines():
        match = CRITERION.match(line.strip())
        if not match:
            continue
        identifier, description = match.group(1), match.group(2).strip()
        if _placeholders(description):
            continue
        if identifier in results:
            raise OteError(f"duplicate criterion: {identifier}")
        results[identifier] = description
    return results


def _tasks(text: str) -> list[dict[str, str]]:
    """
    Parse tasks and their criterion references.
    """
    results: list[dict[str, str]] = []
    for line in text.splitlines():
        match = TASK.match(line.strip())
        if not match:
            continue
        description = match.group(2).strip()
        if _placeholders(description):
            continue
        results.append({"id": match.group(1), "description": description, "criterion": match.group(3)})
    return results


def _evidence(text: str) -> dict[str, str]:
    """
    Parse evidence entries keyed by criterion.
    """
    results: dict[str, str] = {}
    for line in text.splitlines():
        match = EVIDENCE.match(line.strip())
        if not match:
            continue
        value = match.group(2).strip()
        if _placeholders(value):
            continue
        if match.group(1) in results:
            raise OteError(f"duplicate evidence for {match.group(1)}")
        results[match.group(1)] = value
    return results


def plan(root: Path, feature: str) -> dict[str, Any]:
    """
    Validate requirements and task mapping before implementation.
    """
    directory = root / "specs" / slug(feature)
    criteria = _criteria(_read(directory / "requirements.md"))
    tasks = _tasks(_read(directory / "tasks.md"))
    issues: list[str] = []
    if not criteria:
        issues.append("no acceptance criteria found")
    if not tasks:
        issues.append("no tasks found")
    for task in tasks:
        if task["criterion"] not in criteria:
            issues.append(f"{task['id']} references unknown {task['criterion']}")
    covered = {task["criterion"] for task in tasks}
    for identifier in criteria:
        if identifier not in covered:
            issues.append(f"{identifier} has no task")
    return {
        "feature": slug(feature),
        "path": str(directory),
        "criteria": criteria,
        "tasks": tasks,
        "issues": issues,
        "status": "ok" if not issues else "fail",
    }


def verify(root: Path, feature: str) -> dict[str, Any]:
    """
    Verify tasks and evidence against the acceptance criteria.
    """
    directory = root / "specs" / slug(feature)
    missing = [name for name in FILES if not (directory / name).is_file()]
    if missing:
        raise OteError(f"missing spec artifacts: {', '.join(missing)}")
    base = plan(root, feature)
    evidence = _evidence(_read(directory / "evidence.md"))
    issues = list(base["issues"])
    for identifier in base["criteria"]:
        if identifier not in evidence:
            issues.append(f"{identifier} has no evidence")
    for identifier in evidence:
        if identifier not in base["criteria"]:
            issues.append(f"evidence references unknown {identifier}")
    return {
        "feature": base["feature"],
        "path": base["path"],
        "criteria": len(base["criteria"]),
        "tasks": len(base["tasks"]),
        "evidence": len(evidence),
        "issues": issues,
        "status": "ok" if not issues else "fail",
    }

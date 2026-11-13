"""
Spec-driven development artifacts for ``toolwright spec``.

Public API: :func:`create_spec_artifacts`, :func:`list_specs`,
:func:`validate_spec_plan`, and :func:`verify_spec_evidence`.

Each spec lives under ``specs/<slug>/`` with four Markdown artifacts:
requirements, design, tasks, and evidence. Every task must reference an
acceptance criterion and every criterion must have evidence.
"""
from __future__ import annotations
from .specs_strings import (
    ENCODING_UTF8,
    KEY_COMPLETE,
    KEY_CRITERIA,
    KEY_CRITERION,
    KEY_DESCRIPTION,
    KEY_EVIDENCE,
    KEY_FEATURE,
    KEY_ID,
    KEY_ISSUES,
    KEY_NAME,
    KEY_PATH,
    KEY_SPECS,
    KEY_STATUS,
    KEY_TASKS,
    SEPARATOR_COMMA_SPACE,
    STATUS_FAIL,
    STATUS_MISSING,
    STATUS_OK,
    TEXT_AC,
    TEXT_AC_1_DESCRIBE_OBSERVABLE_BEHAVIOR,
    TEXT_AC_D_S,
    TEXT_A_Z0_9,
    TEXT_CRITERIA_MUST_NOT_CONTAIN_ANGLE_BRACKET_PLACEHOLDERS,
    TEXT_DESIGN_COMPONENTS_LIST_THE_MODULES_INTERFACES_AND_DATA_FLOW_,
    TEXT_DESIGN_MD,
    TEXT_DUPLICATE_CRITERION,
    TEXT_DUPLICATE_EVIDENCE_FOR,
    TEXT_EVIDENCE_MD,
    TEXT_EVIDENCE_RECORD_THE_COMMAND_AND_OBSERVED_RESULT_FOR_EVERY_CR,
    TEXT_EVIDENCE_REFERENCES_UNKNOWN,
    TEXT_FEATURE_NAME_MUST_CONTAIN_LETTERS_OR_DIGITS,
    TEXT_HAS_NO_EVIDENCE,
    TEXT_HAS_NO_TASK,
    TEXT_MISSING_SPEC_ARTIFACT,
    TEXT_MISSING_SPEC_ARTIFACTS,
    TEXT_NO_ACCEPTANCE_CRITERIA_FOUND,
    TEXT_NO_TASKS_FOUND,
    TEXT_REFERENCES_UNKNOWN,
    TEXT_REQUIREMENTS_GOALS_DESCRIBE_THE_OUTCOME_THIS_CHANGE_MUST_PRO,
    TEXT_REQUIREMENTS_MD,
    TEXT_SPEC_ALREADY_EXISTS,
    TEXT_TASKS_EACH_TASK_MUST_NAME_THE_CRITERION_IT_SATISFIES_T_1_DES,
    TEXT_TASKS_MD,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_XX_AC_D_S,
    TEXT_XX_T_D_S_S_CRITERION_S_AC_D_S,
)

import re
from pathlib import Path
from typing import Any

from .paths import ToolWrightError

FILES = (TEXT_REQUIREMENTS_MD, TEXT_DESIGN_MD, TEXT_TASKS_MD, TEXT_EVIDENCE_MD)
CRITERION = re.compile(TEXT_XX_AC_D_S)
TASK = re.compile(TEXT_XX_T_D_S_S_CRITERION_S_AC_D_S)
EVIDENCE = re.compile(TEXT_AC_D_S)


def slugify_feature_name(feature: str) -> str:
    value = re.sub(TEXT_A_Z0_9, TEXT_TEXT, feature.lower()).strip(TEXT_TEXT)
    if not value:
        raise ToolWrightError(TEXT_FEATURE_NAME_MUST_CONTAIN_LETTERS_OR_DIGITS)
    return value[:60]


def contains_placeholder(text: str) -> bool:
    return TEXT_TEXT_2 in text and TEXT_TEXT_3 in text


def create_spec_artifacts(root: Path, feature: str, criteria: list[str]) -> Path:
    directory = root / KEY_SPECS / slugify_feature_name(feature)
    if directory.exists():
        raise ToolWrightError(TEXT_SPEC_ALREADY_EXISTS.format(directory))
    cleaned = [item.strip() for item in criteria if item.strip()]
    invalid = [item for item in cleaned if contains_placeholder(item)]
    if invalid:
        raise ToolWrightError(TEXT_CRITERIA_MUST_NOT_CONTAIN_ANGLE_BRACKET_PLACEHOLDERS)
    directory.mkdir(parents=True)
    if cleaned:
        criterion_lines = [TEXT_AC.format(index, text) for index, text in enumerate(cleaned, start=1)]
    else:
        criterion_lines = [TEXT_AC_1_DESCRIBE_OBSERVABLE_BEHAVIOR]
    (directory / TEXT_REQUIREMENTS_MD).write_text(
        TEXT_REQUIREMENTS_GOALS_DESCRIBE_THE_OUTCOME_THIS_CHANGE_MUST_PRO.format(feature, chr(10).join(criterion_lines)),
        encoding=ENCODING_UTF8,
    )
    (directory / TEXT_DESIGN_MD).write_text(
        TEXT_DESIGN_COMPONENTS_LIST_THE_MODULES_INTERFACES_AND_DATA_FLOW_.format(feature),
        encoding=ENCODING_UTF8,
    )
    (directory / TEXT_TASKS_MD).write_text(
        TEXT_TASKS_EACH_TASK_MUST_NAME_THE_CRITERION_IT_SATISFIES_T_1_DES.format(feature),
        encoding=ENCODING_UTF8,
    )
    (directory / TEXT_EVIDENCE_MD).write_text(
        TEXT_EVIDENCE_RECORD_THE_COMMAND_AND_OBSERVED_RESULT_FOR_EVERY_CR.format(feature),
        encoding=ENCODING_UTF8,
    )
    return directory


def list_specs(root: Path) -> list[dict[str, Any]]:
    directory = root / KEY_SPECS
    if not directory.is_dir():
        return []
    results = []
    for path in sorted(item for item in directory.iterdir() if item.is_dir()):
        missing = [name for name in FILES if not (path / name).is_file()]
        results.append(
            {
                KEY_NAME: path.name,
                KEY_PATH: str(path),
                KEY_COMPLETE: not missing,
                STATUS_MISSING: missing,
            }
        )
    return results


def read_spec_artifact(path: Path) -> str:
    if not path.is_file():
        raise ToolWrightError(TEXT_MISSING_SPEC_ARTIFACT.format(path))
    return path.read_text(encoding=ENCODING_UTF8)


def parse_acceptance_criteria(text: str) -> dict[str, str]:
    results: dict[str, str] = {}
    for line in text.splitlines():
        match = CRITERION.match(line.strip())
        if not match:
            continue
        identifier, description = match.group(1), match.group(2).strip()
        if contains_placeholder(description):
            continue
        if identifier in results:
            raise ToolWrightError(TEXT_DUPLICATE_CRITERION.format(identifier))
        results[identifier] = description
    return results


def parse_spec_tasks(text: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for line in text.splitlines():
        match = TASK.match(line.strip())
        if not match:
            continue
        description = match.group(2).strip()
        if contains_placeholder(description):
            continue
        results.append({KEY_ID: match.group(1), KEY_DESCRIPTION: description, KEY_CRITERION: match.group(3)})
    return results


def parse_spec_evidence(text: str) -> dict[str, str]:
    results: dict[str, str] = {}
    for line in text.splitlines():
        match = EVIDENCE.match(line.strip())
        if not match:
            continue
        value = match.group(2).strip()
        if contains_placeholder(value):
            continue
        if match.group(1) in results:
            raise ToolWrightError(TEXT_DUPLICATE_EVIDENCE_FOR.format(match.group(1)))
        results[match.group(1)] = value
    return results


def validate_spec_plan(root: Path, feature: str) -> dict[str, Any]:
    directory = root / KEY_SPECS / slugify_feature_name(feature)
    criteria = parse_acceptance_criteria(read_spec_artifact(directory / TEXT_REQUIREMENTS_MD))
    tasks = parse_spec_tasks(read_spec_artifact(directory / TEXT_TASKS_MD))
    issues: list[str] = []
    if not criteria:
        issues.append(TEXT_NO_ACCEPTANCE_CRITERIA_FOUND)
    if not tasks:
        issues.append(TEXT_NO_TASKS_FOUND)
    for task in tasks:
        if task[KEY_CRITERION] not in criteria:
            issues.append(TEXT_REFERENCES_UNKNOWN.format(task[KEY_ID], task[KEY_CRITERION]))
    covered = {task[KEY_CRITERION] for task in tasks}
    for identifier in criteria:
        if identifier not in covered:
            issues.append(TEXT_HAS_NO_TASK.format(identifier))
    return {
        KEY_FEATURE: slugify_feature_name(feature),
        KEY_PATH: str(directory),
        KEY_CRITERIA: criteria,
        KEY_TASKS: tasks,
        KEY_ISSUES: issues,
        KEY_STATUS: STATUS_OK if not issues else STATUS_FAIL,
    }


def verify_spec_evidence(root: Path, feature: str) -> dict[str, Any]:
    directory = root / KEY_SPECS / slugify_feature_name(feature)
    missing = [name for name in FILES if not (directory / name).is_file()]
    if missing:
        raise ToolWrightError(TEXT_MISSING_SPEC_ARTIFACTS.format(SEPARATOR_COMMA_SPACE.join(missing)))
    base = validate_spec_plan(root, feature)
    evidence = parse_spec_evidence(read_spec_artifact(directory / TEXT_EVIDENCE_MD))
    issues = list(base[KEY_ISSUES])
    for identifier in base[KEY_CRITERIA]:
        if identifier not in evidence:
            issues.append(TEXT_HAS_NO_EVIDENCE.format(identifier))
    for identifier in evidence:
        if identifier not in base[KEY_CRITERIA]:
            issues.append(TEXT_EVIDENCE_REFERENCES_UNKNOWN.format(identifier))
    return {
        KEY_FEATURE: base[KEY_FEATURE],
        KEY_PATH: base[KEY_PATH],
        KEY_CRITERIA: len(base[KEY_CRITERIA]),
        KEY_TASKS: len(base[KEY_TASKS]),
        KEY_EVIDENCE: len(evidence),
        KEY_ISSUES: issues,
        KEY_STATUS: STATUS_OK if not issues else STATUS_FAIL,
    }

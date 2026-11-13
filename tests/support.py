"""
Shared helpers for the repository test suite.

Public API: load_validator, isolated_root, write_file, and artifact builders used
by unit and integration tests.

Side effects: creates temporary directories and mutates the imported validator
module globals inside an isolated context manager. It never writes inside the
repository working tree.
"""
from __future__ import annotations
from tests.support_strings import (
    TEXT_CANNOT_LOAD_VALIDATOR,
    TEXT_DESCRIPTION_PREFIX,
    TEXT_MODE_PREFIX,
    TEXT_RESOURCE_PREFIX,
    TEXT_QUOTE,
    TEXT_HASH_PREFIX,
    TEXT_NAME_PREFIX,
    TEXT_AGENT_PREFIX,
    TEXT_ID_PREFIX,
    TEXT_LOCAL_PREFIX,
)
from tests.support_strings import (
    EMPTY_STRING,
    FLAG_TEXT,
    KEY_ARCHITECT,
    KEY_COORDINATOR,
    KEY_FIXTURES,
    KEY_OTE_VALIDATE_CONFIG,
    KEY_PACKAGES,
    KEY_PLANNER,
    KEY_RESEARCHER,
    KEY_SCRIPTS,
    KEY_SUBAGENT,
    KEY_TOOLWRIGHT_CLI,
    KEY_VALIDATION,
    TEXT_ACTION_EDIT,
    TEXT_ACTION_SHELL,
    TEXT_AGENTS,
    TEXT_AUTHOR_FIXTURE_AUTHOR,
    TEXT_AUTHOR_FIXTURE_AUTHOR_2,
    TEXT_AUTHOR_FIXTURE_AUTHOR_3,
    TEXT_AUTHOR_URL_HTTPS_EXAMPLE_COM_AUTHOR,
    TEXT_AUTHOR_URL_HTTPS_EXAMPLE_COM_AUTHOR_2,
    TEXT_AUTHOR_URL_HTTPS_EXAMPLE_COM_AUTHOR_3,
    TEXT_BACKEND_DEVELOPER,
    TEXT_CODE_REVIEWER,
    TEXT_COMMIT_0000000000000000000000000000000000000000,
    TEXT_DATABASE_SPECIALIST,
    TEXT_DOCUMENTATION_ENGINEER,
    TEXT_EFFECT_ALLOW,
    TEXT_EFFECT_DENY,
    TEXT_FIXTURE,
    TEXT_FIXTURE_BODY,
    TEXT_FIXTURE_COMMAND,
    TEXT_FIXTURE_SKILL_USED_BY_TESTS,
    TEXT_FRONTEND_DEVELOPER,
    TEXT_GIT_ADD,
    TEXT_GIT_CHECKOUT,
    TEXT_GIT_CLEAN,
    TEXT_GIT_COMMIT,
    TEXT_GIT_C_ADD,
    TEXT_GIT_C_ADD_2,
    TEXT_GIT_C_COMMIT,
    TEXT_GIT_C_COMMIT_2,
    TEXT_GIT_C_STAGE,
    TEXT_GIT_C_STAGE_2,
    TEXT_GIT_RESET,
    TEXT_GIT_STAGE,
    TEXT_GIT_STASH,
    TEXT_LICENSE_MIT,
    TEXT_LICENSE_MIT_2,
    TEXT_LICENSE_MIT_3,
    TEXT_METADATA,
    TEXT_MODIFIED_FIXTURE_ONLY,
    TEXT_MODIFIED_FIXTURE_ONLY_2,
    TEXT_MODIFIED_FIXTURE_ONLY_3,
    TEXT_OWNER_FIXTURE_AUTHOR,
    TEXT_PERFORMANCE_ANALYST,
    TEXT_PERMISSIONS,
    TEXT_PROVENANCE,
    TEXT_REPOSITORY_HTTPS_EXAMPLE_COM_UPSTREAM,
    TEXT_RESOURCE,
    TEXT_RETRIEVED_2026_11_12,
    TEXT_RETRIEVED_2026_11_12_2,
    TEXT_RETRIEVED_2026_11_12_3,
    TEXT_SECURITY_REVIEWER,
    TEXT_SOURCES,
    TEXT_SOURCE_FIXTURE,
    TEXT_SOURCE_HTTPS_EXAMPLE_COM_UPSTREAM,
    TEXT_SOURCE_HTTPS_EXAMPLE_COM_UPSTREAM_2,
    TEXT_TEST_AGENT,
    TEXT_TEST_ENGINEER,
    TEXT_TEXT,
    TEXT_TOOLWRIGHT_TEST,
    TEXT_UPDATED_2026_11_12,
    TEXT_UPSTREAM_COMMIT_0000000000000000000000000000000000000000,
    TEXT_UPSTREAM_COMMIT_0000000000000000000000000000000000000000_2,
    TEXT_UPSTREAM_COMMIT_0000000000000000000000000000000000000000_3,
    TEXT_UPSTREAM_PATH_AGENTS_EXAMPLE_MD,
    TEXT_UPSTREAM_PATH_AGENTS_EXAMPLE_MD_2,
    TEXT_UPSTREAM_PATH_COMMANDS_EXAMPLE_MD,
    TEXT_UPSTREAM_PATH_SKILLS_EXAMPLE_SKILL_MD,
    TEXT_UTF_8,
    TEXT_VALIDATE_CONFIG_PY,
    TEXT_VERSION_1,
)

import contextlib
import importlib.util
import sys
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / KEY_SCRIPTS / KEY_VALIDATION / TEXT_VALIDATE_CONFIG_PY
FIXTURES = Path(__file__).resolve().parent / KEY_FIXTURES
CLI_PACKAGE = REPO_ROOT / KEY_PACKAGES / KEY_TOOLWRIGHT_CLI

if str(CLI_PACKAGE) not in sys.path:
    sys.path.insert(0, str(CLI_PACKAGE))

AGENT_ROLES = [
    KEY_COORDINATOR,
    KEY_PLANNER,
    KEY_RESEARCHER,
    KEY_ARCHITECT,
    TEXT_BACKEND_DEVELOPER,
    TEXT_FRONTEND_DEVELOPER,
    TEXT_DATABASE_SPECIALIST,
    TEXT_CODE_REVIEWER,
    TEXT_TEST_ENGINEER,
    TEXT_SECURITY_REVIEWER,
    TEXT_PERFORMANCE_ANALYST,
    TEXT_DOCUMENTATION_ENGINEER,
]

GIT_DENY_RULES = [
    TEXT_GIT_ADD,
    TEXT_GIT_STAGE,
    TEXT_GIT_COMMIT,
    TEXT_GIT_C_ADD,
    TEXT_GIT_C_STAGE,
    TEXT_GIT_C_COMMIT,
    TEXT_GIT_C_ADD_2,
    TEXT_GIT_C_STAGE_2,
    TEXT_GIT_C_COMMIT_2,
    TEXT_GIT_STASH,
    TEXT_GIT_RESET,
    TEXT_GIT_CHECKOUT,
    TEXT_GIT_CLEAN,
]


def load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(KEY_OTE_VALIDATE_CONFIG, VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(TEXT_CANNOT_LOAD_VALIDATOR.format(VALIDATOR_PATH))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def isolated_root(validator: ModuleType) -> Iterator[Path]:
    original_root = validator.ROOT
    with tempfile.TemporaryDirectory(prefix=TEXT_TOOLWRIGHT_TEST) as directory:
        root = Path(directory)
        validator.ROOT = root
        reset_state(validator)
        try:
            yield root
        finally:
            validator.ROOT = original_root
            reset_state(validator)


def reset_state(validator: ModuleType) -> None:
    validator.errors.clear()
    validator.warnings.clear()
    validator.checked = 0


def write_file(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=TEXT_UTF_8)
    return path


def agent_text(role: str, *, mode: str = KEY_SUBAGENT, description: str = TEXT_TEST_AGENT, deny_git: bool = True) -> str:
    lines = [
        FLAG_TEXT,
        TEXT_PROVENANCE,
        TEXT_SOURCE_HTTPS_EXAMPLE_COM_UPSTREAM,
        TEXT_AUTHOR_FIXTURE_AUTHOR,
        TEXT_AUTHOR_URL_HTTPS_EXAMPLE_COM_AUTHOR,
        TEXT_UPSTREAM_PATH_AGENTS_EXAMPLE_MD,
        TEXT_UPSTREAM_COMMIT_0000000000000000000000000000000000000000,
        TEXT_RETRIEVED_2026_11_12,
        TEXT_LICENSE_MIT,
        TEXT_MODIFIED_FIXTURE_ONLY,
        TEXT_DESCRIPTION_PREFIX + description,
        TEXT_MODE_PREFIX + mode,
        TEXT_PERMISSIONS,
        TEXT_ACTION_EDIT,
        TEXT_RESOURCE,
        TEXT_EFFECT_ALLOW,
    ]
    if deny_git:
        for resource in GIT_DENY_RULES:
            lines.append(TEXT_ACTION_SHELL)
            lines.append(TEXT_RESOURCE_PREFIX + resource + TEXT_QUOTE)
            lines.append(TEXT_EFFECT_DENY)
    lines.append(FLAG_TEXT)
    lines.append(EMPTY_STRING)
    lines.append(TEXT_HASH_PREFIX + role)
    lines.append(EMPTY_STRING)
    lines.append(TEXT_FIXTURE_BODY)
    lines.append(EMPTY_STRING)
    return TEXT_TEXT.join(lines)


def skill_text(name: str, *, description: str = TEXT_FIXTURE_SKILL_USED_BY_TESTS) -> str:
    return TEXT_TEXT.join(
        [
            FLAG_TEXT,
            TEXT_NAME_PREFIX + name,
            TEXT_DESCRIPTION_PREFIX + description,
            TEXT_METADATA,
            TEXT_AUTHOR_FIXTURE_AUTHOR_2,
            TEXT_AUTHOR_URL_HTTPS_EXAMPLE_COM_AUTHOR_2,
            TEXT_SOURCE_HTTPS_EXAMPLE_COM_UPSTREAM_2,
            TEXT_UPSTREAM_PATH_SKILLS_EXAMPLE_SKILL_MD,
            TEXT_UPSTREAM_COMMIT_0000000000000000000000000000000000000000_2,
            TEXT_RETRIEVED_2026_11_12_2,
            TEXT_LICENSE_MIT_2,
            TEXT_MODIFIED_FIXTURE_ONLY_2,
            FLAG_TEXT,
            EMPTY_STRING,
            TEXT_HASH_PREFIX + name,
            EMPTY_STRING,
            TEXT_FIXTURE_BODY,
            EMPTY_STRING,
        ]
    )


def command_text(agent: str, *, description: str = TEXT_FIXTURE_COMMAND) -> str:
    return TEXT_TEXT.join(
        [
            FLAG_TEXT,
            TEXT_PROVENANCE,
            TEXT_SOURCE_HTTPS_EXAMPLE_COM_UPSTREAM,
            TEXT_AUTHOR_FIXTURE_AUTHOR,
            TEXT_AUTHOR_URL_HTTPS_EXAMPLE_COM_AUTHOR,
            TEXT_UPSTREAM_PATH_COMMANDS_EXAMPLE_MD,
            TEXT_UPSTREAM_COMMIT_0000000000000000000000000000000000000000,
            TEXT_RETRIEVED_2026_11_12,
            TEXT_LICENSE_MIT,
            TEXT_MODIFIED_FIXTURE_ONLY,
            TEXT_DESCRIPTION_PREFIX + description,
            TEXT_AGENT_PREFIX + agent,
            FLAG_TEXT,
            EMPTY_STRING,
            TEXT_FIXTURE_BODY,
            EMPTY_STRING,
        ]
    )


def registry_text(entries: list[tuple[str, str]]) -> str:
    lines = [TEXT_VERSION_1, TEXT_UPDATED_2026_11_12, EMPTY_STRING, TEXT_SOURCES, TEXT_FIXTURE, TEXT_REPOSITORY_HTTPS_EXAMPLE_COM_UPSTREAM, TEXT_COMMIT_0000000000000000000000000000000000000000, TEXT_LICENSE_MIT_3, TEXT_OWNER_FIXTURE_AUTHOR, TEXT_AUTHOR_FIXTURE_AUTHOR_3, TEXT_AUTHOR_URL_HTTPS_EXAMPLE_COM_AUTHOR_3, EMPTY_STRING, TEXT_AGENTS]
    for identifier, local in entries:
        lines.extend(
            [
                TEXT_ID_PREFIX + identifier,
                TEXT_LOCAL_PREFIX + local + TEXT_QUOTE,
                TEXT_SOURCE_FIXTURE,
                TEXT_UPSTREAM_PATH_AGENTS_EXAMPLE_MD_2,
                TEXT_UPSTREAM_COMMIT_0000000000000000000000000000000000000000_3,
                TEXT_LICENSE_MIT_3,
                TEXT_AUTHOR_FIXTURE_AUTHOR_3,
                TEXT_AUTHOR_URL_HTTPS_EXAMPLE_COM_AUTHOR_3,
                TEXT_RETRIEVED_2026_11_12_3,
                TEXT_MODIFIED_FIXTURE_ONLY_3,
            ]
        )
    lines.append(EMPTY_STRING)
    return TEXT_TEXT.join(lines)

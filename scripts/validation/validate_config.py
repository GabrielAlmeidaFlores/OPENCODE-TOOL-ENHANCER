#!/usr/bin/env python3
"""
Static validation for the ToolWright repository.

The validator checks required files, JSONC and YAML syntax, agent and skill
frontmatter, provenance metadata, git permission ordering, documentation
comments, external links, and the invariants described in AGENTS.md Sections 2A, 2B, and 2C. It performs no
network access unless --links is passed.

Module constants: ``REQUIRED`` lists files every checkout must contain,
``AGENT_ROLES`` and ``SKILLS`` define the expected artifact names, and
``errors``/``warnings``/``checked`` hold the current run state.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.lib.python_strings import (
    EMPTY_STRING,
    KEY_AGENT,
    KEY_AGENTS,
    KEY_COMMANDS,
    KEY_ID,
    KEY_SKILLS,
    KEY_STORE_TRUE,
    TEXT_CATALOG_REGISTRY_JSON,
    TEXT_DOCS_PROVENANCE_REGISTRY_YML,
    TEXT_HEAD,
    TEXT_MAIN,
    TEXT_PACKAGES_TOOLWRIGHT_CLI_PYPROJECT_TOML,
    TEXT_TEXT_5,
    TEXT_UTF_8,
    TEXT_VERSION,
)

import argparse
import ast
import fnmatch
import io
import json
import re
import subprocess
import sys
import tokenize
import urllib.request
from pathlib import Path

FLAG_LINKS = '--links'
FLAG_TEXT = '---'
KEY_ACTION = 'action'
KEY_ALL = 'all'
KEY_ARCHITECT = 'architect'
KEY_BIN = 'bin'
KEY_BODY = 'body'
KEY_BUILD = 'build'
KEY_CONFIGS = 'configs'
KEY_COORDINATOR = 'coordinator'
KEY_DECISIONS = 'decisions'
KEY_DENY = 'deny'
KEY_DESCRIPTION = 'description'
KEY_DOCS = 'docs'
KEY_EFFECT = 'effect'
KEY_EXAMPLES = 'examples'
KEY_FIXTURES = 'fixtures'
KEY_IGNORE = 'ignore'
KEY_LINENO = 'lineno'
KEY_MCP = 'mcp'
KEY_MODE = 'mode'
KEY_MODULE = 'module'
KEY_NAME = 'name'
KEY_NODE_MODULES = 'node_modules'
KEY_OBJ = 'obj'
KEY_PACKAGES = 'packages'
KEY_PLANNER = 'planner'
KEY_PRIMARY = 'primary'
KEY_PROMPT = 'prompt'
KEY_RESEARCHER = 'researcher'
KEY_RESOURCE = 'resource'
KEY_RUBY = 'ruby'
KEY_SCRIPTS = 'scripts'
KEY_SERVERS = 'servers'
KEY_SHELL = 'shell'
KEY_SUBAGENT = 'subagent'
KEY_TESTS = 'tests'
KEY_VERIFICATION = 'verification'
KEY_WORKING_DIRECTORY = 'working_directory'
TEXT_1 = '\\1'
TEXT_1_MODULE_IS_MISSING_A_DOCSTRING = '{}:1: module is missing a docstring'
TEXT_AGENT_MD = 'AGENT.md'
TEXT_API_DESIGN_PRINCIPLES = 'api-design-principles'
TEXT_AUTHOR = '# author:'
TEXT_AUTHOR_2 = 'author:'
TEXT_AUTHOR_URL = '# author_url:'
TEXT_AUTHOR_URL_2 = 'author_url:'
TEXT_AUTH_IMPLEMENTATION_PATTERNS = 'auth-implementation-patterns'
TEXT_A_Z0_9_A_Z0_9 = '^[a-z0-9]+(-[a-z0-9]+)*$'
TEXT_A_ZA_Z0_9_S = '^([A-Za-z0-9_-]+):\\s*(.*)$'
TEXT_BACKEND_DEVELOPER = 'backend-developer'
TEXT_BENCHMARKS_HARNESS = 'benchmarks/harness'
TEXT_BENCHMARKS_METHODOLOGY_README_MD = 'benchmarks/methodology/README.md'
TEXT_BENCHMARKS_TASKS = 'benchmarks/tasks'
TEXT_BLOCK_COMMENTS_ARE_PROHIBITED = '{}:{}: block comments are prohibited'
TEXT_CANNOT_PARSE = '{}: cannot parse: {}'
TEXT_CATALOG_SCHEMA_ENTRY_SCHEMA_JSON = 'catalog/schema/entry.schema.json'
TEXT_CHANGELOG_AUTOMATION = 'changelog-automation'
TEXT_CHECKED = 'checked: {}'
TEXT_CHECK_EXTERNAL_LINKS = 'check external links'
TEXT_CODE_REVIEWER = 'code-reviewer'
TEXT_CODE_REVIEW_EXCELLENCE = 'code-review-excellence'
TEXT_CONFIGS_OPENCODE_MINIMAL_JSONC = 'configs/opencode/minimal.jsonc'
TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC = 'configs/opencode/opencode.jsonc'
TEXT_CONFIGS_PILOTS_PILOTS_TOML = 'configs/pilots/pilots.toml'
TEXT_CONFIGS_RALPH_HATS = 'configs/ralph/hats'
TEXT_CONFIGS_RALPH_HATS_CODE_ASSIST_YML = 'configs/ralph/hats/code-assist.yml'
TEXT_CONFIGS_RALPH_RALPH_YML = 'configs/ralph/ralph.yml'
TEXT_CONTRIBUTING_MD = 'CONTRIBUTING.md'
TEXT_COORDINATOR_MUST_BE_MODE_PRIMARY = 'coordinator must be mode: primary'
TEXT_CS = '*.cs'
TEXT_DATABASE_MIGRATION = 'database-migration'
TEXT_DATABASE_SPECIALIST = 'database-specialist'
TEXT_DEPRECATED = 'Deprecated'
TEXT_DESCRIPTION_LENGTH_NOT_IN_1_1024 = '{}: description length {} not in 1..1024'
TEXT_DOCSTRING_MUST_PLACE_THE_TRIPLE_QUOTES_ON_THEIR_OWN_LINES = '{}:{}: {} docstring must place the triple quotes on their own lines'
TEXT_DOCS_ARCHITECTURE_TESTING_MD = 'docs/architecture/testing.md'
TEXT_DOCS_CATALOG_README_MD = 'docs/catalog/README.md'
TEXT_DOCS_CLI_README_MD = 'docs/cli/README.md'
TEXT_DOCS_DECISIONS_ADR_001_OPENCODE_V2_BASELINE_MD = 'docs/decisions/ADR-001-opencode-v2-baseline.md'
TEXT_DOCS_EVALS_README_MD = 'docs/evals/README.md'
TEXT_DOCS_GOVERNANCE_README_MD = 'docs/governance/README.md'
TEXT_DOCS_MD = 'docs/**/*.md'
TEXT_DOCS_MEMORY_README_MD = 'docs/memory/README.md'
TEXT_DOCS_PROFILES_README_MD = 'docs/profiles/README.md'
TEXT_DOCS_RESEARCH_BASELINE_MD = 'docs/research/baseline.md'
TEXT_DOCS_SPECS_README_MD = 'docs/specs/README.md'
TEXT_DOCS_VERIFICATION_README_MD = 'docs/verification/README.md'
TEXT_DOCUMENTATION_ENGINEER = 'documentation-engineer'
TEXT_E = '-e'
TEXT_EGG_INFO = '.egg-info'
TEXT_ERROR = 'ERROR {}'
TEXT_EVIDENCE = '**Evidence:**'
TEXT_EXPERIMENTAL = 'Experimental'
TEXT_FAILED_WITH_ERROR_S = '\nFAILED with {} error(s)'
TEXT_FRONTEND_DEVELOPER = 'frontend-developer'
TEXT_GITHUB_WORKFLOWS = '.github/workflows'
TEXT_GIT_ADD_A = 'git add -A'
TEXT_GIT_CHECKOUT_MAIN = 'git checkout main'
TEXT_GIT_CLEAN_FD = 'git clean -fd'
TEXT_GIT_COMMIT_M_X = 'git commit -m x'
TEXT_GIT_C_ADD_A = 'git -C . add -A'
TEXT_GIT_C_COMMIT_M_X = 'git -C . commit -m x'
TEXT_GIT_RESET_HARD = 'git reset --hard'
TEXT_GIT_STAGE_FILE = 'git stage file'
TEXT_GIT_STASH = 'git stash'
TEXT_HAS_NO_BODY = '{}:{}: {} has no body'
TEXT_HTTPS_S = 'https?://[^\\s)\\]>]+'
TEXT_INLINE_JSONC_COMMENTS_ARE_PROHIBITED = '{}:{}: inline JSONC comments are prohibited'
TEXT_INLINE_SHELL_COMMENTS_ARE_PROHIBITED = '{}:{}: inline shell comments are prohibited'
TEXT_INVALID_JSON = '{}: invalid JSON: {}'
TEXT_INVALID_JSONC = '{}: invalid JSONC: {}'
TEXT_INVALID_OR_MISSING_MODE = '{}: invalid or missing mode'
TEXT_INVALID_SKILL_NAME = '{}: invalid skill name'
TEXT_INVALID_YAML = '{}: invalid YAML: {}'
TEXT_JSON = '*.json'
TEXT_JSONC = '*.jsonc'
TEXT_LAST_VERIFIED = '**Last verified:**'
TEXT_LAST_VERIFIED_DATE_MUST_BE_ISO_8601 = '{}: last verified date must be ISO 8601'
TEXT_LAST_VERIFIED_S_D_4_D_2_D_2 = '\\*\\*Last verified:\\*\\*\\s*\\d{4}-\\d{2}-\\d{2}'
TEXT_LICENSE = 'LICENSE'
TEXT_LICENSE_2 = 'license:'
TEXT_LINE_COMMENTS_ARE_PROHIBITED_USE_JSDOC_OR_XML_DOCUMENTATION = '{}:{}: line comments are prohibited; use JSDoc or XML documentation'
TEXT_LINK = 'link {}: {}'
TEXT_LINK_HTTP = 'link {}: HTTP {}'
TEXT_MD = '*.md'
TEXT_MISSING_AGENT = 'missing agent: {}'
TEXT_MISSING_AGENT_2 = '{}: missing agent'
TEXT_MISSING_AUTHOR_ATTRIBUTION = '{}: missing author attribution'
TEXT_MISSING_AUTHOR_ATTRIBUTION_AUTHOR_AUTHOR_URL = '{}: missing author attribution (author/author_url)'
TEXT_MISSING_DESCRIPTION = '{}: missing description'
TEXT_MISSING_DOCS_PROVENANCE_REGISTRY_YML = 'missing docs/provenance/registry.yml'
TEXT_MISSING_DOCUMENTATION_STATUS_FIELD = '{}: missing documentation status field {}'
TEXT_MISSING_DOCUMENTATION_STATUS_VALUE = '{}: missing documentation status value'
TEXT_MISSING_FRONTMATTER = '{}: missing frontmatter'
TEXT_MISSING_JSONC_DOCUMENTATION_HEADER = '{}: missing JSONC documentation header'
TEXT_MISSING_JSON_OBJECT = '{}: missing JSON object'
TEXT_MISSING_METADATA = '{}: missing metadata.{}'
TEXT_MISSING_MODULE_DOCSTRING = '{}: missing module docstring'
TEXT_MISSING_OR_EMPTY = '{}: missing or empty {}'
TEXT_MISSING_PROVENANCE_HEADER = '{}: missing provenance header'
TEXT_MISSING_PROVENANCE_HEADER_SOURCE_UPSTREAM_COMMIT = '{}: missing provenance header (source/upstream_commit)'
TEXT_MISSING_REQUIRED_FILE = 'missing required file: {}'
TEXT_MISSING_SCHEMA = '{}: missing $schema'
TEXT_MISSING_SHELL_DOCUMENTATION_HEADER = '{}: missing shell documentation header'
TEXT_MISSING_SKILL = 'missing skill: {}'
TEXT_MUST_BE_MODE_SUBAGENT = '{} must be mode: subagent'
TEXT_NAME = '// Name:'
TEXT_NAME_2 = '# Name:'
TEXT_NAME_MUST_MATCH_DIRECTORY = '{}: name must match directory ({})'
TEXT_NON_DOCUMENTATION_PYTHON_COMMENT = '{}:{}: non-documentation Python comment'
TEXT_NO_RULE = 'no rule'
TEXT_NO_YAML_PARSER_PYYAML_OR_RUBY_YAML_SYNTAX_CHECKS_SKIPPED = 'No YAML parser (PyYAML or Ruby); YAML syntax checks skipped'
TEXT_OK = 'OK'
TEXT_PERFORMANCE_ANALYST = 'performance-analyst'
TEXT_PERMISSIONS = 'permissions:'
TEXT_PLANNED = 'Planned'
TEXT_PNG = '.png'
TEXT_PROFILES_FULL_YML = 'profiles/full.yml'
TEXT_PROFILES_MINIMAL_YML = 'profiles/minimal.yml'
TEXT_PROFILES_STANDARD_YML = 'profiles/standard.yml'
TEXT_PROVENANCE_REGISTRY_POINTS_TO_MISSING_PATH = 'provenance registry points to missing path: {}'
TEXT_PURPOSE = '// Purpose:'
TEXT_PURPOSE_2 = '# Purpose:'
TEXT_PY = '*.py'
TEXT_PYCACHE = '__pycache__'
TEXT_README_MD = 'README.md'
TEXT_REQUESTING_CODE_REVIEW = 'requesting-code-review'
TEXT_RESOLVES_TO_INSTEAD_OF_DENY_ADD_THE_GIT_DENY_RULES_AT_THE_EN = '{}: `{}` resolves to {} instead of deny; add the git deny rules at the end of permissions'
TEXT_ROOT_MUST_BE_AN_OBJECT = '{}: root must be an object'
TEXT_RYAML = '-ryaml'
TEXT_S = ',(\\s*[}\\]])'
TEXT_SCHEMA = '$schema'
TEXT_SECURITY_REVIEWER = 'security-reviewer'
TEXT_SH = '*.sh'
TEXT_SKILL_MD = 'SKILL.md'
TEXT_SOURCE = '# source:'
TEXT_SOURCE_2 = 'source:'
TEXT_SPECS_README_MD = 'specs/README.md'
TEXT_STABLE = 'Stable'
TEXT_STATUS = '**Status:**'
TEXT_STATUS_S_A_ZA_Z = '\\*\\*Status:\\*\\*\\s*([A-Za-z]+)'
TEXT_SVG = '.svg'
TEXT_SYSTEMATIC_DEBUGGING = 'systematic-debugging'
TEXT_S_EFFECT_S_S = '\\s*effect:\\s*\\"?(.*?)\\"?\\s*$'
TEXT_S_LOCAL_S = '^\\s+local:\\s*"([^"]+)"'
TEXT_S_NOQA_TYPE_PRAGMA_SHELLCHECK_FMT = '#\\s*(noqa|type:|pragma:|shellcheck|fmt:)'
TEXT_S_RESOURCE_S_S = '\\s*resource:\\s*\\"?(.*?)\\"?\\s*$'
TEXT_S_S_ACTION_S = '\\s*-\\s*action:\\s*\\"?([^\\"]+)\\"?'
TEXT_TESTS_EVALS_CASES_JSON = 'tests/evals/cases.json'
TEXT_TEST_DRIVEN_DEVELOPMENT = 'test-driven-development'
TEXT_TEST_ENGINEER = 'test-engineer'
TEXT_TEXT = '\\'
TEXT_TEXT_10 = '\t'
TEXT_TEXT_11 = '$'
TEXT_TEXT_12 = '{'
TEXT_TEXT_13 = '}'
TEXT_TEXT_14 = '#'
TEXT_TEXT_15 = '#!'
TEXT_TEXT_16 = '`'
TEXT_TEXT_17 = '*/'
TEXT_TEXT_18 = '/**'
TEXT_TEXT_19 = '/*'
TEXT_TEXT_2 = '"'
TEXT_TEXT_20 = '///'
TEXT_TEXT_21 = '"""'
TEXT_TEXT_22 = '<'
TEXT_TEXT_23 = '>'
TEXT_TEXT_24 = '.,;:`"\''
TEXT_TEXT_3 = "'"
TEXT_TEXT_4 = '/'
TEXT_TEXT_6 = '*'
TEXT_TEXT_7 = '\n---'
TEXT_TEXT_8 = ','
TEXT_TEXT_9 = ' '
TEXT_TOKENIZATION_FAILED = '{}: tokenization failed: {}'
TEXT_TOOLWRIGHT_CONFIG_TOML = '.toolwright/config.toml'
TEXT_TOOLWRIGHT_MEMORY_CATALOG_MD = '.toolwright/memory/catalog.md'
TEXT_TOOLWRIGHT_MEMORY_README_MD = '.toolwright/memory/README.md'
TEXT_TOOLWRIGHT_VALIDATOR = 'toolwright-validator'
TEXT_TS = '*.ts'
TEXT_TSX = '*.tsx'
TEXT_UNKNOWN_AGENT = '{}: unknown agent: {}'
TEXT_UNKNOWN_DOCUMENTATION_STATUS = '{}: unknown documentation status {}'
TEXT_UNTERMINATED_FRONTMATTER = '{}: unterminated frontmatter'
TEXT_UPSTREAM_COMMIT = '# upstream_commit:'
TEXT_UPSTREAM_COMMIT_2 = 'upstream_commit:'
TEXT_UPSTREAM_PATH = 'upstream_path:'
TEXT_USER_AGENT = 'User-Agent'
TEXT_V2_REQUIRES_MCP_SERVERS = '{}: V2 requires mcp.servers'
TEXT_VERIFICATION_BEFORE_COMPLETION = 'verification-before-completion'
TEXT_WARN = 'WARN  {}'
TEXT_WORKING_DIRECTORY_DOES_NOT_EXIST = '{}: working_directory does not exist: {}'
TEXT_WRITING_PLANS = 'writing-plans'
TEXT_YAML_LOAD_FILE = 'YAML.load_file({})'
TEXT_YML = '*.yml'


ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    TEXT_README_MD,
    TEXT_LICENSE,
    TEXT_VERSION,
    TEXT_CONTRIBUTING_MD,
    TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC,
    TEXT_CONFIGS_OPENCODE_MINIMAL_JSONC,
    TEXT_CONFIGS_RALPH_RALPH_YML,
    TEXT_CONFIGS_RALPH_HATS_CODE_ASSIST_YML,
    TEXT_DOCS_DECISIONS_ADR_001_OPENCODE_V2_BASELINE_MD,
    TEXT_DOCS_RESEARCH_BASELINE_MD,
    TEXT_DOCS_ARCHITECTURE_TESTING_MD,
    TEXT_DOCS_CLI_README_MD,
    TEXT_DOCS_CATALOG_README_MD,
    TEXT_DOCS_PROFILES_README_MD,
    TEXT_DOCS_VERIFICATION_README_MD,
    TEXT_DOCS_GOVERNANCE_README_MD,
    TEXT_TOOLWRIGHT_CONFIG_TOML,
    TEXT_TOOLWRIGHT_MEMORY_README_MD,
    TEXT_TOOLWRIGHT_MEMORY_CATALOG_MD,
    TEXT_SPECS_README_MD,
    TEXT_DOCS_MEMORY_README_MD,
    TEXT_DOCS_SPECS_README_MD,
    TEXT_DOCS_EVALS_README_MD,
    TEXT_CONFIGS_PILOTS_PILOTS_TOML,
    TEXT_TESTS_EVALS_CASES_JSON,
    TEXT_CATALOG_REGISTRY_JSON,
    TEXT_CATALOG_SCHEMA_ENTRY_SCHEMA_JSON,
    TEXT_PROFILES_MINIMAL_YML,
    TEXT_PROFILES_STANDARD_YML,
    TEXT_PROFILES_FULL_YML,
    TEXT_PACKAGES_TOOLWRIGHT_CLI_PYPROJECT_TOML,
    TEXT_BENCHMARKS_METHODOLOGY_README_MD,
]

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

SKILLS = [
    TEXT_TEST_DRIVEN_DEVELOPMENT,
    TEXT_SYSTEMATIC_DEBUGGING,
    TEXT_WRITING_PLANS,
    TEXT_VERIFICATION_BEFORE_COMPLETION,
    TEXT_REQUESTING_CODE_REVIEW,
    TEXT_API_DESIGN_PRINCIPLES,
    TEXT_DATABASE_MIGRATION,
    TEXT_CODE_REVIEW_EXCELLENCE,
    TEXT_AUTH_IMPLEMENTATION_PATTERNS,
    TEXT_CHANGELOG_AUTOMATION,
]

errors: list[str] = []
warnings: list[str] = []
checked = 0


def record_error(message: str) -> None:
    errors.append(message)


def record_warning(message: str) -> None:
    warnings.append(message)


def strip_jsonc(text: str) -> str:
    out: list[str] = []
    index = 0
    length = len(text)
    in_string = False
    quote = EMPTY_STRING
    while index < length:
        character = text[index]
        if in_string:
            out.append(character)
            if character == TEXT_TEXT and index + 1 < length:
                out.append(text[index + 1])
                index += 2
                continue
            if character == quote:
                in_string = False
            index += 1
            continue
        if character in (TEXT_TEXT_2, TEXT_TEXT_3):
            in_string = True
            quote = character
            out.append(character)
            index += 1
            continue
        if character == TEXT_TEXT_4 and index + 1 < length and text[index + 1] == TEXT_TEXT_4:
            while index < length and text[index] != TEXT_TEXT_5:
                index += 1
            continue
        if character == TEXT_TEXT_4 and index + 1 < length and text[index + 1] == TEXT_TEXT_6:
            index += 2
            while index + 1 < length and not (text[index] == TEXT_TEXT_6 and text[index + 1] == TEXT_TEXT_4):
                index += 1
            index += 2
            continue
        out.append(character)
        index += 1
    stripped = EMPTY_STRING.join(out)
    return re.sub(TEXT_S, TEXT_1, stripped)


def check_jsonc(path: Path) -> None:
    global checked
    checked += 1
    try:
        data = json.loads(strip_jsonc(path.read_text(encoding=TEXT_UTF_8)))
    except Exception as exc:  # noqa: BLE001 - report any parser failure as a validation error
        record_error(TEXT_INVALID_JSONC.format(path.relative_to(ROOT), exc))
        return
    if not isinstance(data, dict):
        record_error(TEXT_ROOT_MUST_BE_AN_OBJECT.format(path.relative_to(ROOT)))
        return
    if TEXT_SCHEMA not in data:
            record_warning(TEXT_MISSING_SCHEMA.format(path.relative_to(ROOT)))
    if KEY_MCP in data and KEY_SERVERS not in data[KEY_MCP]:
        record_error(TEXT_V2_REQUIRES_MCP_SERVERS.format(path.relative_to(ROOT)))


def check_yaml(path: Path) -> None:
    global checked
    checked += 1
    try:
        import yaml  # type: ignore[import-not-found] - optional dependency
    except ImportError:
        try:
            process = subprocess.run(
                [KEY_RUBY, TEXT_RYAML, TEXT_E, TEXT_YAML_LOAD_FILE.format(json.dumps(str(path)))],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            record_warning(TEXT_NO_YAML_PARSER_PYYAML_OR_RUBY_YAML_SYNTAX_CHECKS_SKIPPED)
            return
        if process.returncode != 0:
            record_error(TEXT_INVALID_YAML.format(path.relative_to(ROOT), process.stderr.strip()[:200]))
        return
    try:
        yaml.safe_load(path.read_text(encoding=TEXT_UTF_8))
    except Exception as exc:  # noqa: BLE001 - report any parser failure as a validation error
        record_error(TEXT_INVALID_YAML.format(path.relative_to(ROOT), exc))


def check_tasks() -> None:
    global checked
    for path in sorted((ROOT / TEXT_BENCHMARKS_TASKS).glob(TEXT_JSON)):
        checked += 1
        try:
            task = json.loads(path.read_text(encoding=TEXT_UTF_8))
        except Exception as exc:  # noqa: BLE001 - report any parser failure as a validation error
            record_error(TEXT_INVALID_JSON.format(path.relative_to(ROOT), exc))
            continue
        for field in (KEY_ID, KEY_PROMPT, KEY_VERIFICATION, KEY_WORKING_DIRECTORY):
            value = task.get(field)
            if not isinstance(value, str) or not value.strip():
                record_error(TEXT_MISSING_OR_EMPTY.format(path.relative_to(ROOT), field))
        working_directory = task.get(KEY_WORKING_DIRECTORY)
        if isinstance(working_directory, str) and working_directory.strip():
            if not (ROOT / working_directory).is_dir():
                record_error(TEXT_WORKING_DIRECTORY_DOES_NOT_EXIST.format(path.relative_to(ROOT), working_directory))


def read_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding=TEXT_UTF_8)
    if not text.startswith(FLAG_TEXT):
        return {}
    end = text.find(TEXT_TEXT_7, 3)
    if end == -1:
        return {}
    block = text[3:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(TEXT_A_ZA_Z0_9_S, line)
        if match:
            data[match.group(1)] = match.group(2).strip().strip(TEXT_TEXT_2).strip(TEXT_TEXT_3)
    return data


def check_agents() -> None:
    global checked
    for role in AGENT_ROLES:
        path = ROOT / KEY_AGENTS / role / TEXT_AGENT_MD
        checked += 1
        if not path.exists():
            record_error(TEXT_MISSING_AGENT.format(path.relative_to(ROOT)))
            continue
        metadata = read_frontmatter(path)
        if not metadata.get(KEY_DESCRIPTION):
            record_error(TEXT_MISSING_DESCRIPTION.format(path.relative_to(ROOT)))
        if metadata.get(KEY_MODE) not in {KEY_PRIMARY, KEY_SUBAGENT, KEY_ALL}:
            record_error(TEXT_INVALID_OR_MISSING_MODE.format(path.relative_to(ROOT)))
        if role == KEY_COORDINATOR and metadata.get(KEY_MODE) != KEY_PRIMARY:
            record_error(TEXT_COORDINATOR_MUST_BE_MODE_PRIMARY)
        if role != KEY_COORDINATOR and metadata.get(KEY_MODE) != KEY_SUBAGENT:
            record_error(TEXT_MUST_BE_MODE_SUBAGENT.format(role))


def check_skills() -> None:
    global checked
    pattern = re.compile(TEXT_A_Z0_9_A_Z0_9)
    for name in SKILLS:
        path = ROOT / KEY_SKILLS / name / TEXT_SKILL_MD
        checked += 1
        if not path.exists():
            record_error(TEXT_MISSING_SKILL.format(path.relative_to(ROOT)))
            continue
        metadata = read_frontmatter(path)
        if metadata.get(KEY_NAME) != name:
            record_error(TEXT_NAME_MUST_MATCH_DIRECTORY.format(path.relative_to(ROOT), name))
        if not pattern.match(name):
            record_error(TEXT_INVALID_SKILL_NAME.format(name))
        description = metadata.get(KEY_DESCRIPTION, EMPTY_STRING)
        if not (1 <= len(description) <= 1024):
            record_error(TEXT_DESCRIPTION_LENGTH_NOT_IN_1_1024.format(path.relative_to(ROOT), len(description)))


def check_commands() -> None:
    global checked
    for path in sorted((ROOT / KEY_COMMANDS).glob(TEXT_MD)):
        checked += 1
        metadata = read_frontmatter(path)
        if not metadata.get(KEY_DESCRIPTION):
            record_error(TEXT_MISSING_DESCRIPTION.format(path.relative_to(ROOT)))
        agent = metadata.get(KEY_AGENT)
        if not agent:
            record_error(TEXT_MISSING_AGENT_2.format(path.relative_to(ROOT)))
        elif agent not in AGENT_ROLES:
            record_error(TEXT_UNKNOWN_AGENT.format(path.relative_to(ROOT), agent))


def check_provenance() -> None:
    global checked
    registry = ROOT / TEXT_DOCS_PROVENANCE_REGISTRY_YML
    checked += 1
    if not registry.exists():
        record_error(TEXT_MISSING_DOCS_PROVENANCE_REGISTRY_YML)
        return
    text = registry.read_text(encoding=TEXT_UTF_8)

    for relative in re.findall(TEXT_S_LOCAL_S, text, re.M):
        for part in [item.strip() for item in relative.split(TEXT_TEXT_8)]:
            if not part or TEXT_TEXT_6 in part:
                continue
            checked += 1
            if not (ROOT / part).exists():
                record_error(TEXT_PROVENANCE_REGISTRY_POINTS_TO_MISSING_PATH.format(part))

    for subdirectory in (KEY_AGENTS, KEY_COMMANDS):
        for path in sorted((ROOT / subdirectory).rglob(TEXT_MD)):
            if path.name == TEXT_README_MD:
                continue
            checked += 1
            head = path.read_text(encoding=TEXT_UTF_8)[:1200]
            if TEXT_SOURCE not in head or TEXT_UPSTREAM_COMMIT not in head:
                record_error(TEXT_MISSING_PROVENANCE_HEADER_SOURCE_UPSTREAM_COMMIT.format(path.relative_to(ROOT)))
            if TEXT_AUTHOR not in head or TEXT_AUTHOR_URL not in head:
                record_error(TEXT_MISSING_AUTHOR_ATTRIBUTION_AUTHOR_AUTHOR_URL.format(path.relative_to(ROOT)))

    for path in sorted((ROOT / KEY_SKILLS).rglob(TEXT_SKILL_MD)):
        checked += 1
        head = path.read_text(encoding=TEXT_UTF_8)[:1600]
        for key in (TEXT_AUTHOR_2, TEXT_AUTHOR_URL_2, TEXT_SOURCE_2, TEXT_UPSTREAM_PATH, TEXT_UPSTREAM_COMMIT_2, TEXT_LICENSE_2):
            if key not in head:
                record_error(TEXT_MISSING_METADATA.format(path.relative_to(ROOT), key))
                break

    for path in sorted((ROOT / TEXT_CONFIGS_RALPH_HATS).glob(TEXT_YML)):
        checked += 1
        head = path.read_text(encoding=TEXT_UTF_8)[:1200]
        if TEXT_SOURCE not in head or TEXT_UPSTREAM_COMMIT not in head:
            record_error(TEXT_MISSING_PROVENANCE_HEADER.format(path.relative_to(ROOT)))
        if TEXT_AUTHOR not in head or TEXT_AUTHOR_URL not in head:
            record_error(TEXT_MISSING_AUTHOR_ATTRIBUTION.format(path.relative_to(ROOT)))


def parse_permissions(frontmatter_text: str) -> list[dict[str, str]]:
    permissions: list[dict[str, str]] = []
    current: dict[str, str] = {}
    in_permissions = False
    for line in frontmatter_text.splitlines():
        if line.startswith(TEXT_PERMISSIONS):
            in_permissions = True
            continue
        if not in_permissions:
            continue
        if line and not line.startswith((TEXT_TEXT_9, TEXT_TEXT_10)):
            break
        match = re.match(TEXT_S_S_ACTION_S, line)
        if match:
            if current:
                permissions.append(current)
            current = {KEY_ACTION: match.group(1).strip()}
            continue
        match = re.match(TEXT_S_RESOURCE_S_S, line)
        if match and current:
            current[KEY_RESOURCE] = match.group(1).strip()
            continue
        match = re.match(TEXT_S_EFFECT_S_S, line)
        if match and current:
            current[KEY_EFFECT] = match.group(1).strip()
    if current:
        permissions.append(current)
    return permissions


def check_git_permissions() -> None:
    global checked
    commands = [
        TEXT_GIT_ADD_A,
        TEXT_GIT_STAGE_FILE,
        TEXT_GIT_COMMIT_M_X,
        TEXT_GIT_C_ADD_A,
        TEXT_GIT_C_COMMIT_M_X,
        TEXT_GIT_STASH,
        TEXT_GIT_RESET_HARD,
        TEXT_GIT_CHECKOUT_MAIN,
        TEXT_GIT_CLEAN_FD,
    ]
    for role in AGENT_ROLES:
        path = ROOT / KEY_AGENTS / role / TEXT_AGENT_MD
        if not path.exists():
            continue
        text = path.read_text(encoding=TEXT_UTF_8)
        if not text.startswith(FLAG_TEXT):
            record_error(TEXT_MISSING_FRONTMATTER.format(path.relative_to(ROOT)))
            continue
        end = text.find(TEXT_TEXT_7, 3)
        if end == -1:
            record_error(TEXT_UNTERMINATED_FRONTMATTER.format(path.relative_to(ROOT)))
            continue
        permissions = parse_permissions(text[3:end])
        checked += 1
        for command in commands:
            effect = None
            for rule in permissions:
                if rule.get(KEY_ACTION) != KEY_SHELL:
                    continue
                if fnmatch.fnmatchcase(command, rule.get(KEY_RESOURCE, EMPTY_STRING)):
                    effect = rule.get(KEY_EFFECT)
            if effect != KEY_DENY:
                record_error(
                    TEXT_RESOLVES_TO_INSTEAD_OF_DENY_ADD_THE_GIT_DENY_RULES_AT_THE_EN.format(path.relative_to(ROOT), command, effect or TEXT_NO_RULE)
                )


def jsonc_comment_lines(text: str) -> list[int]:
    lines: list[int] = []
    index = 0
    line = 1
    length = len(text)
    in_string = False
    quote = EMPTY_STRING
    while index < length:
        character = text[index]
        if in_string:
            if character == TEXT_TEXT and index + 1 < length:
                index += 2
                continue
            if character == quote:
                in_string = False
            if character == TEXT_TEXT_5:
                line += 1
            index += 1
            continue
        if character in (TEXT_TEXT_2, TEXT_TEXT_3):
            in_string = True
            quote = character
            index += 1
            continue
        if character == TEXT_TEXT_4 and index + 1 < length and text[index + 1] == TEXT_TEXT_4:
            lines.append(line)
            while index < length and text[index] != TEXT_TEXT_5:
                index += 1
            continue
        if character == TEXT_TEXT_4 and index + 1 < length and text[index + 1] == TEXT_TEXT_6:
            lines.append(line)
            index += 2
            while index + 1 < length and not (text[index] == TEXT_TEXT_6 and text[index + 1] == TEXT_TEXT_4):
                if text[index] == TEXT_TEXT_5:
                    line += 1
                index += 1
            index += 2
            continue
        if character == TEXT_TEXT_5:
            line += 1
        index += 1
    return lines


def shell_inline_comment(line: str) -> bool:
    in_single = False
    in_double = False
    escaped = False
    brace_depth = 0
    index = 0
    while index < len(line):
        character = line[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if character == TEXT_TEXT and not in_single:
            escaped = True
            index += 1
            continue
        if character == TEXT_TEXT_11 and index + 1 < len(line) and line[index + 1] == TEXT_TEXT_12:
            brace_depth += 1
            index += 2
            continue
        if character == TEXT_TEXT_13 and brace_depth > 0:
            brace_depth -= 1
            index += 1
            continue
        if character == TEXT_TEXT_3 and not in_double:
            in_single = not in_single
            index += 1
            continue
        if character == TEXT_TEXT_2 and not in_single:
            in_double = not in_double
            index += 1
            continue
        if (
            character == TEXT_TEXT_14
            and not in_single
            and not in_double
            and brace_depth == 0
            and not (index > 0 and line[index - 1] == TEXT_TEXT_11)
        ):
            return bool(line[:index].strip())
        index += 1
    return False


def python_sources(base: Path) -> list[Path]:
    def excluded(part: str) -> bool:
        return part in {KEY_BUILD, TEXT_PYCACHE} or part.endswith(TEXT_EGG_INFO)

    return [path for path in sorted(base.rglob(TEXT_PY)) if not any(excluded(part) for part in path.parts)]


def is_test_fixture(path: Path) -> bool:
    try:
        path.resolve().relative_to((ROOT / KEY_TESTS / KEY_FIXTURES).resolve())
    except ValueError:
        return False
    return True


def check_comment_policy() -> None:
    global checked

    for path in sorted((ROOT / KEY_CONFIGS).rglob(TEXT_JSONC)):
        checked += 1
        text = path.read_text(encoding=TEXT_UTF_8)
        header = TEXT_TEXT_5.join(text.splitlines()[:10])
        if TEXT_NAME not in header or TEXT_PURPOSE not in header:
            record_error(TEXT_MISSING_JSONC_DOCUMENTATION_HEADER.format(path.relative_to(ROOT)))
            continue
        body_line = next(
            (number for number, line in enumerate(text.splitlines(), start=1) if line.strip().startswith(TEXT_TEXT_12)),
            None,
        )
        if body_line is None:
            record_error(TEXT_MISSING_JSON_OBJECT.format(path.relative_to(ROOT)))
            continue
        for comment_line in jsonc_comment_lines(text):
            if comment_line >= body_line:
                record_error(TEXT_INLINE_JSONC_COMMENTS_ARE_PROHIBITED.format(path.relative_to(ROOT), comment_line))

    for path in sorted((ROOT / KEY_SCRIPTS).rglob(TEXT_SH)) + sorted((ROOT / TEXT_BENCHMARKS_HARNESS).rglob(TEXT_SH)) + sorted((ROOT / KEY_SKILLS).rglob(TEXT_SH)):
        checked += 1
        lines = path.read_text(encoding=TEXT_UTF_8).splitlines()
        header = TEXT_TEXT_5.join(lines[:12])
        if TEXT_NAME_2 not in header or TEXT_PURPOSE_2 not in header:
            record_error(TEXT_MISSING_SHELL_DOCUMENTATION_HEADER.format(path.relative_to(ROOT)))
        for number, line in enumerate(lines, start=1):
            if shell_inline_comment(line):
                record_error(TEXT_INLINE_SHELL_COMMENTS_ARE_PROHIBITED.format(path.relative_to(ROOT), number))

    for path in python_sources(ROOT / KEY_SCRIPTS) + python_sources(ROOT / KEY_PACKAGES) + python_sources(ROOT / KEY_SKILLS) + python_sources(ROOT / KEY_TESTS):
        if is_test_fixture(path):
            continue
        checked += 1
        text = path.read_text(encoding=TEXT_UTF_8)
        if ast.get_docstring(ast.parse(text)) is None:
            record_error(TEXT_MISSING_MODULE_DOCSTRING.format(path.relative_to(ROOT)))
        try:
            tokens = tokenize.generate_tokens(io.StringIO(text).readline)
            for token in tokens:
                if token.type != tokenize.COMMENT:
                    continue
                value = token.string
                if value.startswith(TEXT_TEXT_15):
                    continue
                if re.match(TEXT_S_NOQA_TYPE_PRAGMA_SHELLCHECK_FMT, value):
                    continue
                record_error(TEXT_NON_DOCUMENTATION_PYTHON_COMMENT.format(path.relative_to(ROOT), token.start[0]))
        except tokenize.TokenError as exc:
            record_error(TEXT_TOKENIZATION_FAILED.format(path.relative_to(ROOT), exc))


def check_docs_status() -> None:
    global checked
    allowed = {TEXT_STABLE, TEXT_EXPERIMENTAL, TEXT_PLANNED, TEXT_DEPRECATED}
    for path in sorted((ROOT / KEY_DOCS).rglob(TEXT_MD)):
        relative = path.relative_to(ROOT)
        if relative.parts[:2] == (KEY_DOCS, KEY_DECISIONS):
            continue
        checked += 1
        head = TEXT_TEXT_5.join(path.read_text(encoding=TEXT_UTF_8).splitlines()[:8])
        missing = [marker for marker in (TEXT_STATUS, TEXT_LAST_VERIFIED, TEXT_EVIDENCE) if marker not in head]
        if missing:
            record_error(TEXT_MISSING_DOCUMENTATION_STATUS_FIELD.format(relative, missing[0]))
            continue
        match = re.search(TEXT_STATUS_S_A_ZA_Z, head)
        if match is None:
            record_error(TEXT_MISSING_DOCUMENTATION_STATUS_VALUE.format(relative))
        elif match.group(1) not in allowed:
            record_error(TEXT_UNKNOWN_DOCUMENTATION_STATUS.format(relative, match.group(1)))
        if not re.search(TEXT_LAST_VERIFIED_S_D_4_D_2_D_2, head):
            record_error(TEXT_LAST_VERIFIED_DATE_MUST_BE_ISO_8601.format(relative))


def code_line_comment(line: str) -> int | None:
    in_single = False
    in_double = False
    in_template = False
    escaped = False
    index = 0
    while index < len(line) - 1:
        character = line[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if character == TEXT_TEXT and (in_single or in_double or in_template):
            escaped = True
            index += 1
            continue
        if character == TEXT_TEXT_3 and not in_double and not in_template:
            in_single = not in_single
        elif character == TEXT_TEXT_2 and not in_single and not in_template:
            in_double = not in_double
        elif character == TEXT_TEXT_16 and not in_single and not in_double:
            in_template = not in_template
        elif (
            character == TEXT_TEXT_4
            and line[index + 1] == TEXT_TEXT_4
            and not in_single
            and not in_double
            and not in_template
        ):
            return index
        index += 1
    return None


def check_source_comments() -> None:
    global checked
    bases = [ROOT / KEY_EXAMPLES, ROOT / KEY_SKILLS]
    patterns = (TEXT_TS, TEXT_TSX, TEXT_CS)
    for base in bases:
        for pattern in patterns:
            for path in sorted(base.rglob(pattern)):
                if {KEY_BIN, KEY_OBJ, KEY_NODE_MODULES}.intersection(path.parts):
                    continue
                checked += 1
                in_block = False
                for number, line in enumerate(path.read_text(encoding=TEXT_UTF_8).splitlines(), start=1):
                    stripped = line.strip()
                    if in_block:
                        if TEXT_TEXT_17 in line:
                            in_block = False
                        continue
                    if stripped.startswith(TEXT_TEXT_18):
                        if TEXT_TEXT_17 not in stripped:
                            in_block = True
                        continue
                    if stripped.startswith(TEXT_TEXT_19):
                        record_error(TEXT_BLOCK_COMMENTS_ARE_PROHIBITED.format(path.relative_to(ROOT), number))
                        if TEXT_TEXT_17 not in stripped:
                            in_block = True
                        continue
                    index = code_line_comment(line)
                    if index is None:
                        continue
                    if line[index : index + 3] == TEXT_TEXT_20:
                        continue
                    record_error(TEXT_LINE_COMMENTS_ARE_PROHIBITED_USE_JSDOC_OR_XML_DOCUMENTATION.format(path.relative_to(ROOT), number))


def check_docstring_form() -> None:
    """
    Require a module docstring and enforce block form on any function or class docstring.

    Function and class docstrings are optional; descriptive names are preferred.
    When a docstring is present, the opening and closing triple quotes must be on
    their own lines. Single-line docstrings read as inline comments and are rejected.
    """
    global checked
    for base in (ROOT / KEY_SCRIPTS, ROOT / KEY_PACKAGES, ROOT / KEY_SKILLS, ROOT / KEY_TESTS):
        for path in python_sources(base):
            if is_test_fixture(path):
                continue
            checked += 1
            source = path.read_text(encoding=TEXT_UTF_8)
            try:
                tree = ast.parse(source)
            except SyntaxError as error:
                record_error(TEXT_CANNOT_PARSE.format(path.relative_to(ROOT), error))
                continue
            lines = source.splitlines()
            nodes: list[ast.AST] = [tree]
            nodes.extend(
                node
                for node in ast.walk(tree)
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            )
            for node in nodes:
                name = getattr(node, KEY_NAME, KEY_MODULE)
                body = getattr(node, KEY_BODY, [])
                if not body:
                    record_error(TEXT_HAS_NO_BODY.format(path.relative_to(ROOT), getattr(node, KEY_LINENO, 1), name))
                    continue
                first = body[0]
                is_docstring = (
                    isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)
                )
                if not is_docstring:
                    if isinstance(node, ast.Module):
                        record_error(TEXT_1_MODULE_IS_MISSING_A_DOCSTRING.format(path.relative_to(ROOT)))
                    continue
                start = first.lineno - 1
                end = first.end_lineno - 1
                if lines[start].strip() != TEXT_TEXT_21 or lines[end].strip() != TEXT_TEXT_21:
                    record_error(
                        TEXT_DOCSTRING_MUST_PLACE_THE_TRIPLE_QUOTES_ON_THEIR_OWN_LINES.format(path.relative_to(ROOT), first.lineno, name)
                    )


def check_links() -> None:
    global checked
    urls: set[str] = set()
    for path in list(ROOT.glob(TEXT_DOCS_MD)) + [ROOT / TEXT_README_MD]:
        text = path.read_text(encoding=TEXT_UTF_8, errors=KEY_IGNORE)
        for url in re.findall(TEXT_HTTPS_S, text):
            if any(character in url for character in (TEXT_TEXT_22, TEXT_TEXT_23)) or url.endswith((TEXT_PNG, TEXT_SVG)):
                continue
            urls.add(url.rstrip(TEXT_TEXT_24))
    for url in sorted(urls):
        checked += 1
        request = urllib.request.Request(url, method=TEXT_HEAD, headers={TEXT_USER_AGENT: TEXT_TOOLWRIGHT_VALIDATOR})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status >= 400:
                    record_warning(TEXT_LINK_HTTP.format(url, response.status))
        except Exception as exc:  # noqa: BLE001 - report unreachable links as warnings
            record_warning(TEXT_LINK.format(url, exc))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(FLAG_LINKS, action=KEY_STORE_TRUE, help=TEXT_CHECK_EXTERNAL_LINKS)
    args = parser.parse_args()

    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            record_error(TEXT_MISSING_REQUIRED_FILE.format(relative))

    for path in sorted((ROOT / KEY_CONFIGS).rglob(TEXT_JSONC)):
        check_jsonc(path)
    for path in sorted((ROOT / KEY_CONFIGS).rglob(TEXT_YML)):
        check_yaml(path)
    for path in sorted((ROOT / TEXT_GITHUB_WORKFLOWS).glob(TEXT_YML)):
        check_yaml(path)
    check_tasks()

    check_agents()
    check_skills()
    check_commands()
    check_provenance()
    check_git_permissions()
    check_comment_policy()
    check_source_comments()
    check_docstring_form()
    check_docs_status()

    if args.links:
        check_links()

    print(TEXT_CHECKED.format(checked))
    for warning in warnings:
        print(TEXT_WARN.format(warning))
    for error in errors:
        print(TEXT_ERROR.format(error))
    if errors:
        print(TEXT_FAILED_WITH_ERROR_S.format(len(errors)))
        return 1
    print(TEXT_OK)
    return 0


if __name__ == TEXT_MAIN:
    sys.exit(main())

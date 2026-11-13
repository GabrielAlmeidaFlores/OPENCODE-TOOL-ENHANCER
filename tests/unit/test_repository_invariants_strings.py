"""
String constants for tests/unit/test_repository_invariants.py.

Side effects: none.
"""
from __future__ import annotations
from tests.constants import (
    FLAG_TEXT,
    KEY_AGENT,
    KEY_AGENTS,
    KEY_COMMANDS,
    KEY_NAME,
    KEY_SKILLS,
    TEXT_MAIN,
    TEXT_MD,
    TEXT_STABLE,
    TEXT_TEXT,
    TEXT_UTF_8,
    TEXT_VERSION,
)

KEY_DECISIONS = 'decisions'
KEY_DOCS = 'docs'
TEXT_AGENT_MD = '*/AGENT.md'
TEXT_AGENT_MD_2 = 'AGENT.md'
TEXT_AUTHOR = '# author:'
TEXT_A_ZA_Z0_9_S = '^([A-Za-z0-9_-]+):\\s*(.*)$'
TEXT_CONFIGS_RALPH_HATS = 'configs/ralph/hats'
TEXT_DEPRECATED = 'Deprecated'
TEXT_DOCS_ARCHITECTURE_TESTING_MD = 'docs/architecture/testing.md'
TEXT_DOCS_DECISIONS = 'docs/decisions'
TEXT_DOCS_MD = 'docs/**/*.md'
TEXT_DOCS_RESEARCH_BASELINE_MD = 'docs/research/baseline.md'
TEXT_D_D_D = '^\\d+\\.\\d+\\.\\d+$'
TEXT_EVIDENCE = '**Evidence:**'
TEXT_EXPERIMENTAL = 'Experimental'
TEXT_GITHUB_WORKFLOWS = '.github/workflows'
TEXT_GIT_ADD = 'git add'
TEXT_GIT_COMMIT = 'git commit'
TEXT_GIT_PUSH = 'git push'
TEXT_GIT_STAGE = 'git stage'
TEXT_LAST_VERIFIED = '**Last verified:**'
TEXT_LAST_VERIFIED_S_D_4_D_2_D_2 = '\\*\\*Last verified:\\*\\*\\s*(\\d{4}-\\d{2}-\\d{2})'
TEXT_M_STATUS_ACCEPTED_PROPOSED_SUPERSEDED_REJECTED = '(?m)^- Status: (Accepted|Proposed|Superseded|Rejected)'
TEXT_PAGES_MISSING_A_STATUS_BLOCK = 'pages missing a status block'
TEXT_PLANNED = 'Planned'
TEXT_README_MD = 'README.md'
TEXT_SKILL_MD = '*/SKILL.md'
TEXT_SOURCE = '# source:'
TEXT_STATUS = '**Status:**'
TEXT_STATUS_S_A_ZA_Z = '\\*\\*Status:\\*\\*\\s*([A-Za-z]+)'
TEXT_TEXT_2 = '<!--'
TEXT_TEXT_3 = '\n---'
from tests.constants import TEXT_QUOTE as TEXT_TEXT_4
TEXT_TEXT_5 = "'"
TEXT_UPSTREAM_COMMIT = '# upstream_commit:'
TEXT_VERSION_IS_REQUIRED_FOR_RELEASE_AND_UPDATE_CHECKS = 'VERSION is required for release and update checks'
TEXT_YML = '*.yml'
TEXT_HAS_NO_STATUS_VALUE = '{} has no status value'
TEXT_USES_UNKNOWN_STATUS = '{} uses an unknown status'
TEXT_HAS_NO_ISO_DATE = '{} has no ISO verification date'
TEXT_HAS_NO_AGENT = '{} has no agent'
TEXT_TARGETS_MISSING_AGENT = '{} targets missing agent {}'
TEXT_MISSING_SOURCE = '{} missing source'
TEXT_MISSING_AUTHOR = '{} missing author'
TEXT_MISSING_COMMIT = '{} missing commit'
TEXT_NOT_VALID_YAML = '{} is not valid YAML'
from tests.constants import TEXT_TASK_ERROR as TEXT_OFFENDER

"""
String constants for specs.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_COMPLETE
from .constants import KEY_DESCRIPTION
from .constants import KEY_ISSUES
from .constants import KEY_SPECS
from .constants import TEXT_A_Z0_9
from .constants import TEXT_TEXT

from .constants import (
    ENCODING_UTF8,
    KEY_FEATURE,
    KEY_ID,
    KEY_NAME,
    KEY_PATH,
    KEY_STATUS,
    KEY_TASKS,
    SEPARATOR_COMMA_SPACE,
    STATUS_FAIL,
    STATUS_MISSING,
    STATUS_OK,
)


KEY_CRITERIA = 'criteria'

KEY_CRITERION = 'criterion'


KEY_EVIDENCE = 'evidence'



TEXT_AC = '- [ ] AC-{}: {}'

TEXT_AC_1_DESCRIBE_OBSERVABLE_BEHAVIOR = '- [ ] AC-1: <describe observable behavior>'

TEXT_AC_D_S = '^- (AC-\\d+):\\s*(.+)$'


TEXT_CRITERIA_MUST_NOT_CONTAIN_ANGLE_BRACKET_PLACEHOLDERS = 'criteria must not contain angle-bracket placeholders'

TEXT_DESIGN_COMPONENTS_LIST_THE_MODULES_INTERFACES_AND_DATA_FLOW_ = '# Design: {}\n\n## Components\n\nList the modules, interfaces, and data flow.\n\n## Decisions\n\nRecord trade-offs and rejected alternatives.\n\n## Risks\n\nList failure modes and mitigations.\n'

TEXT_DESIGN_MD = 'design.md'

TEXT_DUPLICATE_CRITERION = 'duplicate criterion: {}'

TEXT_DUPLICATE_EVIDENCE_FOR = 'duplicate evidence for {}'

TEXT_EVIDENCE_MD = 'evidence.md'

TEXT_EVIDENCE_RECORD_THE_COMMAND_AND_OBSERVED_RESULT_FOR_EVERY_CR = '# Evidence: {}\n\nRecord the command and observed result for every criterion.\n\n- AC-1: <command or artifact that proves the criterion>\n'

TEXT_EVIDENCE_REFERENCES_UNKNOWN = 'evidence references unknown {}'

TEXT_FEATURE_NAME_MUST_CONTAIN_LETTERS_OR_DIGITS = 'feature name must contain letters or digits'

TEXT_HAS_NO_EVIDENCE = '{} has no evidence'

TEXT_HAS_NO_TASK = '{} has no task'

TEXT_MISSING_SPEC_ARTIFACT = 'missing spec artifact: {}'

TEXT_MISSING_SPEC_ARTIFACTS = 'missing spec artifacts: {}'

TEXT_NO_ACCEPTANCE_CRITERIA_FOUND = 'no acceptance criteria found'

TEXT_NO_TASKS_FOUND = 'no tasks found'

TEXT_REFERENCES_UNKNOWN = '{} references unknown {}'

TEXT_REQUIREMENTS_GOALS_DESCRIBE_THE_OUTCOME_THIS_CHANGE_MUST_PRO = '# Requirements: {}\n\n## Goals\n\nDescribe the outcome this change must produce.\n\n## Acceptance Criteria\n\nEvery criterion is binary and testable.\n\n{}\n\n## Non-Goals\n\nList what this change does not do.\n'

TEXT_REQUIREMENTS_MD = 'requirements.md'

TEXT_SPEC_ALREADY_EXISTS = 'spec already exists: {}'

TEXT_TASKS_EACH_TASK_MUST_NAME_THE_CRITERION_IT_SATISFIES_T_1_DES = '# Tasks: {}\n\nEach task must name the criterion it satisfies.\n\n- [ ] T-1: <describe the smallest verifiable task> (criterion: AC-1)\n'

TEXT_TASKS_MD = 'tasks.md'


TEXT_TEXT_2 = '<'

TEXT_TEXT_3 = '>'

TEXT_XX_AC_D_S = '^- \\[[ xX]\\] (AC-\\d+):\\s*(.+)$'

TEXT_XX_T_D_S_S_CRITERION_S_AC_D_S = '^- \\[[ xX]\\] (T-\\d+):\\s*(.+?)\\s*\\(criterion:\\s*(AC-\\d+)\\)\\s*$'

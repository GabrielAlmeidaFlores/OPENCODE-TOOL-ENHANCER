"""
String constants for governance.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import TEXT_TEXT_2 as TEXT_TEXT
from .constants import TEXT_TEXT_2_2 as TEXT_TEXT_2
from .constants import FLAG_TEXT
from .constants import KEY_ADVISORY
from .constants import KEY_AGENT
from .constants import KEY_AGENTS
from .constants import KEY_ALLOWED
from .constants import KEY_COORDINATOR
from .constants import KEY_HIGH
from .constants import KEY_KIND
from .constants import KEY_LOW
from .constants import KEY_MEDIUM
from .constants import KEY_MODE
from .constants import KEY_READ_ONLY
from .constants import KEY_REQUIRED
from .constants import KEY_REVIEW
from .constants import KEY_RISK
from .constants import KEY_SECURITY
from .constants import KEY_TOOL_CALLS
from .constants import KEY_VALIDATOR_MODE
from .constants import KEY_VERIFY
from .constants import KEY_VIOLATIONS
from .constants import TEXT_AGENT_MD
from .constants import TEXT_MISSING_FRONTMATTER
from .constants import TEXT_UNTERMINATED_FRONTMATTER

from .constants import (
    EMPTY_STRING,
    ENCODING_UTF8,
    KEY_DETAIL,
    KEY_STATUS,
    SEPARATOR_SPACE,
    STATUS_OK,
)


KEY_ACTION = 'action'




KEY_ALLOW = 'allow'


KEY_ALLOWED_ACTIONS = 'allowed_actions'

KEY_ARCHITECT = 'architect'

KEY_BOUNCES = 'bounces'

KEY_BUDGET = 'budget'


KEY_COST_USD = 'cost_usd'

KEY_DEADLOCK = 'deadlock'

KEY_DELEGATION_DEPTH = 'delegation_depth'

KEY_DENIED_ACTIONS = 'denied_actions'

KEY_DENIES_EDIT = 'denies_edit'

KEY_DENY = 'deny'

KEY_EDIT = 'edit'

KEY_EFFECT = 'effect'


KEY_ITERATIONS = 'iterations'


KEY_LOOP = 'loop'


KEY_MAX_BOUNCES = 'max_bounces'

KEY_MAX_COST_USD = 'max_cost_usd'

KEY_MAX_DELEGATION_DEPTH = 'max_delegation_depth'

KEY_MAX_ITERATIONS = 'max_iterations'

KEY_MAX_REPEATS = 'max_repeats'

KEY_MAX_TOOL_CALLS = 'max_tool_calls'

KEY_MAX_WRITES = 'max_writes'



KEY_PLANNER = 'planner'

KEY_PRIMARY = 'primary'


KEY_RECORD = 'record'

KEY_REPEATS = 'repeats'


KEY_RESEARCHER = 'researcher'

KEY_RESOURCE = 'resource'




KEY_SUBAGENT = 'subagent'





KEY_WRITES = 'writes'


TEXT_CODE_REVIEWER = 'code-reviewer'

TEXT_COORDINATOR_MUST_BE_PRIMARY = 'coordinator must be primary'

TEXT_EXCEEDS = '{} {} exceeds {} {}'

TEXT_GOVERNANCE_MUST_BE_A_NON_NEGATIVE_NUMBER = 'governance.{} must be a non-negative number'

TEXT_HANDOFF_BOUNCES_EXCEED_MAX_BOUNCES = 'handoff bounces {} exceed max_bounces {}'


TEXT_MODE = 'mode:'

TEXT_NO_AGENTS_FOUND_UNDER = 'no agents found under {}'

TEXT_PERFORMANCE_ANALYST = 'performance-analyst'

TEXT_PERMISSIONS = 'permissions:'

TEXT_READ_ONLY_ROLE_MUST_DENY_EDIT = 'read-only role must deny edit'

TEXT_RECORD_BOUNCES_MUST_BE_A_NON_NEGATIVE_NUMBER = 'record.bounces must be a non-negative number'

TEXT_RECORD_MUST_BE_A_NON_NEGATIVE_NUMBER = 'record.{} must be a non-negative number'

TEXT_RECORD_REPEATS_MUST_BE_A_NON_NEGATIVE_NUMBER = 'record.repeats must be a non-negative number'

TEXT_REPEATED_ACTIONS_EXCEED_MAX_REPEATS = 'repeated actions {} exceed max_repeats {}'

TEXT_SECURITY_REVIEWER = 'security-reviewer'

TEXT_SPECIALIST_MUST_BE_SUBAGENT = 'specialist must be subagent'

TEXT_S_EFFECT_S_S = '\\s*effect:\\s*\\"?(.*?)\\"?\\s*$'

TEXT_S_RESOURCE_S_S = '\\s*resource:\\s*\\"?(.*?)\\"?\\s*$'

TEXT_S_S_ACTION_S = '\\s*-\\s*action:\\s*\\"?([^\\"]+)\\"?'



TEXT_TEXT_3 = '\t'

TEXT_UNKNOWN_RISK_LEVEL = 'unknown risk level: {}'


TEXT_WRITE_ROLE_MUST_ALLOW_EDIT = 'write role must allow edit'

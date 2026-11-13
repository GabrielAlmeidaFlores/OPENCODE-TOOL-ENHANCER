"""
CLI literal constants.

Public API: module constants used by the CLI package.

Side effects: none.
"""
from __future__ import annotations
from ..constants import KEY_AVAILABLE_COMMIT
from ..constants import KEY_BACKUPS
from ..constants import KEY_CATALOG
from ..constants import KEY_COMPLETE
from ..constants import KEY_CURRENT_COMMIT
from ..constants import KEY_DESCRIPTION
from ..constants import KEY_FILES_CHANGED
from ..constants import KEY_ISSUES
from ..constants import KEY_LOCKED_COMMIT
from ..constants import KEY_PROFILES
from ..constants import KEY_SPECS
from ..constants import TEXT_NO_LOCK
from ..constants import TEXT_UPDATE_AVAILABLE
from ..constants import KEY_PLAN
from ..constants import TEXT_INVALID_JSON as TEMPLATE_INVALID_JSON
from ..constants import TEXT_MISSING_2 as TEMPLATE_MISSING
from ..constants import TEXT_VERIFICATION_COMMAND
from ..constants import FLAG_AGENT
from ..constants import FLAG_CHECK
from ..constants import FLAG_FORMAT
from ..constants import FLAG_VERSION
from ..constants import KEY_AGENT
from ..constants import KEY_ALLOWED
from ..constants import KEY_APPROVED
from ..constants import KEY_AUTHOR
from ..constants import KEY_BY_STATUS
from ..constants import KEY_COMMAND
from ..constants import KEY_COORDINATOR
from ..constants import KEY_COST
from ..constants import KEY_DECISION
from ..constants import KEY_DRY_RUN
from ..constants import KEY_ENTRIES
from ..constants import KEY_EXIT_CODE
from ..constants import KEY_EXPIRED
from ..constants import KEY_EXPIRES
from ..constants import KEY_FOCUS
from ..constants import KEY_HIGH
from ..constants import KEY_KIND
from ..constants import KEY_LICENSE
from ..constants import KEY_LOW
from ..constants import KEY_MEDIUM
from ..constants import KEY_MEMORY
from ..constants import KEY_MODE
from ..constants import KEY_OPENCODE_EXIT
from ..constants import KEY_PASSED
from ..constants import KEY_PILOTS
from ..constants import KEY_PROJECT
from ..constants import KEY_READ_ONLY
from ..constants import KEY_REQUIRED
from ..constants import KEY_RISK
from ..constants import KEY_RUN
from ..constants import KEY_SCOPE
from ..constants import KEY_STACK
from ..constants import KEY_STDERR
from ..constants import KEY_STDOUT
from ..constants import KEY_STEPS
from ..constants import KEY_SUCCESS
from ..constants import KEY_TASK
from ..constants import KEY_TASKS
from ..constants import KEY_VALIDATOR_MODE
from ..constants import KEY_VERIFICATION_EXIT
from ..constants import KEY_VIOLATIONS
from ..constants import KEY_WIP_LIMIT
from ..constants import KEY_WORKSPACE
from ..constants import TEXT_EXPIRED
from ..constants import TEXT_OPENCODE_PILOT_MODEL

from ..constants import (
    KEY_FAILED,
    KEY_FAILURE_CLASS,
    BASH as KEY_BASH,
    DEFAULT_COMMIT as KEY_UNKNOWN,
    ISO_TIMESPEC as KEY_SECONDS,
    STATE_DIR_NAME as TEXT_TOOLWRIGHT,
    TOOL_AST_GREP as TEXT_AST_GREP,
    TOOL_CODEGRAPH as KEY_CODEGRAPH,
    TOOL_SERENA as KEY_SERENA,
    ENCODING_UTF8,
    FLAG_TARGET,
    KEY_ARCHIVES,
    KEY_BACKUP,
    KEY_COMMIT,
    KEY_CREATED,
    KEY_FILES,
    KEY_LOCK,
    KEY_PLANNED,
    KEY_PURGED,
    KEY_REMOVABLE,
    KEY_SKIPPED,
    KEY_SUMMARY,
    KEY_VERSION,
    STATUS_MISSING,
    STATUS_MODIFIED,
)


FLAG_APPLY_REQUIRES_BACKUP_DIR = '--apply requires --backup DIR'

FLAG_APPROVED = '--approved'

FLAG_BACKUP = '--backup'

FLAG_BUDGET = '--budget'


FLAG_CHECK_DRIFT = '--check-drift'

FLAG_CONFIDENCE = '--confidence'

FLAG_CONFIG = '--config'

FLAG_CRITERION = '--criterion'


FLAG_JSON = '--json'

FLAG_KEEP = '--keep'

FLAG_LINK = '--link'

FLAG_LIST = '--list'

FLAG_NO_CACHE = '--no-cache'

FLAG_NO_MCP = '--no-mcp'

FLAG_PROMPT = '--prompt'

FLAG_PURGE = '--purge'

FLAG_RECORD = '--record'

FLAG_REMOTE = '--remote'

FLAG_REMOVE = '--remove'

FLAG_REPO = '--repo'

FLAG_RESULTS = '--results'

FLAG_RISK = '--risk'

FLAG_SCOPE = '--scope'

FLAG_SETUP = '--setup'

FLAG_SOURCE = '--source'

FLAG_STATUS = '--status'

FLAG_TITLE = '--title'

FLAG_TTL_DAYS = '--ttl-days'

FLAG_VERIFY = '--verify'


FLAG_WORKSPACE = '--workspace'

FLAG_WORKTREE = '--worktree'








KEY_BUILD = 'build'

KEY_BUILD_ARGUMENT_PARSER = 'build_argument_parser'


KEY_CACHED = 'cached'


KEY_CATALOG_COMMAND = 'catalog_command'



KEY_COMPAT = 'compat'




KEY_COUNT = 'count'

KEY_CSV = 'csv'


KEY_CUSTOM = 'custom'



KEY_DOCTOR_DICT = 'doctor_dict'

KEY_DRIFT = 'drift'



KEY_EVAL = 'eval'




KEY_EXPORT = 'export'





KEY_GATE = 'gate'

KEY_GOVERN = 'govern'

KEY_GOVERN_COMMAND = 'govern_command'


KEY_IDENTIFIER = 'identifier'

KEY_IES = 'ies'






KEY_MAIN = 'main'

KEY_MANUAL = 'manual'



KEY_MEMORY_COMMAND = 'memory_command'

KEY_MINIMAL = 'minimal'


KEY_MOVE = 'move'

KEY_NONE = 'none'




KEY_PILOT_COMMAND = 'pilot_command'


KEY_PREAMBLE = 'preamble'


KEY_PROFILE_COMMAND = 'profile_command'


KEY_PRUNE = 'prune'

KEY_QUERY = 'query'





KEY_RUN_DIAGNOSTIC_CHECKS = 'run_diagnostic_checks'




KEY_SPEC = 'spec'


KEY_SPEC_COMMAND = 'spec_command'


KEY_STATS = 'stats'





KEY_SUMMARIZE_CHECKS = 'summarize_checks'



KEY_TASK_COMMAND = 'task_command'

KEY_TEXT = 'text'

KEY_TOOLWRIGHT = 'toolwright'


KEY_USE = 'use'






KEY_WRITER = 'writer'

KEY_Y = 'y'

TEXT_ADD_A_MEMORY_ENTRY = 'add a memory entry'

TEXT_ADD_A_TASK = 'add a task'

TEXT_ADD_SEARCH_PRUNE_EXPORT_OR_RENDER_PROJECT_MEMORY = 'add, search, prune, export, or render project memory'

TEXT_ALLOW_A_DUPLICATE_TITLE = 'allow a duplicate title'

TEXT_APPLY_A_PROFILE = 'apply a profile'

TEXT_APPLY_EVEN_WHEN_ALREADY_CURRENT = 'apply even when already current'


TEXT_BACKUP_DIRECTORY_TO_RESTORE = 'backup directory to restore'

TEXT_BACK_UP_AND_REPLACE_MANAGED_DIRECTORIES = 'back up and replace managed directories'

TEXT_BENCHMARKS_RESULTS = 'benchmarks/results'

TEXT_CACHED = ' (cached)'

TEXT_CATALOG_MATCHES_THE_REGISTRY = 'catalog matches the registry'

TEXT_COMMAND = 'COMMAND'

TEXT_COMMA_SEPARATED_COMPONENTS_INSTEAD_OF_A_PROFILE = 'comma-separated components instead of a profile'

TEXT_COMPARE_THE_LOCK_WITH_THE_CURRENT_AND_REMOTE_SOURCE = 'compare the lock with the current and remote source'

TEXT_COMPARE_WITH_THE_PROVENANCE_REGISTRY = 'compare with the provenance registry'

TEXT_CONFIG_PATH_DEFAULT_TOOLWRIGHT_CONFIG_TOML = 'config path (default: .toolwright/config.toml)'

TEXT_CONFIRM_COMPLETION = 'confirm completion'

TEXT_CONFIRM_DELETION = 'confirm deletion'

TEXT_CONFIRM_DESTRUCTIVE_REMOVAL = 'confirm destructive removal'

TEXT_CONFIRM_THE_OVERWRITE = 'confirm the overwrite'

TEXT_CONFIRM_WORKTREE_REMOVAL = 'confirm worktree removal'

TEXT_CREATE_AND_VERIFY_SPEC_DRIVEN_DEVELOPMENT_ARTIFACTS = 'create and verify spec-driven development artifacts'

TEXT_CREATE_A_GIT_WORKTREE_FOR_THE_TASK = 'create a Git worktree for the task'

TEXT_CREATE_A_SPEC = 'create a spec'

TEXT_CREATE_OR_REMOVE_A_TASK_WORKTREE = 'create or remove a task worktree'

TEXT_DELETE_EXPIRED_ENTRIES = 'delete expired entries'

TEXT_DEPENDENCY_SETUP_COMMAND_RUN_IN_THE_CLONE = 'dependency setup command run in the clone'

TEXT_DIAGNOSE_THE_REPOSITORY_AND_ENVIRONMENT = 'diagnose the repository and environment'

TEXT_EMIT_MACHINE_READABLE_JSON = 'emit machine-readable JSON'

TEXT_EVALUATE_A_RUN_RECORD_AGAINST_BUDGETS = 'evaluate a run record against budgets'

TEXT_EXECUTE_THE_PLAN = 'execute the plan'

TEXT_EXECUTE_THE_REMOVAL = 'execute the removal'

TEXT_EXECUTE_THE_RESTORE = 'execute the restore'


TEXT_EXPORT_MEMORY = 'export memory'

TEXT_FAIL_WHEN_TOTAL_COST_EXCEEDS_THIS_AMOUNT_IN_USD = 'fail when total cost exceeds this amount in USD'

TEXT_FILTER_BY_ARTIFACT_TYPE = 'filter by artifact type'

TEXT_IGNORE_CACHED_RESULTS = 'ignore cached results'

TEXT_INSPECT_CONTRACTS_AND_EVALUATE_GOVERNANCE_LIMITS = 'inspect contracts and evaluate governance limits'

TEXT_INSTALL_INSPECT_AND_UPDATE_THE_TOOLWRIGHT_PROFILE = 'Install, inspect, and update the ToolWright profile.'

TEXT_JSON_RUN_RECORD = 'JSON run record'

TEXT_KEEP_THE_DISPOSABLE_CLONE = 'keep the disposable clone'

TEXT_LIST_AVAILABLE_PROFILES = 'list available profiles'

TEXT_LIST_BACKUPS_DEFAULT = 'list backups (default)'

TEXT_LIST_CATALOG_ENTRIES = 'list catalog entries'

TEXT_LIST_CONFIGURED_PILOTS = 'list configured pilots'

TEXT_LIST_OR_REMOVE_EXPIRED_ENTRIES = 'list or remove expired entries'

TEXT_LIST_OR_RESTORE_CONFIGURATION_BACKUPS = 'list or restore configuration backups'

TEXT_LIST_OR_RUN_REAL_REPOSITORY_PILOTS = 'list or run real-repository pilots'

TEXT_LIST_SEARCH_VERIFY_OR_BUILD_THE_ARTIFACT_CATALOG = 'list, search, verify, or build the artifact catalog'

TEXT_LIST_SHOW_VERIFY_OR_APPLY_PROFILE_MANIFESTS = 'list, show, verify, or apply profile manifests'

TEXT_LIST_SPECS = 'list specs'

TEXT_LIST_TASKS = 'list tasks'

TEXT_MANAGE_THE_OPTIONAL_MARKDOWN_TASK_BOARD = 'manage the optional Markdown task board'

TEXT_MOVE_A_TASK_TO_A_STATUS = 'move a task to a status'


TEXT_OPENCODE_AGENT_FOR_THE_RUN = 'OpenCode agent for the run'


TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_TO_WRITE_THESE_FILES = '\nplan only. Re-run with --apply to write these files.'

TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_YES_TO_DELETE = 'plan only. Re-run with --apply --yes to delete.'

TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_YES_TO_REMOVE_THESE_FILES = '\nplan only. Re-run with --apply --yes to remove these files.'

TEXT_PLAN_OR_APPLY_AN_INSTALLATION = 'plan or apply an installation'

TEXT_PLAN_OR_REMOVE_FILES_RECORDED_IN_TOOLWRIGHT_LOCK_JSON = 'plan or remove files recorded in toolwright.lock.json'

TEXT_PRINT_THE_PLAN_WITHOUT_CLONING = 'print the plan without cloning'

TEXT_PRINT_THE_PLAN_WITHOUT_REMOVING_DEFAULT = 'print the plan without removing (default)'

TEXT_PRINT_THE_PLAN_WITHOUT_WRITING_DEFAULT = 'print the plan without writing (default)'

TEXT_PROFILE_MANIFEST_NAME_DEFAULT_STANDARD = 'profile manifest name (default: standard)'

TEXT_PROJECT_DIRECTORY_DEFAULTS_TO_THE_CURRENT_DIRECTORY = 'project directory (defaults to the current directory)'

TEXT_PURGED_LOCK_AND_TOOLWRIGHT_STATE = 'purged lock and .toolwright state'

TEXT_QUERY_THE_UPSTREAM_HEAD = 'query the upstream HEAD'

TEXT_READ_ONLY = 'read-only'

TEXT_REFUSING_TO_DELETE_MEMORY_WITHOUT_YES = 'refusing to delete memory without --yes'

TEXT_REFUSING_TO_REMOVE_A_WORKTREE_WITHOUT_YES = 'refusing to remove a worktree without --yes'

TEXT_REFUSING_TO_REMOVE_FILES_WITHOUT_YES = 'refusing to remove files without --yes'

TEXT_REFUSING_TO_RESTORE_WITHOUT_YES = 'refusing to restore without --yes'

TEXT_REGENERATE_THE_CATALOG = 'regenerate the catalog'

TEXT_REMOVE_MODIFIED_FILES_TOO = 'remove modified files too'

TEXT_REMOVE_TOOLWRIGHT_STATE_AND_THE_LOCK = 'remove .toolwright state and the lock'

TEXT_RENDER_THE_BOUNDED_PREAMBLE = 'render the bounded preamble'

TEXT_REPORT_COST_TOKENS_FAILURES_AND_ARM_COMPARISONS = 'report cost, tokens, failures, and arm comparisons'

TEXT_REPORT_STATUS_DEFAULT = 'report status (default)'

TEXT_REPOSITORY_ROOT_DEFAULTS_TO_THE_CURRENT_CHECKOUT = 'repository root (defaults to the current checkout)'

TEXT_RESULT_DIRECTORY_REPEATABLE = 'result directory; repeatable'

TEXT_RUN_DETERMINISTIC_EVALUATION_CASES = 'run deterministic evaluation cases'

TEXT_RUN_ONE_PILOT = 'run one pilot'

TEXT_RUN_ONLY_THE_NAMED_CASE = 'run only the named case'

TEXT_RUN_ONLY_THE_NAMED_CHECK_REPEATABLE = 'run only the named check; repeatable'

TEXT_RUN_THE_CONFIGURED_DETERMINISTIC_VERIFICATION_CHECKS = 'run the configured deterministic verification checks'

TEXT_SCRIPTS_MAINTENANCE_RESTORE_CONFIG_SH = 'scripts/maintenance/restore-config.sh'

TEXT_SEARCH_CATALOG_ENTRIES = 'search catalog entries'

TEXT_SEARCH_MEMORY_LEXICALLY = 'search memory lexically'

TEXT_SHOW_BOARD_COUNTS = 'show board counts'

TEXT_SHOW_DERIVED_AGENT_CONTRACTS = 'show derived agent contracts'

TEXT_SHOW_ONE_PROFILE = 'show one profile'

TEXT_SHOW_THE_OPENCODE_V1_V2_COMPATIBILITY_MATRIX = 'show the OpenCode V1/V2 compatibility matrix'

TEXT_SHOW_THE_REQUIRED_GATES_FOR_A_RISK_LEVEL = 'show the required gates for a risk level'

TEXT_SKIP_THE_MCP_CONNECTIVITY_CHECK = 'skip the MCP connectivity check'

TEXT_TASK_PROMPT = 'task prompt'



TEXT_VALIDATE_CRITERIA_AND_TASKS = 'validate criteria and tasks'

TEXT_VALIDATE_EVERY_PROFILE_MANIFEST = 'validate every profile manifest'

TEXT_VALIDATE_THE_CATALOG = 'validate the catalog'


TEXT_VERIFICATION_COMMAND_RECORDED_WITH_THE_TASK = 'verification command recorded with the task'

TEXT_VERIFY_OPENCODE_STANDALONE_DEBUG_AGENTS = 'verify:   opencode --standalone debug agents'

TEXT_VERIFY_TASKS_AND_EVIDENCE = 'verify tasks and evidence'

TEXT_WORKSPACE_DIRECTORY_DEFAULTS_TO_A_TEMPORARY_DIRECTORY = 'workspace directory (defaults to a temporary directory)'

TEMPLATE_10 = '{:<10} {}'
TEMPLATE_12 = '{}  {:<12} {}'
TEMPLATE_12_2 = '  {:<12} {}'
TEMPLATE_20_22 = '{:<20} {:<22} {}  {}'
TEMPLATE_30 = '{:<30} {}'
TEMPLATE_4_10 = '{:<4} {:<10} {}'
TEMPLATE_4_12 = '{:<4} {:<12} {}'
TEMPLATE_4_12_6_2F_S = '{:<4} {:<12} {:>6.2f}s  {}{}'
TEMPLATE_4_22_8 = '{:<4} {:<22} {:<8} {}'
TEMPLATE_4_24 = '{:<4} {:<24} {}'
TEMPLATE_8_10 = '{:<8} {:<10} {}{}'
TEMPLATE_8_28_22 = '{:<8} {:<28} {:<22} {}'
TEMPLATE_ADDED = 'added {}/{} ({})'
TEMPLATE_ALLOWED = 'allowed: {}'
TEMPLATE_ARTIFACTS_ARTIFACTS = 'artifacts: {}/artifacts'
TEMPLATE_ARTIFACT_S = '\n{} artifact(s)'
TEMPLATE_BACKUP = 'backup:   {}'
TEMPLATE_BACKUP_DIRECTORY_NOT_FOUND = 'backup directory not found: {}'
TEMPLATE_BUDGET_EXCEEDED_6F_6F = 'budget exceeded: ${:.6f} > ${:.6f}'
TEMPLATE_CHANGED = '  changed {} ({})'
TEMPLATE_COMPONENTS = 'components:  {}'
TEMPLATE_COMPONENTS_2 = 'components: {}'
TEMPLATE_COST_6F = 'cost: ${:.6f}'
TEMPLATE_CREATED = 'created {}'
TEMPLATE_DESCRIPTION = 'description: {}'
TEMPLATE_EXPIRED_ENTR = '{} expired entr{}'
TEMPLATE_FAILURE_S = '\n{} failure(s)'
TEMPLATE_FEATURE = 'feature: {}'
TEMPLATE_FILES_NEW_UPDATED_UNCHANGED = 'files:    {} new, {} updated, {} unchanged'
TEMPLATE_KEEP = '  keep   {} ({})'
TEMPLATE_LOCK = 'lock:     {}'
TEMPLATE_MATCH_ES = '\n{} match(es)'
TEMPLATE_MESSAGE = 'message: {}'
TEMPLATE_NAME = 'name:        {}'
TEMPLATE_NO_BACKUPS_UNDER = 'no backups under {}'
TEMPLATE_OPENCODE_EXIT = 'opencode exit: {}'
TEMPLATE_PASSED_FAILED = '\n{} passed, {} failed'
TEMPLATE_PATH = 'path:        {}'
TEMPLATE_PILOT = 'pilot: {}'
TEMPLATE_PROFILE = 'profile:  {}'
TEMPLATE_RECORD_NOT_FOUND = 'record not found: {}'
TEMPLATE_REMOVE = '  remove {}'
TEMPLATE_REQUIRED = '  required: {}'
TEMPLATE_RESTORED_INTO = 'restored {} into {}'
TEMPLATE_RISK = 'risk: {}'
TEMPLATE_RUN_RECORD_MUST_BE_A_JSON_OBJECT = '{}: run record must be a JSON object'
TEMPLATE_SPEC_S = '\n{} spec(s)'
TEMPLATE_STATUS = 'status:  {}'
TEMPLATE_SUCCESS = 'success: {}'
TEMPLATE_SUMMARY_OK_WARN_FAIL = '\nsummary: {} ok, {} warn, {} fail'
TEMPLATE_TARGET = 'target: {}'
TEMPLATE_TARGET_2 = 'target:   {}'
TEMPLATE_TASKS = 'tasks: {}'
TEMPLATE_TASK_S = '\n{} task(s)'
TEMPLATE_TEMPLATE = '  {}'
TEMPLATE_TEMPLATE_2 = '{}'
TEMPLATE_TEMPLATE_3 = '{}: {}'
TEMPLATE_TEMPLATE_4 = '{}/{} ({})'
TEMPLATE_TEMPLATE_5 = '{} {} {}'
TEMPLATE_TEMPLATE_6 = '{} -> {}'
TEMPLATE_TEMPLATE_7 = '  {}: {}'
TEMPLATE_TEMPLATE_8 = '     {}'
TEMPLATE_TOOLS_MAY_INSTALL_GLOBALLY_USE_PROFILE_MINIMAL_TO_ = 'tools:    {} (may install globally; use --profile minimal to skip)'
TEMPLATE_TOOLWRIGHT = 'toolwright: {}'
TEMPLATE_TOOLWRIGHT_2 = 'toolwright {}'
TEMPLATE_TOOLWRIGHT_EXTERNAL_COMMAND_FAILED = 'toolwright: external command failed: {}'
TEMPLATE_TOOLWRIGHT_EXTERNAL_COMMAND_TIMED_OUT = 'toolwright: external command timed out: {}'
TEMPLATE_UNKNOWN_PROFILE = 'unknown profile: {}'
TEMPLATE_VALIDATOR_MODE = 'validator_mode: {}'
TEMPLATE_VERIFICATION_EXIT = 'verification exit: {}'
TEMPLATE_WIP_LIMIT = 'WIP limit: {}'
TEMPLATE_WORKSPACE = 'workspace: {}'
TEMPLATE_WORKTREE = '{} worktree: {}'
TEMPLATE_WORKTREE_2 = 'worktree: {}'
TEMPLATE_CHECK_LINE = '{:<4} {:<{}} {}'

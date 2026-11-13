"""
CLI argument parser.

Public API: :func:`build_argument_parser`.

Side effects: none.
"""
from __future__ import annotations
from .cli_strings import TEXT_TARGET_PLATFORM_ADAPTER
from .cli_strings import TEMPLATE_TOOLWRIGHT_2
from .cli_strings import (
    FLAG_AGENT,
    FLAG_APPROVED,
    FLAG_BACKUP,
    FLAG_BUDGET,
    FLAG_CHECK,
    FLAG_CHECK_DRIFT,
    FLAG_CONFIDENCE,
    FLAG_CONFIG,
    FLAG_CRITERION,
    FLAG_FORMAT,
    FLAG_JSON,
    FLAG_KEEP,
    FLAG_PLATFORM,
    FLAG_LINK,
    FLAG_LIST,
    FLAG_NO_CACHE,
    FLAG_NO_MCP,
    FLAG_PROMPT,
    FLAG_PURGE,
    FLAG_RECORD,
    FLAG_REMOTE,
    FLAG_REMOVE,
    FLAG_REPO,
    FLAG_RESULTS,
    FLAG_RISK,
    FLAG_SCOPE,
    FLAG_SETUP,
    FLAG_SOURCE,
    FLAG_STATUS,
    FLAG_TARGET,
    FLAG_TITLE,
    FLAG_TTL_DAYS,
    FLAG_VERIFY,
    FLAG_VERSION,
    FLAG_WORKSPACE,
    FLAG_WORKTREE,
    KEY_BUILD,
    KEY_CATALOG,
    KEY_CATALOG_COMMAND,
    KEY_COMMAND,
    KEY_COMPAT,
    KEY_COORDINATOR,
    KEY_CSV,
    KEY_DECISION,
    KEY_EVAL,
    KEY_EXPORT,
    KEY_GATE,
    KEY_GOVERN,
    KEY_GOVERN_COMMAND,
    KEY_HIGH,
    KEY_IDENTIFIER,
    KEY_LOW,
    KEY_MANUAL,
    KEY_MEDIUM,
    KEY_MEMORY,
    KEY_MEMORY_COMMAND,
    KEY_MINIMAL,
    KEY_MOVE,
    KEY_PILOT_COMMAND,
    KEY_PLAN,
    KEY_PREAMBLE,
    KEY_PROFILE_COMMAND,
    KEY_PROJECT,
    KEY_PRUNE,
    KEY_QUERY,
    KEY_RUN,
    KEY_SPEC,
    KEY_SPEC_COMMAND,
    KEY_STATS,
    KEY_TASK,
    KEY_TASK_COMMAND,
    KEY_TEXT,
    KEY_TOOLWRIGHT,
    KEY_USE,
    KEY_VERSION,
    TEXT_ADD_A_MEMORY_ENTRY,
    TEXT_ADD_A_TASK,
    TEXT_ADD_SEARCH_PRUNE_EXPORT_OR_RENDER_PROJECT_MEMORY,
    TEXT_ALLOW_A_DUPLICATE_TITLE,
    TEXT_APPLY_A_PROFILE,
    TEXT_APPLY_EVEN_WHEN_ALREADY_CURRENT,
    TEXT_BACKUP_DIRECTORY_TO_RESTORE,
    TEXT_BACK_UP_AND_REPLACE_MANAGED_DIRECTORIES,
    TEXT_COMMAND,
    TEXT_COMMA_SEPARATED_COMPONENTS_INSTEAD_OF_A_PROFILE,
    TEXT_COMPARE_THE_LOCK_WITH_THE_CURRENT_AND_REMOTE_SOURCE,
    TEXT_COMPARE_WITH_THE_PROVENANCE_REGISTRY,
    TEXT_CONFIG_PATH_DEFAULT_TOOLWRIGHT_CONFIG_TOML,
    TEXT_CONFIRM_COMPLETION,
    TEXT_CONFIRM_DELETION,
    TEXT_CONFIRM_DESTRUCTIVE_REMOVAL,
    TEXT_CONFIRM_THE_OVERWRITE,
    TEXT_CONFIRM_WORKTREE_REMOVAL,
    TEXT_CREATE_AND_VERIFY_SPEC_DRIVEN_DEVELOPMENT_ARTIFACTS,
    TEXT_CREATE_A_GIT_WORKTREE_FOR_THE_TASK,
    TEXT_CREATE_A_SPEC,
    TEXT_CREATE_OR_REMOVE_A_TASK_WORKTREE,
    TEXT_DELETE_EXPIRED_ENTRIES,
    TEXT_DEPENDENCY_SETUP_COMMAND_RUN_IN_THE_CLONE,
    TEXT_DIAGNOSE_THE_REPOSITORY_AND_ENVIRONMENT,
    TEXT_EMIT_MACHINE_READABLE_JSON,
    TEXT_EVALUATE_A_RUN_RECORD_AGAINST_BUDGETS,
    TEXT_EXECUTE_THE_PLAN,
    TEXT_EXECUTE_THE_REMOVAL,
    TEXT_EXECUTE_THE_RESTORE,
    TEXT_EXPORT_MEMORY,
    TEXT_FAIL_WHEN_TOTAL_COST_EXCEEDS_THIS_AMOUNT_IN_USD,
    TEXT_FILTER_BY_ARTIFACT_TYPE,
    TEXT_IGNORE_CACHED_RESULTS,
    TEXT_INSPECT_CONTRACTS_AND_EVALUATE_GOVERNANCE_LIMITS,
    TEXT_INSTALL_INSPECT_AND_UPDATE_THE_TOOLWRIGHT_PROFILE,
    TEXT_JSON_RUN_RECORD,
    TEXT_KEEP_THE_DISPOSABLE_CLONE,
    TEXT_LIST_AVAILABLE_PROFILES,
    TEXT_LIST_BACKUPS_DEFAULT,
    TEXT_LIST_CATALOG_ENTRIES,
    TEXT_LIST_CONFIGURED_PILOTS,
    TEXT_LIST_OR_REMOVE_EXPIRED_ENTRIES,
    TEXT_LIST_OR_RESTORE_CONFIGURATION_BACKUPS,
    TEXT_LIST_OR_RUN_REAL_REPOSITORY_PILOTS,
    TEXT_LIST_SEARCH_VERIFY_OR_BUILD_THE_ARTIFACT_CATALOG,
    TEXT_LIST_SHOW_VERIFY_OR_APPLY_PROFILE_MANIFESTS,
    TEXT_LIST_SPECS,
    TEXT_LIST_TASKS,
    TEXT_MANAGE_THE_OPTIONAL_MARKDOWN_TASK_BOARD,
    TEXT_MOVE_A_TASK_TO_A_STATUS,
    TEXT_OPENCODE_AGENT_FOR_THE_RUN,
    TEXT_PLAN_OR_APPLY_AN_INSTALLATION,
    TEXT_PLAN_OR_REMOVE_FILES_RECORDED_IN_TOOLWRIGHT_LOCK_JSON,
    TEXT_PRINT_THE_PLAN_WITHOUT_CLONING,
    TEXT_PRINT_THE_PLAN_WITHOUT_REMOVING_DEFAULT,
    TEXT_PRINT_THE_PLAN_WITHOUT_WRITING_DEFAULT,
    TEXT_PROFILE_MANIFEST_NAME_DEFAULT_STANDARD,
    TEXT_PROJECT_DIRECTORY_DEFAULTS_TO_THE_CURRENT_DIRECTORY,
    TEXT_QUERY_THE_UPSTREAM_HEAD,
    TEXT_REGENERATE_THE_CATALOG,
    TEXT_REMOVE_MODIFIED_FILES_TOO,
    TEXT_REMOVE_TOOLWRIGHT_STATE_AND_THE_LOCK,
    TEXT_RENDER_THE_BOUNDED_PREAMBLE,
    TEXT_REPORT_COST_TOKENS_FAILURES_AND_ARM_COMPARISONS,
    TEXT_REPORT_STATUS_DEFAULT,
    TEXT_REPOSITORY_ROOT_DEFAULTS_TO_THE_CURRENT_CHECKOUT,
    TEXT_RESULT_DIRECTORY_REPEATABLE,
    TEXT_RUN_DETERMINISTIC_EVALUATION_CASES,
    TEXT_RUN_ONE_PILOT,
    TEXT_RUN_ONLY_THE_NAMED_CASE,
    TEXT_RUN_ONLY_THE_NAMED_CHECK_REPEATABLE,
    TEXT_RUN_THE_CONFIGURED_DETERMINISTIC_VERIFICATION_CHECKS,
    TEXT_SEARCH_CATALOG_ENTRIES,
    TEXT_SEARCH_MEMORY_LEXICALLY,
    TEXT_SHOW_BOARD_COUNTS,
    TEXT_SHOW_DERIVED_AGENT_CONTRACTS,
    TEXT_SHOW_ONE_PROFILE,
    TEXT_SHOW_THE_OPENCODE_V1_V2_COMPATIBILITY_MATRIX,
    TEXT_SHOW_THE_REQUIRED_GATES_FOR_A_RISK_LEVEL,
    TEXT_SKIP_THE_MCP_CONNECTIVITY_CHECK,
    TEXT_TASK_PROMPT,
    TEXT_VALIDATE_CRITERIA_AND_TASKS,
    TEXT_VALIDATE_EVERY_PROFILE_MANIFEST,
    TEXT_VALIDATE_THE_CATALOG,
    TEXT_VERIFICATION_COMMAND,
    TEXT_VERIFICATION_COMMAND_RECORDED_WITH_THE_TASK,
    TEXT_VERIFY_TASKS_AND_EVIDENCE,
    TEXT_WORKSPACE_DIRECTORY_DEFAULTS_TO_A_TEMPORARY_DIRECTORY,
)

import argparse

from .. import __version__
from ..cli_constants import (
    ARG_APPEND, ARG_STORE_TRUE, COMMAND_ADD, COMMAND_CHECK, COMMAND_CONTRACTS,
    COMMAND_DOCTOR, COMMAND_INSTALL, COMMAND_LIST, COMMAND_NEW, COMMAND_PILOT,
    COMMAND_ROLLBACK, COMMAND_SEARCH, COMMAND_SHOW, COMMAND_UNINSTALL, COMMAND_UPDATE,
    COMMAND_VERIFY, COMMAND_WORKTREE, FLAG_APPLY, FLAG_CLEAN, FLAG_DRY_RUN, FLAG_FORCE,
    FLAG_ONLY, FLAG_PROFILE, FLAG_TYPE, FLAG_YES, FORMAT_JSON, FORMAT_MARKDOWN, KEY_PROFILE,
    KEY_STATUS, KEY_TYPE,
)
from ..constants import EMPTY_STRING, KEY_FEATURE, KEY_NAME, KEY_TITLE, PLATFORM_CHOICES
from .. import board as board_module
from .. import memory as memory_module
from ..profiles import DEFAULT_PROFILE

def build_argument_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(FLAG_REPO, help=TEXT_REPOSITORY_ROOT_DEFAULTS_TO_THE_CURRENT_CHECKOUT)
    common.add_argument(FLAG_TARGET, help=TEXT_PROJECT_DIRECTORY_DEFAULTS_TO_THE_CURRENT_DIRECTORY)
    common.add_argument(FLAG_JSON, action=ARG_STORE_TRUE, help=TEXT_EMIT_MACHINE_READABLE_JSON)

    parser = argparse.ArgumentParser(
        prog=KEY_TOOLWRIGHT,
        description=TEXT_INSTALL_INSPECT_AND_UPDATE_THE_TOOLWRIGHT_PROFILE,
    )
    parser.add_argument(FLAG_VERSION, action=KEY_VERSION, version=TEMPLATE_TOOLWRIGHT_2.format(__version__))
    subparsers = parser.add_subparsers(dest=KEY_COMMAND, required=True, metavar=TEXT_COMMAND)

    doctor = subparsers.add_parser(COMMAND_DOCTOR, parents=[common], help=TEXT_DIAGNOSE_THE_REPOSITORY_AND_ENVIRONMENT)
    doctor.add_argument(FLAG_NO_MCP, action=ARG_STORE_TRUE, help=TEXT_SKIP_THE_MCP_CONNECTIVITY_CHECK)

    install_parser = subparsers.add_parser(
        COMMAND_INSTALL, parents=[common], help=TEXT_PLAN_OR_APPLY_AN_INSTALLATION
    )
    install_parser.add_argument(FLAG_PROFILE, default=DEFAULT_PROFILE, help=TEXT_PROFILE_MANIFEST_NAME_DEFAULT_STANDARD)
    install_parser.add_argument(FLAG_ONLY, help=TEXT_COMMA_SEPARATED_COMPONENTS_INSTEAD_OF_A_PROFILE)
    mode = install_parser.add_mutually_exclusive_group()
    mode.add_argument(FLAG_APPLY, action=ARG_STORE_TRUE, help=TEXT_EXECUTE_THE_PLAN)
    mode.add_argument(FLAG_DRY_RUN, action=ARG_STORE_TRUE, help=TEXT_PRINT_THE_PLAN_WITHOUT_WRITING_DEFAULT)
    install_parser.add_argument(FLAG_FORCE, action=ARG_STORE_TRUE, help=TEXT_APPLY_EVEN_WHEN_ALREADY_CURRENT)
    install_parser.add_argument(FLAG_CLEAN, action=ARG_STORE_TRUE, help=TEXT_BACK_UP_AND_REPLACE_MANAGED_DIRECTORIES)
    install_parser.add_argument(FLAG_PLATFORM, default=PLATFORM_CHOICES[0], choices=PLATFORM_CHOICES, help=TEXT_TARGET_PLATFORM_ADAPTER)

    uninstall_parser = subparsers.add_parser(
        COMMAND_UNINSTALL, parents=[common], help=TEXT_PLAN_OR_REMOVE_FILES_RECORDED_IN_TOOLWRIGHT_LOCK_JSON
    )
    uninstall_mode = uninstall_parser.add_mutually_exclusive_group()
    uninstall_mode.add_argument(FLAG_APPLY, action=ARG_STORE_TRUE, help=TEXT_EXECUTE_THE_REMOVAL)
    uninstall_mode.add_argument(FLAG_DRY_RUN, action=ARG_STORE_TRUE, help=TEXT_PRINT_THE_PLAN_WITHOUT_REMOVING_DEFAULT)
    uninstall_parser.add_argument(FLAG_YES, action=ARG_STORE_TRUE, help=TEXT_CONFIRM_DESTRUCTIVE_REMOVAL)
    uninstall_parser.add_argument(FLAG_FORCE, action=ARG_STORE_TRUE, help=TEXT_REMOVE_MODIFIED_FILES_TOO)
    uninstall_parser.add_argument(FLAG_PURGE, action=ARG_STORE_TRUE, help=TEXT_REMOVE_TOOLWRIGHT_STATE_AND_THE_LOCK)

    update_parser = subparsers.add_parser(
        COMMAND_UPDATE, parents=[common], help=TEXT_COMPARE_THE_LOCK_WITH_THE_CURRENT_AND_REMOTE_SOURCE
    )
    update_parser.add_argument(FLAG_CHECK, action=ARG_STORE_TRUE, help=TEXT_REPORT_STATUS_DEFAULT)
    update_parser.add_argument(FLAG_REMOTE, action=ARG_STORE_TRUE, help=TEXT_QUERY_THE_UPSTREAM_HEAD)

    rollback_parser = subparsers.add_parser(
        COMMAND_ROLLBACK, parents=[common], help=TEXT_LIST_OR_RESTORE_CONFIGURATION_BACKUPS
    )
    rollback_parser.add_argument(FLAG_LIST, action=ARG_STORE_TRUE, help=TEXT_LIST_BACKUPS_DEFAULT)
    rollback_parser.add_argument(FLAG_BACKUP, help=TEXT_BACKUP_DIRECTORY_TO_RESTORE)
    rollback_parser.add_argument(FLAG_APPLY, action=ARG_STORE_TRUE, help=TEXT_EXECUTE_THE_RESTORE)
    rollback_parser.add_argument(FLAG_YES, action=ARG_STORE_TRUE, help=TEXT_CONFIRM_THE_OVERWRITE)

    profile_parser = subparsers.add_parser(
        KEY_PROFILE, parents=[common], help=TEXT_LIST_SHOW_VERIFY_OR_APPLY_PROFILE_MANIFESTS
    )
    profile_commands = profile_parser.add_subparsers(dest=KEY_PROFILE_COMMAND, required=True)
    profile_commands.add_parser(COMMAND_LIST, parents=[common], help=TEXT_LIST_AVAILABLE_PROFILES)
    profile_show = profile_commands.add_parser(COMMAND_SHOW, parents=[common], help=TEXT_SHOW_ONE_PROFILE)
    profile_show.add_argument(KEY_NAME)
    profile_commands.add_parser(COMMAND_VERIFY, parents=[common], help=TEXT_VALIDATE_EVERY_PROFILE_MANIFEST)
    profile_use = profile_commands.add_parser(KEY_USE, parents=[common], help=TEXT_APPLY_A_PROFILE)
    profile_use.add_argument(KEY_NAME)
    use_mode = profile_use.add_mutually_exclusive_group()
    use_mode.add_argument(FLAG_APPLY, action=ARG_STORE_TRUE, help=TEXT_EXECUTE_THE_PLAN)
    use_mode.add_argument(FLAG_DRY_RUN, action=ARG_STORE_TRUE, help=TEXT_PRINT_THE_PLAN_WITHOUT_WRITING_DEFAULT)
    profile_use.add_argument(FLAG_FORCE, action=ARG_STORE_TRUE, help=TEXT_APPLY_EVEN_WHEN_ALREADY_CURRENT)
    profile_use.add_argument(FLAG_CLEAN, action=ARG_STORE_TRUE, help=TEXT_BACK_UP_AND_REPLACE_MANAGED_DIRECTORIES)
    profile_use.add_argument(FLAG_PLATFORM, default=PLATFORM_CHOICES[0], choices=PLATFORM_CHOICES, help=TEXT_TARGET_PLATFORM_ADAPTER)

    catalog_parser = subparsers.add_parser(
        KEY_CATALOG, parents=[common], help=TEXT_LIST_SEARCH_VERIFY_OR_BUILD_THE_ARTIFACT_CATALOG
    )
    catalog_commands = catalog_parser.add_subparsers(dest=KEY_CATALOG_COMMAND, required=True)
    catalog_list = catalog_commands.add_parser(COMMAND_LIST, parents=[common], help=TEXT_LIST_CATALOG_ENTRIES)
    catalog_list.add_argument(FLAG_TYPE, help=TEXT_FILTER_BY_ARTIFACT_TYPE)
    catalog_search = catalog_commands.add_parser(COMMAND_SEARCH, parents=[common], help=TEXT_SEARCH_CATALOG_ENTRIES)
    catalog_search.add_argument(KEY_QUERY)
    catalog_verify = catalog_commands.add_parser(COMMAND_VERIFY, parents=[common], help=TEXT_VALIDATE_THE_CATALOG)
    catalog_verify.add_argument(FLAG_CHECK_DRIFT, action=ARG_STORE_TRUE, help=TEXT_COMPARE_WITH_THE_PROVENANCE_REGISTRY)
    catalog_commands.add_parser(KEY_BUILD, parents=[common], help=TEXT_REGENERATE_THE_CATALOG)

    subparsers.add_parser(KEY_COMPAT, parents=[common], help=TEXT_SHOW_THE_OPENCODE_V1_V2_COMPATIBILITY_MATRIX)

    task_parser = subparsers.add_parser(
        KEY_TASK, parents=[common], help=TEXT_MANAGE_THE_OPTIONAL_MARKDOWN_TASK_BOARD
    )
    task_commands = task_parser.add_subparsers(dest=KEY_TASK_COMMAND, required=True)
    task_add = task_commands.add_parser(COMMAND_ADD, parents=[common], help=TEXT_ADD_A_TASK)
    task_add.add_argument(KEY_TITLE)
    task_add.add_argument(FLAG_WORKTREE, action=ARG_STORE_TRUE, help=TEXT_CREATE_A_GIT_WORKTREE_FOR_THE_TASK)
    task_add.add_argument(FLAG_VERIFY, default=EMPTY_STRING, help=TEXT_VERIFICATION_COMMAND_RECORDED_WITH_THE_TASK)
    task_list = task_commands.add_parser(COMMAND_LIST, parents=[common], help=TEXT_LIST_TASKS)
    task_list.add_argument(FLAG_STATUS, choices=list(board_module.STATUSES))
    task_move = task_commands.add_parser(KEY_MOVE, parents=[common], help=TEXT_MOVE_A_TASK_TO_A_STATUS)
    task_move.add_argument(KEY_IDENTIFIER)
    task_move.add_argument(KEY_STATUS, choices=list(board_module.STATUSES))
    task_move.add_argument(FLAG_APPROVED, action=ARG_STORE_TRUE, help=TEXT_CONFIRM_COMPLETION)
    task_commands.add_parser(KEY_STATUS, parents=[common], help=TEXT_SHOW_BOARD_COUNTS)
    task_worktree = task_commands.add_parser(COMMAND_WORKTREE, parents=[common], help=TEXT_CREATE_OR_REMOVE_A_TASK_WORKTREE)
    task_worktree.add_argument(KEY_IDENTIFIER)
    task_worktree.add_argument(FLAG_REMOVE, action=ARG_STORE_TRUE)
    task_worktree.add_argument(FLAG_FORCE, action=ARG_STORE_TRUE)
    task_worktree.add_argument(FLAG_YES, action=ARG_STORE_TRUE, help=TEXT_CONFIRM_WORKTREE_REMOVAL)

    verify_parser = subparsers.add_parser(
        COMMAND_VERIFY, parents=[common], help=TEXT_RUN_THE_CONFIGURED_DETERMINISTIC_VERIFICATION_CHECKS
    )
    verify_parser.add_argument(FLAG_ONLY, action=ARG_APPEND, default=[], help=TEXT_RUN_ONLY_THE_NAMED_CHECK_REPEATABLE)
    verify_parser.add_argument(FLAG_NO_CACHE, action=ARG_STORE_TRUE, help=TEXT_IGNORE_CACHED_RESULTS)
    verify_parser.add_argument(FLAG_CONFIG, help=TEXT_CONFIG_PATH_DEFAULT_TOOLWRIGHT_CONFIG_TOML)

    govern_parser = subparsers.add_parser(
        KEY_GOVERN, parents=[common], help=TEXT_INSPECT_CONTRACTS_AND_EVALUATE_GOVERNANCE_LIMITS
    )
    govern_commands = govern_parser.add_subparsers(dest=KEY_GOVERN_COMMAND, required=True)
    govern_commands.add_parser(COMMAND_CONTRACTS, parents=[common], help=TEXT_SHOW_DERIVED_AGENT_CONTRACTS)
    govern_gate = govern_commands.add_parser(KEY_GATE, parents=[common], help=TEXT_SHOW_THE_REQUIRED_GATES_FOR_A_RISK_LEVEL)
    govern_gate.add_argument(FLAG_RISK, required=True, choices=[KEY_LOW, KEY_MEDIUM, KEY_HIGH])
    govern_check = govern_commands.add_parser(COMMAND_CHECK, parents=[common], help=TEXT_EVALUATE_A_RUN_RECORD_AGAINST_BUDGETS)
    govern_check.add_argument(FLAG_RECORD, required=True, help=TEXT_JSON_RUN_RECORD)

    memory_parser = subparsers.add_parser(
        KEY_MEMORY, parents=[common], help=TEXT_ADD_SEARCH_PRUNE_EXPORT_OR_RENDER_PROJECT_MEMORY
    )
    memory_commands = memory_parser.add_subparsers(dest=KEY_MEMORY_COMMAND, required=True)
    memory_add = memory_commands.add_parser(COMMAND_ADD, parents=[common], help=TEXT_ADD_A_MEMORY_ENTRY)
    memory_add.add_argument(KEY_TEXT)
    memory_add.add_argument(FLAG_TYPE, default=KEY_DECISION, choices=list(memory_module.TYPES))
    memory_add.add_argument(FLAG_TITLE)
    memory_add.add_argument(FLAG_SCOPE, default=KEY_PROJECT, choices=list(memory_module.SCOPES))
    memory_add.add_argument(FLAG_SOURCE, default=KEY_MANUAL)
    memory_add.add_argument(FLAG_CONFIDENCE, type=float, default=0.8)
    memory_add.add_argument(FLAG_LINK, action=ARG_APPEND, default=[])
    memory_add.add_argument(FLAG_TTL_DAYS, type=int)
    memory_add.add_argument(FLAG_FORCE, action=ARG_STORE_TRUE, help=TEXT_ALLOW_A_DUPLICATE_TITLE)
    memory_search = memory_commands.add_parser(COMMAND_SEARCH, parents=[common], help=TEXT_SEARCH_MEMORY_LEXICALLY)
    memory_search.add_argument(KEY_QUERY)
    memory_search.add_argument(FLAG_TYPE, choices=list(memory_module.TYPES))
    memory_search.add_argument(FLAG_SCOPE, choices=list(memory_module.SCOPES))
    memory_prune = memory_commands.add_parser(KEY_PRUNE, parents=[common], help=TEXT_LIST_OR_REMOVE_EXPIRED_ENTRIES)
    memory_prune.add_argument(FLAG_APPLY, action=ARG_STORE_TRUE, help=TEXT_DELETE_EXPIRED_ENTRIES)
    memory_prune.add_argument(FLAG_YES, action=ARG_STORE_TRUE, help=TEXT_CONFIRM_DELETION)
    memory_export = memory_commands.add_parser(KEY_EXPORT, parents=[common], help=TEXT_EXPORT_MEMORY)
    memory_export.add_argument(FLAG_FORMAT, default=FORMAT_MARKDOWN, choices=[FORMAT_MARKDOWN, FORMAT_JSON])
    memory_preamble = memory_commands.add_parser(KEY_PREAMBLE, parents=[common], help=TEXT_RENDER_THE_BOUNDED_PREAMBLE)
    memory_preamble.add_argument(FLAG_BUDGET, type=int)

    spec_parser = subparsers.add_parser(
        KEY_SPEC, parents=[common], help=TEXT_CREATE_AND_VERIFY_SPEC_DRIVEN_DEVELOPMENT_ARTIFACTS
    )
    spec_commands = spec_parser.add_subparsers(dest=KEY_SPEC_COMMAND, required=True)
    spec_new = spec_commands.add_parser(COMMAND_NEW, parents=[common], help=TEXT_CREATE_A_SPEC)
    spec_new.add_argument(KEY_FEATURE)
    spec_new.add_argument(FLAG_CRITERION, action=ARG_APPEND, default=[])
    spec_commands.add_parser(COMMAND_LIST, parents=[common], help=TEXT_LIST_SPECS)
    spec_plan = spec_commands.add_parser(KEY_PLAN, parents=[common], help=TEXT_VALIDATE_CRITERIA_AND_TASKS)
    spec_plan.add_argument(KEY_FEATURE)
    spec_verify = spec_commands.add_parser(COMMAND_VERIFY, parents=[common], help=TEXT_VERIFY_TASKS_AND_EVIDENCE)
    spec_verify.add_argument(KEY_FEATURE)

    stats_parser = subparsers.add_parser(
        KEY_STATS, parents=[common], help=TEXT_REPORT_COST_TOKENS_FAILURES_AND_ARM_COMPARISONS
    )
    stats_parser.add_argument(FLAG_RESULTS, action=ARG_APPEND, help=TEXT_RESULT_DIRECTORY_REPEATABLE)
    stats_parser.add_argument(FLAG_FORMAT, default=FORMAT_MARKDOWN, choices=[FORMAT_MARKDOWN, FORMAT_JSON, KEY_CSV])
    stats_parser.add_argument(FLAG_BUDGET, type=float, help=TEXT_FAIL_WHEN_TOTAL_COST_EXCEEDS_THIS_AMOUNT_IN_USD)

    eval_parser = subparsers.add_parser(
        KEY_EVAL, parents=[common], help=TEXT_RUN_DETERMINISTIC_EVALUATION_CASES
    )
    eval_parser.add_argument(FLAG_ONLY, action=ARG_APPEND, default=[], help=TEXT_RUN_ONLY_THE_NAMED_CASE)

    pilot_parser = subparsers.add_parser(
        COMMAND_PILOT, parents=[common], help=TEXT_LIST_OR_RUN_REAL_REPOSITORY_PILOTS
    )
    pilot_commands = pilot_parser.add_subparsers(dest=KEY_PILOT_COMMAND, required=True)
    pilot_commands.add_parser(COMMAND_LIST, parents=[common], help=TEXT_LIST_CONFIGURED_PILOTS)
    pilot_run = pilot_commands.add_parser(KEY_RUN, parents=[common], help=TEXT_RUN_ONE_PILOT)
    pilot_run.add_argument(KEY_NAME)
    pilot_run.add_argument(FLAG_WORKSPACE, help=TEXT_WORKSPACE_DIRECTORY_DEFAULTS_TO_A_TEMPORARY_DIRECTORY)
    pilot_run.add_argument(FLAG_PROMPT, help=TEXT_TASK_PROMPT)
    pilot_run.add_argument(FLAG_VERIFY, help=TEXT_VERIFICATION_COMMAND)
    pilot_run.add_argument(FLAG_PROFILE, default=KEY_MINIMAL)
    pilot_run.add_argument(FLAG_AGENT, default=KEY_COORDINATOR, help=TEXT_OPENCODE_AGENT_FOR_THE_RUN)
    pilot_run.add_argument(FLAG_SETUP, help=TEXT_DEPENDENCY_SETUP_COMMAND_RUN_IN_THE_CLONE)
    pilot_run.add_argument(FLAG_KEEP, action=ARG_STORE_TRUE, help=TEXT_KEEP_THE_DISPOSABLE_CLONE)
    pilot_run.add_argument(FLAG_DRY_RUN, action=ARG_STORE_TRUE, help=TEXT_PRINT_THE_PLAN_WITHOUT_CLONING)

    return parser

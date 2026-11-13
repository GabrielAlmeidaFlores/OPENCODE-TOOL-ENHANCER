"""
Install, uninstall, update, rollback, and doctor command handlers.

Public API: command handler functions used by :mod:`toolwright_cli.cli.main`.

Side effects: delegates to the installer, updater, and diagnostic modules.
"""
from __future__ import annotations
from ..cli_strings import TEMPLATE_BACKUP_DIRECTORY_NOT_FOUND, TEMPLATE_CHANGED, TEMPLATE_KEEP, TEMPLATE_MESSAGE, TEMPLATE_NO_BACKUPS_UNDER, TEMPLATE_REMOVE, TEMPLATE_RESTORED_INTO, TEMPLATE_STATUS, TEMPLATE_TARGET, TEMPLATE_TEMPLATE, TEMPLATE_TEMPLATE_2, TEMPLATE_TEMPLATE_3
from ..cli_strings import (
    FLAG_APPLY_REQUIRES_BACKUP_DIR,
    KEY_ARCHIVES,
    KEY_AVAILABLE_COMMIT,
    KEY_BACKUPS,
    KEY_BASH,
    KEY_CURRENT_COMMIT,
    KEY_CUSTOM,
    KEY_FILES_CHANGED,
    KEY_LOCKED_COMMIT,
    KEY_PROJECT,
    KEY_PURGED,
    KEY_REMOVABLE,
    KEY_SKIPPED,
    KEY_UNKNOWN,
    STATUS_MODIFIED,
    TEXT_NO_LOCK,
    TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_YES_TO_REMOVE_THESE_FILES,
    TEXT_PURGED_LOCK_AND_TOOLWRIGHT_STATE,
    TEXT_REFUSING_TO_REMOVE_FILES_WITHOUT_YES,
    TEXT_REFUSING_TO_RESTORE_WITHOUT_YES,
    TEXT_SCRIPTS_MAINTENANCE_RESTORE_CONFIG_SH,
    TEXT_TOOLWRIGHT,
    TEXT_UPDATE_AVAILABLE,
)

import argparse
from pathlib import Path

from ..common import emit_payload, print_checks, print_install_result, resolve_repository_root
from ...constants import (
    KEY_APPLIED, KEY_PATH, KEY_PROFILE, KEY_STATUS, KEY_TARGET, STATUS_FAIL,
)
from ...cli_constants import (
    COMMAND_CHECK, FLAG_APPLY, FLAG_PROFILE, KEY_DETAIL, KEY_MESSAGE, KEY_OUTPUT,
    STATUS_OK,
)
from ...doctor import checks_as_dict as doctor_dict, run_diagnostic_checks, summarize_checks
from ...installer import install, list_backups, uninstall
from ...paths import ToolWrightError, resolve_target
from ...process import run_command
from ...profiles import load_profiles, resolve_components
from ...updater import check_for_updates

def _command_doctor(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    target = resolve_target(args.target)
    checks = run_diagnostic_checks(root, target, mcp=not args.no_mcp)
    if args.json:
        emit_payload(doctor_dict(checks), True)
    else:
        print_checks(checks)
    return 1 if summarize_checks(checks)[STATUS_FAIL] else 0


def _command_install(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    target = resolve_target(args.target)
    profiles = load_profiles(root)
    components = resolve_components(profiles, args.profile, args.only)
    profile = KEY_CUSTOM if args.only else args.profile
    result = install(
        root=root,
        target=target,
        profile=profile,
        components=components,
        apply=args.apply,
        force=args.force,
        clean=args.clean,
    )
    if args.json:
        emit_payload(result, True)
    else:
        print_install_result(result)
    return 0


def _command_uninstall(args: argparse.Namespace) -> int:
    target = resolve_target(args.target)
    if args.apply and not args.yes:
        raise ToolWrightError(TEXT_REFUSING_TO_REMOVE_FILES_WITHOUT_YES)
    result = uninstall(target=target, apply=args.apply, force=args.force, purge=args.purge)
    if args.json:
        emit_payload(result, True)
        return 0
    print(TEMPLATE_TARGET.format(result[KEY_TARGET]))
    for path in result[KEY_REMOVABLE]:
        print(TEMPLATE_REMOVE.format(path))
    for entry in result[KEY_SKIPPED]:
        print(TEMPLATE_KEEP.format(entry[KEY_PATH], entry[KEY_STATUS]))
    if not result[KEY_APPLIED]:
        print(TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_YES_TO_REMOVE_THESE_FILES)
    elif result.get(KEY_PURGED):
        print(TEXT_PURGED_LOCK_AND_TOOLWRIGHT_STATE)
    return 0


def _command_update(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    target = resolve_target(args.target)
    result = check_for_updates(root, target, remote=args.remote)
    if args.json:
        emit_payload(result, True)
    else:
        print(TEMPLATE_STATUS.format(result[KEY_STATUS]))
        print(TEMPLATE_MESSAGE.format(result[KEY_MESSAGE]))
        for key in (KEY_LOCKED_COMMIT, KEY_CURRENT_COMMIT, KEY_AVAILABLE_COMMIT):
            if result.get(key):
                print(TEMPLATE_TEMPLATE_3.format(key, result[key]))
        for entry in result.get(KEY_FILES_CHANGED, []):
            print(TEMPLATE_CHANGED.format(entry[KEY_PATH], entry[KEY_STATUS]))
    if result[KEY_STATUS] == TEXT_NO_LOCK:
        return 2
    if result[KEY_STATUS] in {TEXT_UPDATE_AVAILABLE, STATUS_MODIFIED, KEY_UNKNOWN}:
        return 1
    return 0


def _command_rollback(args: argparse.Namespace) -> int:
    target = resolve_target(args.target)
    backups = list_backups(target)
    if not args.apply:
        if args.json:
            emit_payload({KEY_TARGET: str(target), KEY_BACKUPS: backups}, True)
            return 0
        if not backups:
            print(TEMPLATE_NO_BACKUPS_UNDER.format(target / TEXT_TOOLWRIGHT / KEY_BACKUPS))
            return 0
        for entry in backups:
            print(TEMPLATE_TEMPLATE_2.format(entry[KEY_PATH]))
            for name in entry[KEY_ARCHIVES]:
                print(TEMPLATE_TEMPLATE.format(name))
        return 0
    if not args.backup:
        raise ToolWrightError(FLAG_APPLY_REQUIRES_BACKUP_DIR)
    if not args.yes:
        raise ToolWrightError(TEXT_REFUSING_TO_RESTORE_WITHOUT_YES)
    backup = Path(args.backup).expanduser().resolve()
    if not backup.is_dir():
        raise ToolWrightError(TEMPLATE_BACKUP_DIRECTORY_NOT_FOUND.format(backup))
    script = resolve_repository_root(args) / TEXT_SCRIPTS_MAINTENANCE_RESTORE_CONFIG_SH
    run_command([KEY_BASH, str(script), str(backup), KEY_PROJECT], cwd=target)
    print(TEMPLATE_RESTORED_INTO.format(backup, target))
    return 0

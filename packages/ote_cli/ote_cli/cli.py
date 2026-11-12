"""
Command-line entry point for ``ote``.

Public API: :func:`main`.

Side effects: delegates to the selected command. Commands that write files do so
only after an explicit ``--apply`` and never stage or commit Git changes.

Module constants: ``DEFERRED`` maps commands owned by later phases to the phase
that implements them.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

from . import __version__
from .doctor import as_dict as doctor_dict
from .doctor import run_checks, summarize
from .installer import (
    PROFILES,
    install,
    list_backups,
    resolve_components,
    uninstall,
)
from .paths import OteError, find_repo_root, resolve_target
from .process import run
from .updater import check as update_check

DEFERRED = {
    "profile": "Phase 3 (profile matrix)",
    "catalog": "Phase 3 (verified catalog)",
    "compat": "Phase 3 (compatibility adapter)",
    "verify": "Phase 4 (verification engine)",
    "memory": "Phase 5 (Markdown memory)",
    "spec": "Phase 5 (spec workflow)",
    "stats": "Phase 6 (observability)",
    "eval": "Phase 6 (evaluations)",
    "pilot": "Phase 6 (pilot runner)",
}


def _build_parser() -> argparse.ArgumentParser:
    """
    Build the full argument parser.
    """
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", help="repository root (defaults to the current checkout)")
    common.add_argument("--target", help="project directory (defaults to the current directory)")
    common.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    parser = argparse.ArgumentParser(
        prog="ote",
        description="Install, inspect, and update the OPENCODE-TOOL-ENHANCER profile.",
    )
    parser.add_argument("--version", action="version", version=f"ote {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    doctor = subparsers.add_parser("doctor", parents=[common], help="diagnose the repository and environment")
    doctor.add_argument("--no-mcp", action="store_true", help="skip the MCP connectivity check")

    install_parser = subparsers.add_parser(
        "install", parents=[common], help="plan or apply an installation"
    )
    install_parser.add_argument("--profile", choices=sorted(PROFILES), default="standard")
    install_parser.add_argument("--only", help="comma-separated components instead of a profile")
    mode = install_parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="execute the plan")
    mode.add_argument("--dry-run", action="store_true", help="print the plan without writing (default)")
    install_parser.add_argument("--force", action="store_true", help="apply even when already current")
    install_parser.add_argument("--clean", action="store_true", help="back up and replace managed directories")

    uninstall_parser = subparsers.add_parser(
        "uninstall", parents=[common], help="plan or remove files recorded in ote.lock.json"
    )
    uninstall_mode = uninstall_parser.add_mutually_exclusive_group()
    uninstall_mode.add_argument("--apply", action="store_true", help="execute the removal")
    uninstall_mode.add_argument("--dry-run", action="store_true", help="print the plan without removing (default)")
    uninstall_parser.add_argument("--yes", action="store_true", help="confirm destructive removal")
    uninstall_parser.add_argument("--force", action="store_true", help="remove modified files too")
    uninstall_parser.add_argument("--purge", action="store_true", help="remove .ote state and the lock")

    update_parser = subparsers.add_parser(
        "update", parents=[common], help="compare the lock with the current and remote source"
    )
    update_parser.add_argument("--check", action="store_true", help="report status (default)")
    update_parser.add_argument("--remote", action="store_true", help="query the upstream HEAD")

    rollback_parser = subparsers.add_parser(
        "rollback", parents=[common], help="list or restore configuration backups"
    )
    rollback_parser.add_argument("--list", action="store_true", help="list backups (default)")
    rollback_parser.add_argument("--backup", help="backup directory to restore")
    rollback_parser.add_argument("--apply", action="store_true", help="execute the restore")
    rollback_parser.add_argument("--yes", action="store_true", help="confirm the overwrite")

    for name, phase in DEFERRED.items():
        command = subparsers.add_parser(name, parents=[common], help=f"available in {phase}")
        command.set_defaults(deferred=name, phase=phase)

    return parser


def _emit(payload: Any, as_json: bool) -> None:
    """
    Print a payload as JSON or as formatted text.
    """
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if isinstance(payload, str):
        print(payload)


def _print_checks(checks: list[Any]) -> None:
    """
    Print diagnostic checks with aligned status labels.
    """
    width = max((len(check.id) for check in checks), default=0)
    for check in checks:
        print(f"{check.status.upper():<4} {check.id:<{width}} {check.detail}")
    summary = summarize(checks)
    print(f"\nsummary: {summary['ok']} ok, {summary['warn']} warn, {summary['fail']} fail")


def _print_install(result: dict[str, Any]) -> None:
    """
    Print an installation result.
    """
    print(f"target:   {result['target']}")
    print(f"profile:  {result['profile']}")
    print(f"components: {', '.join(result['components'])}")
    summary = result["summary"]
    print(f"files:    {summary['new']} new, {summary['updated']} updated, {summary['unchanged']} unchanged")
    tools = [component for component in result["components"] if component in {"ast-grep", "serena", "codegraph"}]
    if tools:
        print(f"tools:    {', '.join(tools)} (may install globally; use --profile minimal to skip)")
    if result.get("output"):
        print(result["output"])
    if result["applied"]:
        if result.get("backup"):
            print(f"backup:   {result['backup']}")
        if result.get("lock"):
            print(f"lock:     {result['lock']}")
        print("verify:   opencode --standalone debug agents")
        return
    if result.get("message"):
        print(result["message"])
        return
    for path in result["planned"]:
        print(f"  {path}")
    print("\nplan only. Re-run with --apply to write these files.")


def _command_doctor(args: argparse.Namespace) -> int:
    """
    Run diagnostics.
    """
    root = _repo(args)
    target = resolve_target(args.target)
    checks = run_checks(root, target, mcp=not args.no_mcp)
    if args.json:
        _emit(doctor_dict(checks), True)
    else:
        _print_checks(checks)
    return 1 if summarize(checks)["fail"] else 0


def _command_install(args: argparse.Namespace) -> int:
    """
    Plan or apply an installation.
    """
    root = _repo(args)
    target = resolve_target(args.target)
    components = resolve_components(args.profile, args.only)
    profile = "custom" if args.only else args.profile
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
        _emit(result, True)
    else:
        _print_install(result)
    return 0


def _command_uninstall(args: argparse.Namespace) -> int:
    """
    Plan or remove managed files.
    """
    target = resolve_target(args.target)
    if args.apply and not args.yes:
        raise OteError("refusing to remove files without --yes")
    result = uninstall(target=target, apply=args.apply, force=args.force, purge=args.purge)
    if args.json:
        _emit(result, True)
        return 0
    print(f"target: {result['target']}")
    for path in result["removable"]:
        print(f"  remove {path}")
    for entry in result["skipped"]:
        print(f"  keep   {entry['path']} ({entry['status']})")
    if not result["applied"]:
        print("\nplan only. Re-run with --apply --yes to remove these files.")
    elif result.get("purged"):
        print("purged lock and .ote state")
    return 0


def _command_update(args: argparse.Namespace) -> int:
    """
    Report update state.
    """
    root = _repo(args)
    target = resolve_target(args.target)
    result = update_check(root, target, remote=args.remote)
    if args.json:
        _emit(result, True)
    else:
        print(f"status:  {result['status']}")
        print(f"message: {result['message']}")
        for key in ("locked_commit", "current_commit", "available_commit"):
            if result.get(key):
                print(f"{key}: {result[key]}")
        for entry in result.get("files_changed", []):
            print(f"  changed {entry['path']} ({entry['status']})")
    if result["status"] == "no-lock":
        return 2
    if result["status"] in {"update-available", "modified", "unknown"}:
        return 1
    return 0


def _command_rollback(args: argparse.Namespace) -> int:
    """
    List or restore configuration backups.
    """
    target = resolve_target(args.target)
    backups = list_backups(target)
    if not args.apply:
        if args.json:
            _emit({"target": str(target), "backups": backups}, True)
            return 0
        if not backups:
            print(f"no backups under {target / '.ote' / 'backups'}")
            return 0
        for entry in backups:
            print(f"{entry['path']}")
            for name in entry["archives"]:
                print(f"  {name}")
        return 0
    if not args.backup:
        raise OteError("--apply requires --backup DIR")
    if not args.yes:
        raise OteError("refusing to restore without --yes")
    backup = Path(args.backup).expanduser().resolve()
    if not backup.is_dir():
        raise OteError(f"backup directory not found: {backup}")
    script = _repo(args) / "scripts/maintenance/restore-config.sh"
    run(["bash", str(script), str(backup), "project"], cwd=target)
    print(f"restored {backup} into {target}")
    return 0


def _command_deferred(args: argparse.Namespace) -> int:
    """
    Report that a planned command is not implemented yet.
    """
    print(
        f"ote {args.deferred}: not available until {args.phase}. "
        "See docs/cli/README.md for the current command surface.",
        file=sys.stderr,
    )
    return 2


def _repo(args: argparse.Namespace) -> Path:
    """
    Resolve the repository root from arguments and environment.
    """
    return find_repo_root(Path(args.repo) if args.repo else None)


def main(argv: Sequence[str] | None = None) -> int:
    """
    Run the CLI and return a process exit code.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "doctor": _command_doctor,
        "install": _command_install,
        "uninstall": _command_uninstall,
        "update": _command_update,
        "rollback": _command_rollback,
    }
    try:
        handler = handlers.get(args.command, _command_deferred)
        return handler(args)
    except OteError as error:
        print(f"ote: {error}", file=sys.stderr)
        return error.exit_code
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or "").strip() or str(error)
        print(f"ote: external command failed: {detail}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired as error:
        print(f"ote: external command timed out: {error}", file=sys.stderr)
        return 2
    except (ValueError, OSError) as error:
        print(f"ote: {error}", file=sys.stderr)
        return 2

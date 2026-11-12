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
from . import catalog as catalog_module
from . import compat as compat_module
from . import governance as governance_module
from . import memory as memory_module
from . import specs as specs_module
from . import verify as verify_module
from .installer import install, list_backups, uninstall
from .paths import OteError, find_repo_root, resolve_target
from .process import run
from .profiles import DEFAULT_PROFILE, load_profiles, resolve_components, verify_profiles
from .updater import check as update_check

DEFERRED = {
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
    install_parser.add_argument("--profile", default=DEFAULT_PROFILE, help="profile manifest name (default: standard)")
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

    profile_parser = subparsers.add_parser(
        "profile", parents=[common], help="list, show, verify, or apply profile manifests"
    )
    profile_commands = profile_parser.add_subparsers(dest="profile_command", required=True)
    profile_commands.add_parser("list", parents=[common], help="list available profiles")
    profile_show = profile_commands.add_parser("show", parents=[common], help="show one profile")
    profile_show.add_argument("name")
    profile_commands.add_parser("verify", parents=[common], help="validate every profile manifest")
    profile_use = profile_commands.add_parser("use", parents=[common], help="apply a profile")
    profile_use.add_argument("name")
    use_mode = profile_use.add_mutually_exclusive_group()
    use_mode.add_argument("--apply", action="store_true", help="execute the plan")
    use_mode.add_argument("--dry-run", action="store_true", help="print the plan without writing (default)")
    profile_use.add_argument("--force", action="store_true", help="apply even when already current")
    profile_use.add_argument("--clean", action="store_true", help="back up and replace managed directories")

    catalog_parser = subparsers.add_parser(
        "catalog", parents=[common], help="list, search, verify, or build the artifact catalog"
    )
    catalog_commands = catalog_parser.add_subparsers(dest="catalog_command", required=True)
    catalog_list = catalog_commands.add_parser("list", parents=[common], help="list catalog entries")
    catalog_list.add_argument("--type", help="filter by artifact type")
    catalog_search = catalog_commands.add_parser("search", parents=[common], help="search catalog entries")
    catalog_search.add_argument("query")
    catalog_verify = catalog_commands.add_parser("verify", parents=[common], help="validate the catalog")
    catalog_verify.add_argument("--check-drift", action="store_true", help="compare with the provenance registry")
    catalog_commands.add_parser("build", parents=[common], help="regenerate the catalog")

    subparsers.add_parser("compat", parents=[common], help="show the OpenCode V1/V2 compatibility matrix")

    verify_parser = subparsers.add_parser(
        "verify", parents=[common], help="run the configured deterministic verification checks"
    )
    verify_parser.add_argument("--only", action="append", default=[], help="run only the named check; repeatable")
    verify_parser.add_argument("--no-cache", action="store_true", help="ignore cached results")
    verify_parser.add_argument("--config", help="config path (default: .ote/config.toml)")

    govern_parser = subparsers.add_parser(
        "govern", parents=[common], help="inspect contracts and evaluate governance limits"
    )
    govern_commands = govern_parser.add_subparsers(dest="govern_command", required=True)
    govern_commands.add_parser("contracts", parents=[common], help="show derived agent contracts")
    govern_gate = govern_commands.add_parser("gate", parents=[common], help="show the required gates for a risk level")
    govern_gate.add_argument("--risk", required=True, choices=["low", "medium", "high"])
    govern_check = govern_commands.add_parser("check", parents=[common], help="evaluate a run record against budgets")
    govern_check.add_argument("--record", required=True, help="JSON run record")

    memory_parser = subparsers.add_parser(
        "memory", parents=[common], help="add, search, prune, export, or render project memory"
    )
    memory_commands = memory_parser.add_subparsers(dest="memory_command", required=True)
    memory_add = memory_commands.add_parser("add", parents=[common], help="add a memory entry")
    memory_add.add_argument("text")
    memory_add.add_argument("--type", default="decision", choices=list(memory_module.TYPES))
    memory_add.add_argument("--title")
    memory_add.add_argument("--scope", default="project", choices=list(memory_module.SCOPES))
    memory_add.add_argument("--source", default="manual")
    memory_add.add_argument("--confidence", type=float, default=0.8)
    memory_add.add_argument("--link", action="append", default=[])
    memory_add.add_argument("--ttl-days", type=int)
    memory_add.add_argument("--force", action="store_true", help="allow a duplicate title")
    memory_search = memory_commands.add_parser("search", parents=[common], help="search memory lexically")
    memory_search.add_argument("query")
    memory_search.add_argument("--type", choices=list(memory_module.TYPES))
    memory_search.add_argument("--scope", choices=list(memory_module.SCOPES))
    memory_prune = memory_commands.add_parser("prune", parents=[common], help="list or remove expired entries")
    memory_prune.add_argument("--apply", action="store_true", help="delete expired entries")
    memory_prune.add_argument("--yes", action="store_true", help="confirm deletion")
    memory_export = memory_commands.add_parser("export", parents=[common], help="export memory")
    memory_export.add_argument("--format", default="markdown", choices=["markdown", "json"])
    memory_preamble = memory_commands.add_parser("preamble", parents=[common], help="render the bounded preamble")
    memory_preamble.add_argument("--budget", type=int)

    spec_parser = subparsers.add_parser(
        "spec", parents=[common], help="create and verify spec-driven development artifacts"
    )
    spec_commands = spec_parser.add_subparsers(dest="spec_command", required=True)
    spec_new = spec_commands.add_parser("new", parents=[common], help="create a spec")
    spec_new.add_argument("feature")
    spec_new.add_argument("--criterion", action="append", default=[])
    spec_commands.add_parser("list", parents=[common], help="list specs")
    spec_plan = spec_commands.add_parser("plan", parents=[common], help="validate criteria and tasks")
    spec_plan.add_argument("feature")
    spec_verify = spec_commands.add_parser("verify", parents=[common], help="verify tasks and evidence")
    spec_verify.add_argument("feature")

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
    profiles = load_profiles(root)
    components = resolve_components(profiles, args.profile, args.only)
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


def _command_profile(args: argparse.Namespace) -> int:
    """
    List, show, verify, or apply profile manifests.
    """
    root = _repo(args)
    action = args.profile_command
    if action == "list":
        profiles = load_profiles(root)
        payload = [
            {"name": profile.name, "description": profile.description, "components": list(profile.components)}
            for profile in profiles.values()
        ]
        if args.json:
            _emit(payload, True)
            return 0
        for profile in profiles.values():
            print(f"{profile.name:<10} {profile.description}")
        return 0
    if action == "show":
        profiles = load_profiles(root)
        if args.name not in profiles:
            raise OteError(f"unknown profile: {args.name}")
        profile = profiles[args.name]
        payload = {
            "name": profile.name,
            "description": profile.description,
            "components": list(profile.components),
            "path": str(profile.path),
        }
        if args.json:
            _emit(payload, True)
            return 0
        print(f"name:        {profile.name}")
        print(f"description: {profile.description}")
        print(f"components:  {', '.join(profile.components)}")
        print(f"path:        {profile.path}")
        return 0
    if action == "verify":
        results = verify_profiles(root)
        if args.json:
            _emit({"profiles": results}, True)
        else:
            for result in results:
                print(f"{result['status'].upper():<4} {result['profile']:<10} {result['detail']}")
        return 1 if any(result["status"] == "fail" for result in results) else 0
    profiles = load_profiles(root)
    components = resolve_components(profiles, args.name, None)
    target = resolve_target(args.target)
    result = install(
        root=root,
        target=target,
        profile=args.name,
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


def _command_catalog(args: argparse.Namespace) -> int:
    """
    List, search, verify, or build the artifact catalog.
    """
    root = _repo(args)
    action = args.catalog_command
    if action == "build":
        result = catalog_module.build(root)
        print(result["output"])
        return 0 if result["status"] == "ok" else 2
    document = catalog_module.load_catalog(root)
    artifacts = document.get("artifacts", [])
    if action == "list":
        selected = artifacts
        if args.type:
            selected = [entry for entry in artifacts if entry.get("type") == args.type]
        if args.json:
            _emit({"artifacts": selected, "count": len(selected)}, True)
            return 0
        for entry in selected:
            print(f"{entry['type']:<8} {entry['id']:<28} {entry['author']:<22} {entry['license']}")
        print(f"\n{len(selected)} artifact(s)")
        return 0
    if action == "search":
        matches = catalog_module.search(document, args.query)
        if args.json:
            _emit({"artifacts": matches, "count": len(matches)}, True)
            return 0
        for entry in matches:
            print(f"{entry['type']:<8} {entry['id']:<28} {entry['author']:<22} {entry['license']}")
        print(f"\n{len(matches)} match(es)")
        return 0
    results = catalog_module.verify(root, document)
    failures = [result for result in results if result["status"] == "fail"]
    if args.check_drift:
        drift = catalog_module.drift(root)
        results.append(
            {
                "check": "drift",
                "status": "ok" if drift["status"] == "ok" else "fail",
                "detail": drift["output"] or "catalog matches the registry",
            }
        )
        failures = [result for result in results if result["status"] == "fail"]
    if args.json:
        _emit({"results": results, "failures": len(failures)}, True)
    else:
        for result in results:
            print(f"{result['status'].upper():<4} {result['check']:<24} {result['detail']}")
        print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


def _command_compat(args: argparse.Namespace) -> int:
    """
    Print the OpenCode V1/V2 compatibility matrix.
    """
    if args.json:
        _emit(compat_module.as_dict(), True)
    else:
        print(compat_module.render_text())
    return 0


def _command_verify(args: argparse.Namespace) -> int:
    """
    Run the configured verification checks.
    """
    root = _repo(args)
    config_path = None
    if args.config:
        candidate = Path(args.config).expanduser()
        config_path = candidate if candidate.is_absolute() else root / candidate
    checks, _ = verify_module.load_config(root, config_path)
    results = verify_module.run_checks(
        root,
        checks,
        only=args.only or None,
        use_cache=not args.no_cache,
    )
    summary = verify_module.summarize(results)
    if args.json:
        _emit(
            {
                "results": [
                    {
                        "name": result.name,
                        "status": result.status,
                        "exit_code": result.exit_code,
                        "seconds": result.seconds,
                        "failure_class": result.failure_class,
                        "cached": result.cached,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    }
                    for result in results
                ],
                "summary": summary,
            },
            True,
        )
    else:
        for result in results:
            suffix = " (cached)" if result.cached else ""
            label = result.failure_class if result.status == "fail" else "ok"
            print(f"{result.status.upper():<4} {result.name:<12} {result.seconds:>6.2f}s  {label}{suffix}")
            if result.status == "fail":
                output = (result.stdout + "\n" + result.stderr).strip().splitlines()
                for line in output[-10:]:
                    print(f"     {line}")
        print(f"\n{summary['passed']} passed, {summary['failed']} failed")
    return 1 if summary["failed"] else 0


def _command_govern(args: argparse.Namespace) -> int:
    """
    Inspect contracts or evaluate governance limits.
    """
    root = _repo(args)
    action = args.govern_command
    if action == "contracts":
        results = governance_module.contracts(root)
        failures = [result for result in results if result["status"] == "fail"]
        if args.json:
            _emit({"contracts": results, "failures": len(failures)}, True)
        else:
            for result in results:
                label = "read-only" if result["read_only"] else "writer"
                print(f"{result['status'].upper():<4} {result['agent']:<22} {result['mode']:<8} {label}")
                for violation in result["violations"]:
                    print(f"     {violation}")
            print(f"\n{len(failures)} failure(s)")
        return 1 if failures else 0
    if action == "gate":
        gate = governance_module.risk_gate(args.risk)
        if args.json:
            _emit(gate, True)
        else:
            print(f"risk: {gate['risk']}")
            for requirement in gate["required"]:
                print(f"  required: {requirement}")
        return 0
    record_path = Path(args.record).expanduser()
    if not record_path.is_file():
        raise OteError(f"record not found: {record_path}")
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise OteError(f"{record_path}: invalid JSON: {error}") from error
    if not isinstance(record, dict):
        raise OteError(f"{record_path}: run record must be a JSON object")
    _, governance = verify_module.load_config(root)
    evaluation = governance_module.evaluate_record(record, governance)
    if args.json:
        _emit(evaluation, True)
    else:
        print(f"allowed: {evaluation['allowed']}")
        print(f"validator_mode: {evaluation['validator_mode']}")
        for violation in evaluation["violations"]:
            print(f"  {violation['kind']}: {violation['detail']}")
    return 0 if evaluation["allowed"] else 1


def _command_memory(args: argparse.Namespace) -> int:
    """
    Add, search, prune, export, or render Markdown memory.
    """
    root = _repo(args)
    action = args.memory_command
    if action == "add":
        entry = memory_module.add(
            root=root,
            text=args.text,
            entry_type=args.type,
            title=args.title,
            scope=args.scope,
            source=args.source,
            confidence=args.confidence,
            links=args.link,
            ttl_days=args.ttl_days,
            force=args.force,
        )
        if args.json:
            _emit({"id": entry.identifier, "scope": entry.scope, "title": entry.title, "path": str(entry.path)}, True)
        else:
            print(f"added {entry.scope}/{entry.identifier} ({entry.entry_type})")
        return 0
    if action == "search":
        results = memory_module.search(root, args.query, entry_type=args.type, scope=args.scope)
        if args.json:
            _emit({"entries": [{"id": item.identifier, "scope": item.scope, "type": item.entry_type, "title": item.title, "expires": item.expires, "expired": item.expired()} for item in results]}, True)
        else:
            for item in results:
                marker = " (expired)" if item.expired() else ""
                print(f"{item.scope:<8} {item.entry_type:<10} {item.title}{marker}")
            print(f"\n{len(results)} match(es)")
        return 0
    if action == "prune":
        if args.apply and not args.yes:
            raise OteError("refusing to delete memory without --yes")
        expired = memory_module.prune(root, apply=args.apply)
        if args.json:
            _emit({"expired": [item.identifier for item in expired], "applied": args.apply}, True)
        else:
            for item in expired:
                print(f"{item.scope}/{item.identifier} ({item.expires})")
            print(f"{len(expired)} expired entr{'y' if len(expired) == 1 else 'ies'}")
            if not args.apply:
                print("plan only. Re-run with --apply --yes to delete.")
        return 0
    if action == "export":
        output = memory_module.export(root, "json" if args.json else args.format)
        print(output, end="" if output.endswith("\n") else "\n")
        return 0
    print(memory_module.preamble(root, args.budget), end="")
    return 0


def _command_spec(args: argparse.Namespace) -> int:
    """
    Create, list, plan, or verify spec artifacts.
    """
    root = _repo(args)
    action = args.spec_command
    if action == "new":
        directory = specs_module.create(root, args.feature, args.criterion)
        if args.json:
            _emit({"feature": directory.name, "path": str(directory), "files": list(specs_module.FILES)}, True)
        else:
            print(f"created {directory}")
            for name in specs_module.FILES:
                print(f"  {name}")
        return 0
    if action == "list":
        results = specs_module.list_specs(root)
        if args.json:
            _emit({"specs": results}, True)
        else:
            for result in results:
                state = "complete" if result["complete"] else f"missing {', '.join(result['missing'])}"
                print(f"{result['name']:<30} {state}")
            print(f"\n{len(results)} spec(s)")
        return 0
    result = specs_module.plan(root, args.feature) if action == "plan" else specs_module.verify(root, args.feature)
    if args.json:
        _emit(result, True)
    else:
        print(f"feature: {result['feature']}")
        print(f"status:  {result['status']}")
        for issue in result["issues"]:
            print(f"  {issue}")
    return 0 if result["status"] == "ok" else 1


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
        "profile": _command_profile,
        "catalog": _command_catalog,
        "compat": _command_compat,
        "verify": _command_verify,
        "govern": _command_govern,
        "memory": _command_memory,
        "spec": _command_spec,
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

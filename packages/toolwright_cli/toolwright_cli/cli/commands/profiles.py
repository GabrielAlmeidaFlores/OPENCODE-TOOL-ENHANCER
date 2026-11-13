"""
Profile, catalog, and compatibility command handlers.

Public API: command handler functions used by :mod:`toolwright_cli.cli.main`.

Side effects: delegates to profile, catalog, and compatibility modules.
"""
from __future__ import annotations
from ..cli_strings import TEMPLATE_10, TEMPLATE_4_10, TEMPLATE_4_24, TEMPLATE_8_28_22, TEMPLATE_ARTIFACT_S, TEMPLATE_COMPONENTS, TEMPLATE_DESCRIPTION, TEMPLATE_FAILURE_S, TEMPLATE_MATCH_ES, TEMPLATE_NAME, TEMPLATE_PATH, TEMPLATE_UNKNOWN_PROFILE
from ..cli_strings import (
    KEY_AUTHOR,
    KEY_BUILD,
    KEY_COUNT,
    KEY_DESCRIPTION,
    KEY_DRIFT,
    KEY_LICENSE,
    KEY_PROFILES,
    TEXT_CATALOG_MATCHES_THE_REGISTRY,
)

import argparse

from ..common import emit_payload, print_install_result, resolve_repository_root
from ...constants import (
    KEY_ARTIFACTS, KEY_COMPONENTS, KEY_DETAIL, KEY_ID, KEY_NAME, KEY_OUTPUT, KEY_PATH,
    KEY_PROFILE, KEY_STATUS, KEY_TYPE, STATUS_FAIL, STATUS_OK, SEPARATOR_COMMA_SPACE,
)
from ...cli_constants import (
    COMMAND_CHECK, COMMAND_LIST, COMMAND_SEARCH, COMMAND_SHOW, COMMAND_VERIFY,
    KEY_FAILURES, KEY_RESULTS,
)
from ... import catalog as catalog_module
from ... import compat as compat_module
from ...installer import install
from ...paths import ToolWrightError, resolve_target
from ...profiles import load_profiles, resolve_components, verify_profiles

def _command_profile(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    action = args.profile_command
    if action == COMMAND_LIST:
        profiles = load_profiles(root)
        payload = [
            {KEY_NAME: profile.name, KEY_DESCRIPTION: profile.description, KEY_COMPONENTS: list(profile.components)}
            for profile in profiles.values()
        ]
        if args.json:
            emit_payload(payload, True)
            return 0
        for profile in profiles.values():
            print(TEMPLATE_10.format(profile.name, profile.description))
        return 0
    if action == COMMAND_SHOW:
        profiles = load_profiles(root)
        if args.name not in profiles:
            raise ToolWrightError(TEMPLATE_UNKNOWN_PROFILE.format(args.name))
        profile = profiles[args.name]
        payload = {
            KEY_NAME: profile.name,
            KEY_DESCRIPTION: profile.description,
            KEY_COMPONENTS: list(profile.components),
            KEY_PATH: str(profile.path),
        }
        if args.json:
            emit_payload(payload, True)
            return 0
        print(TEMPLATE_NAME.format(profile.name))
        print(TEMPLATE_DESCRIPTION.format(profile.description))
        print(TEMPLATE_COMPONENTS.format(SEPARATOR_COMMA_SPACE.join(profile.components)))
        print(TEMPLATE_PATH.format(profile.path))
        return 0
    if action == COMMAND_VERIFY:
        results = verify_profiles(root)
        if args.json:
            emit_payload({KEY_PROFILES: results}, True)
        else:
            for result in results:
                print(TEMPLATE_4_10.format(result[KEY_STATUS].upper(), result[KEY_PROFILE], result[KEY_DETAIL]))
        return 1 if any(result[KEY_STATUS] == STATUS_FAIL for result in results) else 0
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
        adapter=args.platform,
    )
    if args.json:
        emit_payload(result, True)
    else:
        print_install_result(result)
    return 0


def _command_catalog(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    action = args.catalog_command
    if action == KEY_BUILD:
        result = catalog_module.build_catalog(root)
        print(result[KEY_OUTPUT])
        return 0 if result[KEY_STATUS] == STATUS_OK else 2
    document = catalog_module.load_catalog(root)
    artifacts = document.get(KEY_ARTIFACTS, [])
    if action == COMMAND_LIST:
        selected = artifacts
        if args.type:
            selected = [entry for entry in artifacts if entry.get(KEY_TYPE) == args.type]
        if args.json:
            emit_payload({KEY_ARTIFACTS: selected, KEY_COUNT: len(selected)}, True)
            return 0
        for entry in selected:
            print(TEMPLATE_8_28_22.format(entry[KEY_TYPE], entry[KEY_ID], entry[KEY_AUTHOR], entry[KEY_LICENSE]))
        print(TEMPLATE_ARTIFACT_S.format(len(selected)))
        return 0
    if action == COMMAND_SEARCH:
        matches = catalog_module.search_catalog(document, args.query)
        if args.json:
            emit_payload({KEY_ARTIFACTS: matches, KEY_COUNT: len(matches)}, True)
            return 0
        for entry in matches:
            print(TEMPLATE_8_28_22.format(entry[KEY_TYPE], entry[KEY_ID], entry[KEY_AUTHOR], entry[KEY_LICENSE]))
        print(TEMPLATE_MATCH_ES.format(len(matches)))
        return 0
    results = catalog_module.verify_catalog(root, document)
    failures = [result for result in results if result[KEY_STATUS] == STATUS_FAIL]
    if args.check_drift:
        drift = catalog_module.check_catalog_drift(root)
        results.append(
            {
                COMMAND_CHECK: KEY_DRIFT,
                KEY_STATUS: STATUS_OK if drift[KEY_STATUS] == STATUS_OK else STATUS_FAIL,
                KEY_DETAIL: drift[KEY_OUTPUT] or TEXT_CATALOG_MATCHES_THE_REGISTRY,
            }
        )
        failures = [result for result in results if result[KEY_STATUS] == STATUS_FAIL]
    if args.json:
        emit_payload({KEY_RESULTS: results, KEY_FAILURES: len(failures)}, True)
    else:
        for result in results:
            print(TEMPLATE_4_24.format(result[KEY_STATUS].upper(), result[COMMAND_CHECK], result[KEY_DETAIL]))
        print(TEMPLATE_FAILURE_S.format(len(failures)))
    return 1 if failures else 0


def _command_compat(args: argparse.Namespace) -> int:
    if args.json:
        emit_payload(compat_module.as_compatibility_dict(), True)
    else:
        print(compat_module.render_text())
    return 0

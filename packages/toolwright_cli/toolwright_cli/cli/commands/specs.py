"""
Spec workflow command handler.

Public API: :func:`_command_spec`.

Side effects: delegates to the specs module.
"""
from __future__ import annotations
from ..cli_strings import TEMPLATE_30, TEMPLATE_CREATED, TEMPLATE_FEATURE, TEMPLATE_MISSING, TEMPLATE_SPEC_S, TEMPLATE_STATUS, TEMPLATE_TEMPLATE
from ..cli_strings import (
    KEY_COMPLETE,
    KEY_FILES,
    KEY_ISSUES,
    KEY_PLAN,
    KEY_SPECS,
    STATUS_MISSING,
)

import argparse

from ..common import emit_payload, resolve_repository_root
from ...constants import (
    KEY_FEATURE, KEY_NAME, KEY_PATH, KEY_STATUS, STATUS_OK, SEPARATOR_COMMA_SPACE,
)
from ...cli_constants import COMMAND_LIST, COMMAND_NEW
from ... import specs as specs_module

def _command_spec(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    action = args.spec_command
    if action == COMMAND_NEW:
        directory = specs_module.create_spec_artifacts(root, args.feature, args.criterion)
        if args.json:
            emit_payload({KEY_FEATURE: directory.name, KEY_PATH: str(directory), KEY_FILES: list(specs_module.FILES)}, True)
        else:
            print(TEMPLATE_CREATED.format(directory))
            for name in specs_module.FILES:
                print(TEMPLATE_TEMPLATE.format(name))
        return 0
    if action == COMMAND_LIST:
        results = specs_module.list_specs(root)
        if args.json:
            emit_payload({KEY_SPECS: results}, True)
        else:
            for result in results:
                state = KEY_COMPLETE if result[KEY_COMPLETE] else TEMPLATE_MISSING.format(SEPARATOR_COMMA_SPACE.join(result[STATUS_MISSING]))
                print(TEMPLATE_30.format(result[KEY_NAME], state))
            print(TEMPLATE_SPEC_S.format(len(results)))
        return 0
    result = specs_module.validate_spec_plan(root, args.feature) if action == KEY_PLAN else specs_module.verify_spec_evidence(root, args.feature)
    if args.json:
        emit_payload(result, True)
    else:
        print(TEMPLATE_FEATURE.format(result[KEY_FEATURE]))
        print(TEMPLATE_STATUS.format(result[KEY_STATUS]))
        for issue in result[KEY_ISSUES]:
            print(TEMPLATE_TEMPLATE.format(issue))
    return 0 if result[KEY_STATUS] == STATUS_OK else 1

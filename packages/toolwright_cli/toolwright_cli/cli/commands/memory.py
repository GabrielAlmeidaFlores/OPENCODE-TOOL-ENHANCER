"""
Memory command handler.

Public API: :func:`_command_memory`.

Side effects: delegates to the memory module.
"""
from __future__ import annotations
from ..cli_strings import TEMPLATE_8_10, TEMPLATE_ADDED, TEMPLATE_EXPIRED_ENTR, TEMPLATE_MATCH_ES, TEMPLATE_TEMPLATE_4
from ..cli_strings import (
    KEY_ENTRIES,
    KEY_EXPIRED,
    KEY_EXPIRES,
    KEY_EXPORT,
    KEY_IES,
    KEY_PRUNE,
    KEY_SCOPE,
    KEY_Y,
    TEXT_EXPIRED,
    TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_YES_TO_DELETE,
    TEXT_REFUSING_TO_DELETE_MEMORY_WITHOUT_YES,
)

import argparse

from ..common import emit_payload, resolve_repository_root
from ...constants import (
    KEY_APPLIED, KEY_ID, KEY_PATH, KEY_TITLE, KEY_TYPE, NEWLINE,
)
from ...cli_constants import (
    COMMAND_ADD, COMMAND_SEARCH, EMPTY_STRING, FORMAT_JSON,
)
from ... import memory as memory_module
from ...paths import ToolWrightError

def _command_memory(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    action = args.memory_command
    if action == COMMAND_ADD:
        entry = memory_module.add_memory_entry(
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
            emit_payload({KEY_ID: entry.identifier, KEY_SCOPE: entry.scope, KEY_TITLE: entry.title, KEY_PATH: str(entry.path)}, True)
        else:
            print(TEMPLATE_ADDED.format(entry.scope, entry.identifier, entry.entry_type))
        return 0
    if action == COMMAND_SEARCH:
        results = memory_module.search_memory_entries(root, args.query, entry_type=args.type, scope=args.scope)
        if args.json:
            emit_payload({KEY_ENTRIES: [{KEY_ID: item.identifier, KEY_SCOPE: item.scope, KEY_TYPE: item.entry_type, KEY_TITLE: item.title, KEY_EXPIRES: item.expires, KEY_EXPIRED: item.expired()} for item in results]}, True)
        else:
            for item in results:
                marker = TEXT_EXPIRED if item.expired() else EMPTY_STRING
                print(TEMPLATE_8_10.format(item.scope, item.entry_type, item.title, marker))
            print(TEMPLATE_MATCH_ES.format(len(results)))
        return 0
    if action == KEY_PRUNE:
        if args.apply and not args.yes:
            raise ToolWrightError(TEXT_REFUSING_TO_DELETE_MEMORY_WITHOUT_YES)
        expired = memory_module.prune_expired_entries(root, apply=args.apply)
        if args.json:
            emit_payload({KEY_EXPIRED: [item.identifier for item in expired], KEY_APPLIED: args.apply}, True)
        else:
            for item in expired:
                print(TEMPLATE_TEMPLATE_4.format(item.scope, item.identifier, item.expires))
            print(TEMPLATE_EXPIRED_ENTR.format(len(expired), KEY_Y if len(expired) == 1 else KEY_IES))
            if not args.apply:
                print(TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_YES_TO_DELETE)
        return 0
    if action == KEY_EXPORT:
        output = memory_module.export_memory_entries(root, FORMAT_JSON if args.json else args.format)
        print(output, end=EMPTY_STRING if output.endswith(NEWLINE) else NEWLINE)
        return 0
    print(memory_module.render_memory_preamble(root, args.budget), end=EMPTY_STRING)
    return 0

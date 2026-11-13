"""
Enforce the shell string-constant migration ledger.

Public API: none. The module is a unittest test case.

Side effects: reads shell scripts and the migration ledger. It does not write.

The scanner extracts quoted shell strings, ignores comments and pure variable or
command expansions, and compares exact counts with the ledger.
"""
from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from pathlib import Path

from tests import support

LEDGER = support.FIXTURES / "shell_literals_ledger.txt"
SCRIPTS = support.REPO_ROOT / "scripts"
CONSTANT_LIBRARY = SCRIPTS / "lib/strings.sh"
QUOTED = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\'')
VARIABLE = re.compile(r"\$(?:\([^)]*\)|\{[^}]*\}|[A-Za-z_][A-Za-z0-9_]*|[0-9@*#?$!-])")


def is_literal(value: str) -> bool:
    if "$" in value:
        return False
    if value.strip() in {"EOF", "0", "1"}:
        return False
    if value.endswith((")", "}")) or value.startswith("("):
        return False
    if not re.search(r"[A-Za-z]", value):
        return False
    return bool(VARIABLE.sub("", value).strip())


def collect_file(path: Path) -> Counter[str]:
    values: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        for match in QUOTED.finditer(line):
            value = match.group(1) if match.group(1) is not None else match.group(2)
            if value is not None and is_literal(value):
                values[value] += 1
    return values


def collect_tree() -> Counter[str]:
    entries: Counter[str] = Counter()
    for path in sorted(SCRIPTS.rglob("*.sh")):
        if path == CONSTANT_LIBRARY:
            continue
        relative = path.relative_to(support.REPO_ROOT).as_posix()
        for value, count in collect_file(path).items():
            entries[f"{relative}\t{count}\t{json.dumps(value, ensure_ascii=False)}"] += 1
    return entries


def load_ledger() -> Counter[str]:
    entries: Counter[str] = Counter()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries[line] += 1
    return entries


class ShellLiteralMigrationTests(unittest.TestCase):

    def test_shell_literals_match_the_ledger(self) -> None:
        actual = collect_tree()
        expected = load_ledger()
        added = sorted(set(actual) - set(expected))
        removed = sorted(set(expected) - set(actual))
        messages = []
        if added:
            messages.append("New shell literals must become variables:\n" + "\n".join(added[:20]))
        if removed:
            messages.append("Stale shell ledger entries must be removed:\n" + "\n".join(removed[:20]))
        self.assertFalse(messages, "\n\n".join(messages))


if __name__ == "__main__":
    unittest.main()

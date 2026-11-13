"""
Enforce the string-constant migration ledger.

Public API: none. The module is a unittest test case.

Side effects: reads first-party Python sources and the migration ledger. It does
not write files.

The ledger records existing direct string literals by file, value, and count.
The test fails when a new literal appears or when the ledger contains a stale
entry, so every refactor must shrink the ledger instead of growing it.
"""
from __future__ import annotations

import ast
import json
import unittest
from collections import Counter
from pathlib import Path

from tests import support

LEDGER = support.FIXTURES / "string_literals_ledger.txt"
CONSTANT_LEDGER = support.FIXTURES / "string_constant_duplicates_ledger.txt"
EXCLUDED_PARTS = frozenset({"__pycache__", "build", "fixtures"})
EXCLUDED_FILES = frozenset({
    support.REPO_ROOT / "tests/unit/test_string_literals.py",
    support.REPO_ROOT / "tests/unit/test_shell_literals.py",
})
SCAN_ROOTS = (
    support.CLI_PACKAGE / "toolwright_cli",
    support.REPO_ROOT / "scripts",
    support.REPO_ROOT / "tests",
)


def _docstring_nodes(tree: ast.AST) -> set[int]:
    nodes: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
                nodes.add(id(body[0].value))
    return nodes


def _is_named_constant(node: ast.Constant, parents: dict[int, ast.AST]) -> bool:
    parent = parents.get(id(node))
    if isinstance(parent, (ast.Assign, ast.AnnAssign)):
        targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
        return all(isinstance(target, ast.Name) for target in targets)
    return False


def collect_literals(path: Path) -> Counter[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = _docstring_nodes(tree)
    parents = {id(child): parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    literals: Counter[str] = Counter()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if id(node) in docstrings or _is_named_constant(node, parents):
            continue
        if "tests" in path.parts and "\n" in node.value:
            continue
        literals[node.value] += 1
    return literals


def collect_constant_definitions(path: Path) -> list[tuple[str, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    definitions: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        value = node.value
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                definitions.append((target.id, value.value))
    return definitions


def collect_duplicate_constants() -> Counter[str]:
    definitions: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for root in SCAN_ROOTS:
        for path in sorted(root.rglob("*.py")):
            if EXCLUDED_PARTS.intersection(path.parts) or path in EXCLUDED_FILES:
                continue
            relative = path.relative_to(support.REPO_ROOT).as_posix()
            domain = relative.split("/", 1)[0]
            for name, value in collect_constant_definitions(path):
                definitions.setdefault((domain, value), []).append((relative, name))
    entries: Counter[str] = Counter()
    for (domain, value), owners in definitions.items():
        if len(owners) < 2:
            continue
        for relative, name in owners:
            entries[f"{domain}\t{json.dumps(value, ensure_ascii=False)}\t{relative}\t{name}"] += 1
    return entries


def load_constant_ledger() -> Counter[str]:
    entries: Counter[str] = Counter()
    for line in CONSTANT_LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries[line] += 1
    return entries


def collect_tree() -> Counter[str]:
    entries: Counter[str] = Counter()
    for root in SCAN_ROOTS:
        for path in sorted(root.rglob("*.py")):
            if EXCLUDED_PARTS.intersection(path.parts) or path in EXCLUDED_FILES:
                continue
            relative = path.relative_to(support.REPO_ROOT).as_posix()
            for value, count in collect_literals(path).items():
                entries[f"{relative}\t{count}\t{json.dumps(value, ensure_ascii=False)}"] += 1
    return entries


def load_ledger() -> Counter[str]:
    entries: Counter[str] = Counter()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries[line] += 1
    return entries


class StringLiteralMigrationTests(unittest.TestCase):

    def test_direct_string_literals_match_the_ledger(self) -> None:
        actual = collect_tree()
        expected = load_ledger()
        added = sorted(set(actual) - set(expected))
        removed = sorted(set(expected) - set(actual))
        messages = []
        if added:
            messages.append("New direct literals must be constants:\n" + "\n".join(added[:20]))
        if removed:
            messages.append("Stale ledger entries must be removed:\n" + "\n".join(removed[:20]))
        self.assertFalse(messages, "\n\n".join(messages))

    def test_duplicate_constant_values_match_the_ledger(self) -> None:
        actual = collect_duplicate_constants()
        expected = load_constant_ledger()
        added = sorted(set(actual) - set(expected))
        removed = sorted(set(expected) - set(actual))
        messages = []
        if added:
            messages.append("Duplicate constant values must be consolidated:\n" + "\n".join(added[:20]))
        if removed:
            messages.append("Stale constant-lock entries must be removed:\n" + "\n".join(removed[:20]))
        self.assertFalse(messages, "\n\n".join(messages))


if __name__ == "__main__":
    unittest.main()

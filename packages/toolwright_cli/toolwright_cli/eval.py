"""
Deterministic evaluation cases for ``toolwright eval``.

Public API: :func:`load_cases` and :func:`run_evaluation_cases`.

Cases live in ``tests/evals/cases.json`` and exercise repository invariants
that must hold without a model. No network access and no paid calls occur.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from . import catalog as catalog_module
from . import governance as governance_module
from .paths import ToolWrightError
from .process import capture_command
from .profiles import verify_profiles

CASES = Path("tests/evals/cases.json")
KNOWN = {"profiles", "catalog", "governance", "validator"}


def load_cases(root: Path) -> list[dict[str, Any]]:
    path = root / CASES
    if not path.is_file():
        raise ToolWrightError(f"evaluation cases not found: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ToolWrightError(f"{path}: invalid JSON: {error}") from error
    if not isinstance(document, dict):
        raise ToolWrightError(f"{path}: cases must be a JSON object")
    if document.get("schema_version") != 1:
        raise ToolWrightError(f"{path}: unsupported schema_version")
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ToolWrightError(f"{path}: cases must be a non-empty list")
    for case in cases:
        if not isinstance(case, dict) or case.get("id") not in KNOWN:
            raise ToolWrightError(f"{path}: unknown evaluation case {case!r}")
    return cases


def build_evaluation_result(identifier: str, description: str, status: str, detail: str) -> dict[str, str]:
    return {"id": identifier, "description": description, "status": status, "detail": detail}


def _evaluate(case: dict[str, Any], root: Path) -> dict[str, str]:
    identifier = str(case["id"])
    description = str(case.get("description", ""))
    expected = case.get("expected", {})
    if identifier == "profiles":
        results = verify_profiles(root)
        failures = [result for result in results if result["status"] == "fail"]
        if failures:
            return build_evaluation_result(identifier, description, "fail", f"{len(failures)} invalid profile(s)")
        if "profiles" in expected and len(results) != expected["profiles"]:
            return build_evaluation_result(identifier, description, "fail", f"expected {expected['profiles']} profiles, found {len(results)}")
        return build_evaluation_result(identifier, description, "ok", f"{len(results)} profile(s) valid")
    if identifier == "catalog":
        document = catalog_module.load_catalog(root)
        results = catalog_module.verify_catalog(root, document)
        failures = [result for result in results if result["status"] == "fail"]
        if failures:
            return build_evaluation_result(identifier, description, "fail", f"{len(failures)} catalog failure(s)")
        count = len(document.get("artifacts", []))
        if "artifacts" in expected and count != expected["artifacts"]:
            return build_evaluation_result(identifier, description, "fail", f"expected {expected['artifacts']} artifacts, found {count}")
        return build_evaluation_result(identifier, description, "ok", f"{count} artifact(s) valid")
    if identifier == "governance":
        results = governance_module.load_agent_contracts(root)
        failures = [result for result in results if result["status"] == "fail"]
        if failures:
            return build_evaluation_result(identifier, description, "fail", f"{len(failures)} contract failure(s)")
        if "contracts" in expected and len(results) != expected["contracts"]:
            return build_evaluation_result(identifier, description, "fail", f"expected {expected['contracts']} contracts, found {len(results)}")
        return build_evaluation_result(identifier, description, "ok", f"{len(results)} contract(s) valid")
    script = root / "scripts/validation/validate_config.py"
    code, stdout, stderr = capture_command([sys.executable, str(script)], cwd=root, timeout=300)
    expected_code = int(expected.get("exit_code", 0))
    if code != expected_code:
        detail = (stderr or stdout or f"exit {code}").splitlines()[0]
        return build_evaluation_result(identifier, description, "fail", detail)
    return build_evaluation_result(identifier, description, "ok", "validator passed")


def run_evaluation_cases(root: Path, only: list[str] | None = None) -> list[dict[str, str]]:
    cases = load_cases(root)
    selected = set(only) if only else None
    unknown = selected.difference(KNOWN) if selected else set()
    if unknown:
        raise ToolWrightError(f"unknown evaluation cases: {', '.join(sorted(unknown))}")
    results: list[dict[str, str]] = []
    for case in cases:
        if selected and case["id"] not in selected:
            continue
        try:
            results.append(_evaluate(case, root))
        except ToolWrightError as error:
            results.append(
                build_evaluation_result(str(case["id"]), str(case.get("description", "")), "fail", str(error))
            )
    return results

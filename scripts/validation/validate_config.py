#!/usr/bin/env python3
"""Static validation for the OPENCODE-TOOL-ENHANCER repository.

Checks:
- JSON/JSONC syntax for configs
- YAML syntax for Ralph configs and benchmark tasks
- required files
- agent frontmatter (description, mode)
- skill frontmatter (name matches directory, description length)
- optional external link reachability

No network access unless --links is passed.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "configs/opencode/opencode.jsonc",
    "configs/opencode/minimal.jsonc",
    "configs/ralph/ralph.yml",
    "configs/ralph/hats/code-assist.yml",
    "docs/decisions/ADR-001-opencode-v2-baseline.md",
    "benchmarks/methodology/README.md",
]

AGENT_ROLES = [
    "coordinator", "planner", "researcher", "architect",
    "backend-developer", "frontend-developer", "database-specialist",
    "code-reviewer", "test-engineer", "security-reviewer",
    "performance-analyst", "documentation-engineer",
]

SKILLS = [
    "test-driven-development", "systematic-debugging", "writing-plans",
    "verification-before-completion", "requesting-code-review",
    "api-design-principles", "database-migration", "code-review-excellence",
    "auth-implementation-patterns", "changelog-automation",
]

errors: list[str] = []
warnings: list[str] = []
checked = 0


def fail(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments outside strings, then trailing commas."""
    out = []
    i = 0
    n = len(text)
    in_str = False
    quote = ""
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == quote:
                in_str = False
            i += 1
            continue
        if c in ('"', "'"):
            in_str = True
            quote = c
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    stripped = "".join(out)
    # Remove trailing commas before } or ]
    stripped = re.sub(r",(\s*[}\]])", r"\1", stripped)
    return stripped


def check_jsonc(path: Path) -> None:
    global checked
    checked += 1
    try:
        data = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001
        fail(f"{path.relative_to(ROOT)}: invalid JSONC: {exc}")
        return
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)}: root must be an object")
        return
    if "$schema" not in data:
        warn(f"{path.relative_to(ROOT)}: missing $schema")
    if "mcp" in data and "servers" not in data["mcp"]:
        fail(f"{path.relative_to(ROOT)}: V2 requires mcp.servers")


def check_yaml(path: Path) -> None:
    global checked
    checked += 1
    try:
        import yaml  # type: ignore
    except ImportError:
        # Fall back to Ruby, which ships with macOS and most Linux images.
        import subprocess
        try:
            proc = subprocess.run(
                ["ruby", "-ryaml", "-e", f"YAML.load_file({json.dumps(str(path))})"],
                capture_output=True, text=True,
            )
        except FileNotFoundError:
            warn("No YAML parser (PyYAML or Ruby); YAML syntax checks skipped")
            return
        if proc.returncode != 0:
            fail(f"{path.relative_to(ROOT)}: invalid YAML: {proc.stderr.strip()[:200]}")
        return
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")


def check_json(path: Path) -> None:
    global checked
    checked += 1
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return data


def check_agents() -> None:
    global checked
    for role in AGENT_ROLES:
        path = ROOT / "agents" / role / "AGENT.md"
        checked += 1
        if not path.exists():
            fail(f"missing agent: {path.relative_to(ROOT)}")
            continue
        fm = frontmatter(path)
        if not fm.get("description"):
            fail(f"{path.relative_to(ROOT)}: missing description")
        if fm.get("mode") not in {"primary", "subagent", "all"}:
            fail(f"{path.relative_to(ROOT)}: invalid or missing mode")
        if role == "coordinator" and fm.get("mode") != "primary":
            fail("coordinator must be mode: primary")
        if role != "coordinator" and fm.get("mode") != "subagent":
            fail(f"{role} must be mode: subagent")


def check_skills() -> None:
    global checked
    pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    for name in SKILLS:
        path = ROOT / "skills" / name / "SKILL.md"
        checked += 1
        if not path.exists():
            fail(f"missing skill: {path.relative_to(ROOT)}")
            continue
        fm = frontmatter(path)
        if fm.get("name") != name:
            fail(f"{path.relative_to(ROOT)}: name must match directory ({name})")
        if not pattern.match(name):
            fail(f"{name}: invalid skill name")
        desc = fm.get("description", "")
        if not (1 <= len(desc) <= 1024):
            fail(f"{path.relative_to(ROOT)}: description length {len(desc)} not in 1..1024")


def check_commands() -> None:
    global checked
    for path in sorted((ROOT / "commands").glob("*.md")):
        checked += 1
        fm = frontmatter(path)
        if not fm.get("description"):
            fail(f"{path.relative_to(ROOT)}: missing description")


def check_provenance() -> None:
    """Enforce AGENTS.md Section 2A."""
    global checked
    registry = ROOT / "docs/provenance/registry.yml"
    checked += 1
    if not registry.exists():
        fail("missing docs/provenance/registry.yml")
        return
    text = registry.read_text(encoding="utf-8")

    # Every registered local path must exist.
    for rel in re.findall(r'^\s+local:\s*"([^"]+)"', text, re.M):
        for part in [p.strip() for p in rel.split(",")]:
            if not part:
                continue
            # allow glob-ish entries used by original_artifacts
            if "*" in part:
                continue
            checked += 1
            if not (ROOT / part).exists():
                fail(f"provenance registry points to missing path: {part}")

    # Agents and commands: provenance block in frontmatter comments.
    for sub in ("agents", "commands"):
        for path in sorted((ROOT / sub).rglob("*.md")):
            if path.name == "README.md":
                continue
            checked += 1
            head = path.read_text(encoding="utf-8")[:1200]
            if "# source:" not in head or "# upstream_commit:" not in head:
                fail(f"{path.relative_to(ROOT)}: missing provenance header (source/upstream_commit)")

    # Skills: structured metadata (OpenCode-supported field).
    for path in sorted((ROOT / "skills").rglob("SKILL.md")):
        checked += 1
        head = path.read_text(encoding="utf-8")[:1600]
        for key in ("source:", "upstream_path:", "upstream_commit:", "license:"):
            if key not in head:
                fail(f"{path.relative_to(ROOT)}: missing metadata.{key}")
                break

    # Ralph hats: provenance header comments.
    for path in sorted((ROOT / "configs/ralph/hats").glob("*.yml")):
        checked += 1
        head = path.read_text(encoding="utf-8")[:1200]
        if "# source:" not in head or "# upstream_commit:" not in head:
            fail(f"{path.relative_to(ROOT)}: missing provenance header")


def check_links() -> None:
    import urllib.request

    urls: set[str] = set()
    for path in list(ROOT.glob("docs/**/*.md")) + [ROOT / "README.md"]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for url in re.findall(r"https?://[^\s)\]>]+", text):
            if any(x in url for x in ("<", ">")) or url.endswith((".png", ".svg")):
                continue
            urls.add(url.rstrip(".,;:`"))
    for url in sorted(urls):
        global checked
        checked += 1
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ote-validator"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status >= 400:
                    warn(f"link {url}: HTTP {resp.status}")
        except Exception as exc:  # noqa: BLE001
            warn(f"link {url}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--links", action="store_true", help="check external links")
    args = parser.parse_args()

    for rel in REQUIRED:
        checked_path = ROOT / rel
        if not checked_path.exists():
            fail(f"missing required file: {rel}")

    for path in sorted((ROOT / "configs").rglob("*.jsonc")):
        check_jsonc(path)
    for path in sorted((ROOT / "configs").rglob("*.yml")):
        check_yaml(path)
    for path in sorted((ROOT / "benchmarks/tasks").glob("*.json")):
        check_json(path)

    check_agents()
    check_skills()
    check_commands()
    check_provenance()

    if args.links:
        check_links()

    print(f"checked: {checked}")
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\nFAILED with {len(errors)} error(s)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

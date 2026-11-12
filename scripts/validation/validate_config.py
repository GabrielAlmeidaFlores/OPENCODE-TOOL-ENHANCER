#!/usr/bin/env python3
"""Static validation for the OPENCODE-TOOL-ENHANCER repository.

The validator checks required files, JSONC and YAML syntax, agent and skill
frontmatter, provenance metadata, git permission ordering, external links, and
the invariants described in AGENTS.md Sections 2A, 2B, and 2C. It performs no
network access unless --links is passed.
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import io
import json
import re
import subprocess
import sys
import tokenize
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "README.md",
    "LICENSE",
    "VERSION",
    "CONTRIBUTING.md",
    "configs/opencode/opencode.jsonc",
    "configs/opencode/minimal.jsonc",
    "configs/ralph/ralph.yml",
    "configs/ralph/hats/code-assist.yml",
    "docs/decisions/ADR-001-opencode-v2-baseline.md",
    "docs/research/baseline.md",
    "docs/architecture/testing.md",
    "benchmarks/methodology/README.md",
]

AGENT_ROLES = [
    "coordinator",
    "planner",
    "researcher",
    "architect",
    "backend-developer",
    "frontend-developer",
    "database-specialist",
    "code-reviewer",
    "test-engineer",
    "security-reviewer",
    "performance-analyst",
    "documentation-engineer",
]

SKILLS = [
    "test-driven-development",
    "systematic-debugging",
    "writing-plans",
    "verification-before-completion",
    "requesting-code-review",
    "api-design-principles",
    "database-migration",
    "code-review-excellence",
    "auth-implementation-patterns",
    "changelog-automation",
]

errors: list[str] = []
warnings: list[str] = []
checked = 0


def fail(message: str) -> None:
    """Record a validation failure."""
    errors.append(message)


def warn(message: str) -> None:
    """Record a validation warning."""
    warnings.append(message)


def strip_jsonc(text: str) -> str:
    """Remove JSONC comments and trailing commas while preserving string contents."""
    out: list[str] = []
    index = 0
    length = len(text)
    in_string = False
    quote = ""
    while index < length:
        character = text[index]
        if in_string:
            out.append(character)
            if character == "\\" and index + 1 < length:
                out.append(text[index + 1])
                index += 2
                continue
            if character == quote:
                in_string = False
            index += 1
            continue
        if character in ('"', "'"):
            in_string = True
            quote = character
            out.append(character)
            index += 1
            continue
        if character == "/" and index + 1 < length and text[index + 1] == "/":
            while index < length and text[index] != "\n":
                index += 1
            continue
        if character == "/" and index + 1 < length and text[index + 1] == "*":
            index += 2
            while index + 1 < length and not (text[index] == "*" and text[index + 1] == "/"):
                index += 1
            index += 2
            continue
        out.append(character)
        index += 1
    stripped = "".join(out)
    return re.sub(r",(\s*[}\]])", r"\1", stripped)


def check_jsonc(path: Path) -> None:
    """Validate a JSONC file and its OpenCode V2 shape."""
    global checked
    checked += 1
    try:
        data = json.loads(strip_jsonc(path.read_text(encoding="utf-8")))
    except Exception as exc:  # noqa: BLE001 - report any parser failure as a validation error
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
    """Validate a YAML file with PyYAML when available, otherwise with Ruby."""
    global checked
    checked += 1
    try:
        import yaml  # type: ignore[import-not-found] - optional dependency
    except ImportError:
        try:
            process = subprocess.run(
                ["ruby", "-ryaml", "-e", f"YAML.load_file({json.dumps(str(path))})"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            warn("No YAML parser (PyYAML or Ruby); YAML syntax checks skipped")
            return
        if process.returncode != 0:
            fail(f"{path.relative_to(ROOT)}: invalid YAML: {process.stderr.strip()[:200]}")
        return
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - report any parser failure as a validation error
        fail(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")


def check_tasks() -> None:
    """Validate benchmark task definitions and their working directories."""
    global checked
    for path in sorted((ROOT / "benchmarks/tasks").glob("*.json")):
        checked += 1
        try:
            task = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - report any parser failure as a validation error
            fail(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
            continue
        for field in ("id", "prompt", "verification", "working_directory"):
            value = task.get(field)
            if not isinstance(value, str) or not value.strip():
                fail(f"{path.relative_to(ROOT)}: missing or empty {field}")
        working_directory = task.get("working_directory")
        if isinstance(working_directory, str) and working_directory.strip():
            if not (ROOT / working_directory).is_dir():
                fail(f"{path.relative_to(ROOT)}: working_directory does not exist: {working_directory}")


def frontmatter(path: Path) -> dict[str, str]:
    """Return the simple top-level string fields from a Markdown frontmatter block."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            data[match.group(1)] = match.group(2).strip().strip('"').strip("'")
    return data


def check_agents() -> None:
    """Validate required agent files and their frontmatter fields."""
    global checked
    for role in AGENT_ROLES:
        path = ROOT / "agents" / role / "AGENT.md"
        checked += 1
        if not path.exists():
            fail(f"missing agent: {path.relative_to(ROOT)}")
            continue
        metadata = frontmatter(path)
        if not metadata.get("description"):
            fail(f"{path.relative_to(ROOT)}: missing description")
        if metadata.get("mode") not in {"primary", "subagent", "all"}:
            fail(f"{path.relative_to(ROOT)}: invalid or missing mode")
        if role == "coordinator" and metadata.get("mode") != "primary":
            fail("coordinator must be mode: primary")
        if role != "coordinator" and metadata.get("mode") != "subagent":
            fail(f"{role} must be mode: subagent")


def check_skills() -> None:
    """Validate required skill files, names, descriptions, and naming format."""
    global checked
    pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    for name in SKILLS:
        path = ROOT / "skills" / name / "SKILL.md"
        checked += 1
        if not path.exists():
            fail(f"missing skill: {path.relative_to(ROOT)}")
            continue
        metadata = frontmatter(path)
        if metadata.get("name") != name:
            fail(f"{path.relative_to(ROOT)}: name must match directory ({name})")
        if not pattern.match(name):
            fail(f"{name}: invalid skill name")
        description = metadata.get("description", "")
        if not (1 <= len(description) <= 1024):
            fail(f"{path.relative_to(ROOT)}: description length {len(description)} not in 1..1024")


def check_commands() -> None:
    """Validate every command file and its target agent."""
    global checked
    for path in sorted((ROOT / "commands").glob("*.md")):
        checked += 1
        metadata = frontmatter(path)
        if not metadata.get("description"):
            fail(f"{path.relative_to(ROOT)}: missing description")
        agent = metadata.get("agent")
        if not agent:
            fail(f"{path.relative_to(ROOT)}: missing agent")
        elif agent not in AGENT_ROLES:
            fail(f"{path.relative_to(ROOT)}: unknown agent: {agent}")


def check_provenance() -> None:
    """Enforce AGENTS.md Section 2A across registered artifacts."""
    global checked
    registry = ROOT / "docs/provenance/registry.yml"
    checked += 1
    if not registry.exists():
        fail("missing docs/provenance/registry.yml")
        return
    text = registry.read_text(encoding="utf-8")

    for relative in re.findall(r'^\s+local:\s*"([^"]+)"', text, re.M):
        for part in [item.strip() for item in relative.split(",")]:
            if not part or "*" in part:
                continue
            checked += 1
            if not (ROOT / part).exists():
                fail(f"provenance registry points to missing path: {part}")

    for subdirectory in ("agents", "commands"):
        for path in sorted((ROOT / subdirectory).rglob("*.md")):
            if path.name == "README.md":
                continue
            checked += 1
            head = path.read_text(encoding="utf-8")[:1200]
            if "# source:" not in head or "# upstream_commit:" not in head:
                fail(f"{path.relative_to(ROOT)}: missing provenance header (source/upstream_commit)")
            if "# author:" not in head or "# author_url:" not in head:
                fail(f"{path.relative_to(ROOT)}: missing author attribution (author/author_url)")

    for path in sorted((ROOT / "skills").rglob("SKILL.md")):
        checked += 1
        head = path.read_text(encoding="utf-8")[:1600]
        for key in ("author:", "author_url:", "source:", "upstream_path:", "upstream_commit:", "license:"):
            if key not in head:
                fail(f"{path.relative_to(ROOT)}: missing metadata.{key}")
                break

    for path in sorted((ROOT / "configs/ralph/hats").glob("*.yml")):
        checked += 1
        head = path.read_text(encoding="utf-8")[:1200]
        if "# source:" not in head or "# upstream_commit:" not in head:
            fail(f"{path.relative_to(ROOT)}: missing provenance header")
        if "# author:" not in head or "# author_url:" not in head:
            fail(f"{path.relative_to(ROOT)}: missing author attribution")


def parse_permissions(frontmatter_text: str) -> list[dict[str, str]]:
    """Parse the action, resource, and effect fields from agent permissions."""
    permissions: list[dict[str, str]] = []
    current: dict[str, str] = {}
    in_permissions = False
    for line in frontmatter_text.splitlines():
        if line.startswith("permissions:"):
            in_permissions = True
            continue
        if not in_permissions:
            continue
        if line and not line.startswith((" ", "\t")):
            break
        match = re.match(r"\s*-\s*action:\s*\"?([^\"]+)\"?", line)
        if match:
            if current:
                permissions.append(current)
            current = {"action": match.group(1).strip()}
            continue
        match = re.match(r"\s*resource:\s*\"?(.*?)\"?\s*$", line)
        if match and current:
            current["resource"] = match.group(1).strip()
            continue
        match = re.match(r"\s*effect:\s*\"?(.*?)\"?\s*$", line)
        if match and current:
            current["effect"] = match.group(1).strip()
    if current:
        permissions.append(current)
    return permissions


def check_git_permissions() -> None:
    """Verify that every agent resolves git write commands to deny as the last matching rule."""
    global checked
    commands = [
        "git add -A",
        "git stage file",
        "git commit -m x",
        "git -C . add -A",
        "git -C . commit -m x",
        "git stash",
        "git reset --hard",
        "git checkout main",
        "git clean -fd",
    ]
    for role in AGENT_ROLES:
        path = ROOT / "agents" / role / "AGENT.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            fail(f"{path.relative_to(ROOT)}: missing frontmatter")
            continue
        end = text.find("\n---", 3)
        if end == -1:
            fail(f"{path.relative_to(ROOT)}: unterminated frontmatter")
            continue
        permissions = parse_permissions(text[3:end])
        checked += 1
        for command in commands:
            effect = None
            for rule in permissions:
                if rule.get("action") != "shell":
                    continue
                if fnmatch.fnmatchcase(command, rule.get("resource", "")):
                    effect = rule.get("effect")
            if effect != "deny":
                fail(
                    f"{path.relative_to(ROOT)}: `{command}` resolves to {effect or 'no rule'} "
                    "instead of deny; add the git deny rules at the end of permissions"
                )


def jsonc_comment_lines(text: str) -> list[int]:
    """Return the 1-based line numbers of comments outside JSON strings."""
    lines: list[int] = []
    index = 0
    line = 1
    length = len(text)
    in_string = False
    quote = ""
    while index < length:
        character = text[index]
        if in_string:
            if character == "\\" and index + 1 < length:
                index += 2
                continue
            if character == quote:
                in_string = False
            if character == "\n":
                line += 1
            index += 1
            continue
        if character in ('"', "'"):
            in_string = True
            quote = character
            index += 1
            continue
        if character == "/" and index + 1 < length and text[index + 1] == "/":
            lines.append(line)
            while index < length and text[index] != "\n":
                index += 1
            continue
        if character == "/" and index + 1 < length and text[index + 1] == "*":
            lines.append(line)
            index += 2
            while index + 1 < length and not (text[index] == "*" and text[index + 1] == "/"):
                if text[index] == "\n":
                    line += 1
                index += 1
            index += 2
            continue
        if character == "\n":
            line += 1
        index += 1
    return lines


def shell_inline_comment(line: str) -> bool:
    """Return True when a shell line contains a comment after executable text."""
    in_single = False
    in_double = False
    escaped = False
    brace_depth = 0
    index = 0
    while index < len(line):
        character = line[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if character == "\\" and not in_single:
            escaped = True
            index += 1
            continue
        if character == "$" and index + 1 < len(line) and line[index + 1] == "{":
            brace_depth += 1
            index += 2
            continue
        if character == "}" and brace_depth > 0:
            brace_depth -= 1
            index += 1
            continue
        if character == "'" and not in_double:
            in_single = not in_single
            index += 1
            continue
        if character == '"' and not in_single:
            in_double = not in_double
            index += 1
            continue
        if (
            character == "#"
            and not in_single
            and not in_double
            and brace_depth == 0
            and not (index > 0 and line[index - 1] == "$")
        ):
            return bool(line[:index].strip())
        index += 1
    return False


def check_comment_policy() -> None:
    """Enforce the documentation-comment policy from AGENTS.md Section 2C."""
    global checked

    for path in sorted((ROOT / "configs").rglob("*.jsonc")):
        checked += 1
        text = path.read_text(encoding="utf-8")
        header = "\n".join(text.splitlines()[:10])
        if "// Name:" not in header or "// Purpose:" not in header:
            fail(f"{path.relative_to(ROOT)}: missing JSONC documentation header")
            continue
        body_line = next(
            (number for number, line in enumerate(text.splitlines(), start=1) if line.strip().startswith("{")),
            None,
        )
        if body_line is None:
            fail(f"{path.relative_to(ROOT)}: missing JSON object")
            continue
        for comment_line in jsonc_comment_lines(text):
            if comment_line >= body_line:
                fail(f"{path.relative_to(ROOT)}:{comment_line}: inline JSONC comments are prohibited")

    for path in sorted((ROOT / "scripts").rglob("*.sh")) + sorted((ROOT / "benchmarks/harness").rglob("*.sh")):
        checked += 1
        lines = path.read_text(encoding="utf-8").splitlines()
        header = "\n".join(lines[:12])
        if "# Name:" not in header or "# Purpose:" not in header:
            fail(f"{path.relative_to(ROOT)}: missing shell documentation header")
        for number, line in enumerate(lines, start=1):
            if shell_inline_comment(line):
                fail(f"{path.relative_to(ROOT)}:{number}: inline shell comments are prohibited")

    for path in sorted((ROOT / "scripts").rglob("*.py")):
        checked += 1
        text = path.read_text(encoding="utf-8")
        if ast.get_docstring(ast.parse(text)) is None:
            fail(f"{path.relative_to(ROOT)}: missing module docstring")
        try:
            tokens = tokenize.generate_tokens(io.StringIO(text).readline)
            for token in tokens:
                if token.type != tokenize.COMMENT:
                    continue
                value = token.string
                if value.startswith("#!"):
                    continue
                if re.match(r"#\s*(noqa|type:|pragma:|shellcheck|fmt:)", value):
                    continue
                fail(f"{path.relative_to(ROOT)}:{token.start[0]}: non-documentation Python comment")
        except tokenize.TokenError as exc:
            fail(f"{path.relative_to(ROOT)}: tokenization failed: {exc}")


def check_docs_status() -> None:
    """Enforce the Phase 0 documentation status block on every docs page."""
    global checked
    allowed = {"Stable", "Experimental", "Planned", "Deprecated"}
    for path in sorted((ROOT / "docs").rglob("*.md")):
        relative = path.relative_to(ROOT)
        if relative.parts[:2] == ("docs", "decisions"):
            continue
        checked += 1
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
        missing = [marker for marker in ("**Status:**", "**Last verified:**", "**Evidence:**") if marker not in head]
        if missing:
            fail(f"{relative}: missing documentation status field {missing[0]}")
            continue
        match = re.search(r"\*\*Status:\*\*\s*([A-Za-z]+)", head)
        if match is None:
            fail(f"{relative}: missing documentation status value")
        elif match.group(1) not in allowed:
            fail(f"{relative}: unknown documentation status {match.group(1)}")
        if not re.search(r"\*\*Last verified:\*\*\s*\d{4}-\d{2}-\d{2}", head):
            fail(f"{relative}: last verified date must be ISO 8601")


def check_links() -> None:
    """Check external HTTP links found in documentation."""
    global checked
    urls: set[str] = set()
    for path in list(ROOT.glob("docs/**/*.md")) + [ROOT / "README.md"]:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for url in re.findall(r"https?://[^\s)\]>]+", text):
            if any(character in url for character in ("<", ">")) or url.endswith((".png", ".svg")):
                continue
            urls.add(url.rstrip(".,;:`\"'"))
    for url in sorted(urls):
        checked += 1
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "ote-validator"})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status >= 400:
                    warn(f"link {url}: HTTP {response.status}")
        except Exception as exc:  # noqa: BLE001 - report unreachable links as warnings
            warn(f"link {url}: {exc}")


def main() -> int:
    """Run every validation check and return a process exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--links", action="store_true", help="check external links")
    args = parser.parse_args()

    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            fail(f"missing required file: {relative}")

    for path in sorted((ROOT / "configs").rglob("*.jsonc")):
        check_jsonc(path)
    for path in sorted((ROOT / "configs").rglob("*.yml")):
        check_yaml(path)
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        check_yaml(path)
    check_tasks()

    check_agents()
    check_skills()
    check_commands()
    check_provenance()
    check_git_permissions()
    check_comment_policy()
    check_docs_status()

    if args.links:
        check_links()

    print(f"checked: {checked}")
    for warning in warnings:
        print(f"WARN  {warning}")
    for error in errors:
        print(f"ERROR {error}")
    if errors:
        print(f"\nFAILED with {len(errors)} error(s)")
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

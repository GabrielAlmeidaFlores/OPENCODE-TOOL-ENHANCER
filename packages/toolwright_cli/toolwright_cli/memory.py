"""
Markdown project memory for ``toolwright memory``.

Public API: :class:`Entry`, :func:`add_memory_entry`, :func:`search_memory_entries`,
:func:`prune_expired_entries`, :func:`export_memory_entries`, and
:func:`render_memory_preamble`.

Memory is plain Markdown with a small frontmatter block. There are no
embeddings, no background service, and no network access. Search is lexical.

Scopes: ``project`` (tracked with the repository), ``shared`` (published),
and ``user`` (local preference). Precedence for the preamble is
project > user > shared.
"""
from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .paths import ToolwrightError

TYPES = ("decision", "constraint", "convention", "failure", "question")
SCOPES = ("project", "user", "shared")
PRECEDENCE = ("project", "user", "shared")
DEFAULT_TTL_DAYS = 30
DEFAULT_TOKEN_BUDGET = 2000

SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9/_-]{16,}"),
)


@dataclass
class Entry:

    path: Path
    scope: str
    identifier: str
    entry_type: str
    title: str
    created: str
    source: str
    confidence: float
    expires: str
    links: list[str] = field(default_factory=list)
    body: str = ""

    def expired(self, today: date | None = None) -> bool:
        current = today or datetime.now(timezone.utc).date()
        try:
            return date.fromisoformat(self.expires) < current
        except ValueError:
            return True


def settings(root: Path) -> dict[str, int]:
    values = {"token_budget": DEFAULT_TOKEN_BUDGET, "ttl_days": DEFAULT_TTL_DAYS}
    path = root / ".toolwright/config.toml"
    if not path.is_file():
        return values
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ToolwrightError(f"{path}: invalid TOML: {error}") from error
    section = data.get("memory", {})
    if not isinstance(section, dict):
        raise ToolwrightError(f"{path}: memory must be a table")
    for key in values:
        if key in section:
            value = section[key]
            if not isinstance(value, int) or value <= 0:
                raise ToolwrightError(f"{path}: memory.{key} must be a positive integer")
            values[key] = value
    return values


def ensure_memory_directory(root: Path) -> Path:
    directory = root / ".toolwright/memory"
    for scope in SCOPES:
        (directory / scope).mkdir(parents=True, exist_ok=True)
    return directory


def slugify_memory_title(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:60] or "entry"


def current_utc_date() -> date:
    return datetime.now(timezone.utc).date()


def scan_secrets(text: str) -> list[str]:
    return [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]


def render_memory_frontmatter(entry_type: str, title: str, created: str, source: str, confidence: float, expires: str, links: list[str]) -> str:
    link_value = ", ".join(links)
    return (
        "---\n"
        f"type: {entry_type}\n"
        f"title: {title}\n"
        f"created: {created}\n"
        f"source: {source}\n"
        f"confidence: {confidence}\n"
        f"expires: {expires}\n"
        f"links: [{link_value}]\n"
        "---\n\n"
    )


def parse_memory_entry(path: Path, scope: str) -> Entry:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ToolwrightError(f"{path}: missing frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ToolwrightError(f"{path}: unterminated frontmatter")
    metadata: dict[str, str] = {}
    for line in text[3:end].splitlines():
        match = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    required = ("type", "title", "created", "source", "confidence", "expires")
    missing = [key for key in required if not metadata.get(key)]
    if missing:
        raise ToolwrightError(f"{path}: missing {', '.join(missing)}")
    if metadata["type"] not in TYPES:
        raise ToolwrightError(f"{path}: unknown type {metadata['type']}")
    links_value = metadata.get("links", "[]").strip("[]").strip()
    links = [item.strip().strip('"').strip("'") for item in links_value.split(",") if item.strip()]
    try:
        confidence = float(metadata["confidence"])
    except ValueError as error:
        raise ToolwrightError(f"{path}: confidence must be a number") from error
    body = text[end + 4 :].lstrip("\n")
    return Entry(
        path=path,
        scope=scope,
        identifier=path.stem,
        entry_type=metadata["type"],
        title=metadata["title"],
        created=metadata["created"],
        source=metadata["source"],
        confidence=confidence,
        expires=metadata["expires"],
        links=links,
        body=body.strip(),
    )


def load_memory_entries(root: Path, scope: str | None = None) -> list[Entry]:
    directory = ensure_memory_directory(root)
    selected = (scope,) if scope else SCOPES
    if scope and scope not in SCOPES:
        raise ToolwrightError(f"unknown scope: {scope}")
    results: list[Entry] = []
    for current in selected:
        for path in sorted((directory / current).glob("*.md")):
            results.append(parse_memory_entry(path, current))
    return results


def write_memory_catalog(root: Path, items: list[Entry]) -> None:
    directory = root / ".toolwright/memory"
    lines = [
        "# Memory Catalog",
        "",
        "Generated by `toolwright memory`; do not edit by hand.",
        "",
        "| Scope | Type | Title | Created | Expires | Source |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for entry in items:
        marker = " (expired)" if entry.expired() else ""
        lines.append(
            f"| {entry.scope} | {entry.entry_type} | {entry.title}{marker} | "
            f"{entry.created} | {entry.expires} | {entry.source} |"
        )
    lines.append("")
    target = directory / "catalog.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")


def add_memory_entry(
    root: Path,
    text: str,
    entry_type: str,
    title: str | None,
    scope: str,
    source: str,
    confidence: float,
    links: list[str],
    ttl_days: int | None = None,
    force: bool = False,
) -> Entry:
    if entry_type not in TYPES:
        raise ToolwrightError(f"unknown type: {entry_type}")
    if scope not in SCOPES:
        raise ToolwrightError(f"unknown scope: {scope}")
    if not 0 <= confidence <= 1:
        raise ToolwrightError("confidence must be between 0 and 1")
    body = text.strip()
    if not body:
        raise ToolwrightError("memory text is required")
    resolved_title = (title or body.splitlines()[0]).strip()
    if not resolved_title:
        raise ToolwrightError("memory title is required")
    for label, value in (("title", resolved_title), ("source", source), *((f"link {index}", link) for index, link in enumerate(links, start=1))):
        if "\n" in value or "\r" in value or value.strip() == "---":
            raise ToolwrightError(f"{label} must be a single line without a frontmatter separator")
    found = scan_secrets("\n".join([resolved_title, body, source, " ".join(links)]))
    if found:
        raise ToolwrightError("refusing to store a possible credential (matched a secret pattern)")

    existing = load_memory_entries(root, scope)
    normalized = re.sub(r"\s+", " ", resolved_title.lower())
    for entry in existing:
        if re.sub(r"\s+", " ", entry.title.lower()) == normalized and not force:
            raise ToolwrightError(f"duplicate title in {scope}: {entry.title} (use --force to add anyway)")

    ttl = settings(root)["ttl_days"] if ttl_days is None else ttl_days
    if ttl < 0:
        raise ToolwrightError("ttl must not be negative")
    created = current_utc_date()
    expires = created + timedelta(days=ttl)
    identifier = f"{created.isoformat()}-{slugify_memory_title(resolved_title)}"
    target = root / ".toolwright/memory" / scope / f"{identifier}.md"
    suffix = 2
    while target.exists():
        target = root / ".toolwright/memory" / scope / f"{identifier}-{suffix}.md"
        suffix += 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        render_memory_frontmatter(
            entry_type,
            resolved_title,
            created.isoformat(),
            source,
            confidence,
            expires.isoformat(),
            links,
        )
        + f"{body}\n",
        encoding="utf-8",
    )
    result = parse_memory_entry(target, scope)
    write_memory_catalog(root, load_memory_entries(root))
    return result


def search_memory_entries(root: Path, query: str, entry_type: str | None = None, scope: str | None = None) -> list[Entry]:
    needle = query.strip().lower()
    if not needle:
        return []
    results: list[Entry] = []
    for entry in load_memory_entries(root, scope):
        if entry_type and entry.entry_type != entry_type:
            continue
        haystack = " ".join([entry.title, entry.body, entry.source, entry.entry_type]).lower()
        if needle in haystack:
            results.append(entry)
    return results


def prune_expired_entries(root: Path, apply: bool) -> list[Entry]:
    expired = [entry for entry in load_memory_entries(root) if entry.expired()]
    if apply:
        for entry in expired:
            entry.path.unlink(missing_ok=True)
        write_memory_catalog(root, load_memory_entries(root))
    return expired


def export_memory_entries(root: Path, output: str = "markdown") -> str:
    items = load_memory_entries(root)
    if output == "json":
        return json.dumps(
            {
                "entries": [
                    {
                        "scope": entry.scope,
                        "id": entry.identifier,
                        "type": entry.entry_type,
                        "title": entry.title,
                        "created": entry.created,
                        "source": entry.source,
                        "confidence": entry.confidence,
                        "expires": entry.expires,
                        "links": entry.links,
                        "body": entry.body,
                        "expired": entry.expired(),
                    }
                    for entry in items
                ]
            },
            indent=2,
            sort_keys=True,
        )
    if output != "markdown":
        raise ToolwrightError(f"unknown export format: {output}")
    lines = ["# Memory Export", ""]
    for entry in items:
        lines.extend(
            [
                f"## {entry.title}",
                "",
                f"- scope: {entry.scope}",
                f"- type: {entry.entry_type}",
                f"- created: {entry.created}",
                f"- expires: {entry.expires}",
                f"- source: {entry.source}",
                "",
                entry.body,
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_memory_preamble(root: Path, budget_tokens: int | None = None) -> str:
    limit = settings(root)["token_budget"] if budget_tokens is None else budget_tokens
    if limit <= 0:
        raise ToolwrightError("budget must be a positive integer")
    items = [entry for entry in load_memory_entries(root) if not entry.expired()]
    order = {scope: index for index, scope in enumerate(PRECEDENCE)}
    items.sort(key=lambda entry: (order.get(entry.scope, 99), entry.identifier))
    lines = ["# Project Memory", ""]
    used = len("\n".join(lines))
    for entry in items:
        summary = next(
            (line.strip()[:200] for line in entry.body.splitlines() if line.strip() and not line.lstrip().startswith("#")),
            "",
        )
        line = f"- [{entry.entry_type}] {entry.title} ({entry.source}, {entry.created}): {summary}"
        cost = len(line) + 1
        if (used + cost) // 4 > limit:
            continue
        lines.append(line)
        used += cost
    return "\n".join(lines) + "\n"

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
from .constants import KEY_FAILURE
from .memory_strings import (
    EMPTY_STRING,
    ENCODING_UTF8,
    FLAG_BEGIN_A_Z_PRIVATE_KEY,
    FLAG_TEXT,
    FLAG_TYPE_TITLE_CREATED_SOURCE_CONFIDENCE_EXPIRES_LINKS,
    KEY_BODY,
    KEY_CONFIDENCE,
    KEY_CONSTRAINT,
    KEY_CONVENTION,
    KEY_CREATED,
    KEY_DECISION,
    KEY_ENTRIES,
    KEY_ENTRY,
    KEY_EXPIRED,
    KEY_EXPIRES,
    KEY_ID,
    KEY_JSON,
    KEY_LINKS,
    KEY_MARKDOWN,
    KEY_MEMORY,
    KEY_PROJECT,
    KEY_QUESTION,
    KEY_SCOPE,
    KEY_SHARED,
    KEY_SOURCE,
    KEY_TITLE,
    KEY_TOKEN_BUDGET,
    KEY_TTL_DAYS,
    KEY_TYPE,
    KEY_USER,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_SPACE,
    TEXT_AKIA_0_9A_Z_16,
    TEXT_A_Z0_9,
    TEXT_A_Z_S,
    TEXT_BUDGET_MUST_BE_A_POSITIVE_INTEGER,
    TEXT_CATALOG_MD,
    TEXT_CONFIDENCE_MUST_BE_A_NUMBER,
    TEXT_CONFIDENCE_MUST_BE_BETWEEN_0_AND_1,
    TEXT_CREATED,
    TEXT_DUPLICATE_TITLE_IN_USE_FORCE_TO_ADD_ANYWAY,
    TEXT_EXPIRED,
    TEXT_EXPIRES,
    TEXT_GENERATED_BY_TOOLWRIGHT_MEMORY_DO_NOT_EDIT_BY_HAND,
    TEXT_GH_POUSR_A_ZA_Z0_9_36,
    TEXT_INVALID_TOML,
    TEXT_I_API_KEY_SECRET_TOKEN_PASSWORD_S_S_A_ZA_Z0_9_16,
    TEXT_LINK,
    TEXT_MD,
    TEXT_MD_2,
    TEXT_MD_3,
    TEXT_MEMORY_CATALOG,
    TEXT_MEMORY_EXPORT,
    TEXT_MEMORY_MUST_BE_A_POSITIVE_INTEGER,
    TEXT_MEMORY_MUST_BE_A_TABLE,
    TEXT_MEMORY_TEXT_IS_REQUIRED,
    TEXT_MEMORY_TITLE_IS_REQUIRED,
    TEXT_MISSING,
    TEXT_MISSING_FRONTMATTER,
    TEXT_MUST_BE_A_SINGLE_LINE_WITHOUT_A_FRONTMATTER_SEPARATOR,
    TEXT_PROJECT_MEMORY,
    TEXT_REFUSING_TO_STORE_A_POSSIBLE_CREDENTIAL_MATCHED_A_SECRET_PAT,
    TEXT_S,
    TEXT_SCOPE,
    TEXT_SCOPE_TYPE_TITLE_CREATED_EXPIRES_SOURCE,
    TEXT_SK_A_ZA_Z0_9_20,
    TEXT_SOURCE,
    TEXT_TEXT,
    TEXT_TEXT_10,
    TEXT_TEXT_11,
    TEXT_TEXT_12,
    TEXT_TEXT_13,
    TEXT_TEXT_14,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_TEXT_4,
    TEXT_TEXT_5,
    TEXT_TEXT_6,
    TEXT_TEXT_7,
    TEXT_TEXT_8,
    TEXT_TEXT_9,
    TEXT_TOOLWRIGHT_CONFIG_TOML,
    TEXT_TOOLWRIGHT_MEMORY,
    TEXT_TTL_MUST_NOT_BE_NEGATIVE,
    TEXT_TYPE,
    TEXT_UNKNOWN_EXPORT_FORMAT,
    TEXT_UNKNOWN_SCOPE,
    TEXT_UNKNOWN_TYPE,
    TEXT_UNKNOWN_TYPE_2,
    TEXT_UNTERMINATED_FRONTMATTER,
)

import json
import re
import tomllib
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .paths import ToolWrightError

TYPES = (KEY_DECISION, KEY_CONSTRAINT, KEY_CONVENTION, KEY_FAILURE, KEY_QUESTION)
SCOPES = (KEY_PROJECT, KEY_USER, KEY_SHARED)
PRECEDENCE = (KEY_PROJECT, KEY_USER, KEY_SHARED)
DEFAULT_TTL_DAYS = 30
DEFAULT_TOKEN_BUDGET = 2000

SECRET_PATTERNS = (
    re.compile(TEXT_AKIA_0_9A_Z_16),
    re.compile(TEXT_GH_POUSR_A_ZA_Z0_9_36),
    re.compile(TEXT_SK_A_ZA_Z0_9_20),
    re.compile(FLAG_BEGIN_A_Z_PRIVATE_KEY),
    re.compile(TEXT_I_API_KEY_SECRET_TOKEN_PASSWORD_S_S_A_ZA_Z0_9_16),
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
    body: str = EMPTY_STRING

    def expired(self, today: date | None = None) -> bool:
        current = today or datetime.now(timezone.utc).date()
        try:
            return date.fromisoformat(self.expires) < current
        except ValueError:
            return True


def settings(root: Path) -> dict[str, int]:
    values = {KEY_TOKEN_BUDGET: DEFAULT_TOKEN_BUDGET, KEY_TTL_DAYS: DEFAULT_TTL_DAYS}
    path = root / TEXT_TOOLWRIGHT_CONFIG_TOML
    if not path.is_file():
        return values
    try:
        data = tomllib.loads(path.read_text(encoding=ENCODING_UTF8))
    except tomllib.TOMLDecodeError as error:
        raise ToolWrightError(TEXT_INVALID_TOML.format(path, error)) from error
    section = data.get(KEY_MEMORY, {})
    if not isinstance(section, dict):
        raise ToolWrightError(TEXT_MEMORY_MUST_BE_A_TABLE.format(path))
    for key in values:
        if key in section:
            value = section[key]
            if not isinstance(value, int) or value <= 0:
                raise ToolWrightError(TEXT_MEMORY_MUST_BE_A_POSITIVE_INTEGER.format(path, key))
            values[key] = value
    return values


def ensure_memory_directory(root: Path) -> Path:
    directory = root / TEXT_TOOLWRIGHT_MEMORY
    for scope in SCOPES:
        (directory / scope).mkdir(parents=True, exist_ok=True)
    return directory


def slugify_memory_title(value: str) -> str:
    slug = re.sub(TEXT_A_Z0_9, TEXT_TEXT_6, value.lower()).strip(TEXT_TEXT_6)
    return slug[:60] or KEY_ENTRY


def current_utc_date() -> date:
    return datetime.now(timezone.utc).date()


def scan_secrets(text: str) -> list[str]:
    return [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]


def render_memory_frontmatter(entry_type: str, title: str, created: str, source: str, confidence: float, expires: str, links: list[str]) -> str:
    link_value = SEPARATOR_COMMA_SPACE.join(links)
    return (
        FLAG_TYPE_TITLE_CREATED_SOURCE_CONFIDENCE_EXPIRES_LINKS.format(entry_type, title, created, source, confidence, expires, link_value)
    )


def parse_memory_entry(path: Path, scope: str) -> Entry:
    text = path.read_text(encoding=ENCODING_UTF8)
    if not text.startswith(FLAG_TEXT):
        raise ToolWrightError(TEXT_MISSING_FRONTMATTER.format(path))
    end = text.find(TEXT_TEXT_7, 3)
    if end == -1:
        raise ToolWrightError(TEXT_UNTERMINATED_FRONTMATTER.format(path))
    metadata: dict[str, str] = {}
    for line in text[3:end].splitlines():
        match = re.match(TEXT_A_Z_S, line)
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    required = (KEY_TYPE, KEY_TITLE, KEY_CREATED, KEY_SOURCE, KEY_CONFIDENCE, KEY_EXPIRES)
    missing = [key for key in required if not metadata.get(key)]
    if missing:
        raise ToolWrightError(TEXT_MISSING.format(path, SEPARATOR_COMMA_SPACE.join(missing)))
    if metadata[KEY_TYPE] not in TYPES:
        raise ToolWrightError(TEXT_UNKNOWN_TYPE.format(path, metadata[KEY_TYPE]))
    links_value = metadata.get(KEY_LINKS, TEXT_TEXT_8).strip(TEXT_TEXT_8).strip()
    links = [item.strip().strip(TEXT_TEXT_9).strip(TEXT_TEXT_10) for item in links_value.split(TEXT_TEXT_11) if item.strip()]
    try:
        confidence = float(metadata[KEY_CONFIDENCE])
    except ValueError as error:
        raise ToolWrightError(TEXT_CONFIDENCE_MUST_BE_A_NUMBER.format(path)) from error
    body = text[end + 4 :].lstrip(NEWLINE)
    return Entry(
        path=path,
        scope=scope,
        identifier=path.stem,
        entry_type=metadata[KEY_TYPE],
        title=metadata[KEY_TITLE],
        created=metadata[KEY_CREATED],
        source=metadata[KEY_SOURCE],
        confidence=confidence,
        expires=metadata[KEY_EXPIRES],
        links=links,
        body=body.strip(),
    )


def load_memory_entries(root: Path, scope: str | None = None) -> list[Entry]:
    directory = ensure_memory_directory(root)
    selected = (scope,) if scope else SCOPES
    if scope and scope not in SCOPES:
        raise ToolWrightError(TEXT_UNKNOWN_SCOPE.format(scope))
    results: list[Entry] = []
    for current in selected:
        for path in sorted((directory / current).glob(TEXT_MD_3)):
            results.append(parse_memory_entry(path, current))
    return results


def write_memory_catalog(root: Path, items: list[Entry]) -> None:
    directory = root / TEXT_TOOLWRIGHT_MEMORY
    lines = [
        TEXT_MEMORY_CATALOG,
        EMPTY_STRING,
        TEXT_GENERATED_BY_TOOLWRIGHT_MEMORY_DO_NOT_EDIT_BY_HAND,
        EMPTY_STRING,
        TEXT_SCOPE_TYPE_TITLE_CREATED_EXPIRES_SOURCE,
        TEXT_TEXT_12,
    ]
    for entry in items:
        marker = TEXT_EXPIRED if entry.expired() else EMPTY_STRING
        lines.append(
            TEXT_TEXT_3.format(entry.scope, entry.entry_type, entry.title, marker, entry.created, entry.expires, entry.source)
        )
    lines.append(EMPTY_STRING)
    target = directory / TEXT_CATALOG_MD
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(NEWLINE.join(lines), encoding=ENCODING_UTF8)


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
        raise ToolWrightError(TEXT_UNKNOWN_TYPE_2.format(entry_type))
    if scope not in SCOPES:
        raise ToolWrightError(TEXT_UNKNOWN_SCOPE.format(scope))
    if not 0 <= confidence <= 1:
        raise ToolWrightError(TEXT_CONFIDENCE_MUST_BE_BETWEEN_0_AND_1)
    body = text.strip()
    if not body:
        raise ToolWrightError(TEXT_MEMORY_TEXT_IS_REQUIRED)
    resolved_title = (title or body.splitlines()[0]).strip()
    if not resolved_title:
        raise ToolWrightError(TEXT_MEMORY_TITLE_IS_REQUIRED)
    for label, value in ((KEY_TITLE, resolved_title), (KEY_SOURCE, source), *((TEXT_LINK.format(index), link) for index, link in enumerate(links, start=1))):
        if NEWLINE in value or TEXT_TEXT_13 in value or value.strip() == FLAG_TEXT:
            raise ToolWrightError(TEXT_MUST_BE_A_SINGLE_LINE_WITHOUT_A_FRONTMATTER_SEPARATOR.format(label))
    found = scan_secrets(NEWLINE.join([resolved_title, body, source, SEPARATOR_SPACE.join(links)]))
    if found:
        raise ToolWrightError(TEXT_REFUSING_TO_STORE_A_POSSIBLE_CREDENTIAL_MATCHED_A_SECRET_PAT)

    existing = load_memory_entries(root, scope)
    normalized = re.sub(TEXT_S, SEPARATOR_SPACE, resolved_title.lower())
    for entry in existing:
        if re.sub(TEXT_S, SEPARATOR_SPACE, entry.title.lower()) == normalized and not force:
            raise ToolWrightError(TEXT_DUPLICATE_TITLE_IN_USE_FORCE_TO_ADD_ANYWAY.format(scope, entry.title))

    ttl = settings(root)[KEY_TTL_DAYS] if ttl_days is None else ttl_days
    if ttl < 0:
        raise ToolWrightError(TEXT_TTL_MUST_NOT_BE_NEGATIVE)
    created = current_utc_date()
    expires = created + timedelta(days=ttl)
    identifier = TEXT_TEXT.format(created.isoformat(), slugify_memory_title(resolved_title))
    target = root / TEXT_TOOLWRIGHT_MEMORY / scope / TEXT_MD.format(identifier)
    suffix = 2
    while target.exists():
        target = root / TEXT_TOOLWRIGHT_MEMORY / scope / TEXT_MD_2.format(identifier, suffix)
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
        + TEXT_TEXT_4.format(body),
        encoding=ENCODING_UTF8,
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
        haystack = SEPARATOR_SPACE.join([entry.title, entry.body, entry.source, entry.entry_type]).lower()
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


def export_memory_entries(root: Path, output: str = KEY_MARKDOWN) -> str:
    items = load_memory_entries(root)
    if output == KEY_JSON:
        return json.dumps(
            {
                KEY_ENTRIES: [
                    {
                        KEY_SCOPE: entry.scope,
                        KEY_ID: entry.identifier,
                        KEY_TYPE: entry.entry_type,
                        KEY_TITLE: entry.title,
                        KEY_CREATED: entry.created,
                        KEY_SOURCE: entry.source,
                        KEY_CONFIDENCE: entry.confidence,
                        KEY_EXPIRES: entry.expires,
                        KEY_LINKS: entry.links,
                        KEY_BODY: entry.body,
                        KEY_EXPIRED: entry.expired(),
                    }
                    for entry in items
                ]
            },
            indent=2,
            sort_keys=True,
        )
    if output != KEY_MARKDOWN:
        raise ToolWrightError(TEXT_UNKNOWN_EXPORT_FORMAT.format(output))
    lines = [TEXT_MEMORY_EXPORT, EMPTY_STRING]
    for entry in items:
        lines.extend(
            [
                TEXT_TEXT_5.format(entry.title),
                EMPTY_STRING,
                TEXT_SCOPE.format(entry.scope),
                TEXT_TYPE.format(entry.entry_type),
                TEXT_CREATED.format(entry.created),
                TEXT_EXPIRES.format(entry.expires),
                TEXT_SOURCE.format(entry.source),
                EMPTY_STRING,
                entry.body,
                EMPTY_STRING,
            ]
        )
    return NEWLINE.join(lines).rstrip() + NEWLINE


def render_memory_preamble(root: Path, budget_tokens: int | None = None) -> str:
    limit = settings(root)[KEY_TOKEN_BUDGET] if budget_tokens is None else budget_tokens
    if limit <= 0:
        raise ToolWrightError(TEXT_BUDGET_MUST_BE_A_POSITIVE_INTEGER)
    items = [entry for entry in load_memory_entries(root) if not entry.expired()]
    order = {scope: index for index, scope in enumerate(PRECEDENCE)}
    items.sort(key=lambda entry: (order.get(entry.scope, 99), entry.identifier))
    lines = [TEXT_PROJECT_MEMORY, EMPTY_STRING]
    used = len(NEWLINE.join(lines))
    for entry in items:
        summary = next(
            (line.strip()[:200] for line in entry.body.splitlines() if line.strip() and not line.lstrip().startswith(TEXT_TEXT_14)),
            EMPTY_STRING,
        )
        line = TEXT_TEXT_2.format(entry.entry_type, entry.title, entry.source, entry.created, summary)
        cost = len(line) + 1
        if (used + cost) // 4 > limit:
            continue
        lines.append(line)
        used += cost
    return NEWLINE.join(lines) + NEWLINE

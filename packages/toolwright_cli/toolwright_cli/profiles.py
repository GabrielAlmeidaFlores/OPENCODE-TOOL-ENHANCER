"""
Profile manifest loading and validation.

Public API: :class:`Profile`, :data:`FILE_COMPONENTS`, :data:`TOOL_COMPONENTS`,
:func:`load_profiles`, :func:`load_profile`, :func:`resolve_components`, and
:func:`verify_profiles`.

Side effects: reads files under ``profiles/`` only.

The manifest format is a restricted YAML subset: top-level scalar keys and lists
of strings. This keeps the CLI free of a YAML runtime dependency while the
manifests stay readable and diffable.
"""
from __future__ import annotations
from .profiles_strings import (
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    ENCODING_UTF8,
    KEY_AGENTS,
    KEY_COMMANDS,
    KEY_COMPONENTS,
    KEY_DESCRIPTION,
    KEY_DETAIL,
    KEY_NAME,
    KEY_PLUGIN,
    KEY_PROFILE,
    KEY_PROFILES,
    KEY_RALPH,
    KEY_SKILLS,
    KEY_STANDARD,
    KEY_STATUS,
    SEPARATOR_COMMA_SPACE,
    STATUS_FAIL,
    STATUS_OK,
    TEXT_A_Z_S,
    TEXT_COMPONENTS_MUST_BE_A_NON_EMPTY_LIST,
    TEXT_COMPONENT_S,
    TEXT_DESCRIPTION_IS_REQUIRED,
    TEXT_DUPLICATE_COMPONENTS,
    TEXT_DUPLICATE_PROFILE_NAME,
    TEXT_LIST_ITEM_OUTSIDE_A_LIST_KEY,
    TEXT_MISSING_PROFILES_DIRECTORY,
    TEXT_NAME_IS_REQUIRED,
    TEXT_NAME_MUST_MATCH_THE_FILE_NAME,
    TEXT_NO_MANIFESTS_UNDER,
    TEXT_NO_PROFILES_FOUND_UNDER,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_TEXT_4,
    TEXT_TEXT_5,
    TEXT_UNKNOWN_COMPONENTS,
    TEXT_UNKNOWN_COMPONENTS_2,
    TEXT_UNKNOWN_PROFILE_AVAILABLE,
    TEXT_UNKNOWN_PROFILE_KEY,
    TEXT_UNSUPPORTED_INDENTATION,
    TEXT_UNSUPPORTED_PROFILE_SYNTAX,
    TEXT_YML,
    TOOL_AST_GREP,
    TOOL_CODEGRAPH,
    TOOL_SERENA,
)

import re
from dataclasses import dataclass
from pathlib import Path

from .paths import ToolWrightError

FILE_COMPONENTS = (DEFAULT_ADAPTER, KEY_AGENTS, KEY_COMMANDS, KEY_SKILLS, KEY_RALPH)
TOOL_COMPONENTS = (TOOL_AST_GREP, TOOL_SERENA, TOOL_CODEGRAPH)
OPTIONAL_COMPONENTS = (KEY_PLUGIN,)
KNOWN_COMPONENTS = FILE_COMPONENTS + TOOL_COMPONENTS + OPTIONAL_COMPONENTS
DEFAULT_PROFILE = KEY_STANDARD

_KEY = re.compile(TEXT_A_Z_S)
_ALLOWED_KEYS = {KEY_NAME, KEY_DESCRIPTION, KEY_COMPONENTS}


@dataclass(frozen=True)
class Profile:

    name: str
    description: str
    components: tuple[str, ...]
    path: Path


def parse_profile_yaml(text: str, source: Path) -> dict[str, str | list[str]]:
    data: dict[str, str | list[str]] = {}
    current: str | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith(TEXT_TEXT):
            continue
        if stripped.startswith(TEXT_TEXT_2):
            if current is None or not isinstance(data.get(current), list):
                raise ToolWrightError(TEXT_LIST_ITEM_OUTSIDE_A_LIST_KEY.format(source, number))
            data[current].append(stripped[2:].strip().strip(TEXT_TEXT_3).strip(TEXT_TEXT_4))
            continue
        if line[:1].isspace():
            raise ToolWrightError(TEXT_UNSUPPORTED_INDENTATION.format(source, number))
        match = _KEY.match(line)
        if match is None:
            raise ToolWrightError(TEXT_UNSUPPORTED_PROFILE_SYNTAX.format(source, number))
        key, value = match.group(1), (match.group(2) or EMPTY_STRING).strip()
        if key not in _ALLOWED_KEYS:
            raise ToolWrightError(TEXT_UNKNOWN_PROFILE_KEY.format(source, number, key))
        if value:
            data[key] = value.strip(TEXT_TEXT_3).strip(TEXT_TEXT_4)
            current = None
        else:
            data[key] = []
            current = key
    return data


def load_profile(path: Path) -> Profile:
    data = parse_profile_yaml(path.read_text(encoding=ENCODING_UTF8), path)
    name = data.get(KEY_NAME)
    description = data.get(KEY_DESCRIPTION)
    components = data.get(KEY_COMPONENTS)
    if not isinstance(name, str) or not name:
        raise ToolWrightError(TEXT_NAME_IS_REQUIRED.format(path))
    if name != path.stem:
        raise ToolWrightError(TEXT_NAME_MUST_MATCH_THE_FILE_NAME.format(path, path.stem))
    if not isinstance(description, str) or not description:
        raise ToolWrightError(TEXT_DESCRIPTION_IS_REQUIRED.format(path))
    if not isinstance(components, list) or not components:
        raise ToolWrightError(TEXT_COMPONENTS_MUST_BE_A_NON_EMPTY_LIST.format(path))
    duplicates = sorted({item for item in components if components.count(item) > 1})
    if duplicates:
        raise ToolWrightError(TEXT_DUPLICATE_COMPONENTS.format(path, SEPARATOR_COMMA_SPACE.join(duplicates)))
    unknown = [item for item in components if item not in KNOWN_COMPONENTS]
    if unknown:
        raise ToolWrightError(TEXT_UNKNOWN_COMPONENTS.format(path, SEPARATOR_COMMA_SPACE.join(unknown)))
    return Profile(name=name, description=description, components=tuple(components), path=path)


def load_profiles(root: Path) -> dict[str, Profile]:
    directory = root / KEY_PROFILES
    if not directory.is_dir():
        raise ToolWrightError(TEXT_MISSING_PROFILES_DIRECTORY.format(directory))
    profiles: dict[str, Profile] = {}
    for path in sorted(directory.glob(TEXT_YML)):
        profile = load_profile(path)
        if profile.name in profiles:
            raise ToolWrightError(TEXT_DUPLICATE_PROFILE_NAME.format(profile.name))
        profiles[profile.name] = profile
    if not profiles:
        raise ToolWrightError(TEXT_NO_PROFILES_FOUND_UNDER.format(directory))
    return profiles


def resolve_components(profiles: dict[str, Profile], name: str, only: str | None) -> list[str]:
    if only:
        selected = [item.strip() for item in only.split(TEXT_TEXT_5) if item.strip()]
        unknown = [item for item in selected if item not in KNOWN_COMPONENTS]
        if unknown:
            raise ToolWrightError(TEXT_UNKNOWN_COMPONENTS_2.format(SEPARATOR_COMMA_SPACE.join(unknown)))
        return selected
    if name not in profiles:
        available = SEPARATOR_COMMA_SPACE.join(sorted(profiles))
        raise ToolWrightError(TEXT_UNKNOWN_PROFILE_AVAILABLE.format(name, available))
    return list(profiles[name].components)


def verify_profiles(root: Path) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    directory = root / KEY_PROFILES
    for path in sorted(directory.glob(TEXT_YML)):
        try:
            profile = load_profile(path)
            results.append(
                {
                    KEY_PROFILE: profile.name,
                    KEY_STATUS: STATUS_OK,
                    KEY_DETAIL: TEXT_COMPONENT_S.format(len(profile.components)),
                }
            )
        except ToolWrightError as error:
            results.append({KEY_PROFILE: path.stem, KEY_STATUS: STATUS_FAIL, KEY_DETAIL: str(error)})
    if not results:
        results.append({KEY_PROFILE: KEY_PROFILES, KEY_STATUS: STATUS_FAIL, KEY_DETAIL: TEXT_NO_MANIFESTS_UNDER.format(directory)})
    return results

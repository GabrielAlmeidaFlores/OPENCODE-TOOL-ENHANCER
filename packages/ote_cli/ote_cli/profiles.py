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

import re
from dataclasses import dataclass
from pathlib import Path

from .paths import OteError

FILE_COMPONENTS = ("opencode", "agents", "commands", "skills", "ralph")
TOOL_COMPONENTS = ("ast-grep", "serena", "codegraph")
KNOWN_COMPONENTS = FILE_COMPONENTS + TOOL_COMPONENTS
DEFAULT_PROFILE = "standard"

_KEY = re.compile(r"^([a-z_]+):(?:\s*(.*))?$")
_ALLOWED_KEYS = {"name", "description", "components"}


@dataclass(frozen=True)
class Profile:
    """
    One installable profile manifest.
    """

    name: str
    description: str
    components: tuple[str, ...]
    path: Path


def _parse_simple_yaml(text: str, source: Path) -> dict[str, str | list[str]]:
    """
    Parse the restricted YAML subset used by profile manifests.
    """
    data: dict[str, str | list[str]] = {}
    current: str | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            if current is None or not isinstance(data.get(current), list):
                raise OteError(f"{source}:{number}: list item outside a list key")
            data[current].append(stripped[2:].strip().strip('"').strip("'"))
            continue
        if line[:1].isspace():
            raise OteError(f"{source}:{number}: unsupported indentation")
        match = _KEY.match(line)
        if match is None:
            raise OteError(f"{source}:{number}: unsupported profile syntax")
        key, value = match.group(1), (match.group(2) or "").strip()
        if key not in _ALLOWED_KEYS:
            raise OteError(f"{source}:{number}: unknown profile key {key}")
        if value:
            data[key] = value.strip('"').strip("'")
            current = None
        else:
            data[key] = []
            current = key
    return data


def load_profile(path: Path) -> Profile:
    """
    Load and validate one profile manifest.
    """
    data = _parse_simple_yaml(path.read_text(encoding="utf-8"), path)
    name = data.get("name")
    description = data.get("description")
    components = data.get("components")
    if not isinstance(name, str) or not name:
        raise OteError(f"{path}: name is required")
    if name != path.stem:
        raise OteError(f"{path}: name must match the file name ({path.stem})")
    if not isinstance(description, str) or not description:
        raise OteError(f"{path}: description is required")
    if not isinstance(components, list) or not components:
        raise OteError(f"{path}: components must be a non-empty list")
    duplicates = sorted({item for item in components if components.count(item) > 1})
    if duplicates:
        raise OteError(f"{path}: duplicate components: {', '.join(duplicates)}")
    unknown = [item for item in components if item not in KNOWN_COMPONENTS]
    if unknown:
        raise OteError(f"{path}: unknown components: {', '.join(unknown)}")
    return Profile(name=name, description=description, components=tuple(components), path=path)


def load_profiles(root: Path) -> dict[str, Profile]:
    """
    Load every profile manifest under ``profiles/``.
    """
    directory = root / "profiles"
    if not directory.is_dir():
        raise OteError(f"missing profiles directory: {directory}")
    profiles: dict[str, Profile] = {}
    for path in sorted(directory.glob("*.yml")):
        profile = load_profile(path)
        if profile.name in profiles:
            raise OteError(f"duplicate profile name: {profile.name}")
        profiles[profile.name] = profile
    if not profiles:
        raise OteError(f"no profiles found under {directory}")
    return profiles


def resolve_components(profiles: dict[str, Profile], name: str, only: str | None) -> list[str]:
    """
    Resolve a profile name or an explicit component list.
    """
    if only:
        selected = [item.strip() for item in only.split(",") if item.strip()]
        unknown = [item for item in selected if item not in KNOWN_COMPONENTS]
        if unknown:
            raise OteError(f"unknown components: {', '.join(unknown)}")
        return selected
    if name not in profiles:
        available = ", ".join(sorted(profiles))
        raise OteError(f"unknown profile: {name} (available: {available})")
    return list(profiles[name].components)


def verify_profiles(root: Path) -> list[dict[str, str]]:
    """
    Validate every manifest, returning one result per file instead of raising.
    """
    results: list[dict[str, str]] = []
    directory = root / "profiles"
    for path in sorted(directory.glob("*.yml")):
        try:
            profile = load_profile(path)
            results.append(
                {
                    "profile": profile.name,
                    "status": "ok",
                    "detail": f"{len(profile.components)} component(s)",
                }
            )
        except OteError as error:
            results.append({"profile": path.stem, "status": "fail", "detail": str(error)})
    if not results:
        results.append({"profile": "profiles", "status": "fail", "detail": f"no manifests under {directory}"})
    return results

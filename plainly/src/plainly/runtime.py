from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


MAX_STYLE_BYTES = 8192
SETTINGS_DIRECTORY = Path(".noory") / "plainly"
SETTINGS_FILENAME = "settings.json"


@dataclass(frozen=True)
class Profile:
    name: str
    label: str
    description: str
    path: Path


@dataclass(frozen=True)
class ProfileCatalog:
    default: str
    profiles: Mapping[str, Profile]


@dataclass(frozen=True)
class ResolvedStyle:
    text: str
    source: str
    profile: str | None
    diagnostics: tuple[str, ...] = ()


def load_catalog(plugin_root: Path) -> ProfileCatalog:
    registry_path = plugin_root / "styles" / "profiles.json"
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Plainly profile registry is invalid: {exc}") from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("profiles"), dict):
        raise RuntimeError("Plainly profile registry must contain a profiles object")

    profiles: dict[str, Profile] = {}
    for name, entry in raw["profiles"].items():
        if not isinstance(name, str) or not isinstance(entry, dict):
            raise RuntimeError("Plainly profile entries must be named objects")
        file_name = entry.get("file")
        label = entry.get("label")
        description = entry.get("description")
        if not all(isinstance(value, str) and value for value in (file_name, label, description)):
            raise RuntimeError(f"Plainly profile {name!r} has incomplete metadata")
        profiles[name] = Profile(
            name=name,
            label=label,
            description=description,
            path=plugin_root / "styles" / file_name,
        )

    default = raw.get("default")
    if not isinstance(default, str) or default not in profiles:
        raise RuntimeError("Plainly profile registry has an unknown default")
    return ProfileCatalog(default=default, profiles=profiles)


def settings_path(scope: str, project_root: Path, home: Path | None = None) -> Path:
    if scope == "project":
        base = project_root
    elif scope == "user":
        base = home if home is not None else Path.home()
    else:
        raise ValueError(f"Unknown settings scope: {scope}")
    return base.expanduser().resolve() / SETTINGS_DIRECTORY / SETTINGS_FILENAME


def read_style_file(path: Path) -> tuple[str | None, str | None]:
    resolved = path.expanduser().resolve()
    try:
        with resolved.open("rb") as stream:
            content = stream.read(MAX_STYLE_BYTES + 1)
    except OSError as exc:
        return None, f"Cannot read style file {resolved}: {exc}"

    if len(content) > MAX_STYLE_BYTES:
        return None, f"Style file {resolved} exceeds the {MAX_STYLE_BYTES}-byte limit"
    try:
        text = content.decode("utf-8").strip()
    except UnicodeDecodeError:
        return None, f"Style file {resolved} must be UTF-8"
    if not text:
        return None, f"Style file {resolved} is empty"
    return text, None


def resolve_style(
    plugin_root: Path,
    cwd: Path,
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> ResolvedStyle:
    catalog = load_catalog(plugin_root)
    environment = os.environ if environ is None else environ
    project_root = cwd.expanduser().resolve()
    user_home = Path.home() if home is None else home.expanduser().resolve()
    diagnostics: list[str] = []

    env_file = environment.get("NOORY_STYLE_FILE", "").strip()
    if env_file:
        resolved = _external_path(env_file, project_root)
        text, error = read_style_file(resolved)
        if text is not None:
            return ResolvedStyle(
                text=text,
                source=f"file:{resolved}",
                profile=None,
                diagnostics=tuple(diagnostics),
            )
        if error:
            diagnostics.append(error)

    env_profile = environment.get("NOORY_STYLE_PROFILE", "").strip()
    if env_profile:
        resolved = _builtin_style(catalog, env_profile, "env:NOORY_STYLE_PROFILE", diagnostics)
        if resolved is not None:
            return resolved
        diagnostics.append(f"Unknown Plainly profile from NOORY_STYLE_PROFILE: {env_profile}")

    project_settings = settings_path("project", project_root, user_home)
    user_settings = settings_path("user", project_root, user_home)
    candidates = (
        (project_settings, project_root, project_root),
        (user_settings, user_settings.parent, None),
    )
    seen: set[Path] = set()
    for candidate, relative_base, confined_root in candidates:
        if candidate in seen or not candidate.exists():
            continue
        seen.add(candidate)
        resolved = _style_from_settings(
            candidate,
            relative_base,
            confined_root,
            catalog,
            diagnostics,
        )
        if resolved is not None:
            return resolved

    default = _builtin_style(catalog, catalog.default, f"builtin:{catalog.default}", diagnostics)
    if default is None:
        raise RuntimeError(f"Plainly default profile {catalog.default!r} cannot be loaded")
    return default


def _external_path(value: str, base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def _builtin_style(
    catalog: ProfileCatalog,
    name: str,
    source: str,
    diagnostics: list[str],
) -> ResolvedStyle | None:
    profile = catalog.profiles.get(name)
    if profile is None:
        return None
    text, error = read_style_file(profile.path)
    if error:
        diagnostics.append(error)
        return None
    if text is None:
        return None
    return ResolvedStyle(
        text=text,
        source=source,
        profile=name,
        diagnostics=tuple(diagnostics),
    )


def _style_from_settings(
    path: Path,
    relative_base: Path,
    confined_root: Path | None,
    catalog: ProfileCatalog,
    diagnostics: list[str],
) -> ResolvedStyle | None:
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        diagnostics.append(f"Cannot read Plainly settings {path}: {exc}")
        return None
    if not isinstance(raw, dict):
        diagnostics.append(f"Plainly settings {path} must contain a JSON object")
        return None

    file_value = raw.get("style_file")
    if isinstance(file_value, str) and file_value.strip():
        style_path = _external_path(file_value.strip(), relative_base)
        if confined_root is not None:
            try:
                style_path.relative_to(confined_root.resolve())
            except ValueError:
                diagnostics.append(
                    f"Project Plainly style file must stay within project root "
                    f"{confined_root.resolve()}: {style_path}"
                )
                style_path = None
        if style_path is not None:
            text, error = read_style_file(style_path)
            if text is not None:
                return ResolvedStyle(
                    text=text,
                    source=f"file:{style_path}",
                    profile=None,
                    diagnostics=tuple(diagnostics),
                )
            if error:
                diagnostics.append(error)

    profile_value = raw.get("profile")
    if isinstance(profile_value, str) and profile_value.strip():
        name = profile_value.strip()
        resolved = _builtin_style(catalog, name, f"settings:{path}", diagnostics)
        if resolved is not None:
            return resolved
        if name not in catalog.profiles:
            diagnostics.append(f"Unknown Plainly profile in {path}: {name}")

    if not file_value and not profile_value:
        diagnostics.append(f"Plainly settings {path} has no profile or style_file")
    return None

# The hook must run wherever `python3` points on a host machine (3.9+), so this
# module keeps the same annotation-laziness contract as stage_guard.py.
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import stage_topology

# Schema-v4 authorization-zone constants. Read-only consumers can still inspect
# schema-v3 projects so audit and migration never strand an older harness.
STAGE_OFFICIAL_ROOT = ".stage/official"
STAGE_OFFICIAL_ARCHIVE_ROOT = f"{STAGE_OFFICIAL_ROOT}/work/archive"

ACTIVE_TOPOLOGY_V3 = "v3"
ACTIVE_TOPOLOGY_V4 = "v4"
SETTINGS_JSON_NAME = "settings.json"
SETTINGS_JSONC_NAME = "settings.jsonc"


def strip_json_comments(text: str) -> str:
    """Replace JSON line and block comments with whitespace.

    Keeping comment spans the same length preserves useful JSON decoder
    positions. Comment markers inside strings remain data.
    """

    characters = list(text)
    index = 0
    in_string = False
    escaped = False
    while index < len(characters):
        character = characters[index]
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            index += 1
            continue
        if character == '"':
            in_string = True
            index += 1
            continue
        if character != "/" or index + 1 >= len(characters):
            index += 1
            continue

        following = characters[index + 1]
        if following == "/":
            characters[index] = " "
            characters[index + 1] = " "
            index += 2
            while index < len(characters) and characters[index] not in "\r\n":
                characters[index] = " "
                index += 1
            continue
        if following == "*":
            comment_start = index
            characters[index] = " "
            characters[index + 1] = " "
            index += 2
            while index + 1 < len(characters):
                if characters[index] == "*" and characters[index + 1] == "/":
                    characters[index] = " "
                    characters[index + 1] = " "
                    index += 2
                    break
                if characters[index] not in "\r\n":
                    characters[index] = " "
                index += 1
            else:
                raise json.JSONDecodeError("Unterminated block comment", text, comment_start)
            continue
        index += 1
    return "".join(characters)


def replace_top_level_setting(text: str, key: str, value: object) -> str | None:
    """Replace one existing top-level JSON/JSONC value without reformatting."""

    clean_text = strip_json_comments(text)
    decoder = json.JSONDecoder()
    index = 0
    while index < len(clean_text) and clean_text[index].isspace():
        index += 1
    if index >= len(clean_text) or clean_text[index] != "{":
        return None
    index += 1

    while index < len(clean_text):
        while index < len(clean_text) and (
            clean_text[index].isspace() or clean_text[index] == ","
        ):
            index += 1
        if index >= len(clean_text) or clean_text[index] == "}":
            return None
        try:
            candidate, key_end = decoder.raw_decode(clean_text, index)
        except json.JSONDecodeError:
            return None
        if not isinstance(candidate, str):
            return None
        index = key_end
        while index < len(clean_text) and clean_text[index].isspace():
            index += 1
        if index >= len(clean_text) or clean_text[index] != ":":
            return None
        index += 1
        while index < len(clean_text) and clean_text[index].isspace():
            index += 1
        value_start = index
        try:
            _current_value, value_end = decoder.raw_decode(clean_text, value_start)
        except json.JSONDecodeError:
            return None
        if candidate == key:
            return (
                text[:value_start]
                + json.dumps(value, ensure_ascii=False)
                + text[value_end:]
            )
        index = value_end

    return None


def write_setting_preserving_comments(
    settings_path: Path,
    settings: dict[str, object],
    key: str,
    value: object,
) -> None:
    """Write one setting without silently erasing user-authored comments."""

    source = settings_path.read_text(encoding="utf-8")
    clean_source = strip_json_comments(source)
    settings[key] = value
    if clean_source != source:
        updated = replace_top_level_setting(source, key, value)
        if updated is None:
            raise ValueError(
                f"cannot safely add missing `{key}` to commented {settings_path.name}; "
                "add the key manually and re-run"
            )
        settings_path.write_text(updated, encoding="utf-8")
        return
    settings_path.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def read_settings(
    stage_root: Path,
) -> tuple[Path, object, OSError | json.JSONDecodeError | None]:
    """Read and parse the project settings without choosing a failure policy."""

    json_path = stage_root / SETTINGS_JSON_NAME
    jsonc_path = stage_root / SETTINGS_JSONC_NAME
    if json_path.exists() and jsonc_path.exists():
        error = FileExistsError(
            f"{SETTINGS_JSON_NAME} and {SETTINGS_JSONC_NAME} both exist; keep exactly one"
        )
        return jsonc_path, None, error
    settings_path = jsonc_path if jsonc_path.exists() or not json_path.exists() else json_path
    try:
        source = settings_path.read_text(encoding="utf-8")
        return settings_path, json.loads(strip_json_comments(source)), None
    except (OSError, json.JSONDecodeError) as exc:
        return settings_path, None, exc


def active_topology(stage_root: Path) -> str:
    """Return the topology selected by this project's settings.

    Schema v4 is active only when the project carries the exact integer v4
    marker. Missing, unreadable, malformed, and older markers keep read-only
    consumers on the legacy resolver; mutation gates separately fail closed
    with the stage-migrate banner.
    """

    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return ACTIVE_TOPOLOGY_V3
    schema_version = data.get(stage_topology.SCHEMA_VERSION_KEY) if isinstance(data, dict) else None
    if type(schema_version) is int and schema_version == stage_topology.SCHEMA_VERSION:
        return ACTIVE_TOPOLOGY_V4
    return ACTIVE_TOPOLOGY_V3


def load_schema_version(stage_root: Path) -> object:
    """Return the raw schema marker, preserving missing/malformed distinctions."""

    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return None
    return data.get(stage_topology.SCHEMA_VERSION_KEY) if isinstance(data, dict) else None


def schema_migration_banner(stage_root: Path) -> str:
    """Actionable mutation blocker for a project behind the enforced contract.

    A wholly absent settings file is left to the established partial-init/repair
    behavior. Once settings.json exists, a missing, malformed, or older marker is
    behind and every mutation entry point must name the user-facing migration skill.
    """

    settings_path, data, error = read_settings(stage_root)
    if not settings_path.exists():
        return ""
    schema_version = (
        data.get(stage_topology.SCHEMA_VERSION_KEY)
        if error is None and isinstance(data, dict)
        else None
    )
    if type(schema_version) is int and schema_version == STAGE_SCHEMA_VERSION:
        return ""
    displayed = f"v{schema_version}" if type(schema_version) is int else "missing/invalid"
    return (
        f"Stage schema gate: this project is on schema {displayed}; the plugin requires "
        f"v{STAGE_SCHEMA_VERSION} — run the stage-migrate skill. Read-only stage-audit and "
        "stage-migrate remain available."
    )


def clean_path_text(path: str) -> str:
    """Surface cleanup only — strip quotes, unify separators, collapse repeated
    slashes, drop leading `./`. Keeps `..` INTACT so a filesystem resolve can
    follow symlinks before collapsing `..` (lexical collapse first would
    mis-target a symlink parent). Preserves a Windows UNC prefix (`\\\\server`)."""
    value = path.strip().strip("'\"`")
    value = value.replace("\\", "/")
    unc = value.startswith("//")  # UNC share root — keep the double slash
    leading_slash = value.startswith("/")
    core = re.sub(r"/+", "/", value).lstrip("/")  # `.//src` must not become `/src`
    if unc:
        value = "//" + core
    elif leading_slash:
        value = "/" + core
    else:
        value = core
    while value.startswith("./"):
        value = value[2:]
    return value


def normalize_path_text(path: str) -> str:
    """Cleaned path with `.`/`..` collapsed lexically — for string comparisons
    and slot keys that never hit the filesystem. For classifying a real write
    target, go through `relative_to_workspace` (resolves symlinks first)."""
    return collapse_dot_segments(clean_path_text(path))


def collapse_dot_segments(value: str) -> str:
    """Lexically resolve `.`/`..` so `.stage/../src` cannot masquerade as a
    `.stage`-internal path (and vice versa). Purely textual — no filesystem
    access, so it is safe for not-yet-existing targets and identical on every
    host. Leading `..` that escapes the anchor is preserved (it still reads as
    outside the workspace to every gate)."""
    if not value:
        return value
    absolute_prefix = ""
    rest = value
    drive = re.match(r"^([A-Za-z]:)(.*)$", rest)
    if drive:
        absolute_prefix = drive.group(1)
        rest = drive.group(2)
    if rest.startswith("/"):
        absolute_prefix += "/"
        rest = rest.lstrip("/")
    stack: list[str] = []
    for segment in rest.split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if stack and stack[-1] != "..":
                stack.pop()
            elif not absolute_prefix:
                stack.append("..")
            # An absolute path cannot escape its own root: drop the `..`.
            continue
        stack.append(segment)
    return absolute_prefix + "/".join(stack)


def stage_real_root(workspace_root: Path) -> Path | None:
    """The real filesystem location of `<workspace>/.stage`, following a
    symlinked `.stage` itself. Used to classify writes against the true tree.

    Returns None for a degenerate root (`.stage -> .` or `-> ..`) that equals or
    contains the workspace — otherwise every ordinary write would remap into a
    logical `.stage/...` and be excluded from governance."""
    try:
        workspace_resolved = workspace_root.resolve()
        stage = (workspace_root / ".stage").resolve()
    except (OSError, RuntimeError):  # RuntimeError = symlink loop on Python 3.9
        return None
    if stage == workspace_resolved:
        return None
    try:
        workspace_resolved.relative_to(stage)  # workspace lies inside stage → ancestor
        return None
    except ValueError:
        return stage


def relative_to_workspace(path: str | Path, workspace_root: Path) -> str:
    """Canonical workspace-relative form of a write target (P28 single model).

    Resolves symlink components and `..` in filesystem order (symlinks first,
    then `..`), then re-maps a target that lands inside the REAL `.stage` tree
    back to a logical `.stage/...` string — so `link/../past` (link ->
    `.stage/present`), `.stage/../src`, and a symlinked `.stage -> data` all
    classify by where the write truly lands, not how it was spelled. A path that
    escapes the workspace keeps its lexical form so outside-workspace checks
    still fire; unresolvable input degrades to lexical.
    """
    text = clean_path_text(str(path))
    try:
        candidate = Path(text).expanduser()
    except RuntimeError:
        # `~user` with no such account raises on POSIX (e.g. `~draft.py`) — it is
        # an ordinary workspace-relative filename, not a home reference.
        candidate = Path(text)
    try:
        workspace_resolved = workspace_root.resolve()
    except (OSError, RuntimeError):
        workspace_resolved = workspace_root
    base = candidate if candidate.is_absolute() else (workspace_resolved / text)
    try:
        resolved = base.resolve()
    except (OSError, RuntimeError):  # RuntimeError = symlink loop on Python 3.9
        return normalize_path_text(text)

    stage_real = stage_real_root(workspace_root)
    if stage_real is not None:
        if resolved == stage_real:
            return ".stage"
        try:
            return ".stage/" + resolved.relative_to(stage_real).as_posix()
        except ValueError:
            pass
    try:
        return normalize_path_text(resolved.relative_to(workspace_resolved).as_posix())
    except ValueError:
        # Resolved outside the workspace (e.g. `~/…`, an escaping symlink): return
        # the absolute path so outside-workspace checks fire — not the lexical
        # spelling, which would read as a governed workspace path.
        return resolved.as_posix()


def entry_relative_to_workspace(path: str | Path, workspace_root: Path) -> str:
    """Canonical workspace-relative form that keeps FINAL-ENTRY identity:
    parent components are resolved (symlinks first, then `..`), the last
    component is kept as named. Exact-entry authorizations (a work item's
    `promotes`, pending intents, archive filenames) name entries, not targets —
    `rm`/`mv` act on the entry a path NAMES, and two symlinked leaves aliasing
    one target are distinct grants. A spelling with no leaf identity (trailing
    `/` or `/.`, bare `.`/`..`) falls back to the fully resolved form."""
    text = clean_path_text(str(path))
    stripped = text.rstrip()
    name = Path(text).name if text else ""
    if name in ("", ".", "..") or stripped.endswith("/") or stripped.endswith("/."):
        return relative_to_workspace(text, workspace_root)
    parent = relative_to_workspace(str(Path(text).parent), workspace_root)
    if parent in ("", "."):
        return name
    return parent.rstrip("/") + "/" + name


def stage_relative_forms(path: str | Path, workspace_root: Path) -> tuple[str, str, str]:
    """(fully-resolved, entry-canonical, lexical) forms of one write target.
    Detection gates classify by the union of the three — fail closed: the
    resolved form catches symlink/`..` re-entry, the entry form catches an
    aliased parent whose LEAF is itself an outward symlink, the lexical form
    catches a degenerate `.stage -> .` and plain spellings."""
    return (
        relative_to_workspace(path, workspace_root),
        entry_relative_to_workspace(path, workspace_root),
        normalize_path_text(str(path)),
    )


# Predicates below take a CANONICAL workspace-relative path (from
# relative_to_workspace) — do not pass a raw, unresolved spelling.
def path_targets_stage_root(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return "/.stage/" in normalized or normalized.endswith("/.stage")


def _path_targets_stage_zone(path: str, zone_root: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    anchored_root = "/" + zone_root.strip("/")
    return normalized == anchored_root or anchored_root + "/" in normalized


def path_targets_stage_official(path: str) -> bool:
    """Whether a canonical path targets the schema-v4 authorization zone."""

    return _path_targets_stage_zone(path, STAGE_OFFICIAL_ROOT)


def path_targets_stage_official_archive(path: str) -> bool:
    """Whether a canonical path targets the schema-v4 work archive."""

    return _path_targets_stage_zone(path, STAGE_OFFICIAL_ARCHIVE_ROOT)


def path_targets_stage_past(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return "/.stage/past/" in normalized or normalized.startswith("/.stage/past/")


def path_targets_stage_archive(path: str) -> bool:
    normalized = "/" + normalize_path_text(path).lstrip("/")
    return (
        "/.stage/past/work/archive/" in normalized
        or normalized.startswith("/.stage/past/work/archive/")
        or path_targets_stage_official_archive(path)
    )


def is_stage_internal_path(path: str, workspace_root: Path) -> bool:
    # Union of forms: a symlinked `.stage/settings.json` (resolve lands outside)
    # must stay stage-internal or the malformed-governance gate would deny the
    # very repair it asks for.
    return any(
        form == ".stage" or form.startswith(".stage/")
        for form in stage_relative_forms(path, workspace_root)
    )


def load_governance(stage_root: Path) -> dict[str, Any]:
    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return {}
    if not isinstance(data, dict):
        return {}
    governance = data.get("governance")
    return governance if isinstance(governance, dict) else {}


# Human-readable Stage document language (DE-00000003). Machine tokens (IDs,
# paths, frontmatter keys, enum values, record section headings) never follow
# it. A missing or malformed value falls open to English so hooks keep working
# on any settings state; only the audit reports the malformation.
LANGUAGE_TAG_RE = re.compile(r"^[a-z]{2,8}(-[a-z0-9]{2,8})*$")
DEFAULT_LANGUAGE = "en"


def load_language(stage_root: Path) -> str:
    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return DEFAULT_LANGUAGE
    language = data.get("language") if isinstance(data, dict) else None
    if isinstance(language, str) and LANGUAGE_TAG_RE.match(language):
        return language
    return DEFAULT_LANGUAGE


def load_venue_routing(stage_root: Path) -> dict[str, str]:
    """The project's declared `kind -> venue` role policy (DE-00000004), or {}
    when absent. Only well-formed string entries are returned — hooks and
    registration fail open; the audit owns reporting a malformed map."""
    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return {}
    routing = data.get("venue_routing") if isinstance(data, dict) else None
    if not isinstance(routing, dict):
        return {}
    return {
        kind.strip().lower(): venue.strip()
        for kind, venue in routing.items()
        if isinstance(kind, str) and isinstance(venue, str) and kind.strip() and venue.strip()
    }


# Review strength is a named level the PROJECT binds to a real, verdict-emitting
# command (in settings.json `review.strengths`). The harness fixes no command —
# like `venue`, it ships the vocabulary and the project declares the behavior.
REVIEW_STRENGTHS = ("off", "light", "standard", "deep", "red-team")
REVIEW_STAGES = ("design", "implementation", "promotion")


def load_review_config(stage_root: Path) -> dict[str, Any]:
    """The `review` block of settings.json (per-stage strength + strength→command),
    or {} when absent. A wholly unreadable settings.json is already fail-closed by
    governance_broken(); an absent/non-dict `review` here simply means 'no review'."""
    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return {}
    review = data.get("review") if isinstance(data, dict) else None
    return review if isinstance(review, dict) else {}


def load_executors_config(stage_root: Path) -> object:
    """Return the raw review-sibling ``executors`` section.

    The resolver owns validation so an absent, unreadable, or malformed section
    remains distinguishable from a valid venue-to-command map and callers can
    fail closed.
    """

    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return None
    return data.get("executors") if isinstance(data, dict) else None


def resolve_executor_command(
    executors: object, item_venue: str
) -> tuple[str | None, str]:
    """Resolve the executor command for an item's venue, failing closed.

    Every unusable shape returns ``(None, error)``. A caller must never treat a
    missing executor as permission to skip execution.
    """

    venue = item_venue.strip().lower()
    if not venue:
        return None, "work item venue must be a non-empty string"
    if not isinstance(executors, dict):
        return None, (
            f"executors.{venue} has no command; executors must be an object "
            "mapping venue -> command"
        )

    normalized: dict[str, str] = {}
    for raw_name, raw_command in executors.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            return None, "executors venue names must be non-empty strings"
        name = raw_name.strip().lower()
        if name in normalized:
            return None, f"executors contains duplicate venue `{name}`"
        if not isinstance(raw_command, str) or not raw_command.strip():
            return None, f"executors.{name} must be a non-empty command string"
        normalized[name] = raw_command

    command = normalized.get(venue)
    if command is None:
        return None, f"executors.{venue} has no command"
    return command, ""


LIMIT_KEYS = (
    "max_attempts_per_item",
    "max_iterations",
    "max_wall_clock_seconds",
)


def load_limits_config(stage_root: Path) -> tuple[dict[str, int] | None, str]:
    """Load and validate the optional execution-limit contract.

    Returns ``(limits, "")`` for a valid section and ``(None, "")`` when the
    section is absent. Any unreadable settings file or malformed present
    section returns ``(None, error)``; callers must fail closed on that error.
    """

    _settings_path, data, error = read_settings(stage_root)
    if isinstance(error, OSError):
        return None, f"cannot read settings.json: {error}"
    if isinstance(error, json.JSONDecodeError):
        return None, f"settings.json is not valid JSON: {error}"
    if not isinstance(data, dict):
        return None, "settings.json must contain a JSON object"
    if "limits" not in data:
        return None, ""

    raw_limits = data["limits"]
    if not isinstance(raw_limits, dict):
        return None, "limits must be an object"
    unknown = sorted(key for key in raw_limits if key not in LIMIT_KEYS)
    if unknown:
        return None, f"limits contains unknown field(s): {', '.join(unknown)}"
    missing = [key for key in LIMIT_KEYS if key not in raw_limits]
    if missing:
        return None, f"limits is missing required field(s): {', '.join(missing)}"

    limits: dict[str, int] = {}
    for key in LIMIT_KEYS:
        value = raw_limits[key]
        if type(value) is not int or value <= 0:
            return None, f"limits.{key} must be a positive integer"
        limits[key] = value
    return limits, ""


def resolve_review_command(review: dict[str, Any], stage: str) -> tuple[str | None, str]:
    """Resolve the review COMMAND to run for a lifecycle stage.

    Returns (command, error). (None, "") means no review is required (the stage is
    `off` or unset). A non-empty error means the config REQUIRES a review here but
    is unusable (typo'd strength, or no command bound) — the caller must FAIL CLOSED,
    never silently skip. A non-empty command string is what to execute.
    """
    stages = review.get("stages", {})
    if not isinstance(stages, dict):
        return None, "review.stages must be an object mapping stage -> strength"
    if stage not in stages:
        return None, ""  # unset -> no review at this stage
    raw = stages[stage]
    # A present-but-non-string value (number, null, list) is malformed, NOT "off":
    # coercing it to off would silently skip a review the project meant to require.
    if not isinstance(raw, str):
        return None, f"review.stages.{stage} must be a strength string, got {type(raw).__name__}"
    strength = raw or "off"
    if strength not in REVIEW_STRENGTHS:
        return None, (
            f"review.stages.{stage} strength `{strength}` is not one of {list(REVIEW_STRENGTHS)}"
        )
    if strength == "off":
        return None, ""
    strengths = review.get("strengths")
    command = strengths.get(strength) if isinstance(strengths, dict) else None
    if not isinstance(command, str) or not command.strip():
        return None, (
            f"review stage `{stage}` requires strength `{strength}`, but "
            f"review.strengths.{strength} has no command"
        )
    return command, ""


def resolve_independent_review_command(
    review: dict[str, Any], item_venue: str
) -> tuple[str | None, str]:
    """Resolve the sole reviewer command whose venue differs from the item's.

    Autonomous completion requires an independent reviewer, so every unusable
    shape returns a non-empty error that callers must fail closed on. The
    two-venue contract deliberately rejects ambiguous N-venue configurations.
    """

    venue = item_venue.strip().lower()
    if not venue:
        return None, "autonomous work item venue must be a non-empty string"

    reviewers = review.get("reviewers")
    if not isinstance(reviewers, dict):
        return None, "review.reviewers must be an object mapping venue -> command"

    normalized: dict[str, str] = {}
    for raw_name, raw_command in reviewers.items():
        if not isinstance(raw_name, str) or not raw_name.strip():
            return None, "review.reviewers venue names must be non-empty strings"
        name = raw_name.strip().lower()
        if name in normalized:
            return None, f"review.reviewers contains duplicate venue `{name}`"
        if not isinstance(raw_command, str) or not raw_command.strip():
            return None, f"review.reviewers.{name} must be a non-empty command string"
        normalized[name] = raw_command

    differing = [(name, command) for name, command in normalized.items() if name != venue]
    if not differing:
        return None, (
            f"review.reviewers configures no reviewer different from item venue `{venue}`"
        )
    if len(differing) != 1:
        names = ", ".join(name for name, _command in differing)
        return None, (
            "review.reviewers must configure exactly one reviewer different from "
            f"item venue `{venue}`; found: {names}"
        )
    return differing[0][1], ""


# Version of the `.stage` artifact/settings contract, independent of the
# plugin release version. stage-init stamps new harnesses via the settings
# template; preserved older settings are never overwritten — the audit warns
# on a missing or different value instead. Bump only when the recorded
# contract changes shape.
# Version 2: common operations docs are plugin-owned and no longer copied
# into `.stage/operations/`.
# Version 3: backlog entries are planned W work cards (the B family retired).
# Version 4: the official authorization zone and responsibility-family roots
# replace the time-wrapper topology. Migrate v3 projects with stage-migrate.
STAGE_SCHEMA_VERSION = 4


def configured_write_tools(stage_root: Path) -> set[str]:
    """Tool names settings.json registers as additional write tools.

    A host or MCP tool that writes files under a name outside the built-in
    allowlist bypasses every gate (see hooks/README.md §Limits); a project
    registers such names in `extra_write_tools` so the write gates classify
    them. Broken settings yield the empty set: the registered names cannot be
    read back, so those tools fall back to the documented ungated default
    while built-in tools stay behind the governance fail-closed deny."""
    _settings_path, data, error = read_settings(stage_root)
    if error is not None:
        return set()
    if not isinstance(data, dict):
        return set()
    names = data.get("extra_write_tools")
    if not isinstance(names, list):
        return set()
    return {str(name).strip() for name in names if str(name).strip()}


def governance_broken(stage_root: Path) -> bool:
    """True when settings.json exists but cannot be trusted (fail-closed signal)."""
    settings_path, data, error = read_settings(stage_root)
    if not settings_path.exists():
        return False
    if error is not None:
        return True
    if not isinstance(data, dict):
        return True
    # A mistyped tool registration means the writer the project meant to gate
    # would silently fall back to the ungated unknown-name default — treat the
    # whole file as untrusted until repaired.
    extra_tools = data.get("extra_write_tools")
    if extra_tools is not None and (
        not isinstance(extra_tools, list)
        or any(not isinstance(name, str) for name in extra_tools)
    ):
        return True
    governance = data.get("governance")
    return governance is not None and not isinstance(governance, dict)


DEFAULT_EXCLUDED_PREFIXES = (".stage", ".git", ".discuss")


def path_has_prefix(relative: str, prefix: str) -> bool:
    clean = prefix.rstrip("/")
    return bool(clean) and (relative == clean or relative.startswith(clean + "/"))


def is_outside_workspace(relative: str) -> bool:
    return (
        not relative
        or relative.startswith("/")
        or bool(re.match(r"^[A-Za-z]:", relative))
        or relative.startswith("../")
        or relative == ".."
        or relative == "~"
        or relative.startswith("~/")  # home dir — but `~draft.py` is a real file
    )


def is_source_path(path: str, workspace_root: Path, follows_symlink: bool = False) -> bool:
    """Whether a write target is a governed workspace source.

    Operation semantics decide which forms classify. A CONTENT write
    (`follows_symlink=True`: Write/Edit) modifies the DEREFERENCED target, so it
    is classified by the resolved form alone — a write to `.git/link.py`
    (-> src/app.py) governs `src/app.py`, not the `.git` entry. An UNLINK/move
    (default) acts on the named ENTRY, so exclusions win on the entry and
    lexical forms (deleting `src/link -> .git/config` targets the entry) while
    inclusion holds across all forms (a symlink entry into governed space stays
    governed when its resolve derefs outward)."""
    resolved, entry, lexical = stage_relative_forms(path, workspace_root)
    if follows_symlink:
        forms = [resolved] if not is_outside_workspace(resolved) else []
        exclude_forms = forms
    else:
        forms = [form for form in (resolved, entry, lexical) if not is_outside_workspace(form)]
        exclude_forms = [form for form in (entry, lexical) if not is_outside_workspace(form)]
    if not forms:
        return False
    if any(
        path_has_prefix(form, prefix)
        for form in exclude_forms
        for prefix in DEFAULT_EXCLUDED_PREFIXES
    ):
        return False

    governance = load_governance(workspace_root / ".stage")
    if any(_form_excluded(form, governance, workspace_root) for form in exclude_forms):
        return False
    return any(_form_included(form, governance, workspace_root) for form in forms)


def _governance_prefix_forms(raw_prefix: str, workspace_root: Path) -> set[str]:
    """Canonical AND lexical forms of a configured prefix. A prefix that is a
    symlink needs both: the canonical form matches writes that reach its target
    directory, the lexical form keeps matching spellings under the entry itself
    when the target escapes the workspace (`generated -> /mnt/generated`)."""
    return {
        relative_to_workspace(raw_prefix, workspace_root),
        normalize_path_text(raw_prefix),
    }


def _form_excluded(relative: str, governance: dict[str, Any], workspace_root: Path) -> bool:
    """Configured (settings.json) exclusions only — structural `.stage`/`.git`/
    `.discuss` prefixes are checked across all forms in is_source_path."""
    raw_exclude_paths = governance.get("exclude_paths")
    if isinstance(raw_exclude_paths, list):
        for raw_prefix in raw_exclude_paths:
            if any(
                path_has_prefix(relative, prefix)
                for prefix in _governance_prefix_forms(str(raw_prefix), workspace_root)
            ):
                return True
    suffix = Path(relative).suffix.lower()
    raw_exclude_extensions = governance.get("exclude_extensions")
    if isinstance(raw_exclude_extensions, list) and suffix in {
        str(ext).lower() for ext in raw_exclude_extensions
    }:
        return True
    return False


def _form_included(relative: str, governance: dict[str, Any], workspace_root: Path) -> bool:
    # Configured prefixes are canonicalized the same way as the target so a
    # symlinked `governance.paths` entry matches the resolved file.
    raw_paths = governance.get("paths")
    suffix = Path(relative).suffix.lower()
    raw_extensions = governance.get("extensions")
    ext_governed = isinstance(raw_extensions, list) and bool(raw_extensions)
    if isinstance(raw_paths, list) and raw_paths:
        for raw_prefix in raw_paths:
            if any(
                path_has_prefix(relative, prefix)
                for prefix in _governance_prefix_forms(str(raw_prefix), workspace_root)
            ):
                return True
        # Paths allowlist present: only listed paths (or listed extensions).
        return ext_governed and suffix in {str(ext).lower() for ext in raw_extensions}
    if ext_governed:
        return suffix in {str(ext).lower() for ext in raw_extensions}
    # Broad default: every non-excluded workspace file is governed.
    return True

"""Server ↔ Viewer schema parity — v0.16.6 (D-2026-05-12-I).

Asserts that, for every kind in the 15-way discriminated union, the
Pydantic class's field set is **identical** to the TypeScript
``XxxJson`` interface's field set in ``viewer/src/domain/{Kind}.ts``.

Closes the schema round-trip loop end-to-end: server-side wire format
(Pydantic ``model_fields``) ⟷ viewer-side wire format (TS
``XxxJson`` interface). Drift in either direction (server adds a
field but TS doesn't, TS renames but server doesn't, etc.) fails
this test with the kind name and the offending field set in the
message.

The TS interface is parsed by regex, not by a TS compiler, because
adding a TS-toolchain dependency to the Python test suite is far
heavier than the test's value. The interface form is stable
(post-v0.15 reset, every per-kind file follows the same template) —
if a future commit changes the interface idiom, this parser is the
brittle piece, and the failure will land here loudly enough to fix.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from plot_mcp.models import BaseNodeFields
from plot_mcp.schema_export import _ALL_KIND_CLASSES

_PLOT_ROOT = Path(__file__).resolve().parent.parent
_DOMAIN_DIR = _PLOT_ROOT / "viewer" / "src" / "domain"


def _snake_to_pascal(kind: str) -> str:
    """``core_value`` → ``CoreValue``; ``actor_ref`` → ``ActorRef``."""
    return "".join(part.capitalize() for part in kind.split("_"))


def _ts_path_for_kind(kind: str) -> Path:
    return _DOMAIN_DIR / f"{_snake_to_pascal(kind)}.ts"


# Match ``export interface XxxJson extends BaseFieldsJson { ... }``.
# Non-greedy body so we stop at the FIRST closing brace.
_INTERFACE_RE = re.compile(
    r"export\s+interface\s+\w+Json\s+extends\s+BaseFieldsJson\s*\{([^}]*)\}",
    re.DOTALL,
)

# Match a field declaration inside the interface body — capture the
# identifier on the left of the colon. Allow optional ``?`` for
# optional fields (none today, but future-proof).
_FIELD_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z_0-9]*)\??\s*:",
    re.MULTILINE,
)


def _ts_kind_fields(kind: str) -> set[str]:
    """Parse the per-kind TS file and return the field names declared
    on the ``XxxJson`` interface (kind-specific fields + ``kind``).
    Returns the field set extending BaseFieldsJson; the 13 base fields
    are added in by the caller."""
    path = _ts_path_for_kind(kind)
    if not path.is_file():
        raise FileNotFoundError(f"missing TS domain file for kind {kind}: {path}")
    src = path.read_text(encoding="utf-8")
    match = _INTERFACE_RE.search(src)
    if not match:
        raise AssertionError(
            f"could not find ``XxxJson extends BaseFieldsJson`` interface in {path}"
        )
    body = match.group(1)
    # Strip /* ... */ block comments + // line comments inside the body.
    body = re.sub(r"/\*[\s\S]*?\*/", "", body)
    body = "\n".join(re.sub(r"//.*$", "", line) for line in body.split("\n"))
    return set(_FIELD_RE.findall(body))


# Base fields declared in BaseNodeFields (Pydantic) and BaseFieldsJson (TS).
# Both layers are SSOTs in their language; this set is the intersection
# both must satisfy. The test asserts each side's claim matches this set.
_EXPECTED_BASE_FIELDS = {
    "id",
    "label",
    "x",
    "y",
    "width",
    "height",
    "color",
    "shape",
    "icon",
    # v0.26.0 (D-2026-05-25-A) — ``parent_id`` removed. Hierarchy
    # moved to directed edges (``SketchEdge.directed``).
    "collapsed",
    "is_root",
    "details_path",
    "owner",  # v0.16.12 (D-2026-05-12-O) — multi-user prep
    "version",  # v0.17.2 Phase 2 (D-2026-05-16-C) — per-node version
    "publish_baseline",  # v0.22.0 (D-2026-05-17-H) — publish dirty baseline
}


def test_base_fields_pydantic_matches_canonical_set() -> None:
    """``BaseNodeFields`` must declare exactly the canonical base set —
    any drift fails this anchor before the per-kind asserts run."""
    actual = set(BaseNodeFields.model_fields.keys())
    assert actual == _EXPECTED_BASE_FIELDS, (
        f"BaseNodeFields fields drifted: "
        f"missing={_EXPECTED_BASE_FIELDS - actual}, "
        f"extra={actual - _EXPECTED_BASE_FIELDS}"
    )


def test_base_fields_ts_matches_canonical_set() -> None:
    """``BaseFieldsJson`` interface in ``viewer/src/domain/BaseFields.ts``
    must declare exactly the canonical base set."""
    base_path = _DOMAIN_DIR / "BaseFields.ts"
    src = base_path.read_text(encoding="utf-8")
    # Match the BaseFieldsJson interface body (top-level interface, no extends).
    base_re = re.compile(
        r"export\s+interface\s+BaseFieldsJson\s*\{([^}]*)\}",
        re.DOTALL,
    )
    match = base_re.search(src)
    assert match is not None, f"BaseFieldsJson interface not found in {base_path}"
    body = re.sub(r"/\*[\s\S]*?\*/", "", match.group(1))
    body = "\n".join(re.sub(r"//.*$", "", line) for line in body.split("\n"))
    actual = set(_FIELD_RE.findall(body))
    assert actual == _EXPECTED_BASE_FIELDS, (
        f"BaseFieldsJson fields drifted: "
        f"missing={_EXPECTED_BASE_FIELDS - actual}, "
        f"extra={actual - _EXPECTED_BASE_FIELDS}"
    )


@pytest.mark.parametrize("kind", sorted(_ALL_KIND_CLASSES.keys()))
def test_per_kind_field_parity(kind: str) -> None:
    """For each of the 15 kinds, Pydantic ``model_fields.keys()`` must
    equal the TS ``XxxJson`` interface's field set (after extending
    BaseFieldsJson)."""
    cls = _ALL_KIND_CLASSES[kind]
    pydantic_fields = set(cls.model_fields.keys())

    # TS side: kind-specific fields from the interface body, PLUS the
    # 13 BaseFieldsJson fields the interface inherits from.
    ts_specific = _ts_kind_fields(kind)
    ts_fields = ts_specific | _EXPECTED_BASE_FIELDS

    missing_in_ts = pydantic_fields - ts_fields
    missing_in_pydantic = ts_fields - pydantic_fields

    assert pydantic_fields == ts_fields, (
        f"\nSchema drift for kind={kind!r}:\n"
        f"  Pydantic class: {cls.__name__}\n"
        f"  TS file:        {_ts_path_for_kind(kind).relative_to(_PLOT_ROOT)}\n"
        f"  Missing in TS:       {sorted(missing_in_ts)}\n"
        f"  Missing in Pydantic: {sorted(missing_in_pydantic)}\n"
        f"  Pydantic full set:   {sorted(pydantic_fields)}\n"
        f"  TS full set:         {sorted(ts_fields)}\n"
    )


def test_all_kinds_covered() -> None:
    """Sanity: the parametrised parity test runs exactly 15 times,
    matching the discriminated union size."""
    assert len(_ALL_KIND_CLASSES) == 15

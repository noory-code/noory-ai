"""Per-provider model catalogue parsing (D-2026-06-22-B).

The chat model selector is populated from each CLI's own live catalogue
instead of a hardcoded list (reverses D-2026-06-16-C for codex/gemini):

  * gemini → ``agy models`` plain-text lines (effort baked into the label,
    passed verbatim to ``--model``).
  * codex  → ``~/.codex/models_cache.json`` (``visibility == "list"`` and
    ``supported_in_api``).
  * claude → the CLI's own documented aliases (still static — claude
    publishes stable aliases, D-2026-06-16-C).
"""

from __future__ import annotations

from plot_mcp.chat_models import (
    CLAUDE_MODELS,
    ModelOption,
    list_models,
    parse_agy_models,
    parse_codex_models,
)


def test_parse_agy_models_one_option_per_nonempty_line() -> None:
    out = parse_agy_models(
        "Gemini 3.5 Flash (Medium)\nGemini 3.1 Pro (Low)\n\n  \nGemini 3 Flash\n"
    )
    # id == label: agy accepts the effort-laden label verbatim as --model.
    assert out == [
        ModelOption(id="Gemini 3.5 Flash (Medium)", label="Gemini 3.5 Flash (Medium)"),
        ModelOption(id="Gemini 3.1 Pro (Low)", label="Gemini 3.1 Pro (Low)"),
        ModelOption(id="Gemini 3 Flash", label="Gemini 3 Flash"),
    ]


def _codex_entry(
    slug: str, *, display: str | None = None, visibility: str = "list", api: bool = True
) -> dict[str, object]:
    entry: dict[str, object] = {"slug": slug, "visibility": visibility, "supported_in_api": api}
    if display is not None:
        entry["display_name"] = display
    return entry


def test_parse_codex_models_filters_to_listed_api_models() -> None:
    cache = {
        "models": [
            _codex_entry("gpt-5.5", display="GPT-5.5"),
            _codex_entry("gpt-5.4", display="GPT-5.4"),
            _codex_entry("internal", display="Internal", visibility="hidden"),
            _codex_entry("no-api", display="NoApi", api=False),
        ]
    }
    out = parse_codex_models(cache)
    assert [m.id for m in out] == ["gpt-5.5", "gpt-5.4"]
    assert out[0].label == "GPT-5.5"


def test_parse_codex_models_tolerates_malformed_entries() -> None:
    cache = {
        "models": [
            {"slug": "ok", "display_name": "OK", "visibility": "list", "supported_in_api": True},
            {"foo": "bar"},  # missing slug → skipped, not crashed on
            "not-a-dict",
        ]
    }
    assert [m.id for m in parse_codex_models(cache)] == ["ok"]


def test_parse_codex_models_label_falls_back_to_slug() -> None:
    cache = {"models": [{"slug": "gpt-x", "visibility": "list", "supported_in_api": True}]}
    out = parse_codex_models(cache)
    assert out == [ModelOption(id="gpt-x", label="gpt-x")]


def test_parse_codex_models_expands_reasoning_levels() -> None:
    # D-2026-06-22-C: a model with supported_reasoning_levels becomes one
    # combined entry per level — id "<slug>:<effort>", label "<display> (<Effort>)".
    cache = {
        "models": [
            {
                "slug": "gpt-5.5",
                "display_name": "GPT-5.5",
                "visibility": "list",
                "supported_in_api": True,
                "supported_reasoning_levels": [
                    {"effort": "low"},
                    {"effort": "high"},
                    {"effort": "xhigh"},
                ],
            }
        ]
    }
    out = parse_codex_models(cache)
    assert [m.id for m in out] == ["gpt-5.5:low", "gpt-5.5:high", "gpt-5.5:xhigh"]
    assert [m.label for m in out] == [
        "GPT-5.5 (Low)",
        "GPT-5.5 (High)",
        "GPT-5.5 (xHigh)",
    ]


def test_claude_models_are_the_documented_aliases() -> None:
    assert [m.id for m in CLAUDE_MODELS] == ["fable", "opus", "sonnet"]


def test_list_models_gemini_runs_agy_and_parses(tmp_path) -> None:
    calls: list[list[str]] = []

    def fake_runner(cmd: list[str]) -> str:
        calls.append(cmd)
        return "Gemini 3.5 Flash (Medium)\nGemini 3 Flash\n"

    out = list_models("gemini", agy_runner=fake_runner)
    assert calls == [["agy", "models"]]
    assert [m.id for m in out] == ["Gemini 3.5 Flash (Medium)", "Gemini 3 Flash"]


def test_list_models_codex_reads_cache(tmp_path) -> None:
    cache_file = tmp_path / "models_cache.json"
    cache_file.write_text(
        '{"models": [{"slug": "gpt-5.5", "display_name": "GPT-5.5",'
        ' "visibility": "list", "supported_in_api": true}]}',
        encoding="utf-8",
    )
    out = list_models("codex", codex_cache_path=cache_file)
    assert [m.id for m in out] == ["gpt-5.5"]


def test_list_models_codex_missing_cache_returns_empty(tmp_path) -> None:
    out = list_models("codex", codex_cache_path=tmp_path / "nope.json")
    assert out == []


def test_list_models_gemini_runner_failure_returns_empty() -> None:
    def boom(cmd: list[str]) -> str:
        raise FileNotFoundError("agy not found")

    assert list_models("gemini", agy_runner=boom) == []


def test_list_models_claude_is_static() -> None:
    assert list_models("claude-code") == CLAUDE_MODELS

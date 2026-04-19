# Changelog

All notable changes to solera-map are recorded here.

## [0.1.0] — 2026-04-19

### Added

- **Service canvas** — fourth tab (left of Plan), upstream of Plan. Renders Personas, Journeys, and Narratives in a three-column swimlane layout: Persona cards on the left, Journeys in the middle (grouped by `walks` Persona), Narratives on the right (anchored to their `in_journey` Journey or to a Persona via `about`). "Loose Narratives" (no `in_journey`) cluster in a tray below.
- **`POST /api/concept/propose-from-narrative`** endpoint creates a stub Concept from a Narrative. The new Concept's `# Intent` is explicitly flagged `"needs human review per solera-write-concept Moment 1 rule"` and the human must run `solera-write-concept update` to fill it. Preserves the Moment 1 collaboration constraint while surfacing the canvas ergonomics.
- **Pydantic models for v4 Living-axis entities**: `Persona`, `Journey` (with `JourneyStep` table parsing), `Narrative` (with `NarrativeForm = "user_story" | "jtbd" | "scenario"`). All read from `.solera/personas/`, `.solera/journeys/`, `.solera/narratives/`. The `Graph` model gains corresponding arrays.
- **SidePanel bodies** for Persona, Journey, and Narrative selections, including the **"Propose as Concept"** modal (with kebab-case-validated `concept_id` + human-readable `concept_name` inputs) on every Narrative.
- **Lens-routed canvas switch** in `App.tsx` — `service` routes to the new `ServiceCanvas`; `plan`/`build`/`live` continue to route to `PlanCanvas` with their existing lens-driven styling. The `WorkspaceLens` type union becomes `"service" | "plan" | "build" | "live"`.
- **`SOLERA_MAP_NO_MCP=1` env var** — skips the MCP stdio task during `_serve()`. Used by the new `solera-map` VSCode extension to spawn the server in HTTP-only mode.

### Changed

- **`resolve_workspace` → `resolve_solera_root`** — looks for `.solera/` first (Solera v4), falls back to `workspace/` (Solera v3) with a deprecation warning, then to the bare directory. The `resolve_workspace` name remains as a deprecated alias for one minor version. **v0.2.0 will drop the `workspace/` fallback** — projects must run `solera-migrate-workspace-to-dotsolera` (Solera v4) before then.
- File watcher tracks the new entity files automatically (the existing `*.md` glob already covers them); module docstring updated to reflect the new Living-axis entries.
- README updated to "four canvases" (Service / Plan / Build / Live) and to point at `.solera/` as the data root.

### Tests

- 18 new tests covering Persona / Journey / Narrative readers, the Steps table parser, frontmatter form fallback, `resolve_solera_root` priority + backward-compat warning, and the full happy/error paths of `propose-from-narrative`.

### Notes

- Requires **Solera v4.0+** to populate Personas/Journeys/Narratives (those are produced by the new `solera-write-persona` / `solera-write-journey` / `solera-write-narrative` skills). Older Solera v3.x projects still render correctly — the Service tab simply shows an empty "no service drawings yet" state.
- The canvas's "Propose as Concept" action **never auto-finalizes a Concept**. The stub it writes is intentionally minimal; running `solera-write-concept update` against the new id is required to fill the real Intent.

---

## [0.0.1] - 2026-04-18

### Added
- Package scaffold (pyproject.toml, plugin manifest, source layout)
- Placeholder `solera_map.server.run` entry point
- `/map` slash command stub
- README and changelog

No functional features yet — implementation begins with Tier 1 per the agreed plan.

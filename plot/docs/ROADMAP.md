# Plot Roadmap

The implementation order for the major release lines. Each step is
an independent, ship-ready commit (Python green, viewer green, plugin
patch bumped, pushed). Together they realise the design captured in
[`VISION.md`](VISION.md), [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md),
[`IDENTITY.md`](IDENTITY.md) and [`CONCEPTS.md`](CONCEPTS.md).

> Status legend: `[ ]` not started · `[~]` in progress · `[x]` shipped.

---

## v0.17+ — Roadmap items (queued, design red-team findings inline)

The three items below were surfaced from
``memory/project_plot_next_session.md`` 's parked backlog after
the v0.15 / v0.16 cycle wrapped. Each has been **adversarially
reviewed via the ``plot-design-red-team`` skill** (D-2026-05-12-K)
before being parked here, so future implementers walk in with the
unresolved questions named.

Pick order intent: **A → B**, then **C** as a separate
product-decision lane. Do not begin A without re-entering plan
mode; each Major / Critical finding below needs an answer in
``DECISIONS.md`` first.

---

### A) isomorphic-git source-data version control  `[ ]`

**Spec mandate (canonical Plot spec §"원천 데이터 버전 관리 (git)"):**
> "캔버스 변경 시 자동 커밋 / 스냅샷 = 커밋 / 에이전트 변경 제안
> = 브랜치 생성 / 사람 승인 = 머지 / 사람 거절 = 브랜치 삭제 /
> 사용자는 git 을 몰라도 되고, 내부적으로 이력이 쌓임 / 나중에
> GitHub 연동 가능성 열어둠"

**Why it matters:** the spec makes git the *retention mechanism* for
the human↔AI co-draw loop. Without it, the "agent proposes / human
merges" workflow has no substrate.

**Design red-team verdict: 🟡 REVISE FIRST.** 6 Major findings need
resolution in ``DECISIONS.md`` before any code:

1. **Major (A2) — UI vocabulary for accept/reject.** Spec says
   "사용자는 git 을 몰라도 되고" — but the user clicks something.
   Decision needed: surfaces as ``Approve / Reject``? ``Apply / Discard``?
   ``Accept / Decline``? Each conveys a different mental model. Pick
   one + pin.

2. **Major (A2) — ``.git/`` location.** Per-project (one repo per
   ``.plot/{project_id}/``) vs per-workspace (one repo at the
   ``.plot/`` root containing all projects) vs per-canvas. Affects
   blast radius of a corrupted index. **Recommend per-project**
   (matches PRODUCT_SPEC §5 "JSON is SSOT" granularity) but pin
   the call first.

3. **Major (A2) — agent commit identity.** Agent commits via
   ``committer=agent@plot``? Or ``committer=<user>`` with
   ``Co-authored-by: agent`` trailer? Determines how ``git log``
   reads from outside Plot if GitHub sync ever lands.

4. **Major (A3) — conflict resolution UX.** User edits Mission;
   agent simultaneously proposes Mission edit. Both diverge from
   the same base. Auto-merge fails. What does the *non-git* user
   see? Decision: "show side-by-side diff and ask user to pick",
   OR "agent's branch fails; agent must re-propose against new
   base"? Spec is silent.

5. **Major (A4) — commit granularity.** Per-mutation (every
   keystroke a commit)? Debounced (e.g. 5-sec idle)? Session-end?
   Per-mutation gives perfect undo but enormous history; session-end
   loses fine-grained recovery. Recommend **debounced (idle 3-5 sec)**
   but pin.

6. **Major (A8) — MVP scope cut.** Risk: implementing full
   git-as-product (diff viewer / blame / log search / GitHub
   OAuth / merge conflict 3-way editor). Cut to Phase 1 MVP:
   auto-commit + agent-branch + accept-as-merge + reject-as-delete
   + flat history list. Defer the rest to later sub-phases.

Minor findings (non-blocking but pin if decided):
- (A3) Multi-tab same-project race conditions — likely
  per-tab-locked.
- (A3) 10k-node canvas commit perf — measure when fixture exists.
- (A6) snapshot-as-context-injection feature (per spec
  §"일감 레이어") needs flat history list as Phase 1 dep.

**Architecture sketch (after the 6 majors land in DECISIONS):**
- New ``plot/plot_mcp/git_store/`` module wrapping isomorphic-git's
  Python equivalent OR (preferred) running isomorphic-git
  *client-side* and treating the MCP server as a passthrough.
- New 3-4 MCP tools: ``snapshot_create`` / ``branch_open`` /
  ``branch_merge`` / ``branch_discard``.
- Viewer surfaces a "Change proposals" panel in the SketchSidebar
  showing pending agent branches; click → preview → accept / reject.
- New static guards in ``structural-guards.test.tsx``: enforce that
  no canvas write bypasses the git_store wrapper.

**Expected sizing:** 2-4 weeks of focused work; 8-12 commits. Each
commit must keep viewer 383+ + server 274+ green.

---

### B) Work-item layer (userstory + task)  `[ ]`

**Spec mandate (canonical Plot spec §"일감 레이어 (시간적)"):**
> "서비스 인터뷰 → 유저스토리 초안 동시 생성 / 유저스토리 → 태스크로
> 파생 / 태스크는 출처 메타데이터 보유 / 스냅샷 = git 커밋, 작업
> 시작 시점 기준으로 에이전트에 컨텍스트 주입"

**Why it matters:** canvas is *spatial* (what the project is);
work-item layer is *temporal* (what we're doing about it). Bridges
plan → execution.

**Hard dependency on A** (snapshot context = git commit reference).

**Design red-team verdict: 🟡 REVISE FIRST.** 4 Major findings:

1. **Major (A2) — work-item file locations.** New file types: where?
   - Option α: ``.plot/{project}/userstories/{id}.json`` +
     ``.plot/{project}/tasks/{id}.json`` (parallel data plane).
   - Option β: new ``userstory`` + ``task`` kinds inside the canvas
     (so they appear AS nodes). Would extend the 15-way union to
     17 — breaks the structural-guards 15-kind invariant unless
     loosened.
   - Recommend **Option α** (separate data plane) — keeps the
     canvas spatial / work-items temporal split clean. Pin first.

2. **Major (A2) — origin-metadata schema.** ``출처 메타데이터`` =
   what? Recommend:
   ```
   origin: {
     service_id: string;
     actor_ref_ids: string[];
     interview_session_id: string;
     snapshot_sha: string;   // from A)
   }
   ```
   Pin before any class lands.

3. **Major (A3) — orphan handling.** Service node deleted → linked
   userstories become orphans. Decision: cascade-delete? Mark
   ``orphan: true`` and keep visible? Detach (clear origin pointer)?
   Each has UX implications for "I deleted the service but I want
   to keep the work I already did."

4. **Major (A6) — MVP schema for userstory / task.** Risk: full
   Jira-style fields (priority / estimate / sprint / assignee /
   comments / attachments / …). Cut to Phase 1: ``title``,
   ``story_text`` (markdown), ``origin``, ``status`` (free string,
   not enum, until usage patterns clarify), ``owner`` (re-uses
   ``BaseNodeFields.owner`` shape from D-2026-05-12-P).

Minor findings:
- (A3) Interview session re-runs producing duplicate userstories
  — dedupe key needed.
- (A7) Tasks linked to ``snapshot_sha`` that gets git-reset out
  of existence — dangling-reference handling (warn or auto-clean).

**Architecture sketch:**
- New ``viewer/src/domain/workitem/`` directory mirroring the
  ``viewer/src/domain/`` per-kind structure but for work-items.
  Pydantic equivalent under ``plot_mcp/workitem_models.py``.
- New MCP tools: ``create_userstory_draft`` (from service
  interview), ``derive_tasks`` (from userstory), ``snapshot_attach``
  (tie a task to a commit).
- Viewer: new "Work" tab or panel — separate from the 4 canvases.

**Expected sizing:** 1-2 weeks after A lands.

---

### C) Plot repository split  `[ ]`

**Spec mandate:** none directly. Filed in
``memory/project_plot_next_session.md`` as "AI recommends; user
decision pending."

**Design red-team verdict: 🟢 READY** — mechanically simple; the
question is **product**, not technical.

The decision the user owns:
- **Split (Plot moves to ``github.com/noory-code/plot``):** cleaner
  contributor surface; Plot has its own issues / PRs / release cadence;
  easier to license and distribute independently; users install via
  plugin marketplace with a stable repo URL.
- **Stay (Plot remains in ``noory-ai`` monorepo):** shared CI infra,
  shared marketplace listing logic; no migration cost; the other 4
  plugins benefit from monorepo synergy.

No code-side findings — when the user picks, the split is a one-time
``git filter-repo`` + readme reshuffle.

**Migration trap (Minor):** existing plugin users have manifests
pointing at ``noory-ai/plot`` — a split breaks their install path
unless we leave a stub redirect in the monorepo. Pin a
``noory-ai/plot/MOVED.md`` if/when the split happens.

---

### D) Forest-anchored AI context (graph-RAG-lite + verification loop)  `[ ]`

**Spec mandate:** none yet — surfaced in the 2026-05-16 ideation
session (see [D-2026-05-16-D](./DECISIONS.md)). Frames the
"tree-in-forest" problem: the AI implements a feature's spec
faithfully but misses the surrounding Identity / tone / sibling-
service coherence that the canvas already captures.

**Why it matters:** Plot's essence ([`VISION.md`](./VISION.md))
hinges on AI work staying anchored to the discovered essence.
Without explicit forest-injection mechanics, Retention (Phase 2) and
Execution (Phase 3) drift apart — the canvas captures intent the
agent does not actually use.

**Three-layer framing (per [D-2026-05-16-D](./DECISIONS.md)):**

| Layer | Question | Cost |
|---|---|---|
| Data structural connection | Is the forest representable as a graph? | **Free** — Plot's typed user-authored graph already is one; the GraphRAG entity-extraction step is zero |
| Input side / call enforcement | Does the AI pull forest data when starting work? | **Small** — `context_envelope` MCP tool + skill rule + interview-pattern strengthening |
| Output side / verification | Did the AI's output actually reflect the forest? | **Large** — needs a verification loop (human PR review today; automated later via Evonest port) |

**Phase plan:**

- **Phase 1 (near-term, Plot-internal only)** — `context_envelope(node_id)`
  MCP tool returning ancestor chain + Symbol resolves (Identity) +
  N-hop neighbours. Skill rule: the agent must call it before
  starting work on a node. Interview pattern
  ([`PRODUCT_SPEC.md` §9](./PRODUCT_SPEC.md)) surfaces the envelope
  result as the interview's opening context. Sizing: days. No new
  deps; no embedding / vector DB.
- **Phase 2 (post Distill port)** — crystallize accumulated
  interview transcripts + decision log into implicit Identity /
  tone signals. Reuses the existing Distill ``fastembed`` +
  ``sqlite-vec`` stack (same monorepo).
- **Phase 3 (post Evonest port)** — automated forest-consistency
  check on agent output (LLM-as-judge against Identity tone +
  Mission alignment + sibling-service contradictions). Sits at the
  PR-style merge gate ([`PRODUCT_SPEC.md` §11](./PRODUCT_SPEC.md)).

**Design red-team verdict:** not yet run. Before Phase 1 starts,
re-enter plan mode and run ``plot-design-red-team`` to surface at
minimum:

- envelope size / token budget tradeoffs (how many hops, how much
  typed text before token cost dominates),
- failure mode when the agent skips the tool call (does any guard
  detect "agent shipped diff without calling envelope"?),
- staleness of cached envelopes when the canvas updates mid-task
  (snapshot-pinning interaction with item A).

**Dependency direction:** Phase 1 has **no hard dependency** on
items A / B / C. Phases 2 / 3 depend on the future Distill /
Evonest ports (currently sibling packages in the monorepo, not
Plot features).

**Expected sizing:** Phase 1 = days; Phases 2 / 3 are downstream of
Distill / Evonest porting and not standalone-sized here.

---

## v0.10 / v0.11 history (shipped)



## v0.11 — Actor / Service redefinition  `[x]` (all four phases shipped 2026-04-30)

| Phase | Decision | Ship |
|---|---|---|
| **A** Actor model | class of people, side ∈ {operator, user}, motivation/pain typed fields, ≥ 2 actors per project, ≥ 2 actor_refs per service | v0.10.7 docs + v0.11.0 |
| **B** Ref orphan UX | foundation refs join actor_ref's orphan UI; ref labels auto-sync from masters | v0.11.1 |
| **C** Service polish | services-canvas anchor hard validator; actor_ref `gives` / `receives` value-flow fields | v0.11.2 |
| **D** Compatibility | time-axis (Mode 2) compatibility verified; v0.11 closes; infrastructure deferred to Mode 2 | (no code) |

Discussion log: `~/.claude/plans/ancient-pondering-petal.md`.

---

## v0.10 — Kind redefinition  `[x]` (shipped 2026-04-28)

## Step 1 — Foundation rename + Mission typed fields  `[x]`

The smallest contained change, so it can land before anything else.

**Python**
- `CanvasKind` literal: rename `"core"` → `"foundation"`.
- `_ALLOWED_KINDS_BY_CANVAS["core"]` → `_ALLOWED_KINDS_BY_CANVAS["foundation"]`.
- `_core_canvas_rules` → `_foundation_canvas_rules` (function name, error
  messages, comparisons).
- `folder_io._canvas_file` already uses `canvas_kind` directly, so renaming
  flows through the disk path automatically (`.plot/{id}/foundation/canvas.json`).
- `migrate.upgrade_core_canvas_if_needed` — extend the early-version
  upgrader to also rename `core/canvas.json` → `foundation/canvas.json`
  on read (idempotent), so v0.9 disk layouts still open in v0.10.
- `SketchNode` typed fields:
  - `what_we_do: str = ""`
  - `why: str = ""`
  - `direction: str = ""`

**Viewer**
- `CanvasKind` / `CanvasKey` types: `"core"` → `"foundation"`.
- Tab labels and slugs follow.
- Inspector renders the three Mission fields when `kind === "mission"`.

**Tests**
- Update fixtures in `test_canvas_doc.py`, `test_folder_io.py`, etc., to
  the `foundation` kind name.
- Add a test that `mission` nodes round-trip with the typed fields.

**Verification**: `pytest -q`, `ruff`, `mypy`, `tsc --noEmit` clean.

## Step 2 — Core Value + Identity typed fields  `[x]`

**Python**
- `SketchNode`:
  - `definition: str = ""` (core_value)
  - `description: str = ""` (identity)
  - `do: str = ""` (shared)
  - `dont: str = ""` (shared)

**Viewer**
- Inspector form maps:
  - `core_value` → label · definition · do · dont
  - `identity` → label · description · do · dont

**Tests**: round-trip + Inspector field rendering.

## Step 3 — Reference kinds (mission_ref / value_ref / identity_ref)  `[x]`

Generalise the existing `actor_ref` symbol pattern to Foundation.

**Python**
- `NodeKind` literal: add `"mission_ref"`, `"value_ref"`, `"identity_ref"`.
- `SketchNode`: add `ref_mission_id`, `ref_value_id`, `ref_identity_id`
  (all `str | None = None`); pre-existing `ref_actor_id` stays.
- `_ALLOWED_KINDS_BY_CANVAS`:
  - `"services"` and `"service_detail"` accept all four ref kinds.
- Validators:
  - Each `*_ref` requires its corresponding `ref_*_id` set.
  - On canvas write, optionally check the referenced master exists in
    the Foundation canvas (warn, don't reject — orphans are useful
    while drafting).

**Viewer**
- Stencil: add Mission ref / Value ref / Identity ref draggables to the
  Services and Service-Detail stencils.
- Each ref kind gets a distinct shape/colour/icon.
- Picker modal (similar to ActorRefPicker) for the master to point at.

**Tests**: validator coverage, picker round-trip.

## Step 4 — Service typed fields (top vs sub)  `[x]`

**Python**
- `SketchNode`: add service-relevant typed fields.
  - Shared: `what`, `value_created`, `scope`, `do`, `dont`.
  - Sub-only (the model just allows them; Inspector decides surfacing):
    `trigger`, `how`, `outcome`.
- Validator (services canvas): each top-level service has either an
  `identity_ref` or a `value_ref` placed near it (as a sibling node)
  OR a non-empty `value_created` field. Exact gating TBD during impl.

**Viewer**
- Inspector branches by canvas:
  - Service on `services` canvas → top-level field set + required
    Foundation ref hint.
  - Service inside a `service_detail` canvas → sub-service field set,
    all optional.

**Tests**: top vs sub field round-trip, Foundation-ref validator.

## Step 5 — New composition kinds (metric, step)  `[x]`

**Python**
- `NodeKind`: add `"metric"`, `"step"`.
- `_ALLOWED_KINDS_BY_CANVAS["service_detail"]` includes both.
- `SketchNode` typed fields:
  - `target: str = ""` (metric)
  - `measurement: str = ""` (metric)
  - `order: int | None = None` (step)
  - `outcome: str = ""` — already added in Step 4 for service, shared
    semantically with step.

**Viewer**
- Stencil: add Metric / Step draggables to the Service-Detail stencil.
- Inspector renders kind-specific forms.

**Tests**: round-trip + visual stencil load.

## Step 6 — rule / content typed-field polish  `[x]`

The composition kinds that already exist gain richer typed fields.

**Python**
- `SketchNode`:
  - `policy: str = ""` (rule)
  - `enforcement: str = ""` (rule)
  - `actor_permissions: dict[str, str] = {}` (rule, keyed by actor id;
    value is e.g. "RUD") — schema TBD when implementing.
  - `format: str = ""` (content)
  - `producer_actor_id: str | None = None` (content)
  - `consumer_actor_id: str | None = None` (content)

**Viewer**
- Inspector forms for `rule` and `content` kinds.
- For permissions, show a small actor × CRUD matrix UI keyed by the
  actor_refs already on the canvas.

**Tests**: round-trip + permission matrix serialisation.

---

## Cross-cutting items (apply to all steps)

- Each step ends with: ruff + mypy + pytest + tsc all green.
- Each step bumps `plugin.json` and adds a `CHANGELOG.md` entry.
- `details.md` per node continues to behave exactly as in v0.9.1 — no
  changes there.
- The watcher and broadcast layers don't need changes; new typed fields
  ride along on existing canvas write paths.

## Out of scope for v0.10

- The "edge utilisation strategy" — keep the existing `action_verb` /
  `value_form` edge metadata as-is; revisit only after the kind
  redefinition is shipped.
- The future task / time-axis layer — Plot keeps room for it (the
  service model doesn't preclude a `delivery_status` typed field
  later) but no work in v0.10.
- Renaming `core_value` to a shorter name — kept as `core_value` per
  user direction in the kind review.

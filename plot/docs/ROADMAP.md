# Plot Roadmap

The implementation order for the major release lines. Each step is
an independent, ship-ready commit (Python green, viewer green, plugin
patch bumped, pushed). Together they realise the design captured in
[`VISION.md`](VISION.md), [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md),
[`IDENTITY.md`](IDENTITY.md) and [`CONCEPTS.md`](CONCEPTS.md).

> Status legend: `[ ]` not started · `[~]` in progress · `[x]` shipped.

---

## v0.17+ — Roadmap items (queued, design red-team findings inline)

The items below were surfaced from
``memory/project_plot_next_session.md`` 's parked backlog after
the v0.15 / v0.16 cycle wrapped. Each has been **adversarially
reviewed via the ``plot-design-red-team`` skill** (D-2026-05-12-K)
before being parked here, so future implementers walk in with the
unresolved questions named.

Pick order intent: **A → B**, then **C** as a separate
product-decision lane. Do not begin A without re-entering plan
mode; each Major / Critical finding below needs an answer in
``DECISIONS.md`` first.

### Deferred (RF 기본 동작 rollback, v0.16.20-23)

User directly requested "RF 기본 동작" rollback after v0.16.15-19's
code-audit fixes did not address user-felt regressions. The
following canonical Plot spec mandates were **deferred** — code is
gone from disk; re-introduction requires fresh plan-mode + explicit
user approval.

| Deferred mandate | Last decision before revert | Revert decision |
|---|---|---|
| **Synthetic project anchor at canvas centre** (spec §"미션/코어밸류/아이덴티티 캔버스" + "프로젝트 노드 가운데") | D-2026-05-04-B/C, D-2026-05-12-Q, -U | D-2026-05-12-X (v0.16.22) |
| **Anchor-radial M/CV/Id auto-placement** (spec "주변에 붙임. 뭐가 먼저고 말고는 없습니다") | D-2026-05-12-N, -O | D-2026-05-12-W (v0.16.21) |
| **Self-loop visual rendering** (spec "셀프 피드백 루프 표현 가능") | D-2026-05-12-M | D-2026-05-12-V (v0.16.20) |

If a future session decides to re-introduce these, the
implementations + tests are recoverable from git history
(commits 2487ba6 / 7edbbf8 / 75ee0b0 / 0713343 / aa385a0). Don't
copy-paste — re-derive from current architecture state and the
canonical spec, with hands-on validation in the user's actual
browser before claiming "done".

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

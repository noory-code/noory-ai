# Node Data Format & Artifact Management — PLAN

> **Status:** PLANNING ONLY — nothing here is implemented yet. Filed
> 2026-06-04 at the user's request (*"각 노드들에 묶여있는 데이터들
> 형식(문서 형식) 과 산출물 관리(버저닝 포함) … 계획 잡아두고 문서
> 만들어두세요. 다음세션에서 이어가야하니까"*). The next session continues
> from §3 (open decisions) → §5 (phased plan).
>
> **Read first:** [`SPEC.md` §Publish](./SPEC.md#publish-v0180),
> [`PUBLISH.md`](./PUBLISH.md), [`CONCEPTS.md`](./CONCEPTS.md) (typed
> fields per kind), [`DECISIONS.md`] D-2026-05-16-E (per-node publish),
> D-2026-05-21-B (blueprint versioning).
>
> **Scope = two coupled concerns the user named:**
> 1. **Node document format** — the data/document bound to each node.
> 2. **Artifact (산출물) management + versioning** — what Plot produces as
>    a deliverable and how it is versioned.

---

## 1. Current state (verified against the BANAS sim, 2026-06-04)

### 1.1 How node data is stored *today*

- **Typed fields, inline in the canvas JSON.** Each node carries its
  per-kind fields directly in `<canvas>/canvas.json` (or
  `services/<id>/detail.json`). There is **no per-node `.md` file in the
  working tree** — the v0.13 "JSON+MD split (Foundation only)" is **not**
  present in live data; typed text lives inline. Examples:
  - `mission` → `what_we_do`, `why`, `direction`, `body`
  - `core_value` → `definition`, `do`, `dont`, `body`
  - `identity` → `description`, `do`, `dont`, `body`
  - `service` → `what`, `value_created`, `scope`, `trigger`, `how`,
    `outcome`, `do`, `dont`, `body`, `target_side`
  - `step` → `order`, `outcome`, `body`, `polarity`
  - `decision` → `body`; `actor` → `motivation`/`pain`/`side`/`body`; etc.
- **`body`** is a **free-markdown** field present on most kinds. It IS used
  (e.g. the BANAS mission node's `body` holds a "## 미션 한 줄 …" block) but
  has **no defined structure or convention** — it's whatever was typed.
- **`details_path`** field exists on every node, **largely unused** (null
  in the sim). Intended as a pointer to an external detail doc.
- **`schema/{kind}.json`** — a per-project **snapshot** of each kind's JSON
  Schema (generated from the server Pydantic models). In the sim it reads
  `schema_version: 2, plot_version: 0.14.18` — i.e. **STALE** (current Plot
  is 0.40.5). The snapshot is not regenerated on Plot upgrades.
- **`schema/{kind}.md.template`** — publish-output templates. **Only 3 of
  15 kinds** have one (`mission`, `core_value`, `identity`). Format =
  `# {label}` + one `## Heading` per typed field (with an
  `<!-- kind.field -->` marker) + a `---` rule + free prose below.

### 1.2 Versioning + artifacts *today*

- **Per-node version** — `version` ("v1.0") + `_publish_baseline` on every
  node.
- **Per-node publish** (D-2026-05-16-E, [`PUBLISH.md`](./PUBLISH.md)):
  the 📤 button bumps the node's **MAJOR**, renders
  `<canvas>/published/{kind}-{slug}-{version}.md` (YAML frontmatter +
  `## heading` per typed field), writes the bumped `canvas.json`, and
  records a git commit with 5 `Publish-*:` trailers. `propagation.py`
  does a **MINOR** bump up the ancestor chain via the edge `relation`.
- **Blueprint version** — `project.json.blueprint_version` (semver, e.g.
  `v0.1.0`) + the **설계도 발행** header button (major/minor/patch),
  D-2026-05-21-B. Tags the project at that point.
- **`project.json.version`** — a separate **integer** (`3` in the sim) =
  internal doc/migration counter, **not** the blueprint semver.

### 1.3 Relationship to the source-of-truth docs

- The BANAS *content* SSOT lives **outside** Plot:
  `project-noory/banas/workspace/{identity,concepts,catalog}`. Plot nodes
  were populated *from* those docs by hand. There is **no stored link**
  from a node back to its source doc.

---

## 2. Gaps / problems to solve

### Node document format
- **G1.** `body` has no convention — free text, no schema, no guidance on
  what belongs in `body` vs a typed field. Inconsistent across the sim.
- **G2.** md templates exist for only 3/15 kinds → publish output is
  uneven; `step` / `service` / `decision` / `actor` etc. have no template.
- **G3.** No SSOT policy for **long-form** content: inline JSON `body` vs a
  separate `.md` file (the v0.13 split) vs `details_path`. Three half-built
  mechanisms, none authoritative.
- **G4.** No node→source-doc link (G1.3). Re-syncing a node when the
  source concept/journey changes is manual and lossy.
- **G5.** `schema/*.json` snapshot is stale + per-project; unclear who
  regenerates it or whether the viewer/MCP even reads it at runtime.

### Artifact / versioning
- **G6.** **Two version axes** (per-node `version` vs `blueprint_version`)
  with **no defined relationship**. When the blueprint is published, are
  node versions snapshotted? Frozen? Ignored?
- **G7.** **"산출물" is undefined.** Candidates: (a) the per-node
  `published/*.md` files, (b) a bundled per-canvas doc, (c) a single
  exported blueprint document/site, (d) the git tag itself. The user's
  intent ("산출물 관리") needs a concrete definition before tooling.
- **G8.** **No export / handoff format** — there is no "produce the
  deliverable" step that turns the design into something handed to a
  developer / stakeholder (PRD, spec bundle, static site, …).
- **G9.** Versioning **granularity** is ambiguous: node / canvas / project
  each can version independently; no rule for which moves when.

---

## 3. Open decisions — RESOLVE THESE NEXT SESSION (with the user)

> Each is a real fork. Recommended option marked **(R)** with its reason.
> Do not implement before the user picks.

- **Q1 — What is `body` for?**
  - (a) **(R)** `body` = free human narrative (markdown); typed fields stay
    the structured/machine layer. *Reason: matches current usage + keeps
    the two-layer split (structured vs prose) the publish md already
    assumes.* → then we just need a *convention/guide*, not a schema.
  - (b) Give `body` a structured sub-format (sections). *Heavier; risks
    re-inventing typed fields.*
  - (c) Drop `body`; everything becomes a typed field. *Loses free prose.*

- **Q2 — Where does long-form content live (SSOT)?**
  - (a) **(R)** Inline in canvas JSON stays the SSOT; `.md` is **publish
    output only**. *Reason: one SSOT, no sync problem; the v0.13 split was
    never finished and the sim proves inline works.*
  - (b) Re-introduce a per-node `.md` working file (revive the v0.13
    split). *Two-file sync burden; needs a strong reason.*
  - (c) Use `details_path` to link a node to an external long doc.

- **Q3 — Extend md.template to all 15 kinds?** (R) **Yes** — uniform
  publish output. Blocked-by nothing; mechanical once Q1/Q2 are fixed.

- **Q4 — Node ↔ source-doc link?**
  - (a) store a `source_ref` (path/URL) per node; (b) **(R)** keep source
    linkage in the node `body` as a markdown link + a "source" line
    (no schema change, YAGNI); (c) none.

- **Q5 — How do node version and `blueprint_version` relate?**
  - (a) **(R)** Independent axes; a **blueprint publish snapshots** the
    current node versions into the tag/manifest (read-only record).
    *Reason: lets components evolve continuously while a blueprint release
    is a frozen cross-section.* (b) Blueprint publish force-bumps all nodes.
    (c) Only one axis (drop per-node publish).

- **Q6 — What IS the deliverable (산출물)?** *(the load-bearing decision)*
  - (a) the `published/*.md` set; (b) a **bundled blueprint
    document** generated at 설계도 발행 (one navigable doc/site assembled
    from all canvases + published nodes, stamped with `blueprint_version`);
    (c) a machine export (JSON bundle) for downstream tooling.
  - **→ Reframed by the recovered user intent — see §3.1 below.** The
    format (a/b/c) is the *container*; the user already defined the
    *content*. Resolve §3.1 first, then pick the container.

### 3.1 Q6 — recovered user intent + draft (2026-06-04)

> Recovered from the 2026-05-30 ServiceDetail 산출물 discussion
> (transcript `3ab5003d`, 02:44–03:17). The user said they had explained
> this once already; this is that explanation, reconstructed.

**What the user said the deliverable is — and is NOT:**

- **NOT** the screens / UI / mockups. *"각 스텝에 해당하는 화면이나
  이런게 있을 건데 그건 표현하지는 않을거에요."* Plot does not draw the UI.
- The deliverable is the **value story of the designed service** — two
  distinct value relations the user explicitly separated:
  - **체현 (embodies)** — what value the service / each step *has*:
    the mission / core_value / tone&manner it carries, and **how that
    foundation "발동(activates)" at each point of the flow**. *"우리가
    정한 미션과 코어밸류, 톤앤매너가 서비스 설계에서 어떻게 발동하는가를
    보여주고 싶은거에요."*
  - **산출 (produces)** — what value the produced **result** *makes*:
    *"만들어진 산출물이 어떤 가치를 지니는지, 만들어진 결과가 어떤
    가치를 지니는지 표시."* (e.g. Login's result = 대시보드 진입 → the
    value/purpose that service delivered.)
- The **flow must carry both positive and negative cases** (login
  success *and* failure paths, reasoned failures vs plain failure), and
  branch / 결정 points render as flowchart **decision diamonds (◇)**.

**What is already SHIPPED (the in-canvas half of this intent):**

- 발동 → **injection edges** (foundation ref → flow node, animated
  violet, v0.28.1).
- 결정 분기 → **`decision` kind** (◇, v0.28.0).
- 네거티브 케이스 → **`step.polarity`** (red/green) + result nodes
  (v0.28.2).
- 산출되는 가치 (instance) → **`metric`** node ("VALUES" stencil).

So the *design surface* already expresses 체현·발동·산출·네거티브. The
**open part is the OUTPUT** — when 설계도 발행 runs, does this rich
flowchart come OUT as a useful value-centric deliverable? (Flagged
unverified in NEXT_SESSION "산출물 검토".)

**Draft definition (to confirm with user):**

> **The deliverable = a per-service "value sheet" assembled at 설계도
> 발행.** For each service, the bundle states: (1) **purpose** + the
> **value it produces** (산출, from `metric` / result nodes); (2) the
> **foundation it embodies** (체현) and **where that foundation
> activates** along the flow (체현·발동, from injection edges); (3) the
> **flow itself** — steps, decisions (◇), positive + negative results;
> (4) per-step / per-service **tone&manner + core_value** where defined
> (optional). Container = the bundled blueprint document (Q6b) stamped
> with `blueprint_version`; the **content schema is this value sheet**,
> not a flat field dump. The existing per-node `published/*.md` are the
> raw material; the bundler composes them into the value story.

**Open sub-questions for the review session:**
- Is the deliverable **per-service** (one value sheet each) or **one
  blueprint-wide** document with a service section each? (lean: both —
  per-service sheets + a blueprint index.)
- Does the value sheet need a **visual** (rendered flowchart image) or
  is **structured text** (flow as an outline + injection/value callouts)
  enough for v1?
- Is 산출(produced value) read from `metric` nodes, from result-node
  text, or a new typed field? (verify against the BANAS sim ServiceDetail
  during the one-by-one review.)

- **Q7 — Schema snapshot:** regenerate `schema/*.json` on blueprint
  publish (or drop it from the project dir if unused at runtime)? Needs a
  quick check of whether viewer/MCP read it. (R) verify-then-decide.

---

## 4. Recommended direction (one-paragraph thesis, to confirm)

Keep **inline typed fields + a free-markdown `body`** as the single
source of truth (Q1a, Q2a). Treat **`.md` strictly as publish output**,
and **extend the md template to all 15 kinds** (Q3) so every node
publishes uniformly. Keep **two version axes** — per-node `version` for
component evolution, `blueprint_version` for releases — and make a
**blueprint publish snapshot the node versions** into a manifest (Q5a).
Define the **deliverable** as a **per-service value sheet** assembled at
설계도 발행 (Q6 reframed — see §3.1): not a flat field dump but the
service's **value story** (purpose + 산출 produced value + 체현/발동
embodied foundation + flow with positive/negative cases), packaged in a
bundled blueprint document stamped with `blueprint_version`. This reuses
everything already built (publish, propagation, blueprint semver, plus the
already-shipped injection / decision / polarity / metric design surface)
and only adds: a `body` convention, 12 missing templates, a snapshot
manifest, and a value-sheet bundler.

---

## 5. Phased plan (after §3 is resolved)

- **Phase A — Spec the node document format.** Write a `NODE_DOCUMENT.md`
  (or a SPEC.md section): for each of the 15 kinds, the typed fields + the
  `body` convention + the source-link convention. Docs only, no code.
- **Phase B — Uniform publish templates.** Add `schema/{kind}.md.template`
  for the 12 missing kinds; cover them in `md_publish.py` + the eligibility
  table. TDD against `test_schema_parity` / publish tests.
- **Phase C — Artifact model spec.** Pin Q5/Q6 in SPEC + DECISIONS:
  version-axis relationship, blueprint snapshot manifest shape, deliverable
  definition + format.
- **Phase D — Blueprint bundler (export).** Implement the deliverable
  generator at 설계도 발행 (assemble canvases + published nodes → the
  chosen artifact format). TDD, incremental.
- **Phase E — (optional) Source-sync.** Node↔source-doc linkage + a
  re-sync helper, only if usage justifies it (YAGNI gate).

Each phase: design-red-team → TDD → Gate 0/4 (SPEC + DECISIONS + CHANGELOG
+ version bump) per `plot/CLAUDE.md`.

---

## 6. Grounding references (verified 2026-06-04)

- Storage: `banas-sim/banas/.plot/banas/{foundation,actors,services}/…json`
  (typed fields inline), `schema/{kind}.json` + `schema/{kind}.md.template`
  (3 kinds), `project.json` (`blueprint_version: v0.1.0`, `version: 3`).
- Publish: `plot_mcp/md_publish.py`, `plot_mcp/propagation.py`,
  `docs/PUBLISH.md`, SPEC §Publish.
- Typed fields per kind: `docs/CONCEPTS.md`, `viewer/src/domain/{Kind}.ts`,
  server Pydantic + `tests/test_schema_parity.py`.
- Blueprint versioning: D-2026-05-21-B; per-node publish: D-2026-05-16-E.

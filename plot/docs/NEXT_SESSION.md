# Plot — NEXT SESSION queue

> **Surfaced automatically by the SessionStart hook
> (`plot/hooks/session_start.py`) at every new session start.**
> When the user invokes a queued item by its trigger keyword, that
> item becomes the active task for the session.

---

## Active queue

### `v0.23.0 — node publish UX (Inspector Published versions) + published-MD folder reorg` (queued, top priority, filed 2026-05-17)

> **Trigger:** user says **"퍼블리시"** / **"발행 문서"** /
> **"published 보기"** / **"폴더 정리"** / **"v0.23"** as the first
> / near-first message.
>
> **Filed:** 2026-05-17 end of session. After v0.22.0 dirty-gate
> ship, user asked where published MD files live + asked for
> deliberate folder reorg, then deferred implementation:
> *"다음 세션에서 노드 퍼블리시 하고 문서 관리 어떻게 할지
> 고민해봐야겠네요."* + *"그리고 어떻게 정리할건지 저한테 말해주고
> 작업합시다."* Critical design questions were locked the same turn.
>
> **Locked decisions (carry from plan-mode 2026-05-17):**
>
> 1. **Folder layout: `kind/slug/v<X>.md`** (user-picked via
>    AskUserQuestion ASCII-tree preview). Human-readable, one folder
>    per logical document, all versions of a node together. Label
>    rename → folder rename → git tracks via rename detection.
>
>    ```
>    .plot/<project_id>/foundation/published/
>      ├── mission/mission/v2.0.md v3.0.md v4.0.md
>      ├── identity/voice/v2.0.md v3.0.md v4.0.md
>      └── core_value/core-value/v2.0.md v3.0.md v4.0.md
>    ```
>
> 2. **Migration: smallest viable**. No other Plot users yet (user
>    confirmed). New code path writes new layout from v0.23.0
>    onward. One-shot idempotent first-read migration in
>    `read_canvas` (same pattern as
>    `_absorb_md_typed_text_into_json`) moves legacy
>    `<canvas>/published/<kind>-<slug>-v<X>.md` files to the new
>    location. No explicit migration commit.
>
> 3. **Inspector UX: "Published versions" section + modal**
>    (user-picked: *"인스펙터에 파일 정보 보여주고요. 클릭하면 모달
>    팝업으로"*). Section lists `{version, published_at, sha}` rows;
>    clicking opens a modal that renders the MD via the existing
>    `MDPreview` component on top of the `SketchBodyModal` scaffold.
>
> **Implementation walk (server → client → docs):**
>
> - **`plot/plot_mcp/md_publish.py::published_md_path`** — change
>   return path to `canvas_dir / "published" / kind / slug / f"{version}.md"`.
> - **`plot/plot_mcp/folder_io.py`** — add
>   `_migrate_published_flat_to_kind_slug` called from `read_canvas`
>   on first read; regex `^(?P<kind>[a-z_]+)-(?P<slug>.+)-v(?P<v>\d+\.\d+)\.md$`
>   matches legacy filenames; skip if destination exists; idempotent.
> - **New endpoint** `GET /api/projects/{id}/canvases/{kind}/nodes/{node_id}/published`
>   returns `[{version, path, published_at, sha, size}]` sorted
>   newest first. `published_at` from MD frontmatter; `sha` from
>   `git log --diff-filter=A -1 --format=%h -- <path>`.
> - **`plot/viewer/src/api.ts`** — `getPublishedVersions(...)`.
> - **New** `viewer/src/canvases/inspectors/shared/PublishedVersionsSection.tsx`
>   — renders in BaseInspector after `DetailsSection`. Watch the 285
>   LOC ceiling on BaseInspector (D-2026-05-17-H); ~5 LOC budget for
>   the prop wiring, otherwise raise the ceiling with a new D entry.
> - **New** `viewer/src/canvases/PublishedMDModal.tsx` — reuses
>   `SketchBodyModal` + `MDPreview`. Escape + backdrop close.
> - **i18n** (`en` + `ko`): `inspector.publishedVersions`,
>   `inspector.publishedVersionsEmpty`, `inspector.publishedAt`.
> - **Tests**: pytest for migration + endpoint;
>   vitest for section empty/non-empty + modal open on click.
> - **Docs**: SPEC.md §Publish "What lands on disk" path examples
>   updated; new §"Published versions in the Inspector". DECISIONS
>   `D-2026-05-17-I` (or next letter) pinning the locks above.
> - **Ship as:** v0.23.0 (minor — new feature).
>
> **Reuse, don't re-derive:**
>
> | Need | Existing piece |
> |---|---|
> | Read MD file | `file_get_endpoint` in `api_endpoints.py:439-459` (`.md` already in `ALLOWED_EXTENSIONS`) |
> | Markdown rendering (GFM + Mermaid) | `MDPreview` |
> | Modal scaffold | `SketchBodyModal` |
> | Inspector insertion point | After `DetailsSection` in `BaseInspector.tsx:245-259` |
> | Idempotent migration pattern | `_absorb_md_typed_text_into_json` in `folder_io.py` |
> | Slug | `slug.py::slugify` (CJK-safe) |
>
> **Out of scope (v0.23.0):**
> - Cross-version diff view ("what changed between v3.0 and v4.0").
> - Unpublish (already in `v0.18.x follow-up` queue).
> - Bulk publish / publish-history viewer / cross-project library.
> - Folder-name collision handling beyond `slug + version`
>   uniqueness (two nodes with identical labels would land in the
>   same folder; users rename to resolve).
>
> **Plan file:** `/Users/woogis/.claude/plans/jolly-bouncing-orbit.md`
> has the full plan that was approved this turn.

---

### `Live Preview Stage 3 — heading / list / image decorations` (queued, deferred from v0.21.0)

> **Trigger:** user says **"Live Preview"** or **"v0.22"** or **"heading style"** or **"image embed"** as the first / near-first message. (Was queued for v0.22.0 previously; check that the version label still makes sense after v0.21.0 ships.)
>
> **Filed:** 2026-05-17 (D-2026-05-17-B follow-up). Stage 2 of the
> 3-stage Obsidian Live Preview track that v0.19.0 started. Render
> ```` ```mermaid ```` code blocks as inline SVG widgets *on top of*
> the source code inside the CodeMirror MdTextarea.
>
> **Scope:**
>
> - CodeMirror ``ViewPlugin`` that walks the syntax tree for
>   ```` ```mermaid```` fenced blocks and inserts a Decoration.widget
>   below each block with the rendered SVG.
> - Mermaid is already a dep + ``viewer/src/edit/MDPreview.tsx``
>   has a working ``mermaid.render`` path that handles errors gracefully —
>   reuse that helper, don't reinvent.
> - **Lazy import**: ``await import("mermaid")`` only when the first
>   mermaid block appears in any open editor. ~700KB raw / ~140KB gzip
>   chunk; keep out of initial bundle.
> - Re-render on content change (debounced ~200ms).
> - SSOT preserved — decoration is visual-only.
>
> **Approach:** plan-mode + plot-design-red-team (edge cases: invalid mermaid
> syntax, very large diagrams, multiple blocks per field, theme).

### `v0.22.0 — Live Preview decorations` (heading / list / image) (queued)

> **Trigger:** user says **"Live Preview"** or **"v0.22"** or **"heading style"** or **"image embed"**.
>
> **Filed:** 2026-05-17 (D-2026-05-17-B follow-up). Stage 3.
>
> - Heading font-size scaling on ``#``/``##``/``###`` lines (visual; raw MD untouched).
> - List bullet rendering (``-`` becomes a styled bullet glyph).
> - Image embed (``![alt](url)``) renders the image inline.
>
> Each is a separate ``ViewPlugin`` decoration on top of the
> CodeMirror MdTextarea. SSOT preserved.

### `MCP-driven node creation via AI conversation` (queued, filed 2026-05-17)

> **Trigger:** user says **"MCP 대화"** or **"AI 로 노드 만들기"** or **"context_envelope"** or **"conversation MCP"**.
>
> **Filed:** 2026-05-17 (user explicit deferral — *"MCP 로 대화하면서
> 만드는건 나중으로 미루고"*). Combines with tree-in-forest
> [D-2026-05-16-D](./DECISIONS.md) Layer 2 (``context_envelope`` MCP
> tool).
>
> **Scope sketch (plan-mode required):**
>
> - New / extended MCP tools: ``context_envelope(node_id)``,
>   ``draft_node_proposal``, ``apply_node_proposal``.
> - Conversation pattern: AI walks user through node creation,
>   pulls context (parent ancestors + sibling identity / mission
>   refs), drafts the typed fields, calls
>   ``update_canvas`` (already exists) to materialize.
> - PSPEC §9 interview pattern surfaces the envelope as the
>   opening context.
>
> **Approach:** plan-mode + plot-design-red-team. Substantial phase
> — own design discussion + likely 2-3 ships.

---

### `cross-kind ref typed-text symmetry` (lower priority, filed 2026-05-16)

> **Trigger:** user says **"ref symmetry"** or **"ref typed text"** or
> **"actor_ref vs mission_ref"** or **"ref 비대칭"**.
>
> **Filed:** 2026-05-16 (D-2026-05-16-F follow-up). actor_ref 만
> ``gives`` / ``receives`` 라는 ref-context-specific typed text 를
> 가지는데, mission_ref / value_ref / identity_ref 는 pure pointer
> (typed text 없음). 의도적 설계인지, actor 만 *행동 단위* 이고 나머지는
> *상태 단위* 라서 비대칭이 합리적인지, 아니면 4 ref 의 모델이 통일되어야
> 하는지 미해결.
>
> **Approach:** 별도 plan-mode 에서:
> - 4 ref 의 의도 비교 — actor 와 다르게 mission/value/identity 가 ref
>   context 에서 자체 typed text 를 가질 의미가 있나?
> - 사용 사례 발견 시 mission_ref 등에도 `notes_in_context` 같은 typed
>   text 추가 검토.
> - 또는 actor_ref 의 `gives` / `receives` 도 별도 placement (e.g.
>   actor_ref 와 actor master 사이의 *edge* 의 typed property) 로 옮기는
>   재검토.

---

### `v0.22.x follow-up — publish-button placement + size` (lower priority, filed 2026-05-17)

> **Trigger:** user says **"publish 버튼 크게"** or **"인스펙터
> 아래 publish"** or **"footer publish"** as the first / near-first
> message.
>
> **Filed:** 2026-05-17 alongside v0.22.0 ship. User's words after
> confirming v0.22.0 worked: *"제 생각엔 퍼블리시 버튼이 인스펙터
> 창 아래로 좀 크게 있으면 좋을 것 같은데.. 이런건 나중에 합시다."*
>
> **Scope (proposal — re-anchor with user before implementing):**
>
> - Move the 📤 publish button from the BaseInspector header (small
>   icon-text button in the right cluster) to a **sticky footer
>   inside the Inspector aside**, full-width, taller (e.g. 36-40 px
>   tall, primary CTA styling).
> - Keep the dirty-gate from D-2026-05-17-H — the larger footer
>   button still disables when clean, with the same tooltip.
> - Sticky positioning so the footer stays visible regardless of
>   how far down the inspector body the user scrolls.
> - Re-evaluate the Inspector chrome — the header would become
>   leaner (just KIND tag + version + delete / width / close
>   buttons; no publish).
>
> **Open questions:**
>
> - Should the footer also surface the version badge prominently
>   (so the user sees "current v3.0" right above the publish CTA)?
> - Should the disabled-state footer collapse / shrink to save
>   space, or stay full-size grey?
> - Mobile / narrow inspector width — does a sticky footer still
>   fit alongside the body scroll?
>
> **Ship as:** v0.22.x patch (UX-only; no schema or behaviour change).
> Requires plot-design-red-team pass given it touches the Inspector's
> primary CTA surface.

---

### `v0.18.x follow-up — Unpublish button` (lower priority)

> **Trigger:** user says **"Unpublish"** or **"미스클릭"** or
> **"publish 취소"** as the first / near-first message.
>
> **Filed:** 2026-05-16. Phase 3 ships without an Unpublish button
> (red-team A4-1; recovery is manual via ``git revert HEAD`` +
> optional MD-file rm, per [`PUBLISH.md`](./PUBLISH.md)). Once
> real usage shows the misclick rate, automate.
>
> **Scope:**
>
> - Inspector header: **↩ unpublish** button next to **📤
>   publish**, visible only when ``node.version != "v1.0"`` (i.e.
>   only when there's a publish event to undo).
> - Server endpoint
>   ``POST /api/projects/{id}/canvases/{kind}/nodes/{node_id}/unpublish``
>   that:
>   1. Finds the most recent publish commit via
>      ``git log --grep "^Publish-Node-Id: {node_id}"``.
>   2. Runs ``git revert <sha> --no-edit``.
>   3. ``rm`` the published MD file that the revert left behind
>      on disk (the revert may not clean working-tree files
>      depending on git version).
> - Confirmation dialog name explicitly: "Unpublish brings the
>   version back to ``v(N-1).0``; the ``-vN.0.md`` file is removed.
>   Continue?"
> - Tests: unit-test the revert flow against the fake-repo fixture
>   used by ``test_git_store.py``.
>
> **Ship as:** v0.18.x patch once the misclick rate justifies it.

---

### (archived 2026-05-17) `v0.21.0 — Mermaid SVG inline decoration` — shipped v0.21.0

> **Trigger:** user said *"네 플랜 모드 필요하죠?"* + entered plan mode 2026-05-17. Plan: ``~/.claude/plans/jolly-bouncing-orbit.md``.
>
> **Filed:** 2026-05-17. **Shipped** 2026-05-17 same session as [D-2026-05-17-D](./DECISIONS.md). Stage 2 of 3-stage Live Preview track.
>
> **7 open questions locked (no AskUserQuestion needed — YAGNI/SSOT/KISS made each answer self-resolve):**
>
> 1. Lazy import singleton via ``loadMermaid()``.
> 2. Reuse MDPreview error pattern (red ``data-mermaid="error"`` block).
> 3. No size cap; ``max-height: 480px; overflow: auto``.
> 4. Block widget *below* the fence (not replacing source) — SSOT keeps the markdown editable + visible.
> 5. Default mermaid theme (matches MDPreview).
> 6. 200 ms debounce.
> 7. New vitest SSOT-invariant test.
>
> **What landed:**
> - ``viewer/src/edit/mermaidLoader.ts`` (new) — singleton lazy import + initialize.
> - ``viewer/src/canvases/inspectors/shared/mdMermaidPlugin.ts`` (new) — ``StateField`` + ``ViewPlugin`` debouncer (CM6 disallows ViewPlugin-sourced block decorations; split is structural, not stylistic).
> - ``MdTextarea`` wires ``mdMermaidPlugin`` into the extensions list (2-LOC delta).
> - ``MDPreview`` switched from static ``import mermaid`` to the shared loader.
> - ``viewer/tests/inspectors/mermaid-decoration.test.tsx`` — 3 cases: SSOT invariant, happy path, error path.
> - Bundle: index ``1,759 KB / 515 KB gzip`` → ``1,185 KB / 381 KB gzip`` (−574 KB raw / −134 KB gzip).
> - tsc clean, vitest **529/529** (524 prior + 3 mermaid + 2 unrelated misc?).
>
> **Trigger phrases preserved:** ``mermaid`` / ``머메이드`` / ``Live Preview`` / ``v0.21``.

---

### (archived 2026-05-17) `Phase 4 — MINOR propagation up the ancestor chain` — shipped v0.20.0

> **Trigger:** user said **"Phase 4"** / **"MINOR propagation"** had been queued since 2026-05-16; user invoked via **"다음 작업 합시다. 브라우저 띄우고"** (2026-05-17) + plan-mode multi-choice (chose Phase 4 over Mermaid SVG decoration).
>
> **Filed:** 2026-05-16. **Shipped** 2026-05-17 same session as [D-2026-05-17-C](./DECISIONS.md). Plan: ``~/.claude/plans/jolly-bouncing-orbit.md``.
>
> **5 open questions answered in plan-mode (user-approved):**
>
> 1. **Scope = ``parent_id`` chain only.** Refs are not walked. Same-id mirrors crossed via id-matching.
> 2. **No new ancestor MD files** — only JSON ``version`` bumps.
> 3. **Single commit** with extra ``Publish-Propagated-Ancestor:`` trailers (not separate commits).
> 4. **Revert is automatic** — ``git revert HEAD`` undoes everything (single commit).
> 5. **No new Inspector UI** — version badge already shows MINOR.
>
> **What landed:**
> - ``plot_mcp/propagation.py`` (new) — pure ``walk_ancestors`` module + ``LogicalAncestor`` dataclass; ignores refs, follows ``parent_id`` and same-id mirrors only.
> - ``plot_mcp/md_publish.py::bump_minor`` (new).
> - ``plot_mcp/folder_io.py::publish_node`` rewired — loads all canvases, MAJOR-bumps target + mirrors, walks ancestors, MINOR-bumps each, persists every touched canvas.
> - ``plot_mcp/git_store.py::publish_snapshot`` — accepts ``propagated`` list; appends ``Publish-Propagated-Ancestor: <id> <from>→<to>`` trailers (one per logical ancestor).
> - ``plot_mcp/api_endpoints.py`` + ``plot_mcp/mcp_tools.py`` — response shape carries new ``propagated`` array.
> - Viewer ``api.ts::PublishNodeResponse`` + new ``PublishPropagatedAncestor`` interface. Existing ``useProject::publishNodeAction`` already re-fetched all canvases, so client picks up ancestor bumps automatically.
> - Tests: 8 new (5 in ``test_propagation.py``, 1 in ``test_md_publish.py`` (×3 bump_minor cases), 3 in ``test_folder_io.py``). Server 385/385 + viewer 524/524.
> - Docs: SPEC §Publish — MINOR propagation; PUBLISH.md commit format + "does not"; DECISIONS D-2026-05-17-C.
>
> **Trigger phrases preserved:** ``Phase 4`` / ``MINOR propagation`` / ``ancestor chain`` / ``MINOR bump`` / ``propagated`` / ``Publish-Propagated-Ancestor``.

---

### (archived 2026-05-17) `v0.19.0 — MD-aware Inspector editor (CodeMirror 6)` — shipped v0.19.0

> **Trigger:** user said *"노드에 있는 각 항목들 md 잖아요. md 편집기 붙일 수 있나요?"* + *"머메이드 차트 지원해뒀으면"* + *"옵시디언 처럼"* (2026-05-17).
>
> **Filed:** 2026-05-17. Shipped same session as [D-2026-05-17-B](./DECISIONS.md). Stage 1 of 3-stage Live Preview track.
>
> **What landed:**
> - ``MdTextarea`` shared component (CodeMirror 6 + ``@codemirror/lang-markdown``); 19 textareas across 11 Inspector files now use it.
> - Bundle delta: gzip +175KB (within 150-180KB plan).
> - viewer 524/524 green; tsc clean.
>
> **Trigger phrases preserved:** ``MD 편집기`` / ``CodeMirror`` / ``markdown editor`` / ``v0.19``.

---

### (archived 2026-05-17) `v0.18.3 — reload fit-view race fix` — shipped v0.18.3

> **Trigger:** user reported *"파운데이션에서 새로고침 하면 노드들 싹다 사라집니다"* (turned out to be viewport-not-fit, not data loss).
>
> **Filed:** 2026-05-17. Shipped same session as [D-2026-05-17-A](./DECISIONS.md).
>
> **What landed:** Moved fitView out of RF's onInit callback into a ``useNodesInitialized`` effect (waits for DOM measurement). v0.16.18 "fit once on mount" intent preserved via ``didInitialFitRef`` gate.

---

### (archived 2026-05-16) `v0.18.2 — typed text MD 통일 + body on 7 publish-eligible kinds` — shipped v0.18.2

> **Trigger:** user same-session confirmation of intent — *"노드 상세
> typed field 값은 모두 MD 문법, body 는 extra, 발행하면 MD"* + *"ref =
> 복사본/링크 (서비스 관계 표현)"*.
>
> **Filed:** 2026-05-16. Shipped same session as
> [D-2026-05-16-F](./DECISIONS.md). Phase 1 (v0.17.0) had covered
> Foundation 3 kinds with the "monospace MD textarea + body" pattern;
> Phase 3 (v0.18.0) shipped publish before bringing the other 7 to
> parity. v0.18.2 closes that gap.
>
> **What landed:**
>
> - **Server** (``plot_mcp/models.py``): ``body: str = ""`` on 7 kinds
>   (actor / service / category / metric / step / rule / content).
> - **Viewer entity** (`viewer/src/domain/{Actor,Service,Category,
>   Metric,Step,Rule,Content}.ts` × 7): ``body`` field through
>   interface + class + constructor + fromJson + toJson.
> - **Viewer inspectors** (7 kinds): monospace MD textarea on every
>   typed text field + ``<BodyField>`` + ``hideDetailsSection``.
>   Shared ``RuleFields`` / ``ContentFields`` lifted to monospace.
> - **Viewer actor_ref** inspector: `gives` / `receives` textarea
>   lifted to monospace MD (ref is still publish-ineligible + no
>   `body`, but input surface is consistent).
> - **Docs**: PUBLISH.md per-kind H2 reference for 15 kinds +
>   ref-as-relation-tool note; SPEC.md §Publish typed-text-and-body
>   subsection; DECISIONS D-2026-05-16-F.
>
> **Verification status:**
> - Server: pytest 359/359 (unchanged — schema-parity auto-flowed);
>   mypy + ruff clean.
> - Viewer: vitest 522/522 (unchanged — entity-roundtrip auto-flowed);
>   tsc clean.
> - LOC ceilings: all 7 per-kind inspectors stay within 250 ceiling;
>   no structural-guards changes.
>
> **Trigger phrases preserved:** ``body 통일`` / ``monospace MD`` /
> ``노트 필드 7 kind`` / ``per-kind MD format``.

---

### (archived 2026-05-16) `Phase 3 — Publish button + per-node MD export + MAJOR bump` — shipped v0.18.0

> **Trigger:** user said **"작업합시다"** as the first / near-first
> message of this session (after Phase 2 ship + silent-state
> archival).
>
> **Filed:** 2026-05-16. Shipped same session as
> [D-2026-05-16-E](./DECISIONS.md).
>
> **What landed:**
>
> - **Server (new module):** ``plot_mcp/md_publish.py`` —
>   uniform-across-15-kinds MD render (YAML 7-key frontmatter +
>   per-typed-field H2 sections) + ``can_publish`` eligibility +
>   ``bump_major`` arithmetic.
> - **Server:** ``folder_io.publish_node`` (atomic read → bump →
>   render → write → commit), ``git_store.publish_snapshot``
>   (commit with 5 ``Publish-*:`` trailers), HTTP endpoint
>   ``POST /api/projects/{id}/canvases/{kind}/nodes/{node_id}/publish``,
>   MCP tool ``publish_node_tool``.
> - **Viewer:** ``BaseInspector`` chrome additions (version badge
>   left cluster + 📤 publish button right cluster + confirm
>   dialog), ``publishEligibility.ts`` (canPublish mirror),
>   ``api.ts::publishNode``, ``useProject::publishNodeAction``,
>   prop threading via SketchCanvas → SketchInspectorBindings →
>   KindInspector → per-kind inspectors (auto-flow via
>   ``{...props}`` spread).
> - **i18n:** 4 new keys (``inspector.publish`` /
>   ``inspector.publishShort`` / ``inspector.publishHint`` /
>   ``inspector.confirmPublish``) in both en + ko.
> - **Docs:** new ``docs/PUBLISH.md`` reference + new SPEC
>   ``§Publish (v0.18.0+)`` section; CHANGELOG; DECISIONS
>   D-2026-05-16-E; PSPEC §6 clarifier shipped separately as
>   v0.17.4 per red-team A5-1.
> - **LOC ceilings raised** (with D-entry justification):
>   SketchCanvas 420 → 440; BaseInspector 220 → 270. Both
>   no-growth henceforth.
>
> **Verification status:**
> - Server: pytest **396/396** green (359 → 396, +37); mypy +
>   ruff clean.
> - Viewer: vitest **522/522** green (514 → 522, +8); tsc clean.
> - Backward-compat smoke: real-project ``plot-test-v013/banas-v013``
>   mission node v1.0 → v2.0 publish flow verified end-to-end on
>   server before commit.
>
> **Trigger phrases preserved verbatim for future reference:**
> ``Phase 3`` / ``Publish 버튼`` / ``publish button`` / ``MD export``
> / ``MAJOR bump``.

---

### (archived 2026-05-16) `Phase 2 — version: str = "v1.0"` in BaseFields — shipped v0.17.2

> **Trigger:** user said **"다음 작업 시작"** as the first / near-first
> message of this session (after Phase 1 ship). Resolved against the
> active queue entry filed earlier in the day.
>
> **Filed:** 2026-05-16. Shipped same session as
> [D-2026-05-16-C](./DECISIONS.md).
>
> **What landed:**
>
> - ``plot_mcp/models.py::BaseNodeFields.version`` — ``str = "v1.0"``
>   default + ``_version_is_valid`` regex validator
>   (``^v\d+\.\d+$``). Inherited by all 15 per-kind classes via
>   the discriminated union.
> - ``viewer/src/domain/BaseFields.ts`` — ``version`` added to both
>   ``BaseFieldsJson`` (wire) and ``BaseFields`` (in-memory)
>   interfaces; ``asVersionString`` helper added to
>   ``parseBaseFields`` mirroring the server regex.
> - 15 per-kind entity classes
>   (``Actor`` / ``ActorRef`` / ``Category`` / ``Content`` /
>   ``CoreValue`` / ``Identity`` / ``IdentityRef`` / ``Metric`` /
>   ``Mission`` / ``MissionRef`` / ``Project`` / ``Rule`` /
>   ``Service`` / ``Step`` / ``ValueRef``) — ``readonly version!:
>   string;`` on the class body + ``version: this.version,`` in
>   ``toJson()``.
> - Tests: 4 server-side (``test_node_models.py``) + 4
>   viewer-side (``base-fields.test.ts``) + 1 server contract
>   line in ``test_schema_parity.py::_EXPECTED_BASE_FIELDS``.
>   The 15-kind parametric parity test auto-flowed the change.
>
> **Verification status:**
> - Server: 318 → 322 tests, all green (mypy + ruff clean).
> - Viewer: 505 → 514 tests, all green (tsc clean).
> - No user-visible change. UI surface lands in Phase 3.

---

### (archived 2026-05-16) `Phase 1 — JSON SSOT 구현 (MD 흡수)` — shipped v0.17.0

> **Trigger:** user says **"Phase 1"** or **"JSON SSOT 구현"** or
> **"MD 흡수"** as the first / near-first message.
>
> **Filed:** 2026-05-13. The JSON SSOT vision was pinned in two
> steps: D-2026-05-13-J (initial 4-point) → D-2026-05-13-O
> (today's 7-principle revision that supersedes J's point #4 and
> adds per-node versioning + folder hierarchy). Phase 0 (docs)
> shipped today (v0.16.40). Phase 1 (code) lands next session.
>
> **Phase 1 scope (per D-2026-05-13-O and plan
> ``~/.claude/plans/sparkling-discovering-blanket.md``):**
>
> - **Server:** replace ``_evict_typed_text_to_md`` +
>   ``_merge_md_typed_text_into_nodes`` +
>   ``_split_foundation_typed_text_to_md`` with a one-shot
>   read-side migrator ``_absorb_md_typed_text_into_json`` that
>   moves ``foundation/{kind}-{slug}.md`` content into JSON node
>   fields and renames the source file to ``foundation/_legacy/``.
> - **Viewer:** typed-field inspectors (mission / core_value /
>   identity) switch from plain ``<textarea>`` to monospace
>   MD-aware editor (preserves newlines, no preview yet).
> - **Migration safety:** 4-scenario coverage. All paths preserve
>   user content; legacy files quarantined not deleted.
> - **Tests:** new ``tests/test_folder_io.py::test_absorb_md_typed_text_into_json_*``.
> - **Ship as:** v0.17.0 (minor — Foundation storage model change).
>
> **Approach:**
> - Plan-mode entry mandatory (Gate 1 — SPEC change).
> - Plan-agent design review before code (large refactor).
> - Hands-on validation in user's real Chrome before commit
>   (Gate 3) — v0.13 project loads and shows the prior MD content
>   in the new inspector.
>
> **Subsequent phases (each its own plan-mode + approval):**
>
> | Phase | Scope | Ship version |
> |---:|---|:---:|
> | 2 | ``version: str = "v1.0"`` in BaseFields | v0.17.1 |
> | 3 | "Publish" button + per-node MD export + MAJOR bump | v0.17.2 |
> | 4 | MINOR propagation (ancestor chain) | v0.18.0 |
> | 5 | Folder hierarchy + container-publish semantics | v0.19.0 |
> | 6 | Legacy purge + final docs sync | v0.19.1 |

---

### (archived 2026-05-13) ``JSON SSOT 논의`` — superseded by Phase 1 trigger

> **Superseded:** by the 6-phase sequence above. The initial
> 4-point vision (D-2026-05-13-J) has been replaced by the
> 7-principle vision (D-2026-05-13-O) and is no longer the active
> entry point.

> **Trigger:** user says **"JSON SSOT"** or **"json 원본"** or
> **"MD 추출"** or **"export 버튼"** or **"phase 2"** or
> **"내일 논의"** as the first / near-first message.
>
> **Filed:** 2026-05-13 end-of-session. User pinned the 4-point
> design vision (D-2026-05-13-J) and asked to resume detail
> discussion next session. Today's ship was docs-only — no code
> changes; this entry is the next-session entry point.
>
> **The 4-point vision (locked, do not re-litigate):**
>
> 1. **JSON = SSOT.** Co-equal storage abolished.
> 2. **JSON value = MD-formatted string.** Typed-text fields
>    stored as MD-formatted strings inside JSON; viewer edits via
>    MD editor.
> 3. **MD export = explicit button.** No auto-sync.
> 4. **Export unit = canvas.** Per-node MD files abolished;
>    single MD file per canvas.
>
> **Open detail questions for the session (from plan file
> `~/.claude/plans/sparkling-discovering-blanket.md`):**
>
> 1. MD editor form (textarea / preview split / WYSIWYG /
>    external trigger)?
> 2. JSON typed-text string line-break handling (`\n` literal /
>    raw newlines / both)?
> 3. Per-canvas MD layout (per-node section + heading / single
>    narrative / other)?
> 4. Migration path (current N per-node MD files → 1
>    per-canvas MD; user data preservation)?
> 5. Export-button placement (canvas toolbar / top-right menu /
>    sidebar)?
> 6. Export idempotence (same JSON → same MD every time)?
> 7. Phase 2 regression guard (vitest / pytest invariant beyond
>    existing schema-parity / no-god-import / entity-roundtrip)?
>
> **Approach:**
> - Plan-mode entry mandatory. No code before detail consensus
>   and plan approval.
> - Vision 4-point is locked — discussion is detail-only.
> - Cross-references: D-2026-05-13-J (vision pin),
>   D-2026-05-12-A §15 #2 (original deferred entry),
>   `plot/docs/PRODUCT_SPEC.md` §15 #2 (updated 2026-05-13).

---

### (Completed 2026-05-16) `잔여 silent state` — 422 PATCH + None→None orphan edge

> **Completed:** 2026-05-16. Confirmed closed by hands-on smoke
> verification in v0.17.2's same-day session: opened test-v010 in
> Chrome via chrome-devtools MCP, performed tab-switch + click
> interactions, observed **0 / 12 requests at HTTP 422 + 0 console
> errors + 0 warnings**. Live storage inventory (raw
> ``proj-monmft3s/{foundation,actors,services}/canvas.json``)
> showed zero dangling edges and zero None-endpoint edges; the
> orphan edge ``e_mopntgek_4y74`` flagged at filing time is no
> longer present.
>
> **Both root issues already fixed before this verification:**
>
> 1. **422 PATCH storm** — fixed in **v0.16.37** (commit 4e43d5a,
>    [D-2026-05-13-M](./DECISIONS.md)). Anchor edge reject path
>    rewritten + error message corrected (was mislabelling edge
>    ids as missing nodes, which is what made the original
>    diagnosis chase the wrong suspect).
> 2. **None→None orphan edge cleanup** — fixed in **v0.16.38**
>    (commit 0e148c9, [D-2026-05-13-N](./DECISIONS.md)). Anchor
>    edge cleanup whitelist landed as the v0.16.37 follow-up.
>
> **Trigger phrases (preserved verbatim for future regression
> re-surface):** ``잔여 silent state`` / ``422`` / ``None edge`` /
> ``orphan edge`` / ``잔여 에러``.

---

### (Completed 2026-05-13) `RF 움직임` — Canvas interaction "엉망" 깊게 파기

> **Completed:** 2026-05-13 end-of-session. After v0.16.24-31
> shipped (anchor visual restoration + 5 catch-up artefacts +
> skill reclassification), user hands-on validation in real Chrome
> confirmed: *"이제 잘 동작하는 거 같아요"* + *"근데 이제 된 거
> 같은데?"* (D-2026-05-13-H). Trigger archived; remaining silent
> state issues surfaced separately above.
>
> **Trigger phrases (preserved for future reference if regression
> resurfaces):** "RF 움직임" / "움직임 엉망" / "RF 기본 동작" /
> "canvas interaction" / "엉망 깊게 파자".
>
> **Filed (history):** 2026-05-12 end-of-session. **Updated
> 2026-05-13:**
> v0.16.24 restored the anchor + radial + self-loop visual layer
> (D-2026-05-13-A) after user clarified the v0.16.20-23 batch was
> over-reach. Interaction "엉망" is now isolated as a **separate**
> concern from the anchor visual layer — restoring the anchor did
> **not** fix the interaction complaint (the complaint pre-existed
> in v0.16.19 with the anchor present).
>
> **Current baseline for diagnosis:** v0.16.29 — anchor + radial +
> self-loop visible; all 5 D-2026-05-12-B catch-up artefacts shipped
> (plot-entity-template skill, plot-domain-design skill,
> no-god-import guard, entity-roundtrip guard, CLAUDE.md anti-pattern
> row). viewer tests: 461 / 461 green.
>
> **Suspects (post-restoration, layers that *survived* the rollback
> and might still cause "엉망"):**
> - **v0.16.16 useStableHandlers** — callback identity stabilisation
> - **v0.16.17 Cmd+A controlled-contract sync**
> - **v0.16.18 fitView gating** (onInit only, not RF prop default)
> - **v0.16.6+ keyboard shortcut hook** (Cmd+Z/C/V/D)
> - **Per-kind NODE_RENDERERS / BaseNode chrome** (v0.15.1+)
> - **useNodesMemo / useEdgesMemo transform** (drop rules / content /
>   hidden-root / value-flow recolour / etc.)
> - **useCollapsedTree** (fold/expand)
> - **useDragAndDrop** (stencil → canvas)
> - **useInspectorRouting** (click → Inspector)
> - **useContextMenus** (pane/node/edge right-click)
>
> **Open questions to answer in this session:**
> 1. What *specific* user-visible motion is "어색"? Drag /
>    pan / zoom / click select / hover / wheel? — user must name
>    or demonstrate concretely.
> 2. Is the regression pre- or post- v0.15 reset? Bisect against
>    a freshly-installed plain ``reactflow@11.11.4`` demo as the
>    "RF baseline" reference.
> 3. (Closed 2026-05-13) Should anchor / radial / self-loop be
>    restored? — **Yes**, done in v0.16.24 (D-2026-05-13-A).
>
> **Approach for the session:**
> - Plan-mode entry **mandatory**. No code before plan approval.
> - **Hands-on validation in user's real Chrome** before any
>   commit is called "done" — Playwright synthetic input cannot
>   drive d3-zoom event paths (plot/CLAUDE.md Gate 3); the entire
>   v0.16.15-19 batch failed because of this very gap.
> - Reference plan: ``~/.claude/plans/sparkling-discovering-blanket.md``
>   (the 2026-05-13 plan that landed v0.16.24-29; its Step 3 layer
>   kill-switch bisect procedure is the entry point for this work).
> - DECISIONS entries to consult: D-2026-05-13-A (restoration),
>   D-2026-05-11-A (cursor SSOT), D-2026-05-04-B (anchor handles),
>   D-2026-05-10-C/F (cursor reset history).
>
> **Reference commits (current state — anchor visual is live):**
> - 7bc96f8 — v0.16.24 anchor visual restoration
> - aa385a0 — v0.16.15 anchor optimistic update (live again post-v0.16.24)
> - 0713343 — v0.16.18 fitView gating
> - 06199cf — v0.16.16 stable handlers
> - 014fa12 — v0.16.17 Cmd+A sync

---

## Roadmap items (queued but lower priority)

The remaining big-scope work is filed in
[`ROADMAP.md` §"v0.17+ — Roadmap items"](./ROADMAP.md), with the
``plot-design-red-team`` 8-attack findings baked into each item:

- **A) isomorphic-git source-data version control** — spec-mandated;
  6 Major findings need ``DECISIONS.md`` answers before any code.
- **B) Work-item layer (userstory + task)** — spec-mandated; hard
  dependency on A; 4 Major findings.
- **C) Plot repository split** — product decision the user owns.

Pick order on the next session: invoke one of the trigger phrases
``isomorphic-git`` / ``git 통합`` / ``일감 레이어`` / ``work-item`` /
``repo split`` / ``레포 분리`` — and the session re-enters plan
mode against the ROADMAP entry's findings as the anchor.

Also queued: **user-driven hands-on review** — user wants to
exercise the v0.16 ship end-to-end before any new feature work.

---

## (archived) `검증` — v0.15 reset Phases 4 + 5

> **Original trigger:** user said **"검증"** or **"verification"** or
> **"phase 4"** or **"phase 5"** or **"커서 sweep"** as the first /
> near-first message of a Plot session.
>
> **Filed:** 2026-05-12 by user — Phase 1+2+3 of the v0.15 reset
> shipped this session (D-2026-05-12-B); Phases 4–5 deferred to a
> dedicated next session because they have a different shape (test
> infra + acceptance gates rather than per-kind work).
>
> **Reference:** [D-2026-05-12-B](./DECISIONS.md), the full plan
> in `~/.claude/plans/dazzling-greeting-diffie.md`, and the
> per-phase changelog from v0.14.15 → v0.16.0.

#### Phase 4 — Per-canvas cursor sweep

The user's complaint that fired the v0.15 reset (*"파운데이션에서
사용되는 커서 컨트롤하고 액터나 서비스에서 사용되는 커서 컨트롤이
다릅니다"*) needs an empirical answer now that the reset's structural
half is done. Phase 4 work:

1. **Audit** — file `D-2026-05-13-X` in `DECISIONS.md` listing
   the `getComputedStyle(...).cursor` returns of every meaningful
   target on each of the 4 canvases (Foundation / Actors /
   Services / ServiceDetail). Compare against `docs/CURSOR.md`
   contract (which says all 4 share one cursor table).
2. **Author Playwright sweep** — `viewer/tests/cursor-sweep.spec.ts`
   that mounts each wrapper, hovers (i) empty pane (ii) regular
   node body (iii) anchor body (iv) connection handle (v) edge
   (vi) resize handle, snapshots cursor inventory per canvas, and
   asserts the 4 inventories are identical (modulo the v0.11.4
   anchor-vs-button asymmetry per D-2026-05-11-A).
3. **Extend the static cursor-baseline guard** — `viewer/tests/
   styles-cursor-baseline.test.tsx` should also verify the 4
   wrapper files contain zero `cursor:` strings.
4. Fixture project under `viewer/tests/fixtures/cursor-sweep-project/`
   with `.plot/` seeded via `domain/createBlankNode` so schema
   drift breaks fixture build before the sweep runs.

Expected output: 2 commits (`v0.15.6` author sweep + `v0.15.7`
extend baseline guard + DECISIONS pin).

#### Phase 5 — Verification gates + kill-switch

5 acceptance gates + 2 static guards + 1 kill-switch. All planned
in detail in the plan file's "Phase 5" section. Highlights:

1. **Per-kind Inspector smoke** — extend
   `viewer/tests/inspectors/inspectors.smoke.test.tsx` to exercise
   every one of the 15 kinds with a synthetic node and assert
   chrome + per-kind body render without `console.error`.
2. **Entity round-trip** — already mostly there in
   `viewer/tests/domain/round-trip.test.ts` and
   `plot/tests/test_node_models.py`; consolidate.
3. **Per-canvas cursor sweep** — Phase 4's spec.
4. **Static guard: `no-god-union-import.test.ts`** — fail the
   build if any `viewer/src/canvases/` `.tsx` matches
   `node.kind === "X"` god dispatch outside the
   `inspectors/` registry's allowlist.
5. **LOC budget guard** — `viewer/tests/loc-budget.test.ts`
   asserting `App.tsx ≤ 400`, wrapper canvases ≤ 150, per-kind
   inspector ≤ 250, per-kind node renderer ≤ 100,
   `BaseInspector ≤ 200`, `BaseNode ≤ 250`.
6. **Kill-switch** — `plot/hooks/pre_commit_gate.py` adds
   `reset_complete_check` that verifies (a) Pydantic
   ``SketchNode`` is the 15-way union, (b) viewer
   ``SketchNode.tsx`` absent, (c) `SketchInspector.tsx` absent,
   (d) zero `doc.canvas_kind` in `viewer/src/canvases/sketch/`,
   (e) all five Phase 5 acceptance gates green. Active for
   v0.15.x; removed at v0.16.0.

Expected output: 3 commits (`v0.15.8` smoke + round-trip
consolidation, `v0.15.9` static guards, `v0.16.0` kill-switch +
final DECISIONS pin + SPEC update + ARCHITECTURE Domain section).

#### What "v0.15 reset complete" means at v0.16.0

- Server: 15-way Pydantic union, no god class, schema_export for
  all 15 kinds, parity test pinning TS↔Pydantic field names.
- Viewer: 15 entity classes, 15 per-kind inspectors, 15 per-kind
  node renderers, 4 canvas wrappers, no god ``SketchInspector.tsx``
  or ``SketchNode.tsx`` on disk, no canvas_kind switches in
  transforms, no ``"sketch"`` god type.
- Tests: 100+ viewer + 200+ server, all green.
- ``pre_commit_gate.reset_complete_check`` returning OK on every
  commit (then retired).

---

### `구조 리셋` (COMPLETED Phase 1+2+3 in this session)

> **Completed Phases 1–3:** 2026-05-12 across v0.14.15 → v0.15.5
> (23 commits). Phases 4–5 → see active `검증` queue above.
>
> **Reference:** [D-2026-05-12-B](./DECISIONS.md).
>
> **What landed in Phase 1+2+3 this session:**
>
> - **Phase 0** v0.14.15 — pre-existing 17 ruff/mypy debts → 0.
> - **Phase 1.1–1.3** v0.14.16–18 — server-side Pydantic 15-way
>   discriminated union, schema_export extended to all 15 kinds,
>   god ``SketchNode`` class deleted server-side.
> - **Phase 2.0–2.10** v0.14.19–v0.15.0 — viewer domain layer
>   (15 entity classes + Canvas + parseEntity + DomainParseError
>   + createBlankNode factory), per-kind Inspector framework
>   (15 inspectors + BaseInspector + KindInspector + 4 shared
>   pieces in `inspectors/shared/`), atomic flip of
>   ``viewer/src/types.ts`` god ``SketchNode`` interface to
>   discriminated union, ``SketchInspector.tsx`` (1491 LOC)
>   deleted from disk.
> - **Phase 3.1–3.5** v0.15.1–5 — 15 per-kind React Flow node
>   renderers (BaseNode + per-kind wrappers + NODE_RENDERERS
>   registry), 4 canvas wrappers (FoundationCanvas / ActorsCanvas
>   / ServicesCanvas / ServiceDetailCanvas), 4 ``canvas_kind``
>   switches stripped from transforms (replaced by 4
>   wrapper-supplied props), ``SketchNode.tsx`` (245 LOC)
>   deleted from disk.
>
> **Verification status:** server 214/214 tests + ruff/mypy clean;
> viewer 106/106 tests + tsc clean. No user-visible behaviour
> change. The "no god object" rule is now enforced end-to-end.

(Original "구조 리셋" trigger text — problem statement, code
evidence, Phase A–F plan, done criteria, skills shortlist — is
preserved in git history at v0.14.14 and in the plan file
`~/.claude/plans/dazzling-greeting-diffie.md`.)

---

## How this file works

- The `SessionStart` hook (`plot/hooks/session_start.py`) reads
  this file at every session start and prepends each `### TRIGGER`
  heading to the assistant's context.
- The assistant then watches for the user's next message. If it
  contains a trigger keyword, the assistant executes the matching
  item.
- After completion, the assistant **moves the item to the
  "Completed" section below** with the date + commit hash, instead
  of deleting it. This preserves the audit trail.

---

## Completed

### `검증` — v0.15 reset Phases 4 + 5 (cursor sweep + verification gates)

> **Completed:** 2026-05-12 over v0.15.7 → v0.16.0 (5 commits).
> **Outcome:** [D-2026-05-12-C](./DECISIONS.md),
> [D-2026-05-12-D](./DECISIONS.md),
> [D-2026-05-12-E](./DECISIONS.md),
> [D-2026-05-12-F](./DECISIONS.md),
> [D-2026-05-12-G](./DECISIONS.md).
>
> **What landed:**
>
> - **v0.15.7 (Phase 4.1)** — cursor uniformity audit + JSDOM
>   ``cursor-sweep.test.tsx`` (8 tests). Replaced the planned
>   Playwright sweep with a static + DOM equivalence proof; the
>   audit table pins zero cursor declarations across all
>   wrapper / node / inspector / hook files.
> - **v0.15.8 (Phase 4.2)** — extended ``styles-cursor-baseline``
>   guard from 1 test to 129 (covers wrappers + BaseNode + 15
>   per-kind node renderers + BaseInspector + 15 per-kind
>   inspectors + shared helpers + 17 sketch hooks).
> - **v0.15.9 (Phase 5.1)** — exhaustive 15-kind smoke + round-trip
>   sweeps across viewer (30 + 45 tests) and server (31 tests).
> - **v0.15.10 (Phase 5.2)** — ``structural-guards.test.tsx`` (44
>   tests): no-god-union-import + LOC budget + registry
>   completeness. CLAUDE.md Gate 2 LOC table updated.
> - **v0.16.0 (Phase 5.3)** — ``reset_complete_check`` kill-switch
>   in ``hooks/pre_commit_gate.py`` + ARCHITECTURE.md Domain
>   layer section + final DECISIONS pin.
>
> **Verification status at v0.16.0:**
>
> - viewer: 361 / 361 vitest + tsc clean.
> - server: 256 / 256 pytest + mypy clean + ruff clean.
> - structural reset complete = single boolean now reads true via
>   ``reset_complete_check``.

### `다음` — Architectural review: cursor / auto-layout coupling

> **Completed:** 2026-05-10 in v0.14.3.
> **Outcome:** [D-2026-05-11-C](./DECISIONS.md).
> Pre-commit gate + static guard + plot-verifier default sweep
> shipped. (Full diagnosis preserved in the file's prior revision
> and the D-entry.)

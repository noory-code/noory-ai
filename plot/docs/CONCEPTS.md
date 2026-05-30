# Plot Concepts (v0.12)

The conceptual reference for Plot — what each canvas, kind, and design
principle means, with examples. This document is the source of truth
that both human users and the AI tooling (Claude, MCP) consult when
they need to know "what is a `service`?" or "where does a `mission_ref`
live?".

> **Read [`IDENTITY.md`](IDENTITY.md) first** if you haven't. It defines
> what Plot *is* (a strategic operations design + alignment tool, not a
> mindmap) and the four use purposes every kind below ultimately serves.
>
> Sibling docs:
> - `IDENTITY.md` — what Plot is and is not (the "why and for whom").
> - `PHILOSOPHY.md` — the underlying value-flow / two-layer thesis.
> - `ROADMAP.md` — the implementation order in which v0.10 is being built.

## Symbol — the cross-canvas referenceable master (v0.24.11, D-2026-05-19-D)

Plot has an asymmetric **producer → consumer** flow between canvases:

```
Producers (define Symbols)              Consumers (use Symbols)
─────────────────────────              ─────────────────────────
Foundation canvas                       Service canvas
  ├─ Mission                              (when designing a service,
  ├─ Core Value         ──referenced──→   drag-drop a Symbol → it lands as
  └─ Identity                             a mission_ref / value_ref /
                                          identity_ref / actor_ref alias
Actors canvas                             node carrying notes_in_context)
  ├─ Actor
  └─ Sub-Actor                          ServiceDetail canvas
                                          (same *_ref pattern + step / rule
                                          / content / metric per-flow)
```

A **Symbol** is any node of the 5 candidate kinds (`mission`, `core_value`,
`identity`, `actor`, sub-actor) that lives on the producer side. **Every
instance of these kinds is a Symbol** — there is no per-node "is this a
symbol?" toggle, because the answer is always yes for these kinds and
never for any other kind. The consumer side references Symbols via the
4 alias kinds (`mission_ref` / `value_ref` / `identity_ref` /
`actor_ref`); the referent is the Symbol id, and the alias node may
carry `notes_in_context` to override field text per-service-context
without mutating the master (4-ref symmetry per [D-2026-05-17-M](./DECISIONS.md)).

This formalises the two-plane structure described in
[`PHILOSOPHY.md`](./PHILOSOPHY.md) — *"관계론적 가치 + 서비스 = 허브노드 +
2층 구조"*. Symbols are the **left plane** (identity / who).
Services are the **right plane** (value-creating hub). Cross-plane
edges + `*_ref` aliases are how they connect.

### What this replaces (history)

Pre-v0.24.11, the field `is_root` on actor nodes was framed as a
"cross-canvas master marker" (SPEC.md §Publish eligibility). In
practice the boolean distinguished nothing — every actor is a
Symbol candidate. The field for actor is deprecated per
[D-2026-05-19-D](./DECISIONS.md); `service.is_root` remains as the
ServiceDetail anchor marker (still load-bearing for that one role).

The original v0.2 intent of `is_root` (singleton trunk per tree, with
its own embedded Mission/Values/Identity per "organisation-side
identity" vs "product-side identity") evaporated in the v0.13 reset
(Foundation kinds became their own nodes on the Foundation canvas, not
embedded in actor/service roots). The field carried a retrofitted
meaning ("cross-canvas master") that this section now formalises as
the Symbol concept, sitting on the kind itself rather than on a per-
instance flag.

---

## Canvases — 4 kinds, each answering a different question

| Canvas | Asks | Holds (kinds) |
|---|---|---|
| **Foundation** | Who are we, and why do we exist? | `project`, `mission`, `core_value`, `identity` |
| **Actors** | Who participates? | `actor` |
| **Services** (top) | What value do we create and exchange? | `project`, `category`, `service` |
| **Service Detail** (modal, per-service) | How does this one service work inside? | `actor_ref`, `mission_ref`, `value_ref`, `identity_ref`, `metric`, `step`, `decision`, `rule`, `content` |

> **v0.11.4** — `project` is also auto-seeded on Actors and Services
> canvases (label-synced from Foundation) so every primary canvas
> visually radiates from the same project anchor.
>
> **v0.11.5** — the Services top view now carries **only**
> `project` + `service`. All composition, references, and value flow
> (metric / step / actor_ref / mission_ref / value_ref / identity_ref)
> live exclusively on Service-Detail canvases, where sub-service
> decomposition already happens. The previous "anchor required" hard
> validator on Services is dropped accordingly. The stencil for a
> Service-Detail canvas now generates **one draggable per master** —
> 10 missions = 10 mission ref entries, each labelled with the
> master's actual name. Drops are direct (no picker).
>
> **v0.12** — what used to be a "top-level service" is now a
> `category` (a thematic grouping). The Services canvas now reads as
> `project → category → service`, with services as **leaves**
> (sub-service is gone — service hierarchy is exactly two levels).
> Service detail is no longer a separate canvas screen; double-clicking
> a service opens a **modal overlay** containing the same content
> (sub-service is gone, but actor_ref / foundation refs / metric /
> step / rule / content / typed fields all still live there).

Foundation defines the project's identity. Actors lists the participants.
Services maps the value economy at a high level — `category → service`.
Double-clicking a service opens its **Service Detail modal** where the
actual work happens — rules, content, metrics, steps, and the actors
that interact via reference symbols.

---

## Foundation kinds — identity, time-independent

### `project` — the project anchor

Auto-seeded, exactly one per project, cannot be deleted. Sits at the
centre of every primary canvas (Foundation, Actors, Services) as a
circle so the mental model "everything spreads out from the project"
reads at a glance — v0.11.4.

- **Asks**: which project is this?
- **Count**: exactly 1 on Foundation (enforced); 1 visible copy on each
  of Actors / Services (auto-seeded, label-synced from Foundation).
- **Label**: mirrors `ProjectDoc.name` on every canvas it appears on;
  editing one of them updates `ProjectDoc.name` and propagates to the
  other copies.
- **Examples**: "BANAS", "Plot", "Auth Demo"

### `mission` — purpose, in space

What we do, why we do it, and where we're heading — **as positioning,
not as a timeline**. Vision and Goals are time-axis concepts; mission
is space-axis.

- **Asks**: what do we do every day, why, and in what direction?
- **Count**: 0..N. A small project may have one; a multi-product org may
  carry several at different layers.
- **Typed fields** (all stored on the node):
  - `what_we_do` — present tense ("we run a community where everyone is
    a fan of someone else").
  - `why` — the reason ("we want people to see each other shine").
  - `direction` — the positioning ("toward an everyday-hero economy");
    no time component.
- **AI use**: when Claude is asked to evaluate a design decision, it
  reads `mission` nodes to check alignment.

### `core_value` — the decision standard

If `mission` is what we do, `core_value` is **how** we behave when
choices conflict. Static (nouns / adjectives), invoked at decision time.

- **Asks**: when there's a conflict, what do we hold to?
- **Count**: 0..N (typically 3–7).
- **Typed fields**:
  - `label` — the value's name ("Tolerance", "Trust", "Speed").
  - `definition` — one or two sentences.
  - `do` (optional, AI-friendly) — concrete behaviours that embody it.
  - `dont` (optional, AI-friendly) — anti-patterns.
- **AI use**: Claude consults `do`/`dont` when simulating "what would
  this team decide?".

### `identity` — a facet of how we appear

Where `mission` is action and `core_value` is criterion, `identity` is
the **expression** — voice, tone, energy, visual feel. Each `identity`
node holds **one facet**.

- **Asks**: how do we look and sound?
- **Count**: 0..N. BANAS uses five (Voice, Energy, Speech style, Visual
  tone, Principles), but other projects may carry just one.
- **Typed fields**:
  - `label` — facet name ("Voice").
  - `description` — how the facet shows up.
  - `do` — what to do in this facet ("warm casual honorifics").
  - `dont` — what to avoid ("ㅋㅋ-style emoji").
- **AI use**: when Claude is asked to draft copy or imagine the brand,
  it reads `identity` nodes for tone and structure.

---

## Actor kind

### `actor` — a class of people participating in the value economy

> An actor is a **class of people** who participate in this project's
> value economy — making, exchanging, and relating to each other.
> (See `IDENTITY.md` for why this definition is load-bearing.)

- **Asks**: who is involved?
- **Class, not individual**: "User" / "Operator", not "Kim Cheol-su".
- **People only**: external APIs, systems, bots, and infrastructure
  are *not* actors — they belong to the **infrastructure** layer,
  which is out of scope until the time-axis (Mode 2) ships.
- **Count**: **≥ 2 per project** — typically an operator/developer
  side and a user side. Value exchange requires both sides; a project
  with fewer is structurally incomplete.
- **Lives on**: the Actors canvas as a master record.
- **Hierarchy**: `parent_id` chains express *is-a* refinement —
  the child is a more specific subclass of the parent. The dimension
  of refinement (subscription tier, fandom, role within a side, etc.)
  is left to the user; Plot doesn't pin it.

#### Actor classification, two orthogonal mechanisms (v0.11)

The two mechanisms are independent and combine freely:

1. **`side` typed field — flat category**
   Every actor declares which side of the value exchange they occupy.
   Values: `operator` (service operator/developer) or `user` (service
   participant/consumer). Two actors with different `side` values are
   structurally different parties; this is what the project-level
   "≥ 2 actor classes" floor checks.
2. **`parent_id` tree — is-a refinement**
   Within a side, sub-actors refine the parent class. *Example*:
   `Fan → Bartender's Fan` is one fandom inside the user side;
   `Operator → Moderator` is one role inside the operator side.
   The dimension of refinement is domain-specific.

This is the answer to "are admin/super-admin and fan/bartender's-fan
the same kind of relationship?" — **no**. Admin vs user is a `side`
distinction; super-admin within admin is a `parent_id` distinction.
Mixing them on one mechanism collapses meaning.

#### Actor typed fields (v0.11)

Mission-style typed fields, intentionally minimal:

- `motivation` — why this actor participates. Pulls them in.
- `pain` — frictions, frustrations, blockers. Pushes against them.

Standard persona-design pair (Goals/Pains, Motivations/Pains in
modern variants). Skip Do/Don't on actors — those work for kinds that
*model behaviour to imitate* (Identity, Core Value), not for the
acting subject itself. Permissions live on `rule.actor_permissions`,
not on the actor.

The Actors canvas is the **single source of truth** for actor
identities. Anywhere else in Plot that needs to refer to one, it does
so via `actor_ref` (see _Reference kinds_ below). v0.11 also
denormalises `side` onto each `actor_ref` so a service detail canvas
can validate its operator/user mix without cross-canvas lookups.

---

## Service kinds

### `category` — a thematic grouping of services (v0.12)

Categories are pure containers on the Services canvas. They don't
create value themselves; they just collect services that share a
common theme (e.g. "Admin" / "App" / "Backend"). Every service on
the Services canvas is nested under a category (`parent_id` →
category id).

- **Asks**: what kinds of service are we grouping here?
- **Counts**: 0..N. Categories are top-level on the Services canvas.
- **Lives on**: the Services canvas only.
- **Typed fields**:
  - `theme` — one-line common thread the category's services share.

`target_side` lives on `service`, not on `category`: a category's
own label usually telegraphs its side (Admin / App), and a single
category can intentionally mix sides at the service level
(e.g. a "Payments" category that bundles a user-facing checkout
service and an operator-facing settlement service).

### `service` — a playground for production and exchange

**v0.11.4 typed field — `target_side`** (`operator` / `user` / `both` / `null`)
classifies the service by which side of the value exchange it exists for.
This is the mirror image of `actor.side`:

| Service example | `target_side` | Tinted hue |
|---|---|---|
| Admin panel | `operator` | blue |
| User-facing app | `user` | red |
| Auth / backend service | `both` | violet |

The Inspector shows a Target side selector on every service. The on-canvas
service node body is tinted accordingly so the operator-vs-user split reads
at a glance — same picture, two layers of meaning.


> A service is a **playground** where stakeholders **produce and
> exchange value** while building relationships with each other.
> (See `IDENTITY.md` for why "produce + exchange" together — not
> "exchange" alone — is the right phrasing.)

The "playground" metaphor matters. A service is not a fixed pipeline
or a transaction queue; it's a space where:

- multiple actors act in parallel (concurrency),
- different kinds of activity coexist — making content, consuming it,
  trading, building relationships (diversity),
- the procedure isn't predetermined (degrees of freedom).

`service` is a **leaf** under a `category` (v0.12). The Services
canvas reads exactly two levels: `category → service`. There is no
sub-service; what used to be a "sub-service" is now the service
itself, and what used to be a "top-level service" is now a category.

- **Asks**: what value do we produce and exchange here, and who is
  involved?
- **Counts**: 0..N per category.
- **Lives on**: the Services canvas (as a leaf inside a category).
  Per-service composition (refs, metric, step, rule, content) lives
  on the **Service Detail modal** opened by double-clicking the
  service.
- **Forces a question**: every service prompts the user with "what
  value does this make?" — Plot's design intent is to make this
  question unavoidable at every level.

#### Service minimum baseline — the only hard floor

Every service must have **at least two participating `actor_ref`
nodes** — and an explicit operator must be one of them.

This is the single non-negotiable validator on services. It encodes
two claims from `IDENTITY.md`:

1. A playground with one person is not a playground; "produce +
   exchange" requires at least two parties.
2. The operator is **never implicit**. Without an explicit operator
   `actor_ref`, the question "who keeps this service aligned with the
   project's mission, values, and identity?" has no answer — and
   alignment ownership is precisely what Plot is meant to make
   visible.

Everything else on `service` follows the wider **rich fields, minimal
required** default — most fields stay optional so the template
prompts thinking without blocking flow.

#### Service typed fields (v0.12)

- `target_side` — `operator` / `user` / `both` / `null` (which side
  of the value exchange this service exists for; mirrors
  `actor.side`). Visualised as a node tint.
- `what` — one-line definition.
- `value_created` — the value it creates.
- `scope` — what it covers vs what is left to a sibling service.
- `trigger` — when it happens.
- `how` — the mechanism.
- `outcome` — what state results.
- `do` / `dont` — design constraints (AI-friendly).

All typed fields are **optional** by design — the template is rich
so it prompts thinking, but Plot never refuses to save a half-empty
service. The Inspector surfaces all of them in one section so the
strategic and operational thinking sit side by side.

Inside the service-detail modal, place `actor_ref` symbols to show
which actors participate, and `mission_ref` / `value_ref` /
`identity_ref` symbols to anchor the service to Foundation. The
exchange itself is captured in the actor_refs + typed fields
combination.

---

## Composition kinds (inside Service Detail)

These exist only inside a Service Detail modal, as `parent_id`
children of the service the modal is for.

### `rule` — policy, constraint, permission

Rules are anything that **constrains or governs** what happens inside
the service — not just policies and SLAs but also access rights and
permission matrices.

- **Asks**: what is enforced here? Who is allowed to do what?
- **Includes**:
  - Policies ("password must be at least 8 chars").
  - Constraints ("lock after 5 failed attempts").
  - SLAs ("p95 latency < 200ms").
  - **Permissions** — actor-by-actor CRUD matrices ("`user` can R/U/D
    own posts; `admin` can R/U/D any post").
- **Typed fields** (planned):
  - `label` — rule name.
  - `policy` — the rule itself.
  - `enforcement` — how it's enforced.
  - `actor_permissions` — optional permission map keyed by actor_ref.

### `content` — artefact, asset, output

Whatever the service produces or carries — data, files, tokens,
templates, messages.

- **Asks**: what does this service produce or handle?
- **Includes**: DB rows, image/MD files, session/JWT tokens, email
  templates, exported reports.
- **Typed fields** (planned):
  - `label` — content name ("Session token").
  - `format` — JSON, MD, binary, etc.
  - `producer` — actor_ref of who creates it.
  - `consumer` — actor_ref of who consumes it.

### `metric` — measurement (new in v0.10)

How we know the service is working. Quantitative or qualitative.

- **Asks**: how do we tell this service is doing its job?
- **Examples**: login success rate, p95 latency, CSAT, NPS.
- **Typed fields** (planned):
  - `label` — metric name.
  - `target` — the desired value (">99%").
  - `measurement` — how it's measured.

### `step` — sequence (new in v0.10)

The ordered sub-actions that make up the service. Use when a service
is a workflow more than an arena.

- **Asks**: in what order does this happen?
- **Examples**: an onboarding flow's "Verify email → Set password →
  Choose handle".
- **Typed fields** (planned):
  - `label` — step name.
  - `order` — sequence number.
  - `actor` — `actor_ref` of who acts in this step.
  - `outcome` — the state after the step.
  - `polarity` — `positive` / `negative` / `neutral` (default
    `neutral`), v0.28.2 (D-2026-05-30-E). Marks a **result** step's
    valence so failure cases read at a glance: `negative` tints the
    node red, `positive` green, `neutral` keeps the user's colour. The
    failure *reason* is the label / `outcome` text. Lets the flow model
    negative cases (로그인 실패 등), not just the happy path.

### `decision` — branch point (new in v0.28.0)

A flowchart **decision** (rendered as a diamond) between action
`step`s: a fork in the service flow. Two flavours, one node — a
**user choice** (방식 선택: email / Google / Magic) or a **system
judgment** (검증 성공 / 실패-이유). Promoting decision to its own kind
keeps `step` = *user action* intact: a system judgment is a
`decision`, never a `step`. See [D-2026-05-30-C](./DECISIONS.md).

- **Asks**: which way does the flow go here?
- **Examples**: "방식 선택?" (user picks a login method), "검증?"
  (system: success vs. wrong-password vs. no-account).
- **Branches**: the outgoing paths are **user-drawn labelled edges**
  (성공 / 실패 / a choice), not a stored field. Typed-failure results
  are ordinary result `step`s the decision branches to; validation
  rules (포맷 / 중복 / 비번 정책) are ordinary `rule` nodes.
- **Typed fields**:
  - `label` — the question ("검증?").
  - `body` — optional notes (Markdown).
- **Shape**: always a diamond, forced at the renderer (the shape *is*
  the semantic; same pattern as the producer-vs-reference shape rule —
  master kinds force a rounded rectangle, `*_ref` force a circle,
  D-2026-05-31-B).
- **Bounded context**: EssenceExecution (Service-Detail composition
  primitive, sibling of `step` / `metric` / `rule` / `content`).

### `group` — flow chunk (new in v0.29.0)

A **container** that chunks a busy ServiceDetail flow — e.g. collapse
the three OAuth branches into one "OAuth path" node. See
[D-2026-05-30-I](./DECISIONS.md).

- **Asks**: which parts of this flow read as one unit?
- **Membership**: `member_ids: string[]` — the SSOT lives on the group,
  so `step` / `decision` carry **no** group field. Created by
  multi-selecting nodes → "Group selected" (canvas context menu).
- **Collapse**: the group uses BaseFields `collapsed`. Collapsed → its
  members are hidden and the group shows a member count (reuses the
  fold ▾/▸ chrome). MECE with `category` — `category` is the
  Services-canvas *thematic* grouping of services; `group` is a
  ServiceDetail *flow* chunk.
- **Typed fields**: `member_ids`, `body`.
- **Bounded context**: EssenceExecution.

---

## Reference kinds — the symbol/component pattern

Plot reuses the symbol/component pattern from design tools (Figma,
Sketch). Each Foundation or Actor concept has a master node on its own
canvas, and **reference instances** can be placed on other canvases to
show "this concept matters here". Editing the master propagates
visually to its references.

- `actor_ref` — points at an `actor` master.
- `mission_ref` — points at a `mission` master.
- `value_ref` — points at a `core_value` master.
- `identity_ref` — points at an `identity` master.

Each ref kind is a separate kind, not a single generic one. They look
visually distinct, validate against the right master kind, and let the
AI ask "which Mission does this service realise?" rigorously.

### `actor_ref` typed fields (v0.11.2)

`actor_ref` carries the **per-actor-per-service value flow** — the
weakened form of PHILOSOPHY.md P6 ("arrows carry action and value").
The flow lives on the ref node rather than on an explicit edge.

- `gives` — what this actor gives to the service.
- `receives` — what this actor receives back.

Both optional. `service.value_created` is the aggregate; `gives` /
`receives` is each actor's individual exchange. The AI uses this pair
to reason about persona behaviour and service value economics without
having to parse free prose. The other ref kinds carry only the
`ref_*_id` link plus the auto-synced label (no value-flow fields —
the foundation refs aren't trade participants).

---

## Design principles

1. **Each kind is a distinct meaning unit.** Plot does not collapse
   different concepts into one kind. Mission ≠ Vision ≠ Goal; rule ≠
   content ≠ metric ≠ step. Each kind carries its own typed fields.

2. **Templates are rich, requirements are minimal — but the floor is
   real.** The Inspector surfaces many typed fields per kind to prompt
   thinking, and most are optional. A small set of hard requirements
   set Plot's quality floor — they encode what Plot *is*, not just
   nice-to-haves. The current floor (v0.12):
   - On the Services canvas, every `service` must sit under a
     `category` (no orphan services); every `category` must be
     top-level (no nested categories).
   - A project's `actors` canvas requires **≥ 2** actor classes.
   - Every service requires **≥ 2** `actor_ref` participants, and one
     of them must be an explicit operator (moderation /
     alignment-keeper). Foundation anchors (`mission_ref` /
     `value_ref` / `identity_ref`) live inside the per-service modal,
     not on the Services canvas itself.

   See `IDENTITY.md` for why these specific floors exist.

3. **AI-first.** Typed fields, `do`/`dont` pairs, and concrete examples
   make Plot canvases directly usable by Claude and other LLMs:
   structured JSON to read, do/dont guidance to imitate, examples to
   keep behaviour consistent.

4. **Two-surface storage: graph in JSON, typed content in MD
   templates.** (v0.13, Foundation only — other canvases follow in
   v0.14+.) A node's *graph data* (id, kind, position, label,
   parent_id, refs, ``details_path``) lives in
   ``{canvas}/canvas.json``. A Foundation node's *typed text* lives
   in ``{canvas}/{kind}-{slug}.md`` as a kind-specific
   heading-section template (``# Label`` / ``## Definition`` /
   ``## Do`` / ``## Don't`` / ``---`` / free prose). **MD is plain
   markdown — no YAML frontmatter.** Plot is the *schema author* and
   external editors (Obsidian, VS Code) are *value editors*; both
   may write the file. Read is **lenient** (missing or unknown
   sections become empty + a UI warning); write is **strict**
   (canonical heading order, schema-conformant). The file system is
   the SSOT; Plot UI is one editor on top of it.

   A frozen schema lives next to the project at ``.plot/{project}/
   schema/`` so the user can tell what each kind expects, and so
   external tools can validate independently. The schema is
   auto-exported on project create and stays in git with the data.

5. **Symbol/Component pattern for cross-canvas references.** A master
   lives on its home canvas; references on other canvases point at it.
   This keeps the SSOT clean and the visual surface flexible.

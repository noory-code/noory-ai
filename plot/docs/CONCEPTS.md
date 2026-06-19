# Plot Concepts (v0.12)

> ⚠ **정본 이전 (2026-06-19, `D-2026-06-19-J`):** kind·캔버스 *의미* 정본 =
> `repos-plot/docs/concepts/` (kinds.md · canvases.md), *와이어 필드* =
> `repos-plot/docs/specs/kinds-fields.md`. 충돌 시 root가 이긴다. 이 파일은 이력
> 레퍼런스 (마라톤 전 본문 — feature/note/entity 추가·6종 폐기 미반영).

The conceptual reference for Plot — what each canvas, kind, and design
principle means, with examples. This document is the source of truth
that both human users and the AI tooling (Claude, MCP) consult when
they need to know "what is a `service`?" or "where does a `feature`
live?".

> **Read [`IDENTITY.md`](../../../docs/IDENTITY.md) first** if you haven't. It defines
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
Foundation canvas                       Services overview
  ├─ Mission                              (a service's 5-field inspector
  ├─ Core Value         ──referenced──→   picks core_value / identity
  └─ Identity                             references as chips, plus
                                          actor references; "뒤 캔버스가
Actors canvas                             앞을 참조" — D-2026-06-17-B)
  └─ Actor (hierarchy)
                                        Feature canvas
                                          (actor_ref per participant —
                                          D-2026-06-17-H)
```

A **Symbol** is any node of the 4 candidate kinds (`mission`,
`core_value`, `identity`, `actor`) that lives on the producer side
(sub-actor is gone — actor hierarchy is now expressed with `parent_id`,
[D-2026-06-17-A](./DECISIONS.md)). **Every instance of these kinds is a
Symbol** — there is no per-node "is this a symbol?" toggle, because the
answer is always yes for these kinds and never for any other kind.

The consumer side references Symbols two ways. On the **Services
overview**, the service inspector picks `core_value` / `identity` /
`actor` references as chips ([D-2026-06-17-B](./DECISIONS.md)) — the
old standalone `mission_ref` / `value_ref` / `identity_ref` alias nodes
are retired (the service inspector chips replace them, D-2026-06-17-B/H).
On the **Feature canvas**, `actor_ref` nodes mark which actors
participate per feature. The referent is always the Symbol id.

### What this replaces (history)

Pre-v0.24.11, the field `is_root` on actor nodes was framed as a
"cross-canvas master marker" (SPEC.md §Publish eligibility). In
practice the boolean distinguished nothing — every actor is a
Symbol candidate. The field for actor is deprecated per
[D-2026-05-19-D](./DECISIONS.md); `service.is_root` was the
Service-Detail anchor marker. **(Superseded framing, D-2026-06-17-D/G:**
the Service-Detail canvas is now the **Feature** canvas and selecting a
service no longer drills — drilling moved to the `feature` kind. Whether
`is_root` is still used under the new drill model is a code-state TBD,
not re-asserted here.)

The original v0.2 intent of `is_root` (singleton trunk per tree, with
its own embedded Mission/Values/Identity per "organisation-side
identity" vs "product-side identity") evaporated in the v0.13 reset
(Foundation kinds became their own nodes on the Foundation canvas, not
embedded in actor/service roots). The field carried a retrofitted
meaning ("cross-canvas master") that this section now formalises as
the Symbol concept, sitting on the kind itself rather than on a per-
instance flag.

---

## Canvases — 5 kinds, each answering a different question

| Canvas | Asks | Holds (kinds) |
|---|---|---|
| **Foundation** | Who are we, and why do we exist? | `project`, `mission`, `core_value`, `identity` |
| **Actors** | Who participates? | `actor` |
| **Entities** | What things does the product handle? | `entity` (AI-maintained) |
| **Services** (overview) | What value do we create and exchange? | `project`, `category`, `service`, `feature` |
| **Feature** (per-feature, drill target) | How does this one feature behave? | `step`, `decision`, flow edges, `note`, `rule`, `actor_ref` |

> **v0.11.4** — `project` is also auto-seeded on Actors and Services
> canvases (label-synced from Foundation) so every primary canvas
> visually radiates from the same project anchor.
>
> **v0.12** — what used to be a "top-level service" is now a
> `category` (a thematic grouping). The Services overview reads as
> `project → category → service` (sub-service is gone).
>
> **2026-06-17 marathon** — the Services overview gains a **`feature`**
> kind nested under a service ([D-2026-06-17-D](./DECISIONS.md)):
> `category → service → feature`. **Selecting a service shows its
> 5-field inspector — it no longer drills.** **Clicking a `feature`**
> drills into what used to be the Service-Detail canvas — so that canvas
> is now the **Feature canvas** (a per-feature behaviour flowchart,
> [D-2026-06-17-G/H](./DECISIONS.md)). The old Service-Detail kind set
> (`mission_ref` / `value_ref` / `identity_ref` / `metric` / `content` /
> `group`) is retired from the feature canvas; the foundation refs now
> live as **inspector chips on the service** (D-2026-06-17-B), and the
> feature canvas keeps only `step` / `decision` / flow edges / `note` /
> `rule` / `actor_ref`. A new project-level **Entities** canvas
> ([D-2026-06-17-I](./DECISIONS.md)) holds the product's data objects.

Foundation defines the project's identity. Actors lists the participants.
Entities lists what the product handles. Services maps the value economy
at a high level — `category → service → feature`. Selecting a service
shows its 5-field inspector; clicking a **feature** opens its **Feature
canvas**, where the actual behaviour is laid out as a flowchart — steps,
decisions, rules, notes, and the actors that interact via reference
symbols.

---

## Foundation kinds — identity, time-independent

> **Essence has no node** ([D-2026-06-16-Q/R](./DECISIONS.md)). Plot
> needs no separate "essence (본질)" kind: the essence is the **emergent
> whole** of the three Foundation concepts — "our service is *this*
> mission + *this* core_value + *these* identities" — conveyed
> **visually by the composition** around the anchor, not stored in any
> container. Its irreducible core is the `mission` node (the root of
> existence); to read the one-line essence, read the mission. Foundation
> stays a **single canvas** (no audience split). The `project` anchor
> carries **only the project / service name** — a visual-grouping
> device, never a content holder.

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
- **Typed fields** (all stored on the node) — collapsed to a single
  declaration + body per [D-2026-06-16-J](./DECISIONS.md):
  - the **declaration** — the single one-sentence statement that *is*
    the node's primary text on the canvas (populates `label`; legacy
    `statement` folds into it on read). A mission is one indivisible
    declaration, not split across `what_we_do` / `why` / `direction`.
  - `body` — free-form prose elaborating the declaration.
- **AI use**: when Claude is asked to evaluate a design decision, it
  reads `mission` nodes to check alignment.

### `core_value` — the decision standard

If `mission` is what we do, `core_value` is **how** we behave when
choices conflict. Static (nouns / adjectives), invoked at decision time.

- **Asks**: when there's a conflict, what do we hold to?
- **Count**: 0..N (typically 3–7).
- **Typed fields** — collapsed to name + body per
  [D-2026-06-16-M](./DECISIONS.md):
  - `label` — the value's name ("Tolerance", "Trust", "Speed"). The name
    is load-bearing (referenced in decisions: "by '관용과 지지' we…").
  - `body` — the value's meaning *and the trade-off it makes* (what it
    chooses / what it sacrifices). The former `definition` field is
    removed (folded into `body` on read); `do` / `dont` pairs are
    dropped.
- **AI use**: Claude consults `core_value` nodes when simulating "what
  would this team decide?".

### `identity` — standing execution / expression rules

Where `mission` is action and `core_value` is criterion, `identity` is
the service's **consistent execution / expression standards, captured
as action-rules** ("we design / speak / behave like ~") that accumulate
into the service's character ([D-2026-06-16-N](./DECISIONS.md)). It is
**not** value-conflict judgment: `core_value` resolves *which value
wins when goods conflict* (a conflict-triggered tie-breaker), while
identity rules are **always-applied standing standards** for how every
output looks, sounds, and behaves (e.g. "design = vivid, appetising").
If the two collide, `core_value` adjudicates. The per-feature `rule`
kind is different again (operational policy).

`identity` is an **output** kind — AI-derived from mission + core_value
(+ accumulated behaviour) and evolving. "AI-derived" does **not** mean
silent auto-generation: the AI drafts the first rules, then interviews /
discusses with the user, and the user confirms (D-2026-06-16-O / P).

- **Asks**: how do we consistently execute and express ourselves?
- **Count**: 0..N. BANAS uses several (Voice, Energy, Speech style,
  Visual tone, Principles), but other projects may carry just one.
- **Typed fields** — reduced to name + an action-rule list per
  [D-2026-06-16-O](./DECISIONS.md):
  - `label` — the identity's name ("Voice").
  - the **action-rule list** — the rules are the content ("we use warm
    casual honorifics"; "we avoid ㅋㅋ-style emoji"). The former
    `description` field is dropped (folded into the rules).
  - `status` / `provenance` are **deferred** until the AI-derive flow
    (ROADMAP 5.7) gives them meaning — both are inert today.
- **AI use**: when Claude is asked to draft copy or imagine the brand,
  it reads `identity` nodes' action-rules and matches them.

---

## Actor kind

### `actor` — a relational role in the value economy

> An actor is a **role / class of participant** in this project's value
> economy — defined by position and resources, **not a person or
> persona** ([D-2026-06-17-A](./DECISIONS.md)). No demographics: one
> person can occupy several actor-roles, and roles can switch. Every
> actor both **gives and receives** value.
> (See `IDENTITY.md` for why this definition is load-bearing.)

- **Asks**: who is involved?
- **Role, not individual**: "User" / "Operator", not "Kim Cheol-su". A
  role is **relational** — a role alone is meaningless, so the Actors
  canvas shows the relationships between roles (see edge types below).
- **People only**: external APIs, systems, bots, and infrastructure
  are *not* actors — they belong to the **infrastructure** layer,
  which is out of scope until the time-axis (Mode 2) ships.
- **Count**: a project naturally carries at least an operator side and a
  user side — but this is an **emergent property** of the role hierarchy
  (operator/user at the top, D-2026-06-17-A), **not a hard ≥2 validator**
  (the old ≥2-actor-classes floor was dropped, D-2026-06-18-A).
- **Lives on**: the Actors canvas as a master record.
- **Hierarchy**: `parent_id` chains express *is-a* refinement — the
  child is a more specific role under the parent (user → hero, fan;
  operator → super-admin, manager). Actor inheritance is **core, not
  optional** (D-2026-06-17-A); the top split is operator vs user
  (`side`), inherited down to child roles.

#### Actor edge types — two, never confused (D-2026-06-17-A)

The Actors canvas carries **two distinct edge types**:

1. **hierarchy edge** ("is-a-kind-of") — structure only, no value; a
   quiet line expressing the `parent_id` tree.
2. **relationship edge** ("gives value to") — a **directed, labelled
   arrow** carrying *what value flows from which role to which* (hero
   →expertise→ fan). A reciprocal relationship is **two arrows** (hero
   →expertise→ fan; fan →support→ hero).

The Actors canvas shows the **general / role-defining** value flow; the
**concrete per-service exchange** (specific value, motivation/pain)
lives on `actor_ref` in the Feature canvas. Two levels: abstract
(Actors) → concrete (Feature).

#### Actor classification, two orthogonal mechanisms (v0.11)

The two mechanisms are independent and combine freely:

1. **`side` typed field — flat category**
   Every actor declares which side of the value exchange they occupy.
   Values: `operator` (service operator/developer) or `user` (service
   participant/consumer). Two actors with different `side` values are
   structurally different parties; the operator/user split is the **top
   of the role hierarchy** (D-2026-06-17-A).
2. **`parent_id` tree — is-a refinement**
   Within a side, child roles refine the parent class. *Example*:
   `Fan → Bartender's Fan` is one fandom inside the user side;
   `Operator → Moderator` is one role inside the operator side.
   The dimension of refinement is domain-specific.

This is the answer to "are admin/super-admin and fan/bartender's-fan
the same kind of relationship?" — **no**. Admin vs user is a `side`
distinction; super-admin within admin is a `parent_id` distinction.
Mixing them on one mechanism collapses meaning.

#### Actor typed fields (v0.11)

The actor master is **identity-only** — `side` + `body`
(D-2026-06-17-A). The per-service stake — `motivation` (why this actor
participates *here*), `pain` (what hurts *here*), and `gives` /
`receives` — does **not** live on the master; it lives on each
`actor_ref`, because participation is asymmetric and varies per service
(PHILOSOPHY P3, D-2026-06-15-J). Skip Do/Don't on actors — those work
for kinds that *model behaviour to imitate* (Identity, Core Value), not
for the acting subject itself. Permissions live on
`rule.actor_permissions`, not on the actor.

The Actors canvas is the **single source of truth** for actor
identities. Anywhere else in Plot that needs to refer to one, it does
so via `actor_ref` (see _Reference kinds_ below). v0.11 also
denormalises `side` onto each `actor_ref` so a feature canvas
can reason about each participant's side without cross-canvas lookups (the old operator/user-mix validator was dropped, D-2026-06-18-A).

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

A category's own label usually telegraphs its side (Admin / App), and a
single category can intentionally mix sides at the service level
(e.g. a "Payments" category that bundles a user-facing checkout
service and an operator-facing settlement service).

### `service` — a playground for production and exchange

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

A `service` sits under a `category` (v0.12), with `feature` nodes
nested under it ([D-2026-06-17-D](./DECISIONS.md)). The Services
overview reads `category → service → feature`. There is no sub-service;
what used to be a "sub-service" is now the service itself, and what
used to be a "top-level service" is now a category.

- **Asks**: what value do we produce and exchange here, and who is
  involved?
- **Counts**: 0..N per category.
- **Lives on**: the Services overview (under a category). **Selecting a
  service shows its 5-field inspector — it does not drill**
  (D-2026-06-17-D). The behaviour lives one level down: each `feature`
  under the service drills into its **Feature canvas** (steps, rules,
  notes, `actor_ref`).
- **Forces a question**: every service prompts the user with "what
  value does this make?" — Plot's design intent is to make this
  question unavoidable at every level.

#### Service participants — baseline

A service needs **at least one** participating `actor_ref`
(`D-2026-05-28-K`; the old hard "≥ 2 with an explicit operator" floor
was dropped, `D-2026-06-18-A`). The operator is the **default
participant** of every service (`D-2026-06-17-B`), so it need not be
asserted as a separate hard validator. The intent the old floor
encoded survives as guidance, not as a gate:

1. A playground with one person is not much of a playground; "produce +
   exchange" usually needs more than one party — a single-participant
   service is a smell worth questioning, not a blocked state.
2. Alignment ownership — who keeps this service consistent with the
   project's mission, values, and identity — still matters, but it
   follows from the operator being the default participant, not from a
   forced explicit-operator `actor_ref`.

Everything else on `service` follows the wider **rich fields, minimal
required** default — most fields stay optional so the template
prompts thinking without blocking flow.

#### Service inspector — 5 question-titled fields (D-2026-06-17-B)

The service inspector is **5 fields, in order**, each titled as a
question so the title doubles as the AI interview prompt
([D-2026-06-17-B](./DECISIONS.md), build-through-discussion D-16-P):

1. **"누가 참여하나?"** — selectable **actor** references (multi-select
   chips).
2. **"왜 필요한가?"** — typed (the gap / need the service fills; renames
   and reframes the old `problem`, dropping the negative "문제" framing).
3. **"뭐가 좋아지나?"** — typed (the improvement it creates; renames the
   old `value_created`).
4. **"뭘 양보 못 하나?"** — selectable **core_value** references
   (multi-select chips).
5. **"어떤 결로 다가가나?"** — selectable **identity** references
   (multi-select chips).

Core values and identities are **picked from the Foundation canvas
exactly like actors** (chips, not free-typed) — the "뒤 캔버스가 앞을
참조" principle. All three reference pickers are multi-select: one
service can hold several actors, core_values, and identities.

The old service text fields — **`what`, `scope`, `trigger`, `how`,
`outcome`, `do`, `dont`** — are **deleted** (not moved to detail): their
substance already lives on the Feature canvas as nodes (`step` = "how",
`rule` = "do/dont") and the per-participant behaviour (하는 일 / 받는 것
/ 페인, which varies per participant) lives on each `actor_ref` on the
feature canvas. Also deleted: **`target_side`** (redundant — participants
are shown directly via "누가 참여하나?", and each actor carries its own
side) and **`body`** (free memo — the 5 structured fields replace it).

### `feature` — a capability a service offers (D-2026-06-17-D)

A **`feature`** is a named capability nested under a service — 글쓰기 /
글편집 / 이모지 반응 — i.e. *what the service lets participants do*, one
level below the service ([D-2026-06-17-D](./DECISIONS.md)). 글쓰기/편집/
삭제 등은 서비스가 아니라 서비스가 제공하는 **능력**.

- **Asks**: what can a participant do in this service?
- **Counts**: 0..N per service.
- **Lives on**: the Services overview (nested under a service). It is the
  **drill target** — **clicking a feature opens its Feature canvas**
  (the behaviour flowchart that used to be the Service-Detail canvas).
- **Inspector**: a small inspector when selected — name + action summary
  (the feature's own inspector content is otherwise lean; open during
  implementation).
- **Promotion rule**: a proposed feature that turns out to carry its
  **own multi-actor value exchange is promoted to a `service`** (the
  value-exchange test). Built top-down by AI interview: rough intent →
  service (5-field interview) → AI-proposed features (human confirms).

Hierarchy: **카테고리 → 서비스 → 기능** (overview) → **행동 / 룰**
(Feature canvas).

---

## Feature-canvas kinds (inside a Feature canvas)

These exist inside a **Feature canvas** — the per-feature behaviour
flowchart (행동 → 분기 → 결과) reached by clicking a `feature`
([D-2026-06-17-G](./DECISIONS.md)). The canvas is the deepest layer
only, so Plot's upper layers stay non-flowchart and IDENTITY.md's "NOT
a flowchart tool" still holds. It inherits the service philosophy — it
is **actor-anchored and value-oriented** (PHILOSOPHY P5/P6), and stops
at action-altitude (user actions → branches → results; it does **not**
descend into implementation logic — that is the user's AI agent's job,
outside Plot).

The allowed kinds are exactly **`step` / `decision` / flow edges /
`note` / `rule` / `actor_ref`** ([D-2026-06-17-H](./DECISIONS.md)).
**Retired** from the old Service-Detail set: `mission_ref` / `value_ref`
/ `identity_ref` (now service-inspector chips, D-17-B — the feature
inherits them), `metric`, `content` (implementation artifacts are below
action-altitude = AI's job; user-facing artifacts are implied by the
producing action or carried by the flow edge), and `group` (its
chunking role is now the `feature` level; folding a busy flow is a
**view affordance, not a node kind**).

### `rule` — operational constraint (per-feature, D-2026-06-17-E)

Rules are **concrete operational / functional constraints** that
**govern** what happens inside the feature — password length, field
validation, limits, access rights, SLAs. A "policy" here is a concrete
operational constraint, **not** identity or core_value
([D-2026-06-17-E](./DECISIONS.md)): identity is brand voice / expression,
core_value is the conflict tie-breaker, and `rule` is operational. Rules
live **inside each feature's canvas, per feature** (provisional — a
genuinely cross-cutting policy spanning features/services is not modelled
yet, YAGNI).

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

### `note` — edgeless, canvas-global context (D-2026-06-17-F)

A **`note`** carries ambient context for the **entire feature canvas**
([D-2026-06-17-F](./DECISIONS.md)) — e.g. "이 기능은 모바일 우선 · 본문
500자 제한". It is **read by the human** as guidance **and is always-on
context the AI takes into account** when it designs / proposes on that
canvas (the canvas is a co-design surface, D-16-P).

- **Asks**: what context applies to this whole feature?
- **Edgeless invariant**: a `note` **never gains an edge** — it never
  connects to another node, because it is ambient, not a participant in
  the flow.
- **Scope**: applies canvas-globally; one or more allowed, each global.
  On the feature canvas for now (reusable elsewhere later if a need
  shows — YAGNI).

### `step` — sequence

The ordered sub-actions that make up the feature. Use when a feature
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
`step`s: a fork in the feature flow. Two flavours, one node — a
**user choice** (방식 선택: email / Google / Magic) or a **system
judgment** (검증 성공 / 실패-이유). Promoting decision to its own kind
keeps `step` = *user action* intact: a system judgment is a
`decision`, never a `step`. See [D-2026-05-30-C](./DECISIONS.md).

- **Asks**: which way does the flow go here?
- **Examples**: "방식 선택?" (user picks a login method), "검증?"
  (system: success vs. wrong-password vs. no-account).
- **Branches**: the outgoing paths are **labelled flow edges** (성공 /
  실패 / a choice), not a stored field; their meaning is governed by the
  edge's definition, not by who draws it ([D-2026-06-17-J](./DECISIONS.md)).
  Typed-failure results are ordinary result `step`s the decision branches
  to; validation rules (포맷 / 중복 / 비번 정책) are ordinary `rule`
  nodes.
- **Typed fields**:
  - `label` — the question ("검증?").
  - `body` — optional notes (Markdown).
- **Shape**: always a diamond, forced at the renderer (the shape *is*
  the semantic; same pattern as the producer-vs-reference shape rule —
  master kinds force a rounded rectangle, `*_ref` force a circle,
  D-2026-05-31-B).
- **Bounded context**: EssenceExecution (Feature-canvas behaviour
  primitive, sibling of `step` / `rule`).

> **`group` retired** ([D-2026-06-17-H](./DECISIONS.md)). The former
> flow-chunk `group` kind is removed from the feature canvas: the
> `feature` level now plays its chunking role, and folding a busy flow
> is a **view affordance, not a node kind**.

---

## Entity kind

### `entity` — a project-wide data object (D-2026-06-17-I)

A **`entity`** is one of the product's **data objects** (글 · 댓글 ·
사용자), held on a project-level **Entities** canvas — symmetric to
Actors (**액터 = 누가 / 엔티티 = 무엇**),
[D-2026-06-17-I](./DECISIONS.md). The user does **not** author it
manually: the AI surfaces entities **together with the user as a
byproduct of designing features / services** and auto-registers them
(the user reviews / refines / confirms — D-16-P, never silent). Born
bottom-up in feature work, managed top-down project-wide; populated last
(a derived surface that accumulates at the end).

- **Asks**: what thing does the product handle?
- **Altitude guard**: Plot holds only the **conceptual** entity — name +
  one-line "무엇을 담나" + rough relationships (사용자 ─쓴다─▶ 글). It is
  *ERD-like in shape* but explicitly **not a technical ERD**: no
  normalisation, no foreign keys, no cardinality, no field types — those
  (physical schema) are the user's AI agent's job, outside Plot (else
  Plot becomes a DB-modelling tool — identity violation).
- **Inspector** (when selected, lean / conceptual — D-2026-06-17-K):
  이름 + **"무엇을 담나?"** (one line, rough fields 제목·본문·작성자, no
  types/FK) + **어디서 쓰이나** (back-reference, read-only — which
  features reference it) + **거친 관계** (rough relationships to other
  entities).
- **Dedup**: before creating an entity the AI must **strongly
  semantic-match** the candidate against the existing registry (글 =
  게시물 = 포스트 → **one** entity); only genuinely ambiguous cases go to
  the user. Never silent-merge, never silent-duplicate (a first-class
  duty of the AI chat playbook, D-2026-06-17-K).
- **Edges allowed**: rough entity↔entity relationships may be drawn,
  including by the AI on this AI-maintained canvas — edges are governed
  by their definition, not by authorship (D-2026-06-17-J).

Feature actions **reference** entities ("발행 → 글 생성").

---

## Reference kinds — the symbol/component pattern

Plot reuses the symbol/component pattern from design tools (Figma,
Sketch). A concept has a master node on its home canvas, and **reference
instances** can be placed on other canvases to show "this concept
matters here". Editing the master propagates visually to its references.

- `actor_ref` — points at an `actor` master. The only standalone
  reference *node* that survives the 2026-06-17 marathon; it lives on the
  **Feature canvas** to mark which actors participate per feature.

The **foundation references** to mission / core_value / identity are no
longer standalone `*_ref` node kinds. They were **retired**
([D-2026-06-17-B/H](./DECISIONS.md)): a service's core_value and identity
references now live as **inspector chips on the service** ("뭘 양보 못
하나?" / "어떤 결로 다가가나?"), and the feature *inherits* them from its
service rather than duplicating ref nodes on the canvas.

### `actor_ref` typed fields (v0.11.2)

`actor_ref` carries the **per-actor-per-feature value flow** — the
weakened form of PHILOSOPHY.md P6 ("arrows carry action and value").
The flow lives on the ref node rather than on an explicit edge.

- `gives` — what this actor gives to the feature.
- `receives` — what this actor receives back.

Both optional. The "뭐가 좋아지나?" on the service is the aggregate;
`gives` / `receives` is each actor's individual exchange. The AI uses
this pair to reason about persona behaviour and value economics without
having to parse free prose.

---

## Design principles

1. **Each kind is a distinct meaning unit.** Plot does not collapse
   different concepts into one kind. Mission ≠ Vision ≠ Goal; `rule` ≠
   `step` ≠ `decision` ≠ `note`. Each kind carries its own typed fields.

2. **Templates are rich, requirements are minimal — but the floor is
   real.** The Inspector surfaces many typed fields per kind to prompt
   thinking, and most are optional. A small set of hard requirements
   set Plot's quality floor — they encode what Plot *is*, not just
   nice-to-haves. The current floor (v0.12):
   - On the Services canvas, every `service` must sit under a
     `category` (no orphan services); every `category` must be
     top-level (no nested categories).
   - A project's `actors` canvas naturally has at least an operator and a
     user role — emergent from the hierarchy, not a hard ≥2 validator
     (old floor dropped, D-2026-06-18-A).
   - Every service needs **≥ 1** `actor_ref` participant
     (D-2026-05-28-K); the operator is the default participant
     (D-2026-06-17-B), so the old "≥ 2 with an explicit operator" floor
     was dropped (D-2026-06-18-A). Foundation anchors (core_value / identity) are
     now **inspector chips on the service** ("뭘 양보 못 하나?" / "어떤
     결로 다가가나?", D-2026-06-17-B), not standalone ref nodes.

   See `IDENTITY.md` for why these specific floors exist.

3. **AI-first — built through discussion.** Every concept / node on
   every canvas is **created through discussion**: the AI is an active
   coach that interviews / proposes, and the human reviews, refines, and
   confirms ([D-2026-06-16-P](./DECISIONS.md)). Two anti-modes are
   excluded — a lonely **blank form** with no AI, and **silent
   auto-generation** committed without the user. Typed fields and
   concrete examples still make canvases directly usable by Claude and
   other LLMs (structured JSON to read), and the AI's per-turn context is
   delivered through a **context envelope** behind a CAG/RAG seam
   ([D-2026-06-17-L](./DECISIONS.md)): active canvas + selection +
   upstream-canvas summary + entity registry + on-demand detail.

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
   This keeps the SSOT clean and the visual surface flexible. After the
   2026-06-17 marathon the only standalone reference *node* is
   `actor_ref` (on the Feature canvas); the foundation references
   (core_value / identity) are surfaced as **service-inspector chips**
   instead ([D-2026-06-17-B/H](./DECISIONS.md)).

6. **Edges are governed by their definition, not by who draws them**
   ([D-2026-06-17-J](./DECISIONS.md)). What an edge *means* — its
   `relation` (flow / injection / inheritance) + payload (direction,
   label) — is what matters, not its author. The AI **may propose / draw
   edges**, especially on AI-maintained canvases (Entities); the user
   can always edit or delete them. A canvas may still be user-draw-only
   by its own spec (Foundation / Actors / Services currently are) — a
   per-canvas choice, not a global law. What stays banned is emitting a
   **meaningless or silently-uneditable** line.

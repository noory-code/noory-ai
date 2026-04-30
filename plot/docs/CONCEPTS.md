# Plot Concepts (v0.10)

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

## Canvases — 4 kinds, each answering a different question

| Canvas | Asks | Holds (kinds) |
|---|---|---|
| **Foundation** | Who are we, and why do we exist? | `project`, `mission`, `core_value`, `identity` |
| **Actors** | Who participates? | `actor` |
| **Services** (top) | What value do we create and exchange? | `service`, `mission_ref`, `value_ref`, `identity_ref` |
| **Service Detail** (per-service) | How does this one service work inside? | `service` (sub via `parent_id`), `rule`, `content`, `metric`, `step`, `actor_ref`, `mission_ref`, `value_ref`, `identity_ref` |

Foundation defines the project's identity. Actors lists the participants.
Services maps the value economy at a high level. Each service drills into
its own Service Detail canvas where the actual work happens — rules,
content, metrics, steps, and the actors that interact via reference
symbols.

---

## Foundation kinds — identity, time-independent

### `project` — the project anchor

Auto-seeded, exactly one per project, cannot be deleted. Sits at the
centre of the Foundation canvas as a circle.

- **Asks**: which project is this?
- **Count**: 1 (enforced)
- **Label**: mirrors `ProjectDoc.name`; editing one updates the other.
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

The same `service` kind is used at every depth: a top-level service
like _Auth_, a sub-service like _Login_ inside it, or a sub-sub-service
inside that. Depth is expressed by `parent_id`.

- **Asks**: what value do we produce and exchange here, who is
  involved, and (for sub-services) how does this contribute to the
  parent service?
- **Counts**: 0..N at every level.
- **Lives on**:
  - Top-level (no `parent_id`): the Services canvas.
  - Sub-service (`parent_id != null`): the parent service's Service
    Detail canvas.
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

#### Top-level service — strategic

Required typed fields:

- `label` — the service name.
- One of: an `identity_ref` or a `value_ref` — every top-level service
  must declare which Foundation it embodies.

Optional typed fields:

- `what` — one-line definition.
- `value_created` — the value it creates at a high level.
- `scope` — what it covers vs what is left to a sibling service.
- `do` / `dont` — design constraints (AI-friendly).

The surrounding canvas may also carry placed `mission_ref` /
`value_ref` / `identity_ref` symbols to make the alignment visible.

#### Sub-service — operational

All typed fields are **optional** by design — the template is rich so
it prompts thinking, but Plot never refuses to save a half-empty
sub-service.

- `value_created` — what specific value this contributes.
- `trigger` — when it happens.
- `how` — the mechanism.
- `outcome` — what state results.
- `do` / `dont` — design constraints.

Around the sub-service, place `actor_ref` symbols to show which actors
participate. The exchange itself is captured in the actor_refs +
typed fields combination.

---

## Composition kinds (inside Service Detail)

These exist only inside a Service Detail canvas, as `parent_id`
children of the service node they decompose.

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
   nice-to-haves. The current floor:
   - A `services` canvas with at least one top-level service requires
     **≥ 1 Foundation anchor** (`mission_ref` / `value_ref` /
     `identity_ref`) on the same canvas — alignment ownership must be
     visible at the top view.
   - A project's `actors` canvas requires **≥ 2** actor classes.
   - Every service requires **≥ 2** `actor_ref` participants, and one
     of them must be an explicit operator (moderation /
     alignment-keeper).

   See `IDENTITY.md` for why these specific floors exist.

3. **AI-first.** Typed fields, `do`/`dont` pairs, and concrete examples
   make Plot canvases directly usable by Claude and other LLMs:
   structured JSON to read, do/dont guidance to imitate, examples to
   keep behaviour consistent.

4. **`details.md` is free prose, never mirrored.** Long-form writing,
   tables, and Mermaid diagrams live in the per-node `details.md`
   file. Plot never parses or duplicates that content into the canvas
   JSON, so external editors (Obsidian, VS Code) can edit the file
   without sync conflicts.

5. **Symbol/Component pattern for cross-canvas references.** A master
   lives on its home canvas; references on other canvases point at it.
   This keeps the SSOT clean and the visual surface flexible.

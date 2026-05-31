# BANAS simulation — backlog

> Live tracking of everything surfaced while populating the real BANAS
> blueprint into Plot (2026-05-31 →). The user fires findings/requests
> rapidly; nothing here is dropped. Status: ✅ done · 🔨 in-progress ·
> 💡 idea (needs design/direction) · ⏳ awaiting user.

## Shipped (committed + pushed)

| # | Item | Ship |
|---|---|---|
| ✅ | Category nodes render with rounded corners | v0.36.2 (D-2026-05-31-AB) |
| ✅ | "+ New folder" in Add-a-Project picker | v0.37.0 (D-2026-05-31-AC) |
| ✅ | **Node click selection sticks** (controlled array carries `selected`) | v0.37.1 (D-2026-05-31-AD) |
| ✅ | **Auto-layout collision avoidance** — no overlapping nodes (Services 11→0) | v0.37.2 (D-2026-06-01-A) |
| ✅ | **Node auto-fit content** (+ anchor, edges, tag margin, layout uses real size; manual resize removed) | v0.38.0 (D-2026-06-01-B) |

## In progress

- (none — node auto-fit shipped v0.38.0)

## Ideas — need design / direction

- 💡 **Foundation intermediate hub node** — user: *"파운데이션 … 아이덴티티
  하고 코어밸류는 중간에 앵커 노드가 하나 더 있어야되겠다."* Today all 20
  foundation nodes inject straight into the BANAS anchor (cluttered). Add a
  mid-level grouping hub per cluster: `BANAS ← [핵심 가치 hub] ← {5 values}`
  and `BANAS ← [아이덴티티 hub] ← {14 identities}` (mirrors how Services
  groups under categories). OPEN: new foundation-group concept vs reuse an
  existing kind; does it inject or just group.
- 💡 **Service-scoped identity in Foundation** — some "identity" I placed in
  Foundation is actually service-specific (디자인 톤/컬러/감정 여정 etc.).
  Ideas given: (A) define in Foundation + a service references it via
  `identity_ref` (scope = who references); (B) move pure service-local
  identity into that service's body/detail; (C) design-system tokens aren't
  "identity" — separate layer. Decision rule drafted; awaiting user pick.

## Awaiting user verify

- ⏳ **Selection fix** (v0.37.1) — confirm real clicks select & stay (my
  synthetic probe can't fully reproduce RF's d3 click path).

## Process note

User (2026-06-01): *"지금 던지는거 다 작업하고 내가 하는 말 못따라가겠다면
어디 기록해둬야합니다."* → this file is that record. Work through it; don't
drop items.

## Active (surfaced 2026-06-01, not yet shipped)

- 🔨 **B — Services auto-layout: cluster children near their parent**, not in
  concentric depth-ring layers. User: *"하위노드를 왜 상위노드에 가깝게 정렬을
  안하는거죠? 마치 레이어가 있는 것처럼 … 상위노드에 가깝게 정렬을 해야지."*
  My v0.34.8 radial depth-ring places all depth-k nodes on one ring (anchor-
  relative radius), so a service sits far from its category. Fix: parent-
  relative branch placement (each subtree fans out from ITS parent at a small
  radius) — a radial *tree*, not concentric rings. Touches
  `computeRadialLayout`. Biggest open item; layout is sensitive (cf. the
  v0.13/v0.34 layout saga) — confirm approach before rewriting.
- 💡 **A — Foundation group hub needs a MODEL change.** The server rejects
  non-`{mission,core_value,identity,project}` kinds on the Foundation canvas
  (422 "kinds not allowed on 'foundation'"). So the user's "핵심 가치 /
  아이덴티티 group hubs" (mission stays direct) can't be added as data — Plot
  must either allow a grouping kind on Foundation or add a dedicated
  foundation-group kind (+ stencil + structural/parity tests). OPEN: which.

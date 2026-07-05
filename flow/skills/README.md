# skills/

Flow procedure skills (mapped onto Agent Teams when available; parallel subagents otherwise). **4 entry points** (user-invocable) + **28 assets** (loaded by the main via `Read`).

- **Entry points** (user-invocable): `flow` (Initiative/Epic/Story/Action orchestration) · `meta` (Skill/Rule/Prompt/Subagent meta management) · `flow-pr` · `flow-verify-commit`
- **Assets** (the main `Read`s per Phase):
  - `flow-*` — planning(epic/story/action) · procedure(initiative/epic/story/action) · phases · completion · branch · archive · retrospective(+templates) · scale-judgment · trigger-classify · issue-handling · playbook-selection · upstream-publish · must-not
  - `debate-protocol` · `debate-redteam` · `handoff-protocol` — debate(RT) · delegation protocols
  - `meta-*` — agent/playbook/skill/rule/prompt creation procedures + the `meta-skill-writing` authoring standard

> 4 tiers: **Initiative → Epic → Story → Action** (`flow-procedure-initiative` is the top). Scale judgment is `flow-scale-judgment`.

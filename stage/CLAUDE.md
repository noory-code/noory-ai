# CLAUDE.md — Stage

Guidance for work inside `stage/`. Repository-wide rules live in the root `CLAUDE.md`.

## What Stage is for

**A stage the heroes can run wild on — but it has to have a purpose.**

Execution stays free; purpose stays strict. Stage never tells the executor how to work. It insists
that work hangs from a purpose and that someone independent judges whether that purpose landed.

Read [docs/PHILOSOPHY.md](docs/PHILOSOPHY.md) before changing gates, skills, or the work contract.
It owns why Stage is shaped this way — who it is for, what counts as an achievement and what is
only maintenance, and why choosing where to cut the work is the design. Changing a rule without reading
it usually means re-deciding something already decided.

## Document language

Explanation is written in Korean, contracts in English.

- Korean: `docs/PHILOSOPHY.md`, `docs/BLUEPRINT.md`, `docs/DISCUSSION.md`,
  `docs/IMPLEMENTATION_AUDIT.md` — a person reads these to understand.
- English: `docs/SCHEMA_V4.md`, `docs/SCHEMA_V5.md`, `README.md`, skills, hooks, scripts, and this
  file — hooks and agents follow these.

## Tests

Stage carries no uv, mypy, or ruff target. It is plain stdlib and runs on any host `python3` 3.9+.

```bash
python3 -m unittest discover -s stage/hooks/tests -q
python3 -m unittest discover -s stage/scripts/tests -q
python3 stage/scripts/audit_stage.py
```

The scripts suite takes about eighty seconds; the hooks suite takes about one. Store the narrow
command on a work card and run the full suites at close — `operations/documentation.md` and the
`stage-work` skill own that rule.

## Release

Do not hand-edit the manifests. Run
`python3 stage/scripts/release_plugin.py stage --bump <patch|minor|major>`, which requires a
non-empty `## Unreleased` section in `CHANGELOG.md`.

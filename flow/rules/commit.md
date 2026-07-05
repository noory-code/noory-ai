# Git Commit Rules

> **Scope**: all commit work. Independent of work type, language, and framework.
> This file is a flow rule that auto-loads when placed in `.claude/rules/`. Use plain-text/backtick references only (no markdown links).

## TL;DR (core 6)

1. **Conventional Commits**: `type: subject` (feat/fix/docs/style/refactor/test/chore/perf/ci/build/revert)
2. **Issue number**: if the project issue tracker has a number, include it in the subject or footer (e.g. `PROJ-1234`)
3. **Work-based commit**: on Action completion, `[epic][story][action] content`
4. **Atomic commit**: 1 commit = 1 responsibility, a verifiable unit (only logically related files)
5. **Commit immediately**: after build/test/lint pass
6. **Subject**: within 50 chars, imperative, lowercase start, no period

## Type

`feat` feature / `fix` bug / `docs` documentation / `style` formatting (no behavior change) / `refactor` refactoring / `test` test / `chore` config / `perf` performance / `ci` CI·CD / `build` build / `revert` revert

## Structure

```
<type>: <subject> (PROJ-NNNN)

<body>

<footer>
```

- General commit example: `feat: add user profile page`
- Work-based commit example: `[checkout][US-001-cart][implement] implement quantity-change logic` / `[hooks][TS-001-regression][test] add regression test`
  - `epic-name` = Epic folder name / `story-title` = Story folder name (User Story `US-NNN-*` or Technical Story `TS-NNN-*` — `ssot-vocabulary`) / `action-title` = role (design/implement/test/docs)
- Issue number: `(PROJ-1234)` at the end of the subject, or `Fixes PROJ-1234` in the footer. If multiple, `(PROJ-1234, PROJ-1235)`. The format follows the project tracker convention.

## Commit timing

- ✅ After an independently verifiable unit of work is complete + build/test/lint pass
- ❌ Multiple features at once / incomplete code

> Pre-commit check = the 6 TL;DR items above (Conventional/work-based format · Subject ≤50 chars·imperative·lowercase·no period · single responsibility · build·test pass · issue number when applicable).

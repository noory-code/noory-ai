---
id: W-00000313
title: rag 서버에 ruff·mypy 를 들이고 지적을 정리한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "cd rag/server && uv run pytest -q -m 'not slow'"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: rag/server/pyproject.toml, rag/server/uv.lock, rag/server/src/, rag/server/tests/, rag/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000313 rag 서버에 ruff·mypy 를 들이고 지적을 정리한다

## Purpose

rag 를 목적별 여러 스타일로 넓히기 전에, 저장소 관례대로 린트와 strict 타입 검사가 깨끗한 바닥에서 시작하게 한다

## Actions

- 지금 상태(2026-11-01): rag 시험은 dev 의존성을 깔면 통과하지만 ruff·mypy 가 rag 의 dev 의존성에 없다. evonest 설정
  기준으로 ruff 22개, mypy strict 11개가 나온다(라이브러리 타입 정보 부재 3개 포함).
- `rag/server/pyproject.toml` 의 dev 추가 의존성에 ruff·mypy 를 넣고 evonest 와 같은 설정을 둔다. 타입 정보가 없는 igraph,
  leidenalg, sqlite_vec 는 mypy override 로 뺀다. `uv lock` 은 새 도구만 더하고 기존 해석은 바꾸지 않는다.
- 동작을 바꾸지 않고 지적을 고친다. `ruff format` 으로 전체를 다시 쓰는 일은 하지 않는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- rag/server 안에서 uv run ruff check src/ tests/ 와 uv run mypy src/ 가 저장소 관례 설정(evonest 와 같은 ruff 규칙·줄 길이 100, mypy strict)으로 오류 없이 끝나고, 그 도구가 rag 의 dev 의존성으로 잠긴다
- 기존 rag 시험(slow 제외)이 그대로 통과해 정리가 동작을 바꾸지 않았음을 보인다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision

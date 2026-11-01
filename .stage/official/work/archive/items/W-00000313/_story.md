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
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000313
promotion: not_applicable
review: passed
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


### Executor report at close — 2026-11-01

```
What changed: rag/server/pyproject.toml adds ruff and mypy to the dev extra and configures them like evonest (ruff target py311, line length 100, rules E F I N W UP; mypy strict with warn_return_any and warn_unused_configs) plus the pydantic mypy plugin and an override for igraph, leidenalg, and sqlite_vec, which ship no type information; uv.lock only adds mypy, ruff, and their dependencies (marker lines the newer uv rewrote for cuda-toolkit extras were restored, and uv lock --check passes); ruff --fix sorted imports, removed unused ones, moved Callable, Iterator, and Iterable to collections.abc, used datetime.UTC, and dropped quotes from annotations in modules that import annotations from __future__; by hand: the Cypher path-length query uses an f-string with a comment that depth is a clamped int, IncompatibleSnapshot is renamed IncompatibleSnapshotError (all uses are inside rag), two long test lines are wrapped, vector_sqlitevec raises RuntimeError if SQLite reports no inserted row id instead of passing None to int(), embedder_st drops an unused type-ignore and returns the query row through np.asarray, and build_fastmcp() is annotated to return FastMCP; rag/CHANGELOG.md gains an Unreleased section with the entry.
Why: W-00000313 - start the planned rag retrieval-style work from a server that passes the repository's lint and strict type checks.
Decisions made: Mirror evonest's ruff and mypy settings, the repository's existing clean reference, rather than invent a new rule set; enable the pydantic mypy plugin instead of rewriting default_factory fields; exempt the three untyped libraries instead of writing stubs; restore the lock's cuda-toolkit marker lines so this card does not change dependency resolution; rename the exception because nothing outside rag imports it; do not run ruff format, which would rewrite 17 files for style only; out-of-scope paths changed: none.
Work not done: The 13 slow tests download embedding models and cannot run here: the environment's proxy returns 403 for the model host, so they were not run; encode_query was checked with a stand-in model instead and still returns a 1-D float32 vector. ruff format is not applied.
```

## Verification

2026-11-01 클라우드 세션에서 코드 커밋 `e6cecb2f` 의 worktree 로 `stage/operations/cloud-execution.md` 절차대로
닫았다. 리뷰는 `stage/scripts/claude_review_companion.py` 대역으로 이 프로젝트의 `implementation` 리뷰 명령을
설정 변경 없이 돌렸다. 같은 모델 계열의 판정이므로 교차 venue 판정이 아니다. slow 시험 13개는 모델 호스트가 이 환경의
프록시에 막혀(403) 돌리지 못했다.


### Executed at close — 2026-11-01

```
$ cd rag/server && uv run pytest -q -m 'not slow'
[exit 0]
........................................................................ [ 59%]
.................................................                        [100%]
121 passed, 13 deselected in 4.81s
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.

$ cd rag/server && uv run ruff check src/ tests/
[exit 0]
All checks passed!
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.

$ cd rag/server && uv run mypy src/
[exit 0]
Success: no issues found in 23 source files
warning: The `UV_NATIVE_TLS` environment variable is deprecated and will be removed in a future release. Use `UV_SYSTEM_CERTS` instead.

$ python3 -m unittest discover -s tests -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 0.002s

OK
```

### Review at close — 2026-11-01

```
Review report: .stage/.runtime/driver/logs/W-00000313.md
Criteria:
- PASS: rag/server 안에서 uv run ruff check src/ tests/ 와 uv run mypy src/ 가 저장소 관례 설정(evonest 와 같은 ruff 규칙·줄 길이 100, mypy strict)으로 오류 없이 끝나고, 그 도구가 rag 의 dev 의존성으로 잠긴다
  Reason: pyproject.toml copies evonest's ruff (py311, line 100, E F I N W UP) and mypy strict settings, adds pydantic plugin plus an override for the three untyped libraries, and puts ruff/mypy in the dev extra; uv.lock diff is 291 additions with no deletions; the fixes in the diff target the reported findings, and the driver's close checks run ruff and mypy themselves (this reviewer could not run them).
- PASS: 기존 rag 시험(slow 제외)이 그대로 통과해 정리가 동작을 바꾸지 않았음을 보인다
  Reason: Source diff is behavior-preserving (import moves, UTC alias, equivalent f-string, exception rename with no remaining old-name references, an unreachable None guard, an explicit float32 cast); test edits only follow the rename and wrap lines; the driver's close checks run the non-slow pytest suite; the Decisions made and Work not done fields state the purpose, report no out-of-scope paths, and disclose the 13 unrun slow tests and the skipped ruff format.
```

## Retrospective


## Promotion decision

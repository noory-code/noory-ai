---
id: W-00000289
title: codex 명령이 설치된 컴패니언 스크립트를 찾아 쓴다
kind: fix
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_codex_companion.py -q"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000289
promotion: not_applicable
review: passed
scope: stage/scripts/codex_companion.py, stage/scripts/tests/test_codex_companion.py, .stage/settings.json, stage/CHANGELOG.md
promotes:
decision_refs: DE-00000079
---

# W-00000289 codex 명령이 설치된 컴패니언 스크립트를 찾아 쓴다

## Purpose

codex 플러그인 버전이 바뀌거나 다른 컴퓨터에서 돌려도 드라이버·리뷰 명령이 말없이 깨지지 않게 한다.

## Actions

- 지금 동작: `.stage/settings.json` 의 codex 실행·리뷰·프로필·회수 명령 일곱 곳이
  `/Users/woogis/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs` 를 직접
  부른다. 다른 컴퓨터·클라우드에서는 돌지 않고, codex 플러그인이 1.0.6 이 아닌 버전으로 바뀌면
  모든 codex 리뷰와 실행이 깨진다.
- `stage/scripts/codex_companion.py` 가 실행 때 컴패니언 스크립트를 찾아 `node` 로 돌린다. 찾는 순서는
  `STAGE_CODEX_COMPANION` 환경 변수, Claude Code 가 `~/.claude/plugins/installed_plugins.json` 에 적은
  `codex@openai-codex` 설치 경로, 플러그인 캐시의 가장 높은 버전이다.
- 일곱 명령이 그 스크립트를 부르게 바꾼다. 회수 명령은 Node 안에서 `status`·`cancel` 을 부르는
  자리를 같은 스크립트로 바꾼다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 에 한 줄을 더한다.

## User value

codex 플러그인을 업데이트하거나 다른 컴퓨터·클라우드에서 열어도 리뷰와 실행이 그대로 돈다. 깨지면
무엇을 찾았는지 적힌 오류로 바로 드러난다.

## Scope

### Included


### Excluded

- codex 플러그인을 클라우드에 설치하는 일.
- Stage 템플릿(`settings.jsonc`) — 템플릿은 이 경로를 담지 않는다.

## Risks

- `installed_plugins.json` 의 형식은 Claude Code 가 정한다. 이 세션에서 확인한 V2 형식(`plugins` 아래
  플러그인 ID 마다 `scope`·`installPath` 를 담은 항목 목록)을 따르고, 읽지 못하면 캐시로 넘어간다.
- 클라우드에는 codex 가 없어 고친 명령이 실제 codex 로 도는지는 여기서 확인할 수 없다(DE-00000079).

## Success criteria

- settings.json 의 codex 명령 일곱 곳이 특정 사용자 홈과 플러그인 버전을 담은 경로를 쓰지 않는다는 것을 테스트가 확인한다
- codex 플러그인 버전이 바뀌어도 명령이 설치된 컴패니언 스크립트를 찾아 실행한다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


### Executor report at close — 2026-10-31

```
What changed: Added stage/scripts/codex_companion.py, which runs the Codex companion with node after resolving it from STAGE_CODEX_COMPANION, then the codex@openai-codex installPath in ~/.claude/plugins/installed_plugins.json (user scope first), then the highest numeric version in the plugin cache, and exits 127 with what it searched when none is found; the six Codex task commands in .stage/settings.json call it, and the codex reaper's inline Node script lists and cancels jobs through it; tests cover each resolution step, the 127 path, argument and exit-code pass-through, the seven commands, and a reaper run against a fake companion that must cancel only the target card's job.
Why: W-00000289 - Codex commands must not break silently on a plugin update or another machine.
Decisions made: Resolve the recorded install path before the cache because Claude Code's install record names the version actually enabled, while the cache can keep older or newer versions; follow the V2 record shape seen in this session's Claude Code (plugin id mapped to entries with scope and installPath) and fall through to the cache when the record is unreadable; keep the script in stage/scripts and call it by a project-relative path because every command already runs from the project root; keep the Stage template untouched because it never contained this path.
Work not done: None.
```

## Verification

2026-10-31 클라우드 세션에서 코드 커밋 `2fdd7a58` 의 worktree 로 닫았다. 이 세션에는 codex 가 없어,
사용자 지시에 따라 `STAGE_CODEX_COMPANION` 을 `claude -p` 로 같은 프롬프트를 돌리는 대역 스크립트로
두었다. 그래서 이 프로젝트의 `implementation` 리뷰 명령과 프롬프트를 설정 변경 없이 그대로 썼다. 판정한
새 Claude 세션은 실행자와 맥락을 나누지 않지만 같은 모델 계열이므로 교차 venue 판정이 아니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s stage/scripts/tests -p test_codex_companion.py -q
[exit 0]
----------------------------------------------------------------------
Ran 10 tests in 0.361s

OK

$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (258 earlier lines omitted)
WARNING: reapers.codex is not configured after executor turn; jobs may remain
[W-00000001] executor failed; retry 1/3
WARNING: preflights.codex is not configured; continuing without a venue health check
WARNING: reapers.codex is not configured after executor turn; jobs may remain
WARNING: reapers.claude is not configured after reviewer turn; jobs may remain
[W-00000001] completed on stage/driver/W-00000001-1793433913
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1793433913. Human review + merge required; the base branch was not modified.
Removed unattended worktree: /tmp/tmpua9xxrsl/unattended/W-00000001-1793433913
Landed W-00000001 from stage/worktree/W-00000001 and removed its worktree and branch
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Schema-v5 migration aborted; the exact pre-migration Stage tree was restored.
Ignoring unrelated schema-v4 migration journal.
Schema-v5 migration complete: 3 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Migration refused: Pending promotion machinery must finish before migration: .runtime/intents/W-00000001.json
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
Stage project already uses schema v5; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 responsibility relocation complete; continuing to schema v5.
Schema-v5 migration complete: 2 flat work card(s) moved into the hierarchy.
This command does not commit. Its successful transaction journal was removed; review the working tree before committing.
----------------------------------------------------------------------
Ran 684 tests in 121.076s

OK
```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000289.md
Criteria:
- PASS: settings.json 의 codex 명령 일곱 곳이 특정 사용자 홈과 플러그인 버전을 담은 경로를 쓰지 않는다는 것을 테스트가 확인한다
  Reason: ProjectSettingsTest checks the six task commands (executor, reviewer, four strengths, count asserted as 6) and the reaper for absence of codex-companion.mjs and /Users/ and presence of the resolver call; settings.json has no /Users/, codex-companion.mjs, or 1.0.6 left.
- PASS: codex 플러그인 버전이 바뀌어도 명령이 설치된 컴패니언 스크립트를 찾아 실행한다는 것을 테스트가 확인한다
  Reason: ResolveCompanionTest covers override, recorded installPath with scope ranking, fall-through when the recorded path lacks the script, numeric highest-version cache choice (1.0.10 over 1.0.9), and none-found; CLI tests cover the 127 error, argument and exit-code pass-through via node, and a reaper run that cancels only the target card's job.
```

## Retrospective

[R-00000289](../../retrospectives/R-00000289.md).

## Promotion decision

이 카드가 연결한 결정은 일회성 venue 예외(DE-00000079)뿐이므로 `not_applicable`이다.

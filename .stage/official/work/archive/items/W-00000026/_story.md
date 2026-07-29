---
id: W-00000026
title: 설정 파일에 주석을 달 수 있게 한다
kind: development
venue: codex
priority: medium
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000067
promotion: not_applicable
scope: stage/hooks/, stage/scripts/, stage/templates/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000026 설정 파일에 주석을 달 수 있게 한다

## Purpose

프로젝트 설정 파일에는 키만 있고 각 키가 무엇을 하는지가 없다. 파일 안에 설명을 달 수 있게
하고, 새로 만드는 프로젝트에는 설명이 달린 파일을 준다

## Source

사용자 요청 2026-07-13.

## User value

설정 파일을 여는 사람이 각 키가 무엇인지 그 자리에서 안다. 지금은 `guidance_overrides`처럼
오늘 생긴 키를 봐도 무슨 뜻인지 알 방법이 없어 플러그인 문서를 뒤져야 한다.

## Scope

### Included

- 설정을 읽을 때 `//`와 `/* */` 주석을 걸러낸 뒤 파싱한다.
- 파일 이름으로 `settings.json`과 `settings.jsonc`를 모두 받는다. 하나만 있어야 하며,
  앞으로 새로 만드는 것은 `settings.jsonc`다.
- 새 프로젝트를 만들 때 각 키에 설명이 달린 `settings.jsonc`를 준다.
- 감사가 두 이름을 모두 알아보고, 둘 다 있으면 오류로 알린다.
- 기존 프로젝트는 아무것도 하지 않아도 그대로 동작해야 한다.

### Excluded

- 설정 스키마 변경. 키를 더하거나 빼지 않는다.
- 자동 변환. 기존 `settings.json`을 `settings.jsonc`로 바꿔주지 않는다.

## Dependencies

W-00000067(완료, 0.41.0)이 선행이었다. 설정을 읽는 자리는 이제 하나다.

## 이미 확인된 것

- 읽는 자리: `stage/hooks/stage_paths.py`의 `read_settings()` 하나다. 경로를 만들고 파싱하는
  것도 여기뿐이며, 못 읽었을 때 무엇을 할지는 부르는 쪽이 각자 정한다. 그 구조를 깨지 말 것.
- **쓰는 자리가 따로 있다.** `stage/scripts/migrate_stage.py`가 `schema_version`을 다시 써
  넣고(`json.dumps`로 파일 전체를 새로 만든다), `stage/scripts/init_stage.py`가 새로 만든
  파일에 `language`를 써 넣는다. 읽는 자리만 고치면 이쪽이 주석을 지운다.
- 새 프로젝트가 받는 설정 원본: `stage/templates/v4/project-stage/settings.json`. 지금 키는
  `schema_version`, `language`, `guidance_overrides`, `operations_overrides`, `venue_routing`,
  `governance`, `extra_write_tools`, `review` 여덟이다.

## Risks

- 주석을 지우는 처리가 문자열 안의 `//`를 건드리면 설정이 깨진다. 예: 경로나 URL.
- 두 파일이 다 있는 프로젝트에서 어느 쪽을 읽을지 조용히 고르면 설정이 무시된 줄 모른다.
  고르지 말고 오류로 멈출 것.
- **다시 쓰는 쪽이 주석을 지운다.** 마이그레이션이 스키마 번호를 박을 때 파일 전체를 다시
  만들면 사용자가 쓴 설명이 통째로 사라진다. 값 한 줄만 바꾸든지, 주석이 있는 파일은 다시
  쓰기를 거부하고 사람에게 시키든지 — 어느 쪽이든 "조용히 지움"은 안 된다.

## Success criteria

- 주석이 달린 설정 파일이 정상적으로 읽힌다.
- 문자열 안의 `//`가 주석으로 잘못 지워지지 않는다(회귀 테스트).
- 마이그레이션이 스키마 번호를 박은 뒤에도 주석이 남아 있다(회귀 테스트).
- 두 이름이 동시에 있으면 감사가 오류로 알린다.
- 주석 없는 기존 `settings.json`만 있는 프로젝트가 그대로 동작한다.
- `python3 -m unittest discover -s stage/scripts/tests -q`와 `-s stage/hooks/tests -q` 통과.

## Next action

codex 창에서 아래로 시작한다.

```
python3 stage/scripts/start_work.py --project-root . W-00000026 \
  --scope "stage/hooks/, stage/scripts/, stage/templates/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json"
```

테스트부터 쓴다. 커밋하지 않는다 — 검토와 커밋은 맡긴 쪽이 한다(`stage-handoff`의 위임 실행).

venue: codex(development).

## Progress

구현은 codex 창이 위임 실행했고(모델 `gpt-5.6-sol`), 검토와 커밋은 claude 창이 했다.

주석을 지울 때 **같은 개수의 공백으로 바꾼다.** 그래서 문자열 안의 `//`가 데이터로 남고, 원본
파일에서 값의 위치가 그대로 유지된다. 뒤의 성질이 쓰는 쪽을 가능하게 했다 — 값 하나만 정확히
잘라 바꾸므로 주석이 손대지지 않는다.

쓰는 쪽 둘(마이그레이션의 스키마 번호, init의 언어)이 새 함수를 쓴다. 주석이 있는 파일에
바꿀 키가 아예 없으면 다시 쓰지 않고 소리내어 실패한다. 조용히 형식을 갈아엎지 않는다.

두 이름이 동시에 있으면 오류다. 어느 쪽을 읽을지 코드가 고르면, 프로젝트가 믿는 설정과 실제
적용되는 설정이 갈릴 수 있다.

검토에서 확인한 것: 테스트 314개(3개 늘었다)와 327개(3개 늘었다) 통과, 검사 오류 0 경고 0.
위험 셋이 전부 테스트로 덮였다 — 문자열 안의 주석 기호, 두 이름 동시 존재, 그리고 실제로
마이그레이션을 돌린 뒤 사용자 주석과 URL 안의 `//`가 살아있는지.

알아 둘 차이 하나: 마이그레이션이 값 하나만 바꾸게 되면서, 주석이 있는 파일에는 예전처럼
`operations_overrides` 기본값이 파일에 새로 채워지지 않는다. 읽는 쪽이 전부 기본값을 주고
읽으므로 동작은 같다.

## Verification

### Executed at close — 2026-07-25

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (7 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1784985215 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784985215
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1784985215. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784985216 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1784985216. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784985216 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784985216
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1784985216
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1784985216 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784985216
[W-00000003] completed on stage/driver/W-00000001-1784985216
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1784985216. Human review + merge required; the base branch was not modified.
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 314 tests in 30.281s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 327 tests in 0.922s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision

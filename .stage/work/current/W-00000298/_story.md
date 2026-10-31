---
id: W-00000298
title: 실제 codex 플러그인으로 codex 명령 경로 찾기를 확인한다
kind: qa
venue: codex
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000298
promotion: not_applicable
review: not_required
scope: stage/scripts/codex_companion.py, .stage/settings.json
promotes:
decision_refs:
---

# W-00000298 실제 codex 플러그인으로 codex 명령 경로 찾기를 확인한다

## Purpose

클라우드에서 가짜 컴패니언으로만 시험한 codex 명령이 실제 설치된 codex 플러그인으로 리뷰와 실행을 해내는지 로컬에서 확인한다.

## Actions

- 실제 작업 하나(W-00000288)를 로컬 Codex 드라이버로 실행하고 `close_work.py` 로 닫아, 실행과 닫기
  리뷰가 모두 `stage/scripts/codex_companion.py` 를 거치게 한다. 시험용 가짜 작업을 따로 만들지 않는다.

## User value

클라우드에서 바꾼 Codex 명령 경로를 이 컴퓨터의 실제 플러그인으로 한 번 끝까지 돌려 봐서, 드라이버와
닫기 리뷰를 믿고 쓸 수 있다.

## Scope

### Included

- 실제 설치된 Codex 플러그인으로 실행 한 판과 닫기 리뷰 한 번을 끝까지 돌린 증거

### Excluded

- `codex_companion.py` 와 설정을 고치는 일. 문제가 나오면 따로 카드로 만든다.

## Risks

- 증거 파일(판정 JSON, 작업 로그)은 git 에 올라가지 않는 `.stage/.runtime/` 에 있다. 그래서 핵심
  내용을 이 카드의 Verification 에 옮겨 적는다.


## Success criteria

- 로컬에서 codex 리뷰 한 번과 codex 실행 한 판이 codex_companion.py 를 거쳐 끝나고 판정 파일과 실행 보고가 남는다

## Next action

## Related truth

## Progress

- 2026-10-31 `python3 stage/scripts/codex_companion.py status --json` 이 실제 companion 을 찾아
  정상 응답했다. 찾은 설치본은 Claude Code 설치 기록(`~/.claude/plugins/installed_plugins.json`)의
  `codex@openai-codex` 1.0.6(`~/.claude/plugins/cache/openai-codex/codex/1.0.6`)이다.
- 같은 날 W-00000288 을 `drive.py --execute` 로 실행했다. 실행 명령은
  `python3 stage/scripts/codex_companion.py task --model gpt-6-astra --effort high --write ...` 였다.
- 이어서 `close_work.py` 로 W-00000288 을 닫았다. 닫기 리뷰(`review.stages.implementation` =
  `standard`)도 `python3 stage/scripts/codex_companion.py task ... --fresh --write` 로 돌았다.

## Verification

- Codex 실행 한 판: W-00000288 작업 로그(`.stage/.runtime/driver/logs/W-00000288.md`)에 Codex 가 쓴
  `### Executor report` 한 개가 남았다. 소스 변경은 커밋 `7bb28cad` 다.
- Codex 리뷰 한 번: 닫기 리뷰가 판정 파일(`.stage/.runtime/driver/verdicts/W-00000288.json`)을 직접
  썼다. 내용은 `approved: true`, 기준 판정 `PASS` 다. 닫기 기록은 커밋 `112667ff` 다.
- 두 명령 모두 플러그인 경로를 직접 적지 않고 `codex_companion.py` 를 거쳤다.

### Executed at close — 2026-10-31

```
$ test -f .stage/.runtime/driver/verdicts/W-00000288.json
[exit 0]


$ grep -q '"approved": true' .stage/.runtime/driver/verdicts/W-00000288.json
[exit 0]


$ grep -q '^### Executor report' .stage/.runtime/driver/logs/W-00000288.md
[exit 0]


$ python3 stage/scripts/audit_stage.py
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

## Retrospective

[R-00000298](../../retrospectives/R-00000298.md).

## Promotion decision

이 카드는 결정을 소유하지 않으므로 `not_applicable`이다.

---
id: W-00000369
title: 닫을 때 카드에 붙는 출력을 판정 한 줄로 줄인다
kind: development
venue: claude
environment: local-no-codex
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000369
promotion: not_applicable
review: passed
scope: stage/skills/stage-retrospective,stage/operations/review.md,stage/scripts,stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000369 닫을 때 카드에 붙는 출력을 판정 한 줄로 줄인다

## Purpose

닫힌 카드가 명령 출력과 리뷰 전문 없이 리뷰마다 기준별 판정 한 줄만 가진다

## Actions


## User value


## Scope

### Included


### Excluded

- 드라이버가 판과 판 사이에 받는 리뷰는 카드에 적지 않는다. 드라이버는 리뷰어를 직접 실행하고 닫는 명령을
  거치지 않는다. 그 자리를 고치려면 드라이버 두 개(`driver_supervised.py`, `driver_unattended.py`)의 판
  처리를 건드려야 하는데, 지금은 드라이버를 실제로 실행해 확인할 수 없다.
- 드라이버가 닫을 때 `## Progress` 에 붙이는 실행 보고 네 줄은 그대로 둔다.


## Risks


## Success criteria

- 새로 닫은 카드의 닫기 기록이 리뷰 한 번마다 날짜와 판정한 쪽과 기준별 통과 여부를 적은 줄이고, 명령 출력과 리뷰 이유 글은 카드에 없다
- 닫는 명령이 실행한 리뷰가 되돌려 보내면 그 줄이 카드에 남아서, 저장소만 읽고 닫을 때 되돌려 보낸 횟수를 셀 수 있다
- 이미 보관된 카드는 고치지 않는다

## Next action

## Related truth

- 덜어낼 것을 고른 결정: DE-00000089 의 1번.
- 닫을 때 카드에 적히는 것의 계약: `stage/operations/review.md` 의 `What close writes on the card`.

## Progress

- 닫는 명령이 카드에 붙이던 명령 출력 블록과 리뷰 이유 블록을 없앴다. 대신 두 가지 줄을 적는다.
  - `- Checks at close <날짜>: <개수> passed — <명령들>`
  - `- Review at close <날짜> by <판정한 쪽>: approved 또는 rejected (1 PASS, 2 FAIL, ...)`
- 닫을 때 받은 리뷰가 되돌려 보내면 그 줄을 열린 카드에 적는다. 맨 위 설정 칸은 고치지 않는다.
- 판정한 쪽의 이름: 자율 실행 카드는 리뷰하는 venue, 그 밖에는 리뷰 명령의 `--label`. `codex` 라벨을
  `STAGE_CODEX_COMPANION` 이 대신했으면 그 파일 이름을 적는다.
- 리뷰어가 쓴 이유와 보고는 전과 같이 작업 로그에 남는다. 작업 로그는 커밋되지 않는다.
- 테스트 5개를 먼저 썼고 고치기 전에는 모두 실패했다. 예전 형식을 확인하던 테스트 7개를 새 형식으로 옮겼다.
- `stage/operations/review.md`, 작업 로그 머리말, 변경 기록을 고쳤다.

## Verification

맥북(macOS)에서 코드 커밋 `b4a8271a` 로 실행했다.

| 명령 | 결과 |
|---|---|
| `python3 -m unittest discover -s stage/scripts/tests -p test_close_work_record.py` | 5개 통과 |
| `python3 -m unittest discover -s stage/hooks/tests -q` | 450개 통과 |
| `python3 -m unittest discover -s stage/scripts/tests -q` | 795개 통과, 2개 건너뜀 |
| `python3 stage/scripts/audit_stage.py` | 오류 0건, 경고 32건 |

- 성공 기준 2번은 닫는 명령이 실행한 리뷰에만 해당한다. 드라이버가 판 사이에 받는 리뷰는 카드에 남지 않는다.
- 이미 보관된 카드는 고치지 않았다.
- 드라이버로 카드를 닫는 흐름은 실제로 실행해 보지 않았다.
- 성공 기준 2번을 고쳤다. 처음에는 "되돌려 보낸 리뷰도 닫힌 카드에 한 줄로 남아서, 저장소만 읽고 리뷰가
  되돌려 보낸 횟수를 셀 수 있다" 였다. 리뷰가 닫는 명령과 드라이버 두 곳에서 실행된다는 것을 모르고 쓴
  기준이다. 사용자에게 드라이버 쪽을 빼는 것을 알렸고 사용자가 그대로 닫으라고 했다.
- 닫기 리뷰는 맥북에서 Claude 대역(`claude_review_companion.py`)으로 받는다. 같은 모델의 리뷰다(DE-00000086).
- 사용자 확인 — 2026-11-21. 고친 내용, 드라이버 쪽을 뺀 것, 확인한 것과 확인하지 않은 것을 보고받고
  "확인, 닫으세요" 라고 했다(DE-00000087).

- Checks at close 2026-11-21: 3 passed — `python3 -m unittest discover -s stage/scripts/tests -p test_close_work_record.py`; `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/audit_stage.py`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS, 3 PASS)

## Retrospective

## Promotion decision

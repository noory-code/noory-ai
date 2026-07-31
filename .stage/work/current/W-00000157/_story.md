---
id: W-00000157
title: 드라이버 시험이 물려받은 환경 변수에 흔들리지 않게 한다
kind: fix
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: completed
retrospective_ref: R-00000157
promotion: not_applicable
review: not_required
scope: stage/scripts/tests/
promotes:
decision_refs:
---

# W-00000157 드라이버 시험이 물려받은 환경 변수에 흔들리지 않게 한다

## Purpose

드라이버는 판정하는 쪽에 환경 변수 몇 개를 넘긴다 — 이전 판정 파일이 어디 있는지, 어느 기준이
떨어졌는지 같은 것. 그 변수가 깔린 창 안에서 시험을 돌리면 드라이버 시험 둘이 거짓으로 실패한다.
시험이 자기 값을 직접 넣는 대신 그 창에 이미 있는 값을 읽기 때문이다.

두 번째 바퀴부터만 드러난다. 첫 바퀴에는 이전 판정 파일이 없어서 변수가 안 실린다.

**이 카드가 만든 문제가 아니다.** 판정한 쪽이 바뀐 파일을 되돌린 사본에서도 똑같이 실패하는 것을
확인했다(2026-07-30, W-00000155 두 번째 바퀴).

실패하는 시험 둘:

- `test_second_review_only_rechecks_failures_and_changed_segment` — 오류로 끝난다.
- `test_missing_previous_verdict_falls_back_to_full_review` — 이전 판정이 없다고 봐야 하는데
  있다고 본다.

## Actions

- 시험이 물려받은 환경을 지우고 자기 값만 쓰게 한다. 지울 변수 일곱 개:
  `STAGE_CHANGED_PATHS_FILE`, `STAGE_PREVIOUS_REVIEW_VERDICT_FILE`,
  `STAGE_REVIEW_FAILED_CRITERIA_FILE`, `STAGE_REVIEW_MODE`, `STAGE_REVIEW_VERDICT_FILE`,
  `STAGE_WORK_ITEM_PATH`, `STAGE_WORK_LOG_PATH`.
- 시험 둘만 고치지 말고 시험 묶음 전체가 같은 보호를 받게 한다. 지금 실패하는 둘만 고치면 다음에
  변수 하나가 늘 때 같은 일이 또 생긴다.

## User value

드라이버가 도는 중에 시험을 돌려도 결과를 믿을 수 있다. 지금은 거짓 실패를 만나면 사람이 원인이
자기 변경인지 환경인지 가려내야 하고, 이번에 판정하는 쪽이 그 확인에 한 번의 리허설을 썼다.

## Scope

### Included

- 드라이버 시험 묶음의 환경 격리.

### Excluded

- 드라이버 자체. 검사 명령은 이 문제에 안 걸린다 — 판정용 변수는 판정하는 쪽에만 실리고, 검사는
  드라이버 자신의 환경으로 돈다. 드라이버를 판정 창 안에서 다시 띄우는 경우만 예외다.

## Risks

- 환경을 통째로 지우면 시험이 실제로 필요한 값까지 사라질 수 있다. 지울 변수를 이름으로 집는다.

## Success criteria

- 일곱 변수가 깔린 창에서 시험 묶음을 돌려도 통과한다.
- 그 변수가 없는 평소 창에서도 그대로 통과한다.
- 사람이 겪는 결과: 드라이버 두 번째 바퀴 뒤에 시험을 돌려도 거짓 실패가 안 나온다.

## Next action

일곱 변수를 깔고 시험 묶음을 돌려 실패를 재현한다.

## Progress

## Verification

## Retrospective

## Promotion decision

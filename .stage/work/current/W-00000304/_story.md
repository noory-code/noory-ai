---
id: W-00000304
title: 사용량 한도로 끝난 리뷰는 시도를 쓰지 않는다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/scripts/driver_review.py, stage/scripts/tests/test_drive.py, .stage/state/observations/O-00000053.md, .stage/state/current.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000304 사용량 한도로 끝난 리뷰는 시도를 쓰지 않는다

## Purpose

리뷰어나 실행자가 사용량 한도로 일을 하지 못하고 끝났을 때 드라이버가 그 판을 실패한 시도로 세어 남은 기회를 태우지 않게 한다.

## Actions

- 지금 동작(O-00000053): `driver_review.infrastructure_failure()` 는 "timed out", "command not found", 종료 코드
  126·127, 신호 종료만 인프라 실패로 알아본다. 리뷰어(`claude -p`)가 "You've hit your session limit" 로 판정 파일
  없이 끝나면 리뷰 실패로 보고 시도를 하나 쓴다. 시도 상한이 3이라 한 번 걸리면 남은 기회가 줄고, 실행이 끝난 판의
  결과까지 버려진다.
- 서비스의 사용량 한도 메시지(Claude 의 session/usage limit, Codex 의 usage limit, HTTP 429, `rate_limit_error`)를
  인프라 표지에 더한다. 리뷰는 이미 "판정 파일이 없을 때만" 인프라 실패로 다시 돌리므로 그 규칙을 그대로 탄다.
- 표지는 실행자 실패 출력에도 쓰이므로, 시험 이름이나 문장에 흔히 나오는 넓은 말("rate limit")은 쓰지 않는다.
- O-00000053 을 닫는다.

## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 사용량 한도 메시지로 판정 파일 없이 끝난 리뷰와 실행이 시도를 쓰지 않는다는 것을 테스트가 확인한다
- 사용량 한도를 일반 문장으로 언급한 실패 출력은 인프라 실패로 보지 않는다는 것을 테스트가 확인한다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision

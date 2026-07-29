---
id: W-00000135
title: 병렬 정리가 도는 역할을 짐작하지 않고 기록에서 읽는다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/drive_parallel.py, stage/scripts/tests/test_drive_parallel.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000135 병렬 정리가 도는 역할을 짐작하지 않고 기록에서 읽는다

## Purpose

시간이 다 됐을 때 무엇이 돌던 중인지 drive_parallel 이 작업 로그 제목으로 짐작한다. 실행자가 보고를 쓰고도 계속 돌면 리뷰어로 오분류돼 엉뚱한 venue 를 거둔다(O-00000010). W-00000118 이 시도 기록에 running_role 을 적기 시작했으므로 읽는 쪽을 그 기록으로 바꾼다. 기록이 없는 옛 상태에서는 지금의 짐작으로 물러나고 그 사실을 출력에 말한다.

## Actions

- 시간 초과 시 거둘 venue 를 시도 기록의 `running_role` 에서 정한다. 로그 제목 짐작을 걷는다.
- `running_role` 이 없는 옛 기록에서는 기존 짐작으로 물러나고, 물러났다는 사실을 출력에
  말한다.

## Scope

`stage/scripts/drive_parallel.py` 와 그 테스트, CHANGELOG 미출시 절. `drive.py` 는 안
건드린다 — 기록을 만드는 쪽은 이미 끝났다(W-00000118).

## Success criteria

- 시간 초과 시 거둘 venue 가 시도 기록의 `running_role` 에서 나온다. 테스트가 고정한다.
- 실행자가 보고를 쓰고도 계속 도는 상황(로그에 보고 있음 + `running_role` 이 executor)에서
  실행자 venue 를 거둔다 — 짐작이 틀리던 그 경우를 테스트가 고정한다.
- `running_role` 이 없는 옛 기록에서는 기존 짐작으로 물러나고 그 사실이 출력에 남는다.
  테스트가 고정한다.
- 스크립트 스위트가 통과한다. CHANGELOG 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- [O-00000010](../../state/observations/O-00000010.md) — 이 카드가 닫는 관측


## Progress


## Verification


## Retrospective


## Promotion decision

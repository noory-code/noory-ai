---
id: W-00000228
title: 병렬 명령이 무인 모드를 그대로 넘긴다
kind: development
venue: codex
milestone:
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -p test_drive_parallel.py -q"
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

# W-00000228 병렬 명령이 무인 모드를 그대로 넘긴다

## Purpose

여러 카드를 무인으로 동시에 돌리려면 지금은 사람이 카드마다 드라이버 명령을 따로 띄워야 하므로, 병렬 명령이 무인 모드를 그대로 넘겨 한 번에 걸 수 있게 한다

## Actions

없음 — 병렬 명령에 옵션 하나를 통과시키고 회귀 시험을 더하는 한 덩어리다.

## User value

카드 여러 장을 무인으로 돌리는 것이 명령 한 번이 된다. 지금은 사람이 카드마다 드라이버를
따로 띄워야 해서, 무인 실행의 값(사람이 안 봐도 된다)이 시작할 때부터 깎인다.

## Scope

### Included

- 병렬 명령에 무인 모드를 넘기는 옵션을 만든다. 카드마다 `drive.py --unattended <카드>` 를
  띄운다.
- **무인일 때는 병렬 명령이 워크트리를 만들지 않는다.** 무인 드라이버가 이미 자기 워크트리와
  가지를 만들기 때문이다(`run_unattended_in_worktree`). 두 겹으로 만들면 안 된다. 그래서
  무인 실행에는 워크트리 준비·정리 단계가 걸리지 않는다.
- 겹침 검사는 그대로 걸린다. 카드들이 같은 자리를 선언하면 무인이든 아니든 거절한다.
- 회귀 시험을 `test_drive_parallel.py` 에 더한다.

### Excluded

- `drive.py` 는 안 고친다. 무인 모드 자체는 이미 있고 이 카드는 넘기기만 한다.
- 무인 실행 결과를 본 가지로 합치는 일은 안 만든다. 지금처럼 사람이 한다.

## Risks

- 워크트리를 두 겹으로 만들면 무인 드라이버가 엉뚱한 자리에서 돈다. 무인일 때 준비 단계를
  건너뛰는 것이 이 카드의 핵심이다.
- 정리 명령(`--cleanup`)은 병렬 명령이 만든 워크트리를 지운다. 무인 실행에는 그런 워크트리가
  없으므로, 무인으로 건 카드에 정리를 부르면 지울 것이 없다고 알리고 끝나야 한다.


## Success criteria

- 병렬 명령에 무인 옵션을 주면 카드마다 무인 드라이버가 돌고, 그 옵션이 없을 때의 기존 동작은 그대로다
- 무인으로 걸 때는 병렬 명령이 워크트리를 따로 만들지 않는다
- 겹침 검사가 무인 실행에도 그대로 걸린다

## Next action


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision

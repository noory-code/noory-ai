---
id: W-00000225
title: stage 0.59.0 을 낸다
kind: release
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000225 stage 0.59.0 을 낸다

## Purpose

드라이버가 죽어도 이어 가는 명령과 잘린 바퀴 인식을 비롯한 여섯 묶음이 아직 이 저장소 안에만 있으므로, 플러그인 버전을 올려 다른 프로젝트가 그것을 쓸 수 있게 한다

## Actions

없음 — 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 움직인다.

## User value

다른 프로젝트의 드라이버도 죽은 자리에서 이어 가고, 잘린 바퀴의 끝난 일을 알아보고, 카드
크기에 맞는 시간을 받는다. 보관 명령이 계층에서 안 죽고, 감사가 두-자리 허가증을 잡는 것이
시험으로 붙들리고, 초기화 문장이 현재 트리를 가리키고, 훅 시험이 셸에 안 흔들린다. 지금은
전부 이 저장소 안에만 있다.

## Scope

### Included

- 부 버전을 올린다(0.58.0 → 0.59.0). 드라이버에 새 명령(`--resume`)이 생겼으므로 고침이
  아니라 기능이다.
- 쌓인 변경 기록 여섯 묶음에 그 버전 제목을 붙이고 다음을 위한 빈 자리를 연다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- 릴리스를 한 번에 커밋하고 푸시한다.

### Excluded

- 다른 프로젝트를 옮기지 않는다. 보태는 변경이라 옛 프로젝트가 그대로 돈다.
- 마일스톤에 걸지 않는다. M-00000003 의 완료 기준은 "사람 개입 없이 스스로 닫힌 병렬 실행이
  있었다"인데 릴리스는 그 칸을 움직이지 않는다(O-00000027 이 남긴 규칙).

## Risks

- 릴리스는 푸시까지가 한 몸이라 되돌리기가 비싸다. 감사와 시험을 먼저 통과시킨다
  (훅 361, 스크립트 595, 둘 다 통과 확인함).
- 코덱스 런타임이 새 버전 캐시를 못 집으면 다음 세션의 훅이 막힌다(P-00000001).


## Success criteria

- 두 매니페스트와 변경 기록이 0.59.0 하나를 말한다
- 릴리스가 원격에 올라가 다른 프로젝트가 받을 수 있다
- 감사가 오류 없이 통과한다

## Next action

`python3 stage/scripts/release_plugin.py stage --bump minor`.

## Related truth

- DE-00000054 — 릴리스 종류의 통과 기준은 "올렸다"가 아니라 "쓸 수 있다"다.


## Progress


## Verification


## Retrospective


## Promotion decision

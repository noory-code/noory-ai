---
id: W-00000204
title: stage 0.57.0 을 낸다
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

# W-00000204 stage 0.57.0 을 낸다

## Purpose

이번 서랍 정리로 들어간 새 명령과 보관 자리가 아직 어느 프로젝트에도 안 실려 있으므로, 플러그인 버전을 올려 다른 프로젝트가 그것을 쓸 수 있게 한다

## Actions

없음 — 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 움직인다.

## User value

다른 프로젝트가 새 명령과 보관 자리를 실제로 쓸 수 있다. 지금은 이 저장소 안에만 있다.

## Scope

### Included

- 부 버전을 올린다(0.56.0 → 0.57.0). 서랍 구조와 명령이 늘었으므로 고침이 아니라 기능이다.
- 쌓인 변경 기록에 그 버전 제목을 붙이고 다음을 위한 빈 자리를 연다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- 릴리스를 한 번에 커밋하고 푸시한다.

### Excluded

- 다른 프로젝트를 옮기지 않는다. 보태는 변경이라 옛 프로젝트가 그대로 돌아간다.

## Risks

- 릴리스는 푸시까지가 한 몸이라 되돌리기가 비싸다. 감사와 시험을 먼저 통과시킨다.
- 코덱스 런타임이 새 버전 캐시를 못 집으면 다음 세션의 훅이 막힌다(P-00000001). 사전 확인
  명령이 그것을 잡는다.

## Success criteria

- 두 매니페스트와 변경 기록이 같은 버전을 말한다.
- 릴리스가 원격에 올라가 다른 프로젝트가 받을 수 있다.
- 감사가 오류 없이 통과한다.

## Next action

`python3 stage/scripts/release_plugin.py stage --bump minor`.

## Related truth

- DE-00000054 — 릴리스 종류의 통과 기준은 "올렸다"가 아니라 "쓸 수 있다"다.

## Progress


## Verification


## Retrospective


## Promotion decision

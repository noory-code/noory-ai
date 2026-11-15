---
id: W-00000333
title: stage 0.66.0 을 낸다
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

# W-00000333 stage 0.66.0 을 낸다

## Purpose

일감마다 모델과 에포트 등급을 고르는 기능과 범위를 넘었다는 거짓 보고를 줄인 수정이 아직 이 저장소 안에만 있으므로, 플러그인 버전을 올려 설치된 세션과 다른 프로젝트가 그것을 쓸 수 있게 한다

## Actions

없음 — 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 움직인다.

## User value

다시나 같은 다른 프로젝트가 설정에 등급 표(`model_tiers`)를 적어 일감마다 모델과 에포트를
고를 수 있다. 프로젝트 파일을 건드리지 않은 쓰기에는 범위를 넘었다는 보고와 전체 작업 맥락이
더 붙지 않는다. 지금은 둘 다 이 저장소의 main 에만 있고 설치본은 0.64.0 이다.

## Scope

### Included

- 부 버전을 올린다(0.65.0 → 0.66.0). 새 설정(`model_tiers`, `tier_routing`)과 새 훅
  (`SubagentStop`)이 생겼으므로 고침이 아니라 기능이다.
- 쌓인 변경 기록 다섯 묶음에 그 버전 제목을 붙이고 다음을 위한 빈 자리를 연다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- 릴리스를 PR 로 올려 main 에 합친다.
- 사용자가 `/plugin` 으로 설치본을 올린 뒤 설치 기록에서 0.66.0 을 확인한다.

### Excluded

- 다시나 설정에 등급 표를 넣지 않는다. 다시나 저장소의 일이다.
- 등급 표가 없는 프로젝트를 옮기지 않는다. 표가 없으면 전과 똑같이 돈다.
- 마일스톤에 걸지 않는다. 열린 마일스톤이 없다.

## Risks

- 설치본은 `/plugin` 을 열어야 바뀐다. `/reload-plugins` 로는 버전이 안 바뀌므로 사용자가
  열어 줄 때까지 이 카드는 열려 있다.
- 새 `SubagentStop` 훅은 Codex 쪽에서 돌려 본 적이 없다. Codex 0.167.0 실행 파일에 그 이벤트
  이름이 있다는 것까지만 확인됐다.
- 훅이 하위 에이전트의 실제 모델을 읽는 자리는 Claude Code 2.1.321 의 기록 파일 안쪽 모양이다.
  Claude Code 가 그 모양을 바꾸면 실제 모델 기록이 빈다.

## Success criteria

- 두 매니페스트와 변경 기록이 0.66.0 하나를 말한다
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다
- 이 컴퓨터의 설치본이 0.66.0 으로 바뀐 것을 설치 기록에서 확인한다
- 감사가 오류 없이 통과한다

## Next action

`python3 stage/scripts/release_plugin.py stage --bump minor`.

## Related truth

- DE-00000054 — 릴리스 종류의 통과 기준은 "올렸다"가 아니라 "쓸 수 있다"다.
- W-00000326 — 등급 표 기능을 만든 에픽(보관됨).
- W-00000332 — 범위를 넘었다는 거짓 보고를 줄인 수정(보관됨).

## Progress


## Verification


## Retrospective


## Promotion decision

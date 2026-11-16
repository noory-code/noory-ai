---
id: W-00000336
title: stage 0.66.1 을 낸다
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

# W-00000336 stage 0.66.1 을 낸다

## Purpose

세션 시작 글의 인라인 코드 규칙과 cd 뒤 변수 경로를 푸는 수정이 아직 이 저장소 안에만 있으므로, 플러그인 버전을 올려 다른 컴퓨터와 프로젝트가 그것을 쓸 수 있게 한다

## Actions

없음 — 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 움직인다.

## User value

다른 컴퓨터나 다른 프로젝트에서 Stage 를 받아 쓰는 세션도, `.stage` 를 건드리는 인라인 코드가
거절된다는 것을 시작할 때 안다. `cd` 로 들어간 폴더에서 변수 경로에 쓸 때 범위를 넘었다는
알림도 더 붙지 않는다. 이 컴퓨터는 저장소 폴더에서 바로 읽으므로 이미 쓰고 있다.

## Scope

### Included

- 패치 버전을 올린다(0.66.0 → 0.66.1). 설정이나 훅이 새로 생기지 않았으므로 고침이다.
- 쌓인 변경 기록 두 묶음(W-00000334, W-00000335)에 그 버전 제목을 붙인다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- PR 로 main 에 합치고, 합친 뒤 `claude plugin list` 로 확인한다.

### Excluded

- 플레인리 릴리스는 이 카드가 아니라 W-00000271 아래에서 한다.

## Risks

- 이 컴퓨터는 플러그인을 저장소 폴더에서 바로 읽어서, 설치본 확인으로는 다른 컴퓨터에서
  받는 경우를 가려내지 못한다. 확인한 범위를 그대로 적는다.

## Success criteria

- 두 매니페스트와 변경 기록이 0.66.1 하나를 말한다
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다
- claude plugin list 가 stage 를 0.66.1 로 읽는다
- 감사가 오류 없이 통과한다

## Next action

`python3 stage/scripts/release_plugin.py stage --bump patch`.

## Related truth

- DE-00000054 — 릴리스 종류의 통과 기준은 "올렸다"가 아니라 "쓸 수 있다"다.
- W-00000334, W-00000335 — 이 릴리스가 담는 두 변경(보관됨).

## Progress


## Verification


## Retrospective


## Promotion decision

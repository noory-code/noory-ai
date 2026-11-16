---
id: W-00000341
title: stage 0.66.2 를 낸다
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

# W-00000341 stage 0.66.2 를 낸다

## Purpose

등록 게이트의 변수 풀기, 감사의 기록 목록 검사, 닫기 도구의 승격 순서 안내가 아직 이 저장소 안에만 있으므로, 플러그인 버전을 올려 다른 컴퓨터와 프로젝트가 그것을 쓸 수 있게 한다

## Actions

없음 — 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 움직인다.

## User value

다른 컴퓨터나 다른 프로젝트에서 Stage 를 받아 쓰는 세션도 세 가지 고침을 받는다. 같은 명령에서
정한 변수로 쓰는 파일이 열린 카드가 없다는 이유로 막히지 않고, 관찰·질문 기록과 목록이 어긋나면
감사가 경고하며, 닫은 뒤 승격을 쓰는 순서를 닫기 도구가 알려 준다. 이 컴퓨터는 저장소 폴더에서
바로 읽으므로 이미 쓰고 있다.

## Scope

### Included

- 패치 버전을 올린다(0.66.1 → 0.66.2). 설정이나 훅이 새로 생기지 않았으므로 고침이다.
- 쌓인 변경 기록 세 묶음(W-00000338, W-00000339, W-00000340)에 그 버전 제목을 붙인다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- PR 로 main 에 합치고, 합친 뒤 `claude plugin list` 로 확인한다.

### Excluded

- 다른 플러그인 릴리스.

## Risks

- 이 컴퓨터는 플러그인을 저장소 폴더에서 바로 읽어서, 설치본 확인으로는 다른 컴퓨터에서
  받는 경우를 가려내지 못한다. 확인한 범위를 그대로 적는다.

## Success criteria

- 두 매니페스트와 변경 기록이 0.66.2 하나를 말한다
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다
- claude plugin list 가 stage 를 0.66.2 로 읽는다
- 감사가 오류 없이 통과한다

## Next action

`python3 stage/scripts/release_plugin.py stage --bump patch`.

## Related truth

- DE-00000054 — 릴리스 종류의 통과 기준은 "올렸다"가 아니라 "쓸 수 있다"다.
- W-00000338, W-00000339, W-00000340 — 이 릴리스가 담는 세 변경(보관됨).

## Progress


## Verification


## Retrospective


## Promotion decision


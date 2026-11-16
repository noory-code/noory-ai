---
id: W-00000350
title: stage 0.66.5 를 낸다
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

# W-00000350 stage 0.66.5 를 낸다

## Purpose

--scope 를 여러 번 넘겨도 모든 경로를 카드에 담는 고침이 아직 이 저장소 안에만 있으므로, 플러그인 버전을 올려 다른 컴퓨터와 프로젝트가 그것을 쓸 수 있게 한다.

## Actions

없음. 릴리스 명령 한 번이 버전과 변경 기록과 두 매니페스트를 함께 옮긴다.

## User value

다른 컴퓨터나 다른 프로젝트에서 Stage 를 받아 쓰는 세션도, 경로마다 `--scope` 를 따로 넘겨 카드를
등록하거나 시작할 수 있다. 넘긴 경로가 모두 카드 범위에 남는다. 이 컴퓨터는 저장소 폴더에서 바로
읽으므로 이미 쓰고 있다.

## Scope

### Included

- 패치 버전을 올린다(0.66.4 → 0.66.5). 설정이나 훅이 새로 생기지 않았으므로 고침이다.
- 쌓인 변경 기록 한 묶음(W-00000349)에 그 버전 제목을 붙인다.
- 두 매니페스트를 같은 버전으로 옮긴다.
- PR 로 main 에 합치고, 합친 뒤 `claude plugin list` 로 확인한다.

### Excluded

- 다른 플러그인 릴리스.

## Risks

- 이 컴퓨터는 플러그인을 저장소 폴더에서 바로 읽어서, 설치본 확인으로는 다른 컴퓨터에서
  받는 경우를 가려내지 못한다. 확인한 범위를 그대로 적는다.

## Success criteria

- 두 매니페스트와 변경 기록이 0.66.5 하나를 말한다
- 릴리스 커밋이 원격 main 에 올라가 다른 프로젝트가 받을 수 있다
- claude plugin list 가 stage 를 0.66.5 로 읽는다

## Next action

PR 을 머지한 뒤 `claude plugin list` 로 0.66.5 를 확인하고 닫는다.

## Related truth

- 사용자 결정(2026-11-17): "네, 릴리스".

## Progress

- `python3 stage/scripts/release_plugin.py stage --bump patch`: "Released stage 0.66.5". 변경 기록에
  `## 0.66.5 — 2026-11-17` 제목이 붙고, 두 매니페스트가 0.66.5 가 됐다.

## Verification


## Retrospective


## Promotion decision


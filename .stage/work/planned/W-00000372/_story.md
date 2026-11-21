---
id: W-00000372
title: Stage 를 릴리스한다
kind: release
venue:
milestone:
status: captured
priority: 8
autonomous: false
acceptance: []
review: not_required
scope: stage/CHANGELOG.md,stage/.claude-plugin,stage/.codex-plugin
---

# W-00000372 Stage 를 릴리스한다

## Purpose

변경 기록의 Unreleased 에 쌓인 고침이 설치본에서 동작한다

## Actions


## User value

사용자가 릴리스를 요청한 적은 아직 없다. 요청하면 시작한다.

- `stage/CHANGELOG.md` 의 `## Unreleased` 에 닫기와 보관을 한 번에 하는 `--archive`, 닫을 때 남기는 한 줄
  기록, 카드의 회고 칸 없애기와 `--maintenance`, README 의 훅 목록이 쌓여 있다.
- 릴리스는 `python3 stage/scripts/release_plugin.py stage --bump <patch|minor|major>` 로 한다.
- Stage 0.67.0 은 Windows 에서 확인한 적이 없다. 0.67.0 은 훅 명령이 Windows 에서 `python` 을 부르게 고친
  버전이다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 맥북의 claude plugin list 가 새 버전과 저장소 폴더에서 읽는다는 줄을 보여 준다
- Windows 세션이 새 버전에서 훅이 실행되는 것을 확인했다

## Next action

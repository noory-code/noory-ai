---
id: W-00000372
title: Stage 를 릴리스한다
kind: release
venue: claude
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/CHANGELOG.md,stage/.claude-plugin,stage/.codex-plugin
promotes:
decision_refs:
---

# W-00000372 Stage 를 릴리스한다

## Purpose

변경 기록의 Unreleased 에 쌓인 고침이 설치본에서 동작한다

## Actions


## User value

- `stage/CHANGELOG.md` 의 `## Unreleased` 에 닫기와 보관을 한 번에 하는 `--archive`, 닫을 때 남기는 한 줄
  기록, 카드의 회고 칸 없애기와 `--maintenance`, README 의 훅 목록이 쌓여 있다.
- 릴리스는 `python3 stage/scripts/release_plugin.py stage --bump <patch|minor|major>` 로 한다.
- Stage 0.67.0 은 훅 명령이 Windows 에서 `python` 을 부르게 고친 버전이다. 2026-11-23 에 한국어
  Windows 11(cp949, Python 3.14.10) 세션이 설치본 0.67.0 에서 훅이 실행되는 것을 확인했다. SessionStart 훅이
  Stage 컨텍스트를 넣었고, PreToolUse 훅이 `.stage` 를 언급하는 `python -c` 명령을 거부했다.
- 같은 날 같은 기기에서 `50a9484e` 를 받아 테스트를 실행했다. `python -m unittest discover -s stage/hooks/tests -q`
  는 467개가 통과했고(44개 건너뜀), `python -m unittest discover -s stage/scripts/tests -q` 는 908개가
  통과했다(6개 건너뜀). 릴리스한 뒤 새 버전에서 훅이 실행되는지는 다시 확인해야 한다.


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 맥북의 claude plugin list 가 새 버전과 저장소 폴더에서 읽는다는 줄을 보여 준다
- Windows 세션이 새 버전에서 훅이 실행되는 것을 확인했다

## Next action

Waiting on user: Windows 세션에서 저장소를 받아 Stage 0.68.0 으로 올린 뒤 훅이 실행되는지 확인한다. SessionStart 훅이
Stage 컨텍스트를 넣는지, PreToolUse 훅이 `.stage` 를 언급하는 `python -c` 명령을 거부하는지 본다. 확인되면
이 카드를 닫는다.

## Related truth

- 릴리스 커밋 `0bcb31c3`, 병합 [PR 118](https://github.com/noory-code/noory-ai/pull/118) (`7e2b6712`).

## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 0.69.0 을 릴리스했다. 다른 세션이 만든 0.68.0 의 릴리스 커밋(0bcb31c3)은 W-00000405, W-00000408, W-00000409 가 병합되기 전의 것이었는데, main 을 합치면서 그 세 항목이 0.68.0 절에 들어가 있었다. 새 CI 점검(`changelog`)이 그것을 잡았고, 세 항목을 Unreleased 로 옮긴 뒤 W-00000410 과 함께 0.69.0 으로 묶었다. 0.69.0 에는 다른 프로젝트의 리뷰 설정을 고쳐야 하는 변경(판정의 `method` 필수)이 들어 있다. 성공 기준의 두 확인(Mac 의 `claude plugin list`, Windows 의 훅 실행)은 이제 0.69.0 으로 해야 한다. 이 카드는 그 확인이 올 때까지 열어 둔다.

- 2026-11-23 사용자가 Mac 세션에서 릴리스를 여기서 마치라고 했다("여기서 마치기").
- `release_plugin.py stage --bump minor` 로 0.67.0 에서 0.68.0 으로 올렸다. 새 스킬(`stage-orchestrate`)과 스크립트와
  설정이 들어가고 W-00000408 이 닫기 리뷰의 계약을 바꿔서 minor 로 골랐다.
- 릴리스 브랜치에 main(`44d36f3f`)을 합쳐 W-00000408 과 W-00000409 의 변경 기록도 0.68.0 절에 넣었다.
- PR 118 의 CI 에서 `test (windows-latest, 3.9, 1)` 이 한 번 실패했다.
  `test_run_check_timeout_ends_the_whole_process_tree_in_time` 이 2.0초 안에 끝나야 하는데 2.687초가 걸렸다.
  실패한 작업만 다시 실행하니 통과했고, 병합한 뒤 main 의 `stage` 워크플로도 24개 작업이 모두 통과했다.
  실패를 본 것은 병합한 뒤다. 병합 전에는 결과의 마지막 15줄만 보고 모두 통과했다고 판단했다.

## Verification

- 성공 기준 1: 2026-11-23 Mac 에서 main(`7e2b6712`)을 받은 뒤 `claude plugin list` 가 `stage@noory-ai` 에
  `Version: 0.68.0`, `Read from: /Users/woogis/Workspace/repo/noory-ai/stage`, `Status: ✔ enabled` 를 보여 줬다.
  새 세션에서 0.68.0 의 훅이 실행되는지는 이 세션에서 보지 않았다.
- 성공 기준 2: 아직 확인하지 않았다.
- 릴리스 전 Mac 에서 `python3 -m unittest discover -s stage/hooks/tests -q` 는 480개가 통과했고(1개 건너뜀),
  `python3 -m unittest discover -s stage/scripts/tests -q` 는 945개가 통과했다(2개 건너뜀).
  `python3 stage/scripts/audit_stage.py` 는 errors=0 이었다.

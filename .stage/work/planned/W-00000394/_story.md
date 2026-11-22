---
id: W-00000394
title: 한국어 Windows 에서 close_work 시험과 검사 출력이 깨지지 않게 한다
kind: fix
venue:
milestone: M-00000005
status: captured
priority: 4
autonomous: false
acceptance: []
review: not_required
scope: stage/hooks/stage_process.py,stage/skills/stage-retrospective/close_work.py,stage/scripts/tests/test_close_work.py,stage/scripts/tests/test_stage_process.py,stage/CHANGELOG.md,.stage/official/work/archive/items/W-00000381/_story.md,.stage/official/work/archive/items/W-00000391/_story.md,.stage/official/work/archive/items/W-00000393/_story.md
---

# W-00000394 한국어 Windows 에서 close_work 시험과 검사 출력이 깨지지 않게 한다

## Purpose

한국어 Windows 에서 test_close_work.py 가 true 명령 없이도 통과하고, 실패한 검사의 메시지가 깨지지 않고 읽힌다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- test_close_work.py 가 true 같은 POSIX 명령 대신 어느 OS 에서나 도는 명령을 쓰고, 한국어 Windows 에서 모두 통과한다
- cmd.exe 가 cp949 로 낸 오류 메시지가 close_work 출력에서 깨지지 않는 시험이 있고 통과한다
- W-00000381, W-00000391, W-00000393 의 Verification 에 2026-11-22 한국어 Windows 실행 결과가 적혀 있다

## Next action

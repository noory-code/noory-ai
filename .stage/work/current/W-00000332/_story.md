---
id: W-00000332
title: 범위 넘음 알림에서 프로젝트 밖 경로와 같은 명령에서 정한 변수 경로를 뺀다
kind: fix
venue: claude
environment: local-no-codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/operations/hooks.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000332 범위 넘음 알림에서 프로젝트 밖 경로와 같은 명령에서 정한 변수 경로를 뺀다

## Purpose

카드 목록 글이 붙는 범위 넘음 알림을 프로젝트 파일을 실제로 범위 밖에서 고칠 때만 띄워 헛신호를 없앤다

## Actions

- 지금 동작(2026-11-14, 설치본 0.64.0과 저장소 0.65.0 훅에 직접 넣어 확인): 0.62.0부터 `PreToolUse` 훅은
  호출이 거부됐거나 쓰기 대상이 열린 카드 어느 범위에도 들지 않을 때만 "Stage work context" 글을 붙인다.
  그 글은 열린 카드 전부의 범위와 목적을 싣는다(지금 약 1,300자, 열린 카드가 늘면 길어진다).
- 그런데 프로젝트 파일을 고치지 않은 호출도 범위 넘음으로 잡힌다. W-00000311 은 장치 파일과 OS 임시 폴더만 뺐고,
  "작업 폴더 밖의 다른 경로는 여전히 알린다"를 완료 기준으로 두었다. 남은 헛신호는 둘이다.
  - 작업 폴더 밖 경로: `~/notes.txt`, 세션 메모 폴더(`~/Library/Application Support/...`) 같은 곳에 쓰면 알린다.
  - 같은 명령 안에서 정한 셸 변수: `S=/tmp/x.py && sed -i '' ... "$S"` 는 훅 환경에 `S` 가 없어서
    `$S` 를 작업 폴더 밑 경로로 보고 알린다.
- 고침: 범위 넘음 보고에서만 작업 폴더 밖으로 풀리는 대상을 뺀다. 앞에 붙은 셸 변수는 같은 명령 안의 앞선
  `NAME=value` 대입을 먼저 보고, 없으면 훅 환경을 본다. 끝내 못 펼친 변수는 지금처럼 알린다.
  `.stage` 쓰기 게이트와 거부 메시지는 바꾸지 않는다.
- 측정 중에 셋째 헛신호를 찾았다: `cd /다른/저장소 && git add README.md && git commit` 은 다른 저장소의
  파일을 이 저장소 기준 경로(`README.md`)로 읽어 알렸다. 명령 안의 모든 `git` 이 작업 폴더 밖에서 돌면
  (`cd` 를 실행된 것으로 따라가고 `git -C <dir>` 를 따른다) 커밋 대상을 보고에서 뺀다. `cd -` 나 모르는 변수로
  간 폴더는 안으로 본다. 커밋 게이트는 그대로다.

## User value

사용자 결정(2026-11-14): 목적은 사용자가 고른 방향이다("헛신호를 없애는 쪽으로 해 주세요").
완료 기준 세 줄과 "마일스톤 없음"은 사용자의 지시("하던 작업들 하라고 다시 지시해주세요")에 따라
오케스트레이터 세션이 정했다.

범위 넘음 알림이 진짜로 프로젝트 파일이 범위를 벗어났을 때만 뜨면, 사람과 에이전트가 그 알림을 믿을 수 있고
헛신호마다 실리던 카드 목록 글이 대화에 쌓이지 않는다.

## Scope

### Included

- 작업 폴더 밖으로 풀리는 쓰기 대상은 범위 넘음 보고에서 빠진다.
- 같은 명령 안에서 대입한 셸 변수로 시작하는 쓰기 대상은 그 값으로 펼쳐서 판단한다.
- 작업 폴더 안의 범위 밖 파일, 그리고 끝내 펼치지 못한 변수 경로는 지금처럼 알린다.
- `stage/operations/hooks.md` 의 범위 넘음 보고 설명과 `CHANGELOG.md` 의 `## Unreleased` 를 맞춘다.

### Excluded

- 거부(deny) 메시지에 붙는 카드 목록 글의 길이와 모양.
- 세션 시작 글(`SessionStart`)의 길이.
- `.stage` 쓰기 게이트와 등록 게이트의 판정.
- 매니페스트 버전과 릴리스.

## Risks

- 카드 범위가 작업 폴더 밖 경로를 적은 경우(예: 다른 저장소 경로): 그 범위에 맞는 쓰기는 지금도 넘음이 아니다.
  그 밖의 작업 폴더 밖 쓰기는 이제 알리지 않는다. 다른 저장소를 고친 사실은 이 알림으로 남지 않는다.
- 셸 대입 파싱을 넓게 잡으면 다른 명령의 인자를 대입으로 잘못 읽을 수 있다. 명령 단어 자리의 `NAME=value` 만 본다.

## Success criteria

- 임시 폴더나 메모 폴더처럼 프로젝트 밖에 쓸 때는 카드 목록 글이 붙지 않는다
- 프로젝트 파일을 카드 범위 밖에서 고칠 때는 지금처럼 알림과 카드 목록 글이 붙는다
- 지난 세션 기록의 같은 도구 호출을 고치기 전과 후의 훅에 넣었을 때 알림이 붙는 횟수가 줄었고 두 값이 카드에 남아 있다

## Next action

사용자가 커밋을 허락하면 코드 커밋을 만든다. 그 커밋에서 회고를 쓰고 `close_work.py` 를 Claude 대역 리뷰
(`STAGE_CODEX_COMPANION=stage/scripts/claude_review_companion.py`)와 hooks·scripts 전체 시험 `--check` 로 돌려 닫는다.

## Related truth

## Progress

- 2026-11-14: `origin/main`(e984664e)에서 딴 worktree `worktree-stage-false-crossing` 에서 진행했다.
  venue 정책은 fix -> codex 지만 DE-00000086 에 따라 `local-no-codex` 환경에서 Claude 가 실행했다.
- `stage_guard.py`: `scratch_target` 을 `outside_report_target` 으로 바꿔 작업 폴더 밖 대상을 모두 뺀다.
  `same_command_assignments` 와 `git_runs_outside_workspace` 를 더했다. 둘 다 범위 넘음 보고에서만 쓴다.
- 시험: `test_stage_guard.py` 에 프로젝트 밖 Write·리다이렉트, 같은 명령 대입 변수(맨/중괄호),
  다른 저장소 커밋(`cd`, `git -C`)을 빼는 경우와, 같은 명령 대입이 프로젝트를 가리키는 경우·`cd` 뒤 안에서 한
  커밋·인자 속 `X=` 를 대입으로 읽지 않는 경우를 더했다. W-00000311 의 "작업 폴더 밖 다른 경로는 알린다"
  단정은 이 카드의 결정으로 뺐다.
- 판별 확인: HEAD 의 `stage_guard.py` 로 바꿔 돌리면 새 시험 여섯 개(밖 경로 둘, 대입 변수 넷)가 깨지고,
  되돌리면 통과한다. 커밋 두 경우는 고치기 전 실행에서 깨졌다.
- `stage/operations/hooks.md` 의 범위 넘음 보고 설명과 `stage/CHANGELOG.md` `## Unreleased` 를 고쳤다.

## Verification

- 전후 측정(셋째 완료 기준): 이 저장소 세션 기록 15개(`~/.claude/projects/-Users-woogis-Workspace-repo-noory-ai/*.jsonl`,
  있는 것 전부)의 Bash·Write·Edit·MultiEdit 호출 1,696건을 같은 `.stage` 복사본에 대고 두 훅에 그대로 넣었다.
  - 고치기 전(HEAD 0.65.0 + main): 범위 넘음 544건, 붙은 글 513,348자.
  - 고친 뒤: 범위 넘음 57건, 붙은 글 51,119자. 거부 22건은 양쪽이 같다.
  - 한계: 기록 당시 있던 임시 폴더가 지금은 없어서, `cd <없어진 폴더> && … > out.log` 같은 호출은 훅이 cd 를
    따라가지 못하고 프로젝트 경로로 본다. 남은 57건 중 `proto.py`·`out.log`·`claude-run.log` 류가 이 경우다.
    실제 세션에서는 폴더가 있으므로 빠진다. 두 훅이 같은 입력을 받았으므로 감소 비교는 공정하다.
- `python3 -m unittest discover -s stage/hooks/tests -q`: 399건 통과.
- `python3 -m unittest discover -s stage/scripts/tests -q`: 736건 통과(2건 건너뜀).
- `python3 stage/scripts/audit_stage.py --project-root .`: errors=0, warnings=32(모두 보관된 카드의 기존 경고).

## Retrospective

## Promotion decision

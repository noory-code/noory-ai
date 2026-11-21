---
id: W-00000365
title: 다음에 할 일의 순서를 .stage 로 옮긴다
kind: planning
venue: claude
environment: local-no-codex
milestone: M-00000005
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000365
promotion: not_applicable
review: passed
scope: .stage/roadmap,.stage/work/planned,.stage/state/observations
promotes:
decision_refs:
---

# W-00000365 다음에 할 일의 순서를 .stage 로 옮긴다

## Purpose

다음에 할 일과 그 순서가 저장소 안에 있어서 어느 세션이든 개인 메모 없이 이어서 일한다

## Actions

카드 하나로 한다. 나누지 않는다.

## User value

다음 할 일이 Claude 의 개인 메모에만 있으면 Windows 세션이나 새 세션은 그것을 읽지 못한다. 2026-11-20 에
사용자와 "다음 세션에 남기기"는 남는 절차라고 정했다. 그 자리를 저장소로 옮긴다. 마일스톤 M-00000005 의
완료 기준 가운데 "다음 할 일을 `.stage` 만으로 읽을 수 있다"가 이 카드다.

## Scope

### Included

- 사용자와 정한 다음 카드 두 장(W-00000366, W-00000367)의 상태를 `selected` 로 바꾼다.
- 개인 메모에만 있던 할 일을 계획 카드로 등록한다.
- 개인 메모에만 있던 미룬 일을 관찰로 남긴다.
- 개인 메모를 `.stage` 를 가리키는 안내로 줄인다. 개인 메모는 저장소 밖에 있다.

### Excluded

- 세션 시작 글을 만드는 훅 코드. 이 카드에서 찾은 고장은 W-00000373 이 고친다.
- `.stage/decisions/pending/` 에 남아 있는 결정 기록을 공식 기록으로 올리는 일.
- 다시나의 다음 할 일. 다시나 저장소가 가진다.

## Risks

- 개인 메모에 있던 진행 기록 200줄을 지웠다. 그 내용은 커밋, PR, 보관된 카드와 회고에 있지만, 메모에만 있던
  사실이 있었다면 사라졌다. 옮길 것을 고를 때 메모를 처음부터 끝까지 다 읽지는 않았다. 제목과 "남은 것",
  "아직" 같은 낱말이 든 문장, 2026-11-17 이후의 절을 읽었다.

## Success criteria

- 새 세션이 Claude 의 개인 메모를 읽지 않고 세션 시작 글과 .stage 기록만으로 다음에 할 일을 말한다
- Claude 의 개인 메모에는 다음 할 일 목록이 없고 .stage 를 가리키는 안내만 있다

## Next action

닫는다. 고친 것이 `.stage/work/planned/` 와 `.stage/state/` 뿐이라 DE-00000087 의 대상 경로가 아니다.

## Related truth

- 계획 카드의 상태 값과 순서: `.stage/work/planned/index.md`, `stage/operations/backlog.md`.
- 세션 시작 글을 만드는 코드: `stage/hooks/stage_context.py` 의 `selected_backlog_lines` 와
  `open_observation_lines`.

## Progress

- W-00000366 과 W-00000367 을 `selected` 로 바꿨다. W-00000366 에는 2026-11-20 에 사용자와 정한 도면 이야기
  (층, 레이어 초안, 초안을 쓰다 찾은 것)를 옮겨 적었다.
- 계획 카드 세 장을 등록했다.
  - W-00000371 회고에 남길 칸을 정한다. DE-00000089 가 미룬 4번이다.
  - W-00000372 Stage 를 릴리스한다. 사용자가 요청하면 시작한다.
  - W-00000373 세션 시작 글이 고른 계획 카드와 관찰의 날짜를 바르게 보여 주게 고친다. 유지 카드다.
- 관찰 세 건을 남겼다.
  - O-00000058 닫기 리뷰는 맨 위 커밋이 고친 파일만 본다.
  - O-00000059 드라이버가 닫는 카드는 손으로 닫는 카드와 두 군데가 다르다.
  - O-00000060 열린 카드가 없으면 관문이 머지 커밋도 막는다.
- 개인 메모 `project_stage_next_session.md` 를 `.stage` 의 다섯 자리를 가리키는 안내로 바꿨다. 이 컴퓨터에만
  통하는 사실(gh 인증, 닫는 명령, LSP)은 다른 메모 파일로 옮겼다. 그 파일에는 할 일을 적지 않는다.
- **이 카드에서 찾은 고장.** 세션 시작 글의 "Selected backlog" 는 지금 카드 구조에서 한 번도 나오지 않는다.
  목록을 만드는 코드가 이름이 `_` 로 시작하는 파일을 건너뛰는데, 카드 파일 이름이 `_story.md` 다. 테스트는
  없어진 구조(`future/backlog/items/B-*.md`)로만 확인한다. 그래서 `selected` 로 바꿔도 세션 시작 글에는 나오지
  않는다. 새 세션은 `work/planned/index.md` 를 읽고 답했다.
- 범위 밖으로 나간 것: `.stage/state/current.md` 에 관찰 세 건의 줄을 넣었다. 관찰의 색인이 그 파일이다.

## Verification

맥북(macOS)에서 커밋 `fc6922bc` 로 확인했다.

- **새 세션에게 물었다.** `claude -p --model sonnet` 을 읽기 도구(Read, Grep, Glob)만 주고 실행했다. 질문은
  "이 저장소에서 다음에 할 일이 무엇입니까? 순서대로 말하고, 카드가 아닌 미뤄 둔 일도 있으면 말해 주세요.
  ~/.claude 아래의 개인 메모 파일은 열지 마세요." 였다.
  - 답: 진행 중인 W-00000365, 그다음 W-00000366, W-00000367, W-00000371, W-00000372 를 우선순위대로 말했다.
    카드가 아닌 일로 열린 관찰 네 건과 `decisions/pending` 의 결정 네 건을 말했다.
  - 읽었다고 적은 파일: 이 카드, `work/planned/index.md`, 계획 카드 네 장, `state/current.md`, 마일스톤,
    결정 기록 네 건의 앞부분, 세션 시작 글.
  - 이 실행은 W-00000373 을 등록하기 전이었다. 그래서 답에 W-00000373 은 없다.
- **한계.** 메모의 색인 파일(`MEMORY.md`)은 세션이 시작할 때 저절로 실린다. 새 세션도 그 색인을 받았다.
  색인의 이 줄은 `.stage` 를 읽으라는 안내뿐이지만, 색인이 아예 없는 세션으로 확인한 것은 아니다.
- **개인 메모.** `project_stage_next_session.md` 는 21줄이고 할 일 목록이 없다. 색인의 줄도 안내로 바꿨다.
- `python3 stage/scripts/audit_stage.py`: 오류 0건, 경고 32건.
- 닫을 때의 리뷰는 만든 쪽과 같은 계열(Claude)이 본다. 기록만 고친 카드라 리뷰 모델은 `sonnet` 으로 한다.
  리뷰어는 저장소 밖의 개인 메모를 볼 수 없어서 둘째 조건은 이 칸의 설명으로만 판정한다.

- Checks at close 2026-11-21: 1 passed — `python3 stage/scripts/audit_stage.py`
- Review at close 2026-11-21 by claude_review_companion: approved (1 PASS, 2 PASS)

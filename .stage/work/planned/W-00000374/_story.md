---
id: W-00000374
title: 목록 파일을 union 으로 합치고 줄을 지우는 목록은 카드에서 만든다
kind: development
venue:
milestone: M-00000005
status: captured
priority: 6
autonomous: false
acceptance: []
review: not_required
scope: .gitattributes,stage/skills/stage-work,stage/scripts,stage/skills/stage-retrospective,stage/skills/stage-archive,stage/hooks,stage/templates,stage/operations,stage/docs,stage/skills,.stage/index.md,.stage/operations/parallel-sessions.md
---

# W-00000374 목록 파일을 union 으로 합치고 줄을 지우는 목록은 카드에서 만든다

## Purpose

두 세션이 따로 카드를 등록하고 닫은 브랜치를 합칠 때 목록 파일에서 충돌이 나지 않게 한다

## Actions


## User value

두 세션이 같은 날 따로 일한 뒤 PR 을 합칠 때 `active.md`, `review.md`, `CHANGELOG.md` 를 손으로 합치지
않는다. 과거 머지 136건 가운데 27건에서 이 일을 했다.

## Scope

### Included

- 저장소 루트에 `.gitattributes` 를 만들고 모든 플러그인의 `CHANGELOG.md` 와 `.stage/official/` 의 보관
  목록에 `merge=union` 을 건다.
- `.stage/work/active.md`, `.stage/work/review.md`, `.stage/work/planned/index.md` 를 저장소에서 빼고,
  이 목록을 읽던 자리가 카드의 `status` 를 읽게 한다.
- 고칠 자리는 DE-00000091 의 "Where this applies" 표에 하나씩 적혀 있다. 그 표를 따라간다.

### Excluded

- 기록 번호. W-00000375 가 한다.
- 항목마다 파일을 하나씩 두는 방식.

## Risks

- 줄을 지우는 목록에 union 을 걸면 닫은 카드의 줄이 되살아난다. 과거 머지로 실행했을 때 18번 가운데
  13번이 그랬다. 이 세 목록에는 union 을 걸지 않는다.
- 관문(`stage/hooks/stage_work.py`)과 점검 규칙(`INDEX000` ~ `INDEX006`)을 고친다. 닫기 전에 사용자에게
  확인을 받는다(DE-00000087).
- 설치된 Stage 를 쓰는 다른 프로젝트에는 세 목록 파일이 이미 있다. 그 프로젝트에서 새 버전이 어떻게
  동작하는지 정해야 한다.

## Success criteria

- 같은 main 에서 갈라진 두 브랜치가 각각 카드를 등록하고 닫고 보관한 뒤 합치면 충돌 없이 합쳐지고, 감사가 오류 0건으로 끝난다
- 두 브랜치가 CHANGELOG.md 의 Unreleased 에 각각 한 줄을 넣고 합치면 두 줄이 모두 남는다
- 세션 시작 글의 Active work 와 Review candidates 가 목록 파일 없이 카드의 상태에서 나온다
- GitHub 의 머지 버튼으로 합쳐도 같은 결과가 나오는지 PR 두 개로 확인한 결과가 카드에 적혀 있다

## Next action

DE-00000091 을 읽고, 세 목록을 파일로 남겨 `.gitignore` 에 넣을지 아예 두지 않을지를 먼저 정한다.

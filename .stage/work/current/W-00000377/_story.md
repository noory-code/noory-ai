---
id: W-00000377
title: 목록 파일을 union 으로 합치고 줄을 지우는 목록은 카드에서 만든다
kind: development
venue: claude
environment: cloud
milestone: M-00000005
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: .gitattributes,.gitignore,.stage/work,.stage/index.md,.stage/operations/parallel-sessions.md,stage
promotes:
decision_refs:
---

# W-00000377 목록 파일을 union 으로 합치고 줄을 지우는 목록은 카드에서 만든다

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

- 기록 번호. W-00000378 가 한다.
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

## Related truth

## Progress

- 세 목록은 파일로 두지 않기로 했다. `.gitignore` 에 넣은 생성 파일은 GitHub 에서 보는 사람에게도, 다른 세션에게도
  보이지 않는다. 읽는 자리는 모두 카드를 읽어 같은 목록을 만들 수 있다: 세션 시작 글(`stage_context.derived_work_view`),
  `archive_work.py --all-completed`(카드의 `status`), 감사(목록과 카드를 비교할 일이 없어진다). 남겨 둘 이유가 없다.
- 이미 세 파일을 가진 다른 프로젝트: 새 버전은 그 파일을 읽지도 쓰지도 않는다. 감사가 파일마다 경고 INDEX007 로
  "지워라" 를 알린다. 경고로 둔 이유는 남은 파일이 도구를 틀리게 만들지는 않고 읽는 사람만 오도하기 때문이다.
  관문은 v5 프로젝트에서 남은 목록 줄로 막지 않는다. 옛 이관 스크립트(v3→v4, v4→v5)는 그대로 두었다. 이관한
  프로젝트에도 같은 INDEX007 경고가 나온다.
- 다른 프로젝트의 `.gitattributes`: `init_stage.py` 가 `.stage/official/**/archive/index.md merge=union` 줄을 넣는다.
  기존 프로젝트는 `init_stage.py` 를 다시 실행하면 기존 파일은 그대로 두고 이 줄만 더한다. `CHANGELOG.md` 는
  프로젝트마다 다르므로 넣지 않는다.
- 감사 규칙 INDEX000~INDEX006, BACKLOG008/BACKLOG009 를 없앴다(v3 구조 포함). 비교할 목록이 없다.
- `register_work.py`, `start_work.py` 의 `--owner` 를 없앴다. 목록의 Owner 칸만 채우던 값이다.

## Verification

- `python3 -m unittest discover -s stage/hooks/tests -q`: 461 tests OK (skipped=1).
- `python3 -m unittest discover -s stage/scripts/tests -q`: 805 tests OK (skipped=2).
- `python3 stage/scripts/audit_stage.py --project-root .`: errors=0, warnings=32 (모두 이 카드 이전부터 있던 경고).
- 성공 기준 1: 이 커밋에서 갈라진 로컬 브랜치 두 개가 각자 `register_work.py` → `close_work.py --allocate-retrospective`
  → `close_work.py --archive` 로 카드를 등록하고 닫고 보관했다(W-00000380, W-00000381, 임시 디렉터리 안). 두 브랜치를
  차례로 합치니 충돌 없이 합쳐졌고 감사는 errors=0 이었다. 같은 병합을 `.git/info/attributes` 로 `merge=text` 를
  강제해서 다시 하면 `stage/CHANGELOG.md` 와 `.stage/official/work/archive/index.md` 에서 충돌한다.
- 성공 기준 2: 위 병합에서 두 브랜치가 `## Unreleased` 에 넣은 줄이 둘 다 남았다. 보관 목록의 두 줄도 둘 다 남았다.
- 성공 기준 3: `stage/hooks/tests/test_derived_work_views.py` 가 목록 파일 없이 카드의 `status` 만으로 세션 시작 글의
  Active work 와 Review candidates 가 나오는지, 남은 옛 `active.md` 의 줄이 세션 시작 글에 들어가지 않는지 확인한다.
- 성공 기준 4(GitHub 머지 버튼): 확인하지 못했다. 임시 브랜치 `claude/w377-union-test-base`, `-a`, `-b` 는 올렸지만
  PR 을 만드는 `gh api` 호출이 이 세션의 권한 분류기에서 거부되었다. 그 뒤 임시 브랜치를 지우는 push 도 git 프록시가
  403 으로 거부해서 세 브랜치가 원격에 남아 있다. 사람이 지워야 한다.

---
id: W-00000375
title: 카드와 기록을 등록할 때 번호를 원격에 잡는다
kind: development
venue:
milestone: M-00000005
status: captured
priority: 6
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/stage_record_ids.py,stage/skills/stage-work/register_work.py,stage/skills/stage-roadmap/manage_roadmap.py,stage/scripts/tests,stage/skills/stage-decision/SKILL.md,stage/operations/cloud-execution.md,stage/docs/BLUEPRINT.md,.stage/operations/parallel-sessions.md
---

# W-00000375 카드와 기록을 등록할 때 번호를 원격에 잡는다

## Purpose

서로의 브랜치를 받아 오지 않은 두 세션이 같은 카드 번호나 기록 번호를 고르지 않게 한다

## Actions


## User value

카드를 등록하기 전에 fetch 하고 등록한 뒤 바로 push 하는 순서를 기억하지 않아도 번호가 겹치지 않는다.
겹친 번호를 다시 매기느라 카드와 회고와 링크를 고치는 일이 없어진다.

## Scope

### Included

- `stage_record_ids.py` 와 `register_work.py` 가 번호를 고른 뒤 원격에 `refs/stage-ids/<번호>` 를 만든다.
  이미 있으면 다음 번호로 넘어간다.
- 원격에 닿지 못하거나 원격이 없으면 지금처럼 번호를 고르고, 잡지 못했다고 출력한다.
- 고칠 자리는 DE-00000092 의 "Where this applies" 표에 하나씩 적혀 있다.

### Excluded

- 목록 파일. W-00000374 가 한다.
- 이미 겹친 번호를 바꾸는 도구.

## Risks

- GitHub 이 `refs/stage-ids/` 라는 이름의 ref 를 받아 주는지 확인하지 않았다. 시험은 로컬의 빈 저장소로
  했다. 받아 주지 않으면 태그 같은 다른 이름을 쓴다.
- 등록할 때마다 원격을 한 번 다녀온다. 느리면 세션이 이 기능을 끄고 일하게 된다.
- 테스트가 실제 원격에 가면 안 된다. 임시 폴더의 빈 저장소를 원격으로 쓴다.

## Success criteria

- 서로 받아 오지 않은 두 클론이 같은 원격을 두고 차례로 카드를 등록하면 서로 다른 번호를 받는다
- 원격에 닿지 못할 때도 등록이 되고, 번호를 원격에 잡지 못했다는 줄이 출력된다
- 원격이 없는 프로젝트에서 등록하면 지금과 같은 번호를 받는다
- 이 저장소의 GitHub 원격이 번호를 잡는 ref 를 받아 주는지 확인한 결과가 카드에 적혀 있다

## Next action

이 저장소의 GitHub 원격에 `refs/stage-ids/` 아래 ref 하나를 만들 수 있는지 먼저 확인한다. 원격에 쓰는
일이므로 사용자에게 묻고 한다.

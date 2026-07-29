---
id: W-00000125
title: 카드마다 자기 작업 트리에서 드라이버가 돈다
kind: development
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
review: not_required
scope: stage/scripts/, stage/scripts/tests/, stage/skills/stage-drive/, stage/CHANGELOG.md
---

# W-00000125 카드마다 자기 작업 트리에서 드라이버가 돈다

## Purpose

DE-00000040 §2. 드라이버는 실행자 호출 전후로 저장소를 스냅샷 떠서 관측하므로(W-00000121), 둘이 같은 체크아웃에 있으면 서로의 변경을 자기 실행자 것으로 본다. git worktree 로 카드마다 트리와 브랜치를 주고 드라이버를 거기에 건다. 드라이버는 이미 --project-root 를 받으므로 가리키기만 하면 된다. 끝나면 어디를 병합하면 되는지 알려준다. 시도 기록은 .gitignore 라 트리마다 저절로 따로 논다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action

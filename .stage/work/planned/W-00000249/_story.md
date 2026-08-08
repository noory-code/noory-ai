---
id: W-00000249
title: 마일스톤 완료 기준을 여러 개 받게 한다
kind: fix
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance: []
review: not_required
scope: stage/scripts/, stage/scripts/tests/
---

# W-00000249 마일스톤 완료 기준을 여러 개 받게 한다

## Purpose

마일스톤을 만들 때 완료 기준을 여러 개 주면 마지막 하나만 남고 나머지가 말없이 사라져서 M-00000003 에서 셋 중 둘을 잃었으므로, 카드 등록 명령의 --success-criterion 과 같은 모양으로 반복 인자를 받게 한다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 완료 기준을 세 개 주면 세 개가 다 마일스톤 기록에 남는다
- 기준이 조용히 사라지면 시험이 잡는다

## Next action

O-00000036 을 먼저 읽는다. 고칠 길 둘 중 어느 쪽이 카드 등록 명령과 결이 같은지가 그 기록에
적혀 있다. 마일스톤 기록이 기준을 목록으로 담는지도 그 자리에서 함께 본다.

---
id: W-00000144
title: 보관된 v5 카드를 게이트가 다시 열 수 있다
kind: fix
venue: codex
milestone:
source:
autonomous: true
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -q"
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/hooks/stage_work.py, stage/hooks/tests/, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000144 보관된 v5 카드를 게이트가 다시 열 수 있다

## Purpose

보관된 카드를 고칠 방법이 없다. 보관 게이트가 v5 배치를 못 읽는다.

게이트는 아카이브 인텐트의 대상 경로에서 작업 항목 ID 를 뽑아 인텐트가 지목한 카드와 같은지 본다.
그 ID 를 **파일 이름**에서 뽑는다(`stage/hooks/stage_work.py:431` — `Path(relative).name` 에서
`.md` 를 떼어낸다). v4 는 `items/W-00000130.md` 였으므로 맞았다. v5 는 계층으로 옮기므로
`items/W-00000130/_story.md` 가 되고, 뽑히는 값이 `_story` 라서 **항상 어긋난다.**

`archive_work.py` 는 v5 구조로 정상 보관한다. 즉 **플러그인이 만든 결과물을 플러그인의 게이트가
못 받는다.** novel-workspace 가 감사 오류 한 건을 고치려다 여기 막혔고, 게이트를 우회하는 선례를
만들지 않기로 하고 오류를 남겨 뒀다. 이 저장소도 같은 상태다 — 오늘 보관한 카드들이 모두
`items/<id>/_story.md` 다.

## Actions

- `archive_target_item_id` 가 v5 계층 경로에서 ID 를 뽑게 한다. 인식할 모양:
  `items/<id>/_story.md`, `items/<epic>/<id>/_story.md`(에픽 안 스토리),
  `items/<epic>/<story>/<id>/_story.md`(액션), 그리고 에픽 자신의 `_epic.md`.
  **ID 는 파일 이름이 아니라 그 파일이 든 폴더 이름에서 나온다.**
- v4 경로(`items/<id>.md`)도 계속 인식한다. 아직 v4 인 프로젝트가 있다.
- `archive_target_retro_id` 는 회고가 여전히 `retrospectives/<id>.md` 라 그대로다. 그 사실을
  확인하고 바꿀 것 없음으로 적는다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절에 항목을 더한다. 매니페스트 버전은 안 건드린다.

## Scope

`stage/hooks/stage_work.py`, `stage/hooks/tests/`, `stage/CHANGELOG.md`.

**안 하는 것**: 결정 하나를 카드 여럿이 참조하는 문제(감사 WORK015). 별개 논점이고
W-00000145 로 잡아 뒀다.

## Success criteria

- **회귀 시험**: v5 로 보관된 카드(`items/<id>/_story.md`)에 아카이브 인텐트를 내고 그 파일을
  수정하면 게이트가 통과한다. 고치기 전 같은 시험이 막히는 것을 먼저 보여야 한다.
- **회귀 시험**: 에픽 안에 든 스토리·액션의 보관 경로도 통과한다. 최상위만 되면 계층 보관에서
  다시 막힌다.
- **회귀 시험**: 인텐트가 지목한 것과 **다른** 카드를 고치려 하면 여전히 막힌다. 이 완화가
  게이트를 열어 버리면 안 된다.
- v4 경로도 여전히 통과한다.
- `python3 -m unittest discover -s stage/hooks/tests -q` 와
  `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 의 `## Unreleased` 절 아래에 항목이 있고 매니페스트 버전은 그대로다.

## Related truth

- 실측 보고: novel-workspace, stage 0.54.4, 2026-07-30. `promote_intent.py --type archive` 로
  인텐트를 냈는데 편집이 "the items/ target filename must match the work_item ID" 로 막혔다.
- `stage/hooks/stage_work.py:423` `archive_target_item_id` — 파일 이름에서 ID 를 뽑는 자리.
- `stage/hooks/stage_runtime.py:444,460` — 그 함수를 불러 인텐트와 대조하는 자리.
- W-00000111 — 계층 보관의 인덱스 계약을 세운 카드. 보관이 계층으로 옮겨진 근거.

## Progress


## Verification


## Retrospective


## Promotion decision

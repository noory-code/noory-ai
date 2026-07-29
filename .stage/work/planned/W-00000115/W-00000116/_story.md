---
id: W-00000116
title: 대조가 드라이버의 지식과 카드 누적 기준으로 움직인다
kind: development
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
review: not_required
scope: stage/scripts/drive.py, stage/skills/stage-retrospective/close_work.py, stage/scripts/tests/, .stage/settings.json, stage/templates/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
---

# W-00000116 대조가 드라이버의 지식과 카드 누적 기준으로 움직인다

## Purpose

DE-00000039 §1. 드라이버가 만들어 넘긴 작업 로그 경로는 드라이버가 대조에서 빼고(O-00000005), 대조 범위를 base_head 대비 누적으로 통일해 재시도가 어긋나지 않게 한다(O-00000006). 실행자 프롬프트 두 벌의 보고 문장도 같은 뜻으로 맞춘다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action

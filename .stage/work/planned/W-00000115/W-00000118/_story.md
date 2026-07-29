---
id: W-00000118
title: 한계값이 규모에서 나오고 venue 사전 점검이 선다
kind: development
venue:
milestone:
status: captured
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, .stage/settings.json, stage/templates/, stage/docs/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
---

# W-00000118 한계값이 규모에서 나오고 venue 사전 점검이 선다

## Purpose

DE-00000039 §3. 명령당 시간 제한 900초 고정을 버리고 시작 시점에 규모에서 계산한다(O-00000003). venue 별 사전 점검 명령을 executors·reapers 와 같은 모양으로 받고, 실패하면 시도를 시작하지 않는다(W-00000092 흡수분). 시작 전에 O-00000003 의 '시도를 쓴다' 서술을 실측으로 검증한다 — timed out 은 이미 인프라 실패로 분류돼 시도를 안 쓰는 것이 현행 코드다.

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria


## Next action

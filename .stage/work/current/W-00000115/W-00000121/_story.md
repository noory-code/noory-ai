---
id: W-00000121
title: 관측 기준이 사람의 편집을 실행자에게 묻지 않는다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
  - "python3 -m unittest discover -s stage/hooks/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000121 관측 기준이 사람의 편집을 실행자에게 묻지 않는다

## Purpose

W-00000116 이 대조를 카드 누적으로 바꾸면서 기준 스냅샷을 첫 시도에 한 번만 찍게 했다(drive.py:1420, 1965). 그래서 스텝 사이에 사람이 고치고 커밋한 파일까지 영원히 목록에 남고, 실행자가 자기가 안 건드린 파일을 주장해야 맞게 된다. 감독 흐름은 스텝 사이의 사람 개입을 전제하므로 다음 재시도에서 바로 터진다. O-00000005·6 과 같은 모양의 셋째 구멍이다. 같은 변경이 들여온 결함 하나를 함께 걷는다 — test_template_v4.py:117 이 플러그인 밖의 운영자 설정(PLUGIN_ROOT.parent/.stage/settings.json)을 읽어, 설치본에서는 그 파일이 없어 스위트가 죽는다.

## Actions


## Scope


## Success criteria


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision

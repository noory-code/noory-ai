---
id: W-00000127
title: 새 버전 규칙이 여섯 플러그인 전부에서 참이 되게 한다
kind: fix
venue: codex
milestone:
source:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: CLAUDE.md, stage/scripts/release_plugin.py, stage/scripts/tests/, stage/skills/stage-handoff/SKILL.md, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000127 새 버전 규칙이 여섯 플러그인 전부에서 참이 되게 한다

## Purpose

W-00000124 가 세운 릴리스 시점 버전 규칙이 지금 세 자리에서 어긋난다. 첫째가 급하다 — 루트 CLAUDE.md 는 여섯 플러그인 전부에 릴리스 명령을 쓰라고 하는데, evonest 는 pyproject.toml 을 버전의 유일한 자리로 선언했고(evonest/CLAUDE.md:36-44) 명령은 매니페스트만 고친다. 지금 그대로 따르면 버전의 진실이 둘로 갈린다. 명령이 pyproject 를 함께 보게 하거나 규칙이 적용 대상을 밝히거나 둘 중 하나. 둘째, 릴리스 뒤 미출시 절을 누가 다시 여는지 규칙이 안 말한다(두 번 연속 돌리면 멈춘다). 셋째, stage-handoff/SKILL.md:76 의 'every change ships a version bump' 이 이제 거짓이다.

## Actions


## Scope


## Success criteria


## Related truth


## Progress


## Verification


## Retrospective


## Promotion decision

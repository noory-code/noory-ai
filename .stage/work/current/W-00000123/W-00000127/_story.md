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

- **여섯 플러그인의 버전 자리를 먼저 센다.** `evonest/`, `rag/`, `stage/`, `plainly/`,
  `flutter-cask/`, `pencil_m3_flutter/` 각각에서 버전이 어디에 적히는지(매니페스트 둘,
  `pyproject.toml`, `pubspec.yaml` 등) 확인하고, 하위 `CLAUDE.md`·`AGENTS.md` 가 그 주제를
  이미 정했는지 본다. 센 결과를 작업 로그에 적는다.
- 그 셈을 근거로 정한다: 릴리스 명령이 플러그인마다 다른 버전 자리를 함께 옮기게 하거나,
  루트 규칙이 적용 대상을 밝히거나. **어느 쪽이든 지금처럼 "여섯 전부에 쓰라"고 두지
  않는다** — 지금 그 지시를 따르면 evonest 의 버전 진실이 둘로 갈린다.
- 릴리스 뒤 미출시 절을 누가 다시 여는지 정하고 그대로 만든다. 명령이 직접 열든, 규칙이
  다음 카드에게 맡기든 한쪽으로 정한다.
- `stage/skills/stage-handoff/SKILL.md:76` 의 "every change ships a version bump" 을 새 규칙에
  맞게 고친다.
- 매니페스트를 다시 쓸 때 기존 들여쓰기를 보존한다 — 지금은 통째로 다시 써서 정규화된다.

## Scope

`CLAUDE.md`(루트 규칙), `stage/scripts/release_plugin.py` 와 그 테스트,
`stage/skills/stage-handoff/SKILL.md`, `stage/CHANGELOG.md` 의 미출시 절.

**안 하는 것**: `evonest/CLAUDE.md` 를 고치는 일. 그 문서는 evonest 가 자기 버전 규칙을 정한
자리이고, 루트가 하위 규칙을 덮어쓰는 것이 아니라 루트가 하위를 인정해야 한다.

## Success criteria

- 여섯 플러그인의 버전 자리와 그것을 정한 하위 규칙이 세어져 작업 로그에 적혀 있다.
- 루트 `CLAUDE.md` 의 Plugin Changes 절이 그 셈과 어긋나지 않는다 — evonest 처럼 자기 버전
  규칙을 가진 플러그인에서 그대로 따라도 진실이 갈리지 않는다.
- 릴리스를 두 번 연속 돌려도 두 번째가 정상 동작한다(미출시 절이 다시 열려 있다). 또는
  규칙이 누가 여는지 명시하고 그 지시가 실제 절차와 맞는다. 어느 쪽이든 테스트가 고정한다.
- `stage/skills/stage-handoff/SKILL.md` 에 버전 올림을 매 변경의 전제로 말하는 문장이 없다.
- 릴리스 명령이 매니페스트의 기존 들여쓰기를 바꾸지 않는다. 테스트가 고정한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- 이 카드의 항목이 `stage/CHANGELOG.md` 의 미출시 절에 적혀 있다. **매니페스트 버전은 안
  건드린다** — 새 규칙이 그렇게 정했다.

## Related truth

- [DE-00000040](../../../official/decisions/records/DE-00000040.md) — 버전 규칙의 소유자
- [R-00000116](../../../work/retrospectives/R-00000116.md) — 이 어긋남이 생긴 경위
- `evonest/CLAUDE.md:36-50` — evonest 가 선언한 버전 SSOT


## Progress


## Verification


## Retrospective


## Promotion decision

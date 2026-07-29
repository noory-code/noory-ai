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

- 대조에 넘기는 목록에서 **사람이 스텝 사이에 바꾼 것**을 뺀다. 실행자가 도는 구간이 아니면
  실행자의 일이 아니다. 드라이버는 실행자를 부르기 직전과 직후를 자기 눈으로 보므로 그
  구간을 안다 — 누적 목록에서 이번 실행자 구간 밖의 사람 변경을 걸러내면 된다.
- 카드 누적 성질은 지킨다. 앞 **시도의 실행자**가 바꾼 것은 계속 목록에 있어야 한다
  (W-00000116 이 고친 O-00000006). 빠지는 것은 사람 몫뿐이다.
- 감독·무인 두 자리에 같이 적용한다 — 기준 스냅샷(`drive.py:1421`, `1966`)과 목록 생성
  (`drive.py:1471`, `2033`).
- `test_template_v4.py` 가 플러그인 밖(`PLUGIN_ROOT.parent / ".stage/settings.json"`)을 읽지
  않게 한다. 플러그인 테스트는 플러그인 것만 본다 — 템플릿이 두 문장을 갖는지만 확인하고,
  운영자 설정이 그것을 따르는지는 플러그인이 판정할 일이 아니다.
- `stage/CHANGELOG.md` 항목과 두 매니페스트 패치 올림.

## Scope

`stage/scripts/drive.py` 의 관측 구간과 두 호출 자리, `stage/scripts/tests/`(사람 편집이
섞이는 상황을 고정하는 테스트와 플러그인 밖을 읽던 테스트의 수정), CHANGELOG, 두 매니페스트.

이 카드가 **안 하는 것**: 리뷰 판정 계약(W-00000117), 한계값과 사전 점검(W-00000118, 코덱스
캐시 잠금이 시도를 먹는 것도 그 카드), 상한 되돌리기(W-00000119).

## Success criteria

- 스텝 사이에 사람이 파일을 고치고 커밋해도, 다음 시도에서 실행자가 그 파일을 안 적었다는
  이유로 실패하지 않는다. 그 상황을 고정하는 테스트가 있다.
- 앞 시도의 실행자가 바꾼 파일은 여전히 목록에 남는다 — W-00000116 이 세운 성질이 안 깨진다.
  같은 묶음의 테스트가 이것도 고정한다.
- 감독·무인 두 자리 모두에서 위 두 성질이 성립한다.
- `test_template_v4.py` 가 플러그인 디렉터리 밖의 파일을 열지 않는다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 와
  `python3 -m unittest discover -s stage/hooks/tests -q` 가 전부 통과한다.
- `stage/CHANGELOG.md` 에 항목이 있고 두 매니페스트 버전이 같은 값으로 패치 올림돼 있다.

### 위험

사람 몫을 걸러내다 실행자 몫까지 걸러내면 W-00000116 이 고친 것이 되돌아간다. 두 성질을 같은
테스트 묶음에서 함께 고정해 한쪽이 다른 쪽을 깨뜨리지 못하게 한다. 커밋이 끼어도 마찬가지다 —
사람이 스텝 사이에 커밋하는 것은 감독 흐름의 정상 동작이므로, 커밋된 사람 변경도 빠져야 한다.

## Related truth

- [DE-00000039](../../../official/decisions/records/DE-00000039.md) §1 — 이 계약의 소유자
- [R-00000113](../../../work/retrospectives/R-00000113.md) — 이 구멍을 연 경위


## Progress


## Verification


## Retrospective


## Promotion decision

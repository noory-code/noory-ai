---
id: W-00000118
title: 한계값이 규모에서 나오고 venue 사전 점검이 선다
kind: development
venue: codex
milestone:
priority:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/scripts/tests -q"
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/scripts/drive.py, stage/scripts/tests/, .stage/settings.json, stage/templates/, stage/docs/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000118 한계값이 규모에서 나오고 venue 사전 점검이 선다

## Purpose

DE-00000039 §3. 명령당 시간 제한 900초 고정을 버리고 시작 시점에 규모에서 계산한다(O-00000003). venue 별 사전 점검 명령을 executors·reapers 와 같은 모양으로 받고, 실패하면 시도를 시작하지 않는다(W-00000092 흡수분). 시작 전에 O-00000003 의 '시도를 쓴다' 서술을 실측으로 검증한다 — timed out 은 이미 인프라 실패로 분류돼 시도를 안 쓰는 것이 현행 코드다.

## Actions

- **먼저 실측한다.** O-00000003 은 "시간 초과가 카드 시도를 쓴다"고 적었는데 현행
  `infrastructure_failure()` 는 `timed out` 을 인프라 실패로 분류한다. 어느 쪽이 참인지 돌려
  보고 결과를 작업 로그에 적는다. 틀린 전제 위에 고치지 않는다.
- 명령당 시간 제한의 고정 기본값(900초)을 버리고 **서브트리 크기에서 계산한다**. 반복·시간
  총량을 그렇게 정하기로 한 DE-00000037 과 같은 자리다.
- venue 별 **사전 점검 명령**을 받는다. `executors`·`reapers` 와 같은 모양이다. 실패하면
  시도를 시작하지 않고 시도를 쓰지도 않는다.
- 사전 점검이 실제로 막아야 할 것 하나가 이미 실측돼 있다 — 코덱스 플러그인 캐시가 낡아
  실행자가 첫 읽기에서 죽는 경우(P-00000001, 2026-07-29 에 두 번). 그날 드라이버가 그것을
  카드 시도로 셌다. 이 카드가 그 자리를 닫는다.
- 점검 명령이 없는 venue 는 그 사실을 설정에 밝힌다. `reapers` 가 `null` 로 "거둘 것 없음"을
  표현한 것과 같은 모양이다 — 표현할 수 없으면 매번 경고가 나고 사람이 경고를 무시하게 된다.
- **O-00000010 을 함께 본다.** 시간이 다 됐을 때 무엇이 돌던 중인지 시도 기록에 적으면 병렬
  쪽이 로그 제목으로 짐작하지 않아도 된다. 이 카드가 `drive.py` 를 만지는 자리다.
- `stage/CHANGELOG.md` 미출시 절에 적는다. **매니페스트 버전은 안 건드린다.**

## User value

큰 카드가 시간에 걸려 죽지 않는다. 실행자가 못 일할 상태면 시도를 쓰기 전에 멈춘다 — 카드
잘못이 아닌 실패로 시도를 잃지 않는다.

## Scope

### Included


### Excluded


## Risks

- 사전 점검을 필수로 만들면 설정이 없는 프로젝트에서 드라이버가 안 돈다. 선택으로 두되
  **없을 때 무엇을 하는지 밝힌다** — 없음과 "점검할 것 없음"을 구분한다.
- 시간 제한을 크기에서 계산하다 너무 짧게 잡으면 지금보다 나빠진다. 계산값이 지금 기본값
  아래로 안 내려가게 한다.

## Success criteria

- O-00000003 의 서술을 실측한 결과가 작업 로그에 있다. 현행 동작과 다르면 관측을 고칠 근거가
  된다.
- 명령당 시간 제한이 서브트리 크기에서 나온다. 잎이 많을수록 커지고, 지금 기본값 아래로는
  안 내려간다. 테스트가 고정한다.
- venue 별 사전 점검 명령을 설정에서 받는다. 점검이 실패하면 실행자를 안 부르고 **시도를
  안 쓴다.** 두 성질을 각각 고정하는 테스트가 있다.
- 점검 명령이 없는 경우와 "점검할 것 없음"으로 밝힌 경우가 구분되고, 앞은 경고하고 뒤는
  조용하다. 테스트가 고정한다.
- 시도 기록에 그 시점에 도는 역할이 적힌다(O-00000010). 병렬 쪽이 로그 제목으로 짐작하지
  않아도 된다. 테스트가 고정한다.
- `stage/docs/` 의 드라이버 절이 시간 제한과 사전 점검을 사실대로 말한다.
- `python3 -m unittest discover -s stage/scripts/tests -q` 가 통과한다.
- `stage/CHANGELOG.md` 미출시 절에 항목이 있고 매니페스트 버전은 그대로다.

### 이 카드가 만드는 것이 못 하게 막지 않는다

사전 점검은 시작을 막는 장치다. 막는 것을 만들 때는 **잘못 막는 경우**부터 센다.

- 점검 명령 자체가 죽으면(도구가 없거나 시간 초과) 그것은 카드 실패가 아니다. 그 경우를
  구분해 시도를 안 쓴다. 테스트가 고정한다.
- 점검을 건너뛰는 길이 있다. 점검이 틀려서 일을 못 하게 되는 상황에 사람이 나갈 문이 있어야
  한다 — 이 프로젝트가 fail-closed 잠금을 네 번 겪었다.

## Next action

끝나면 사람이 O-00000003 과 O-00000010 을 실측 결과에 맞게 정리한다.

## Progress

## Verification

## Retrospective

## Promotion decision

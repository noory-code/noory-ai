---
id: W-00000115
title: 드라이버가 실패 경로에서도 계약대로 움직인다
kind: development
venue: codex
milestone:
priority: 2
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000133
promotion: not_applicable
review: not_required
scope: stage/, .stage/
promotes:
decision_refs:
---

# W-00000115 드라이버가 실패 경로에서도 계약대로 움직인다

## Purpose

**드라이버는 무인 실행을 위해 만들었다. 지금은 사람이 옆에 붙어 매 실패마다 "이건 카드
문제가 아니다"를 판단해 줘야 한다. 그러면 무인이 아니다.** 실전 세 카드(W-00000105~107)에서
드라이버가 낸 실패 여섯 중 다섯이 카드 내용과 무관했고, 사람 개입이 실패 다섯 + 상한 되돌리기
세 번이었다.

이 에픽은 그 개입을 없앤다. 계약(DE-00000039)이 성공하는 한 바퀴만 보고 쓰였던 것을 실패
경로까지 넓혀 코드에 싣는다 — 정직한 보고가 실패로 기록되지 않고, 판정이 읽는 방식 때문에
뒤집히지 않고, 카드 잘못이 아닌 실패가 시도를 먹지 않고, 사람이 개입한 뒤 돌아오는 길이
명령이 된다.

## Stories

| 스토리 | 무엇 | 닫는 빈틈 |
|---|---|---|
| W-00000116 | 대조가 드라이버 지식과 카드 누적 기준으로 | O-00000005·6 |
| W-00000121 | 관측이 사람의 편집을 실행자에게 묻지 않게 | W-116 이 연 구멍 |
| W-00000117 | 리뷰 판정을 파일로 | O-00000004 (하루 일곱 번) |
| W-00000118 | 규모 기반 한계값 + venue 사전 점검 | O-00000003, P-00000001 |
| W-00000119 | 상한 되돌리기가 근거를 남기는 명령으로 | O-00000007 |
| W-00000130 | 문서가 실제 계약을 말하게 | W-117 이 남긴 문서 넷 |

## User value

무인 실행이 이름값을 한다 — 사람이 지켜보지 않아도, 통과한 일이 통과로 기록되고 실패한
일이 왜 실패했는지 남는다.

## Scope

### Included

드라이버(`drive.py`)와 닫기(`close_work.py`)의 판정·관측·한계값, 리뷰·실행자 명령과 템플릿,
드라이버 문서.

### Excluded

병렬 실행 — 에픽 W-00000123 이 했다. 보관 인덱스 계약 — W-00000111. 설치본 스키마 잠금 —
가드·배포의 문제(P-00000001 의 근본 수정은 코덱스 런타임 몫).

## Risks

- 계약을 넓히다 성공 경로를 깨뜨릴 수 있다. 스토리마다 기존 테스트 전체를 인수 검사로 돈다.
- 이 에픽이 고치는 대상(드라이버)으로 이 에픽을 돌린다. 감독 모드로만 돌리고, 스텝마다
  사람이 판정을 확인한다.

## Success criteria

- O-00000003~7 다섯 관측이 전부 "닫힘"으로 정리된다.
- 카드 잘못이 아닌 실패가 카드 시도를 먹는 자리가 없다.
- 스토리 전부가 각자의 인수 검사와 독립 리뷰를 통과한다.

## Next action

없음 — 스토리 전부 종결, 관측 다섯 닫힘 정리 완료.

## Progress

스토리 여섯 + 도중에 실측이 세운 둘(W-00000121·134)이 전부 끝났다(2026-07-29~30). 마지막
스토리의 액션 셋은 사람 개입 없이 한 바퀴씩 끝났다 — 에픽이 없애려던 개입이 실제로 없어졌다.

## Verification

밑의 여덟 장이 각자 인수 검사와 리뷰를 통과했다. 성공 기준 확인: O-00000003~7 전부
닫힘으로 정리됨, 카드 잘못이 아닌 실패가 시도를 먹는 자리 없음(인프라 분류 공유 + 사전
점검 + 판정 파일). 스크립트 483·훅 343 통과, 감사 0/0.

### Executed at close — 2026-07-30

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000133](../../retrospectives/R-00000133.md)

## Promotion decision

not_applicable — 계약은 DE-00000039 가 이미 official 로 갖고 있다.

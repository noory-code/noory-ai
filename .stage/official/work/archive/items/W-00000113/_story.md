---
id: W-00000113
title: 드라이버 한 바퀴 계약을 실제 운행에 맞춘다 — 결정 준비 (P-00000003)
kind: planning
venue: claude
milestone:
source:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000111
promotion: approved
review: not_required
scope: .stage/proposals/, .stage/decisions/, .stage/state/, .stage/work/planned/
promotes: .stage/official/decisions/records/DE-00000039.md, .stage/official/decisions/index.md
decision_refs: DE-00000039
---

# W-00000113 드라이버 한 바퀴 계약을 실제 운행에 맞춘다 — 결정 준비 (P-00000003)

## Purpose

DE-00000034 의 계약이 성공하는 한 바퀴만 보고 쓰여, 실전 세 카드(W-00000105~107)에서 드라이버 실패 여섯 중 다섯이 카드 내용과 무관했다(O-00000003~7). 하나씩 때우지 않고 계약을 실패 경로까지 넓힌다. 적용 자리를 실패 경로부터 코드·설정·문서 전부에서 세고, W-00000092(사전 점검·생존 감시)의 흡수 여부를 판단해 결정 기록을 남기고 구현 카드를 뽑는다.

## Actions

- 관측 다섯(O-00000003~7)과 W-00000092 를 읽고 빈틈이 계약의 어느 바깥인지 가른다.
- 적용 자리를 실패 경로부터 코드·설정·문서·테스트에서 센다.
- 결정 기록(DE-00000039)에 갈림·선택·자리 목록을 적고 사람 확인을 받는다.
- decided 뒤 구현 카드를 규모로 쪼개 등록하고 W-00000092 흡수를 마무리한다.

## Scope

`.stage/` 만 바꾼다 (제안·결정·상태·계획 카드). 플러그인 소스는 구현 카드 몫.

## Success criteria

- 다섯 빈틈 각각에 계약 쪽 답이 정해져 있고 근거가 결정 기록에 있다.
- 적용 자리가 실패 경로부터 세어져 있고, 안 다루는 것도 이유와 함께 적혀 있다.
- W-00000092 흡수 여부가 판정돼 있다.
- `python3 stage/scripts/audit_stage.py` 가 errors=0, warnings=0.

## Related truth

- [P-00000003](../../../proposals/P-00000003.md) — 방향 넷을 세운 제안
- [DE-00000034](../../../official/decisions/records/DE-00000034.md) — 다시 여는 계약
- [DE-00000037](../../../official/decisions/records/DE-00000037.md) — 한계값이 규모에서 나온다는 전제

## Progress

- 관측 다섯 + W-00000092 판독 완료. 다섯이 전부 "성공 바퀴 바깥"임을 확인.
- 적용 자리 셈 완료 — 실패 판정 자리 5, 호출 자리, 같은 문장 여러 벌(리뷰 명령 4벌, 실행자
  2벌, 템플릿 공백) 포함. DE-00000039 의 Where this applies 가 소유.
- O-00000003 의 "시도를 쓴다"가 현행 코드와 어긋나는 것 발견 (`timed out` 은 인프라 실패로
  시도를 안 씀) — 결정문에 검증 필요로 표시.
- DE-00000039 초안 작성 → 사람 확인(2026-07-29) → decided.
- 구현 등록: 에픽 W-00000115 + 스토리 W-00000116~119 (계획, venue codex).
- W-00000092 흡수 판정 완료. 반려 처리는 계획 인덱스 편집을 막는 게이트 결함에 걸려
  O-00000009 + 수정 카드 W-00000114 로 남김.

## Verification


### Executed at close — 2026-07-29

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000111](../../retrospectives/R-00000111.md)

## Promotion decision

approved — DE-00000039 를 status promoted 로 `official/decisions/records/` 에 올리고 official
인덱스에 행 하나를 더한다.

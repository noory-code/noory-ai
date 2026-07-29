---
id: W-00000112
title: 대기 결정 다섯 건을 official 로 승격하고 결정 인덱스 누락을 메꾼다
kind: documentation
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
retrospective_ref: R-00000110
promotion: approved
review: not_required
scope: .stage/decisions/, .stage/official/decisions/
promotes: .stage/official/decisions/records/DE-00000034.md, .stage/official/decisions/records/DE-00000035.md, .stage/official/decisions/records/DE-00000036.md, .stage/official/decisions/records/DE-00000037.md, .stage/official/decisions/records/DE-00000038.md, .stage/official/decisions/index.md
decision_refs:
---

# W-00000112 대기 결정 다섯 건을 official 로 승격하고 결정 인덱스 누락을 메꾼다

## Purpose

지난 에픽이 남긴 결정 DE-00000034~38 은 미래 작업을 구속하는데 pending 에 남아 있다. DE-00000030 이 정한 규칙(구속하는 결정은 승격, venue_exception 은 소진된 허가라 잔류)대로 다섯을 official 로 올리고, 이미 records/ 에 있으면서 인덱스 행이 없는 DE-00000031~33 의 누락도 메꾼다. P-00000003(드라이버 계약 재정비)이 DE-00000037 을 전제로 서므로 먼저 굳힌다.

## Actions

- 대기 결정 아홉을 DE-00000030 의 규칙으로 가른다: 미래 작업을 구속하는 DE-00000034~38 은
  승격 대상, `authorizes: venue_exception` 인 DE-00000006·8·25·26 은 소진된 허가라 잔류.
- 카드 `promotes` 에 승격 대상 여섯 경로(레코드 다섯 + official 결정 인덱스)를 선언한다.
- `decisions/index.md` 의 낡은 행(DE-00000036 을 open 으로 적은 것)을 지운다. 남는 네 건은
  검토 중이 아니므로 표는 비운다.
- 닫은 뒤 승격 인텐트로 다섯 레코드를 `official/decisions/records/` 로 옮기며 status 를
  promoted 로 바꾸고, official 인덱스에 DE-00000031~38 행 여덟을 더한다(31~33 은 records/ 에
  있으면서 행이 없던 누락분).

## Scope

`.stage/decisions/`, `.stage/official/decisions/` — 결정 레코드와 그 인덱스만 움직인다.
플러그인 소스는 건드리지 않으므로 버전 올림 없음.

## Success criteria

- 승격/잔류 판별이 DE-00000030 의 규칙을 그대로 따르고 카드에 그 근거가 적혀 있다.
- 카드 `promotes` 가 승격 대상 여섯 경로를 정확히 선언한다.
- `decisions/index.md` 에 실제 상태와 어긋난 행이 없다.
- `python3 stage/scripts/audit_stage.py` 가 errors=0, warnings=0 으로 통과한다.

## Related truth

- [DE-00000030](../../../official/decisions/records/DE-00000030.md) — 승격/잔류 판별 규칙의 SSOT
- [P-00000003](../../../proposals/P-00000003.md) — DE-00000037 을 전제로 여는 다음 제안


## Progress

- 대기 아홉 건 판별 완료: DE-00000034~38 승격, DE-00000006·8·25·26 잔류 (DE-00000030 규칙).
- `promotes` 여섯 경로 선언, pending 인덱스의 낡은 DE-00000036 행 제거.
- 회고 R-00000110 작성.

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

[R-00000110](../../retrospectives/R-00000110.md)

## Promotion decision

approved — 레코드 다섯을 status promoted 로 `official/decisions/records/` 에 옮기고 official
인덱스에 DE-00000031~38 행 여덟을 더한다. 인텐트는 이 카드 이름으로 경로당 하나.

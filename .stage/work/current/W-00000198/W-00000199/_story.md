---
id: W-00000199
title: 끝난 기록이 어디로 가고 누가 옮기는지 정한다
kind: design
venue: claude
milestone:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py --project-root ."
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: not_required
scope: stage/docs/BLUEPRINT.md, stage/docs/SCHEMA_V5.md, stage/CHANGELOG.md, .stage/decisions/pending/, .stage/official/decisions/records/DE-00000030.md
promotes:
decision_refs:
---

# W-00000199 끝난 기록이 어디로 가고 누가 옮기는지 정한다

## Purpose

끝난 기록의 자리와 그것을 옮기는 주체가 어디에도 안 적혀 있어 매번 다시 판단하게 되므로, 보관 자리와 이동 주체를 결정으로 못박고 설계 문서에 싣는다

## Actions

없음 — 결정 하나와 문서 반영이 한 덩어리라 나누면 목록만 길어진다.

## User value

다음에 새 기록 갈래를 만들 때 "끝나면 어디로 가나"를 다시 토론하지 않는다. 규칙이 한 줄로
읽히고, 그 규칙을 누가 집행하는지도 같이 읽힌다.

## Scope

### Included

- 끝난 기록의 보관 자리를 결정으로 못박는다: 결정·제안·상태 각 갈래가 `official/` 아래
  자기 보관함을 가지고, 카드가 이미 하는 것과 같은 모양이다.
- **폴더가 상태다**를 규칙으로 적는다. 살아 있는 서랍에 있으면 살아 있는 것이고, 보관함에 있으면
  끝난 것이다. 상태를 말하는 frontmatter 칸을 따로 두지 않는다.
- 제안만 실림·접힘·절반 세 결과를 한 칸으로 구분한다. P-00000004 가 절반이라 두 값으로는
  지금 인덱스가 들고 있는 정보가 깎인다.
- 갈래마다 **누가 옮기는지**를 정한다. 허가증은 계산되니 카드 보관 명령이, 나머지는 사람이
  판정하니 닫는 명령이 옮긴다.
- DE-00000030 첫머리에 무엇이 언제 그것을 대체했는지 적는다 — DE-00000030 자신이 정한 규칙이다.
- 새 규칙을 `stage/docs/BLUEPRINT.md` 와 `stage/docs/SCHEMA_V5.md` 에 싣는다.

### Excluded

- 코드는 안 건드린다. 자리를 만드는 것은 W-00000200, 옮기는 쪽은 W-00000201·202 다.
- 스키마 버전은 안 올린다. 그 판단의 근거는 에픽이 들고 있다.

## Risks

- **DE-00000030 은 공식 결정이라 승격 통행증이 있어야 고칠 수 있다.** 대체 표시를 달려면
  `scripts/promote_intent.py` 로 이 카드를 지목한 통행증이 먼저 필요하다.
- 새 결정이 DE-00000030 을 통째로 뒤집는 것처럼 읽히면 안 된다. "구속하는 결정만 승격한다"는
  그대로 살아 있고, 바뀌는 것은 안 올린 기록이 어디에 사는가 하나다.

## Success criteria

- 새 기록 갈래를 만드는 사람이 "끝나면 어디로 가나"를 문서 한 곳에서 답할 수 있다.
- 갈래마다 옮기는 주체가 사람인지 명령인지 명시돼 있다.
- DE-00000030 을 여는 사람이 그 규칙의 어느 부분이 아직 살아 있는지 첫머리에서 안다.
- 감사가 오류 없이 통과한다.

## Next action

`official/decisions/records/DE-00000030.md` 를 고치기 위한 승격 통행증부터 낸다.

## Related truth

- DE-00000030 — "다 쓴 허가증은 승격하지 않는다"까지만 정했고 그것이 어디에 사는지는 비어 있다.
- `stage/docs/PHILOSOPHY.md` §목적이 약속이다 — 규칙이 빈자리를 남기면 아무 일도 안 일어난다.

## Progress


## Verification


## Retrospective


## Promotion decision

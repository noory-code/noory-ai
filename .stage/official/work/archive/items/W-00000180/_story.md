---
id: W-00000180
title: 릴리스에 자기 종류를 주고 클로드로 보낸다
kind: design
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000180
promotion: promoted
review: not_required
scope: .stage/
promotes: .stage/official/decisions/records/DE-00000054.md, .stage/official/decisions/index.md
decision_refs: DE-00000054
---

# W-00000180 릴리스에 자기 종류를 주고 클로드로 보낸다

## Purpose

릴리스가 코덱스로 갈라지는데 실제로는 못 가서 카드마다 일회성 허가를 발급해 왔다.

## Actions

없다. 이 스토리가 스스로 돈다.

## User value

릴리스 카드를 만들면 갈래가 바로 클로드로 잡힌다. 카드마다 허가 문서를 쓰는 일이 없어진다.

## Scope

### Included

- 갈래 표에 `release -> claude` 를 넣는다.
- 검증 기준 표에 `release` 가 무엇으로 통과인지 한 줄 넣는다.
- 이 결정을 기록으로 남긴다. DE-00000045 가 미뤄 둔 물음의 답이다.

### Excluded

- **플러그인이 배포하는 기본값.** 종류 이름은 프로젝트가 정한다 — 다른 프로젝트가 같은 걸
  겪기 전에 위로 올리지 않는다.
- 이미 발급된 일회성 허가 둘(DE-00000041·45). 그 카드들은 끝났다.
- 릴리스 명령 자체. 지금 그대로 쓴다.

## Risks

- **`ops` 로 잡아 둔 옛 릴리스 카드가 있으면 갈래가 어긋난 채로 남는다.** 보관된 카드는 안
  고치는 규칙이 있으니 그대로 두되, 감사가 뭐라 하는지 확인한다.

## Success criteria

- 릴리스 카드를 `--kind release` 로 만들면 갈래가 클로드로 잡히고 허가 문서가 필요 없다.
- 검증 기준 표에 `release` 줄이 있고, 그 줄이 **버전이 올라간 것만이 아니라 새 버전이 실제로
  불러와지는 것까지** 요구한다.
- 결정 기록이 DE-00000045 를 잇는다 — 왜 세 번째에 정책을 고쳤는지가 적혀 있다.
- 감사 오류 0.

## Next action

없다. 다 실렸다.

## Verification

### 실측 — 2026-08-02

- **갈래**: `--kind release` 로 카드를 실제로 만들어 봤다. `venue derived from venue_routing:
  release -> claude` 가 나왔고 허가 문서를 안 물었다(W-00000181).
- **통과 기준**: 검증 기준 표에 `release` 줄이 있고, 버전이 올라간 것만으로는 통과가 아니라고
  적혀 있다.
- **결정 기록**: DE-00000054 가 DE-00000045 를 잇는다. 왜 두 번째엔 안 고치고 세 번째에
  고쳤는지가 적혀 있다.
- **감사**: 오류 0 · 경고 0. 중간에 감사가 새 결정이 목록에 없다고 한 번 잡았고, 어제 만든
  갱신 명령으로 풀었다 — 그 장치가 실제로 돈 첫 사례다.

### Executed at close — 2026-08-02

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Related truth

- **DE-00000041 · DE-00000045** — 릴리스가 클로드 창에서 돌아도 된다는 허가를 카드 한 장씩
  내줬다. 둘 다 같은 이유를 적었다: 릴리스는 명령 실행·커밋·푸시가 한 몸인데 실행하는 쪽은
  계약상 커밋을 안 한다. DE-00000045 가 **"두 번째다. 세 번째가 오면 우연이 아니라 패턴이니
  그때 정책을 고친다"** 고 적고 미뤘다. 이 카드가 그 세 번째다.


## Progress


## Verification


## Retrospective


## Promotion decision

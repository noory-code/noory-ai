---
id: W-00000195
title: 제안과 계획에 남은 것을 전부 처분한다
kind: documentation
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000195
promotion: not_applicable
review: not_required
scope: .stage/
promotes:
decision_refs:
---

# W-00000195 제안과 계획에 남은 것을 전부 처분한다

## Purpose

실린 제안이 계속 제안으로 남아 있고 안 오는 상황을 막는 계획 카드가 줄에 서 있다.

## Actions

없다. 이 스토리가 스스로 돈다.

## User value

서랍을 열면 아직 살아 있는 것만 보인다. 실린 제안과 안 오는 상황을 막는 카드가 줄에 안 서 있다.

## Scope

### Included

- 제안 넷에 무엇이 됐는지 적고 목록 상태를 맞춘다.
- 계획 카드 W-00000154 를 처분한다.
- **제안이 다시 안 쌓이게 닫는 규칙을 적는다.** 지금은 닫는 길이 아예 없다.

### Excluded

- 제안 본문을 고치는 일. 그때 제안한 것은 그때의 사실이다.
- 제안을 지우는 일. 결정 기록과 같은 이유로 안 지운다 — 무엇을 제안했고 무엇이 됐는지가 남아야
  한다.
- P-00000004 뒷절반을 실제로 만드는 일. 큰 변경이라 이 카드가 아니다.

## Risks

- **"실렸다"고 적는 것이 짐작이면 기록이 거짓이 된다.** 넷 다 무엇으로 실렸는지 실측하고
  그 근거를 함께 적는다.

## Success criteria

- 제안 목록에 무엇이 됐는지가 줄마다 있고, 근거(어느 결정·관측·마일스톤)가 붙어 있다.
- 계획 줄에 카드가 없다.
- 제안을 닫는 규칙이 적혀 있어, 다음 제안이 실리면 그 자리에서 닫힌다.
- 감사 오류 0.

## Next action

없다. 다 처분했다.

## Progress

### 실측 — 2026-08-03

넷 다 무엇이 됐는지 열어서 확인했다.

| 제안 | 무엇을 하자고 했나 | 무엇이 됐나 |
|---|---|---|
| **P-00000001** | 코덱스 캐시가 새 버전을 못 잡는 것을 **알려진 문제로 기록하고 완화책을 명시한다** | **실렸다.** 완화책이 드라이버 사전 확인 명령에 들어 있고, 오늘 0.56.0 을 올렸을 때 그 명령이 무엇을 하라고 알려 줘서 그대로 풀었다 |
| **P-00000002** | 일감을 규모(에픽·스토리·액션)로 관리한다 | **실렸다.** DE-00000035 가 정했고 지금 매일 쓴다 |
| **P-00000003** | 드라이버 한 바퀴 계약을 실제 운행에 맞춘다 | **실렸다.** 지목한 관측 다섯(O-3·4·5·6·7)이 전부 닫혔다 |
| **P-00000004** | ① 일감이 성취로 선다 ② 드라이버 껍질을 에이전트 팀으로 바꾼다 | **절반 실렸다.** ①은 M-00000001 과 목적 게이트(DE-00000050). ②는 안 했다 |

**계획 카드 W-00000154** — 그릇이 둘 이상일 때 나는 거절을 없애자는 카드다. **그 거절이 한 번도
난 적이 없다** — 지금 갱신을 미리 돌려 봐도 0건이다. 안 오는 상황을 막는 카드라 반려한다.

## Related truth

- **DE-00000030** — 결정은 안 지우고, 남는 이상 그것이 지금 구속하는지가 읽혀야 한다. 제안도
  같은 이유로 안 지우고 무엇이 됐는지를 적는다.


## Progress


## Verification


### Executed at close — 2026-08-03

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective


## Promotion decision

---
id: W-00000248
title: 들이는 명령이 인덱스를 고칠 수 있게 결정을 잇는다
kind: planning
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: rejected
verification: pending
retrospective: completed
retrospective_ref: R-00000245
promotion: rejected
review: not_required
scope: .stage/decisions/, .stage/state/
promotes:
decision_refs:
---

# W-00000248 들이는 명령이 인덱스를 고칠 수 있게 결정을 잇는다

## Purpose

카드를 닫으면 반드시 바뀌는 인덱스를 들이는 명령의 허용 경로가 금지해서 M-00000004 의 가장 큰 조각을 못 만들고 있으므로, DE-00000065 를 잇는 결정을 세워 조건 3 의 허용 목록을 고친다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- 새 결정이 서고, 그 결정을 근거로 들이는 명령을 만드는 카드가 다시 설 수 있다

## Next action

없다. 거절한다.

## Related truth

- DE-00000066 — 이 카드가 세우려던 바로 그 결정. `supersedes: DE-00000065`, 조건 3을 다시
  썼고 승격까지 끝났다. W-00000239 가 만들었다.
- O-00000040 — 이 카드의 근거였던 관측. `## Next action` 이 DE-00000066 이 선 뒤에도
  안 고쳐져서 "잇는 결정을 세워라"를 그대로 말하고 있었다.

## Progress

아무것도 안 만들었다. 시작한 직후 전제를 확인하다 이미 되어 있는 것을 발견하고 멈췄다.

## Verification

**전제가 틀려서 거절한다. 이 카드가 하려던 일은 이미 되어 있다.**

DE-00000066 을 열어 확인했다. 프론트매터가 `supersedes: DE-00000065`, `status: promoted`
이고, 본문 `### 조건 3 (개정)` 이 허용 목록을 셋으로 다시 쓴다 — 카드의 `scope`, 이 실행이
닫은 카드들의 생애주기 기록, 그리고 현재 작업 구역이 선언한 인덱스 표면. 마지막 항목이
`.stage/work/active.md` 와 `.stage/work/review.md` 를 덮고, 이름을 리터럴로 적는 대신
`v4_lifecycle_paths()` 에서 읽는다.

이 카드의 성공 기준 한 줄 중 앞 절("새 결정이 선다")은 등록 시점에 이미 참이었다. 뒤
절("그 결정을 근거로 명령을 만드는 카드가 다시 설 수 있다")은 이 카드가 아니라 그 명령
카드가 할 일이다.

**왜 이런 카드가 섰나.** 근거로 삼은 관측 O-00000040 의 `## Next action` 이 "DE-00000065 를
잇는 결정을 세운다"를 그대로 말하고 있었다. DE-00000066 이 선 뒤에 그 문장을 아무도 안
고쳤다. 어제 열린 관측 열일곱을 처분하면서 이 관측을 일감으로 세울 때, 관측이 적어 둔 다음
걸음을 그대로 옮기고 그것이 아직 참인지는 안 봤다.

### 범위를 넘은 자리

회고(R-00000245)의 규칙 후보 둘이 승격 조건을 만족해 규칙 파일 둘을 고쳤다. 둘 다 이 카드의
`scope`(`.stage/decisions/, .stage/state/`) 밖이고, 플러그인이 소유하는 자리라 스테이지를 까는
모든 프로젝트에 걸린다.

- `stage/skills/stage-decision/SKILL.md` — 결정을 승격하는 자리에서 그 결정을 부른 관측을
  함께 닫는 걸음을 더했다. 하니스 밖에서 잡혔으므로 1회차로 승격한다.
- `stage/skills/stage-work/SKILL.md` — 이미 있던 "관측을 카드로 옮기기 전에 전제를 돌려 본다"
  규칙이 코드가 움직인 경우만 덮고 있었다. 결정 기록처럼 돌려 볼 동작이 없는 산출물을 더했다.
  2회차다(R-00000211·212·213 이 코드 쪽에서 같은 자리를 적었다).

## Retrospective

## Promotion decision

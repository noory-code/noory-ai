---
id: W-00000215
title: 목적 표시가 빈 카드에서 한 번을 안 쓰게 한다
kind: fix
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s stage/hooks/tests -p test_stage_guard.py -q"
status: archived
terminal_disposition: rejected
verification: pending
retrospective: completed
retrospective_ref: R-00000213
promotion: not_applicable
review: not_required
scope: stage/hooks/stage_guard.py, stage/hooks/tests/test_stage_guard.py, stage/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000215 목적 표시가 빈 카드에서 한 번을 안 쓰게 한다

## Purpose

쓰기 직전에 목적을 띄우는 장치가 막 만든 카드에서는 빈 본문을 보여 주며 세션의 한 번을 써 버리므로, 목적이 빈 카드를 만나면 그 한 번을 아꼈다가 목적이 채워진 뒤에 뜨게 한다

## Actions

없음 — 훅의 소모 판정 한 자리를 고치고 시험을 더하는 한 덩어리다.

## User value

카드를 만들고 바로 본문을 쓰는 가장 흔한 흐름에서, "이거 왜 하는 일이었지"를 보여 주는 장치가
지금은 제목 한 줄만 보여 주고 세션의 한 번을 써 버린다. 고치면 그 한 번이 목적이 실제로
채워진 뒤 — 진짜 필요할 때 — 쓰인다.

## Scope

### Included

- `stage_guard.py` 의 쓰기 직전 목적 표시(`append_purpose_context`, 573행 근처)가 카드의
  `## Purpose` 가 비어 있으면 **세션 한 번을 소모하지 않고** 지나가게 한다. 목적이 채워진
  뒤의 첫 쓰기가 그 한 번을 쓴다.
- 빈 목적 카드 → 본문 채움 → 다음 쓰기에서 목적이 뜨는 흐름의 시험을
  `test_stage_guard.py` 에 더한다.

### Excluded

- 카드 목적이 비면 마일스톤·테마를 대신 보여 주는 길(O-00000018 의 둘째 후보)은 안 간다 —
  등록이 이제 빈 목적을 거부하므로(0.58.0), 빈 본문은 대개 "막 만든 직후" 한순간뿐이다.
  그 순간을 아끼는 쪽이 싸고 충분하다.

## Risks

- 등록 게이트(0.58.0)가 빈 목적 카드를 거의 없앴으므로 이 구멍의 빈도는 낮아졌다. 다만 옛
  카드 32장은 여전히 목적이 비어 있고, 그 카드를 만지는 첫 쓰기가 지금도 한 번을 헛써 버린다.
- "비었다" 판정이 공백·플레이스홀더 문장을 어떻게 볼지 정해야 한다. 좁게(정말 빈 것만) 시작한다.

## Success criteria

- 목적이 빈 카드에 첫 쓰기를 해도 장치의 세션 한 번이 소모되지 않는다
- 목적이 채워진 뒤의 첫 쓰기에서 목적이 뜬다

## Next action

`append_purpose_context` 가 세션 한 번을 소모하는 자리와 카드 본문을 읽는 자리를 확인하고,
빈 목적이면 소모 없이 지나가는 갈래를 끼운다.

## Related truth

- O-00000018 — W-00000167 등록 직후 실측: 돌아온 글에 Purpose 도 User value 도 없이 제목
  한 줄뿐이었다. 이 카드가 닫히면 그 관측을 닫는다.


## Progress

워크트리 병렬 실행 1바퀴. 실행자(코덱스)가 소스를 안 바꾸고 카드를 거절했다 — 카드의 전제
"목적 표시가 세션에 한 번만 뜬다"가 `0f84289c`(0.56.0)에서 죽었다. 지금 장치는 목적을 매
도구 호출마다 다시 계산해 붙이고, 아낄 소모 상태가 없다. 판정자(클로드)가 훅을 직접 돌려
확인했다: 빈 목적 카드로 두 번 호출 → 두 번 다 목적 줄 없음, 상태 파일 없음; 본문을 채운
뒤 호출 → 바로 목적이 뜬다. 감독 세션도 코드에서 같은 것을 확인했다.

## Verification

판정: 기준 둘 다 PASS(전제가 죽어 이미 참), approved, 거절이 맞다는 판정. 소견 처분 —

- O-00000018 은 절반만 죽었다: "한 번만 뜬다"는 사라졌지만 "목적이 빈 카드는 보여 줄 게
  없다"는 실측으로 살아 있다 → **수용.** 관측을 산 절반만 남게 고쳐 쓴다.
- 인수 시험이 환경에 흔들린다: `CLAUDE_PROJECT_DIR` 가 설정돼 있으면 144개가 실패한다
  (`resolve_workspace_root` 가 페이로드 `cwd` 보다 그 변수를 먼저 본다) → **수용.** 새 관측
  O-00000033 으로 적는다.

## Retrospective

R-00000213 참조.

## Promotion decision

not_applicable — 결정 기록 없음, 승격 경로 없음. 카드 자체는 물림(2026-08-06, 감독 세션):
전제가 한 세대 전 코드를 말하고 있었다.

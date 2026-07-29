---
id: W-00000041
title: Plainly 전달 원칙 강화 — baseline 합성·정직성·온보딩 인터뷰
kind: development
venue: codex
source:
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000040
promotion: not_applicable
review: not_required
scope: plainly/
promotes:
decision_refs:
---

# W-00000041 Plainly 전달 원칙 강화 — baseline 합성·정직성·온보딩 인터뷰

## Purpose

4개 스타일 프로필을 공통 baseline + 얇은 델타 구조로 리팩터하고, baseline에 '확신의 정직한 표현'(추측을 사실로 말하지 않기, 미확인 표시) 원칙을 추가하며, plainly-configure에 예시 기반 온보딩 인터뷰(각 축을 쉬운 질문으로 물어 프리셋에 매핑하되, 조합 충돌 시에만 .plainly에 맞춤 스타일 파일을 쓰는 안전판)를 추가한다.

## Scope

- `plainly/styles/` — baseline 스타일 파일 신설, `plain/brief/guided/professional`을 델타만 남기도록 재작성, `profiles.json` 갱신
- `plainly/hooks/inject_style.py`, `plainly/src/plainly/runtime.py` — 주입 시 baseline + 선택 프로필 델타 합성
- `plainly/skills/plainly-configure/SKILL.md`, `plainly/scripts/configure.py` — 예시 기반 온보딩 인터뷰(축별 쉬운 질문 → 프리셋 매핑, 충돌 시 맞춤 파일)
- `plainly/tests/` — 합성·인터뷰 매핑·안전판 테스트
- `plainly/CHANGELOG.md`, `plainly/.claude-plugin/plugin.json`, `plainly/.codex-plugin/plugin.json` — 마이너 버전 bump + 변경 기록

## Success criteria

- baseline 파일 하나가 공통 원칙(결론 먼저·쉬운 말·간결·정직)을 SSOT로 소유하고, 4개 델타 파일에 그 문구가 중복되지 않는다
- 어떤 프로필을 골라도 주입 결과에 baseline 원칙이 포함된다(합성 검증 테스트 통과)
- baseline에 "추측을 사실로 말하지 않고 미확인은 미확인이라 표시" 원칙이 들어간다
- plainly-configure 인터뷰가 용어가 아닌 예시로 각 축을 묻고, 답을 프리셋에 매핑하며, 조합이 어떤 프리셋과도 안 맞을 때만 `.plainly/`에 맞춤 스타일 파일을 쓴다
- `python3 -m unittest discover -s plainly/tests -q` 통과, 8192바이트/보안 경계 계약 유지

## Related truth

- 세션 설계 논의(2026-07-18): plainly는 단일 프로필만 주입 → 공통 baseline 부재가 중복·구멍의 원인. `plain`은 baseline 자체, `brief`는 길이 눈금, `guided`/`professional`만 독립 축.
- venue: development → codex (정책 라우팅). 설계는 Claude 세션에서 완료, 구현은 Codex 인계.

## Progress

### 완료된 맥락 (설계 확정, 2026-07-18 Claude 세션)

- 현재 구조 확인: plainly는 매 턴 프로필 **하나만** 주입(README resolution order). 공통 baseline이 없어 `plain`의 "쉽게", `brief`의 "간략히" 같은 보편 원칙이 특정 프로필에만 갇힘 = 중복 + 구멍의 원인.
- 축 분해 결론: `plain`=공통 뼈대 자체, `brief`=길이 눈금, `guided`=단계별/비전문가(독립 축), `professional`=격식/사실·권고 구분(독립 축).
- 확정한 목표 구조: **baseline 1개 + 얇은 델타 3개**. baseline이 공통 원칙(결론 먼저·쉬운 말·간결·정직) SSOT를 소유하고, `brief/guided/professional`은 자기 델타만 보유. `plain`은 baseline으로 흡수.
- 정직성 보강은 별도 축이 아니라 **baseline에 흡수**: "추측을 사실로 말하지 않고, 미확인은 미확인이라 표시".
- 인터뷰 방식 확정: 용어로 묻지 않고 **예시 두 개를 나란히 보여주고 고르게**(축별 쉬운 질문 — 길이/구조/톤). 답을 프리셋에 매핑하되, **조합이 어떤 프리셋과도 안 맞을 때만** `.plainly/`에 맞춤 스타일 파일을 쓰는 안전판(A+안전판).

### 남은 문제 (구현 대상)

합성 로직(`inject_style.py`/`runtime.py`), 스타일 파일 재편, 인터뷰 흐름(`SKILL.md`/`configure.py`), 테스트, 버전 bump. 8192바이트/보안 sentinel 경계 계약은 유지해야 함.

### NEXT action

Codex 창(또는 브리지 위임)에서 위 목표 구조로 구현 → `python3 -m unittest discover -s plainly/tests -q` 통과 → 마이너 버전 bump(양쪽 plugin.json) + CHANGELOG. 완료 후 교차 검토는 Claude(다른 venue)가 수행.

## Verification


### Executed at close — 2026-07-18

```
$ python3 -m unittest discover -s plainly/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 37 tests in 0.870s

OK
```

## Retrospective


## Promotion decision


---
kind: mission
canvas: foundation
field_count: 4
status: draft   # draft → reviewing → done
---

# mission — 미션

> 그 프로젝트가 무엇을·왜 하는가의 최상위 선언. 정본:
> `viewer/src/domain/Mission.ts`. 공통 BaseFields 는 ../README 참조.

## 1. 고유 필드 — 무엇 + 설계 의도 + 진짜 필요한가

| 필드 | 무엇인가 | 설계 의도 | 진짜 필요/유용한가 |
|---|---|---|---|
| `what_we_do` | 미션 본체 한 문장 (행위+결과) | 미션을 한 줄로 못 박으려고 | ✅ **필수.** 이거 없으면 미션이 아님 |
| `why` | 미션의 인간적 동기/믿음 | "무엇"과 "왜"를 분리해 동기 명시 | ⚠️ **중복 위험.** what_we_do "~위해"에 동기 섞임 |
| `direction` | 작동 원리/지향 | 미션이 굴러가는 방향을 따로 잡으려고 | ❓ **약함.** 실제 값은 *상호성 원리* — 방향이 아니라 세계관 → body 행 |
| `body` | 자유 서술(markdown) | 사람이 읽는 산문 층 | ⚠️ direction 의 순환 개념을 또 반복 → 경계 모호 |

## 2. 핵심 질문

미션의 진짜 필드 셋은 `what_we_do` + `body` 2개로 충분하고
`why`·`direction` 은 body 안의 문단 아닌가?

## 3. 작업 정의

- [ ] `why` 유지 vs `what_we_do` 흡수
- [ ] `direction` 제거(→body) vs 유지 — 우선 결정
- [ ] 결론을 CONCEPTS.md mission 필드 정의에 반영

---
kind: core_value
canvas: foundation
field_count: 4
status: draft   # draft → reviewing → done
---

# core_value — 코어밸류

> 프로젝트가 지키는 핵심 가치(관용/지지/유머/공감/다양성 …). 정본:
> `viewer/src/domain/CoreValue.ts`. 공통 BaseFields 는 ../README 참조.

## 1. 고유 필드 — 무엇 + 설계 의도 + 진짜 필요한가

| 필드 | 무엇인가 | 설계 의도 | 진짜 필요/유용한가 |
|---|---|---|---|
| `definition` | 그 가치가 무엇인지 정의 한 문장 | 가치를 추상어로 안 두고 못 박으려고 | ✅ **필수.** 가치의 본체 |
| `do` | 이 가치에 부합하는 행동 | 추상 가치를 실천 행동으로 내리려고 | ⚠️ 가치마다 다 채워지나? 빈칸이면 노이즈 |
| `dont` | 위배하는 행동 | do 의 반대 경계 | ⚠️ do 와 한 쌍 — 한쪽만이면 비대칭 |
| `body` | 자유 서술 | 산문 보강 | ❓ definition+do+dont 가 이미 구조를 덮음 |

## 2. 핵심 질문

- `do`/`dont` 는 core_value·identity·service 3 kind 공유. 같은 의미인가?
  공통 value-object 로 뽑을 수 있나, 다르면 왜 다른가?
- 가치는 본질상 추상 — do/dont 충전율이 낮으면 필드 존재가 정당한가?

## 3. 작업 정의

- [ ] sim 5개 core_value 의 do/dont 충전율 확인
- [ ] do/dont 를 3 kind 공통으로 볼지 결정
- [ ] body 가 definition 과 겹치면 제거 검토

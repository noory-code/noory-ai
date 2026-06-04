---
kind: identity
canvas: foundation
field_count: 4
status: draft   # draft → reviewing → done
---

# identity — 아이덴티티

> 브랜드/제품 정체성 (보이스·톤·디자인 원칙·안티패턴 …). sim 에서 14개로
> 가장 많이 쓰임. 정본: `viewer/src/domain/Identity.ts`.

## 1. 고유 필드 — 무엇 + 설계 의도 + 진짜 필요한가

| 필드 | 무엇인가 | 설계 의도 | 진짜 필요/유용한가 |
|---|---|---|---|
| `description` | 이 정체성 항목이 무엇인지 서술 | 정체성을 한 단락으로 잡으려고 | ✅ **필수.** 본체 |
| `do` | 이 정체성에 맞는 것 | 실천 경계(+) | ⚠️ core_value 와 동일 필드 — 의미 같나? |
| `dont` | 위배되는 것 (안티패턴) | 실천 경계(−) | ⚠️ "안티패턴" id 노드와 dont 개념 중복 |
| `body` | 자유 서술 | 산문 보강 | ❓ description 과 겹침 |

## 2. 핵심 질문

- **identity 와 core_value 의 필드 셋이 사실상 같다**
  (`definition`↔`description` + do + dont + body). 데이터 형식만으론 두
  kind 가 구분 안 됨 — 합칠지, 형식으로 구분점을 둘지.
- sim 14개 identity 가 성격 제각각(용어체계·보이스·컬러·감정여정·안티패턴…).
  하나의 kind 가 이렇게 이질적인 걸 다 담는 게 맞나? (sub-kind / theme 필요성)

## 3. 작업 정의

- [ ] identity vs core_value 형식 차이 만들지 / 합칠지
- [ ] 14개 identity 이질성 — 분류 축(theme) 필요한지
- [ ] "안티패턴" 항목과 dont 필드 중복 정리

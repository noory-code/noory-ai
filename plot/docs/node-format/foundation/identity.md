---
kind: identity
canvas: foundation
field_count_before: 4   # description, do, dont, body
field_count_after: TBD  # 비판으로 재오픈 — body 이중산문/14 flat/catch-all 미해결
status: reviewing   # draft → reviewing → done
---

# identity — 아이덴티티

> 브랜드/제품의 구별되는 성격을 구체적으로 표현 (보이스·비주얼·용어·감정·
> 안티패턴). sim 14개. 정본: `viewer/src/domain/Identity.ts`.

## 상태 — "그대로 둔다"는 비판으로 기각, 재오픈 (2026-06-05)

처음 "identity 는 분해 오류 없으니 그대로 두자"로 기울었으나, 비판(§자기
비판)으로 **기각.** identity 는 깨끗하지 않다 — 미해결 3개:

```
identity (현재)                         미해결
├── label                               
├── description  14/14  ← 유지           ① body 와 이중-산문 중복
├── do          0/14   ← do/dont 배치 컷  (description+body 둘 다 prose,
├── dont        0/14                       body 가 죽음 → body 컷 후보)
└── body        0/14                     ② 14개 flat 노드 = "노드 가방"
                                            (identity=시스템인데 분류/관계 0
                                             → facet 이 YAGNI 아닌 진짜 갭?)
                                         ③ catch-all: 안티패턴(부정공간)·
                                            감정여정(시간)은 identity 면이 아님
```

**확정된 것:** do/dont 컷(배치), description 은 핵심 prose 로 유지.
**열린 것:** ①body 컷 ②facet 구조 ③catch-all 재분류 — 아래 §결정 대기.

## 근거

### 아이덴티티는 본디 다면적 (이론)
- **Aaker, *Building Strong Brands*** (1996): 브랜드 아이덴티티 =
  product / organization / person / symbol 4관점 시스템.
- **Kapferer, Identity Prism** (1986): 6면(physique·personality·culture·
  relationship·reflection·self-image).
- ⇒ BANAS 14개는 *원래 다면적*이라 많은 게 아닐 수 있다. **그러나** 이론이
  다면적이라는 게 *flat·무관계 14노드* 를 정당화하진 않는다 (§자기비판 2).

### 데이터 (14개)
| 필드 | 충전율 |
|---|---|
| `description` | **14/14** |
| `do` | 0/14 |
| `dont` | 0/14 |
| `body` | 0/14 |

노드당 `description` 하나만 사용. 14개 모두 한 문단(78~147자)으로 **구조
균일** → sub-kind 불필요.

## 자기비판 (self red-team) — "그대로 두자"를 깬다

처음 "분해 오류 없으니 그대로"로 기울었다. 비판으로 기각한다:

1. **이중-산문 중복.** `description`(14/14) + `body`(0/14) = prose 필드 둘,
   하나 죽음 = core_value 의 definition+body 와 *같은 병*. "분해 오류 없다"는
   틀렸다. → **body 컷** 후보 (단일 prose).
2. **14 flat = "노드 가방" (appeal-to-authority 재범).** "Aaker 가 다면적이라
   했으니 14개 OK"는 미션에서 내가 깐 권위논증의 재범. 아이덴티티가
   *시스템*(Aaker)이면 **분류·관계 0 인 낱개 14노드는 그 시스템을 잃는다.**
   → facet 은 YAGNI 가 아니라 *빠진 구조* 일 수 있음. 재검토 필요.
3. **catch-all (MECE 위반).** `안티패턴`=부정 공간(우리가 *아닌* 것),
   `감정 여정`=시간 흐름 — 둘 다 "표현(보이스/컬러/용어)"과 결이 다르다.
   "브랜드스럽다"고 한 kind 에 욱여넣은 분류 실패.
4. **"마이그레이션 비용 아끼자"는 설계 논거가 아니다.** YAGNI 로 위장한
   게으름. 감사의 일은 *맞는 모델* 찾기지 *안 바꾸는 게 싼* 것 고르기가 아님.

n=14 한 작성자 caveat 는 여전하나, ①의 body 중복은 작성자 무관 구조 문제.

## 파운데이션 3종 수렴 (mission·core_value·identity 완료)
| kind | = label + | 단일 prose 필드명 |
|---|---|---|
| mission | 선언 | (body) |
| core_value | 원칙 | definition |
| identity | 표현 | description |

→ 파운데이션 개념 = **label + 단일 prose 필드** (do/dont 전멸). 남은
cross-cutting: 이 prose 필드명을 통일(body?)할지 vs 의미명 유지. (별도 결정.)

## 작업 정의 (재오픈 — 3개 열린 결정)
- [ ] **①body 컷** — description+body 이중산문 → 단일 prose 로 (do/dont 와 함께).
- [ ] **②facet 구조** — 14 flat 노드에 facet 분류/관계를 줄지 (시스템 보존 vs
      YAGNI). deliverable 의 facet 묶음 수요와 함께 결정.
- [ ] **③catch-all 재분류** — 안티패턴(부정공간)·감정여정(시간)을 identity 에
      둘지, 다른 kind/표현으로 뺄지.
- [ ] (확정) do/dont 컷, description 유지.

## 검토 히스토리

> 검토는 반복된다. 매 검토마다 시각 + 바뀐 것을 changelog 로 남긴다.

| 검토 | 시각 (KST) | 결과 / 바뀐 것 |
|---|---|---|
| 생성 | 2026-06-04 23:19 | draft 생성 (필드 4: description/do/dont/body). |
| 1차 | 2026-06-05 03:24 | 검토 — description 14/14, do/dont/body 0/14. label+description 잠정. |
| 2차 | 2026-06-05 03:40 | "그대로 둔다"로 잠정 done 처리. |
| 3차 | 2026-06-05 03:46 | **비판으로 기각·재오픈.** 깨끗하지 않음 — ①body 이중산문 ②14 flat=노드가방(facet 갭) ③catch-all(안티패턴/감정여정). 확정: do/dont 컷·description 유지. status done → reviewing. |

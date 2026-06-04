---
kind: mission
canvas: foundation
field_count_before: 4   # what_we_do, why, direction, body
field_count_after: 1    # body only (+ label carries the statement)
status: done   # draft → reviewing → done
decided: 2026-06-04
---

# mission — 미션

> 그 프로젝트가 무엇을·왜 하는가의 최상위 선언. 정본:
> `viewer/src/domain/Mission.ts`. 공통 BaseFields 는 ../README 참조.

## 결정 (사용자 확정 2026-06-04)

**미션은 쪼개지지 않는 하나의 선언이다. 타입 콘텐츠 필드를 모두 폐기한다.**

```
mission
├── label   ← "미션 한 줄"(선언). 캔버스에서 노드만 봐도 미션이 보이게 승격.
└── body    ← 스토리 · 핵심 통찰 등 (작성자가 정하는 자유 markdown 섹션)

✗ what_we_do   ✗ why   ✗ direction        ← 폐기
```

- 타입 콘텐츠 필드 = **0개.** 미션 = `label`(선언) + `body`(자유 산문).
- 발견된 관계: **mission body ⟷ core_value 참조** — 미션은 가치들의 언어로
  서술된다 (Q6 "체현"과 연결).

## 근거

1. **경영학 프레임워크는 *질문* 만 준다 (필드 스키마 ✗).** Sinek Golden
   Circle(Why/How/What), Drucker("what is our business"), Collins & Porras
   (Core Purpose+Values), Ashridge(Purpose/Strategy/Values/Behaviour) —
   서로 분해가 다르고 수렴하지 않는다. 하나를 골라 필드를 정당화하면
   cherry-picking. 이들은 "미션이 무엇을 답해야 하나"를 밝혀줄 뿐.
2. **why/what/direction 은 한 선언을 각도만 달리 자른 조각.** 그래서 서로
   메아리치고(부분 중복) 어느 하나도 깔끔히 못 자른다. "어느 필드를 컷하나"가
   잘못된 질문 — 옳은 답은 분해 자체를 걷어내기.
3. **실제 BANAS body 가 옳은 형식을 이미 증명.** body 가 작성자가 고른 산문
   섹션(`## 미션 한 줄` / `## 스토리` / `## 핵심 통찰`)으로 구성됨 = 타입
   필드가 아니라 사람이 정한 markdown. 스토리는 core_value(관용·지지·유머·
   공감)를 어휘로 미션을 서술 → 미션은 자기 가치 필드가 불필요.
4. `핵심 통찰`("한 사람이 분야에 따라 히어로이자 팬")은 BANAS 차별적 thesis.
   누가/왜 넣었는지는 확인 불가(추측 안 함)지만 Plot 본질(본질을 *모르는*
   사람이 *찾는다*)에선 가장 가치 있는 부분일 수 있어 body 섹션으로 유지.

## ⚠️ 횡단 함의

이 오류는 미션 고유가 아니라 **"kind = 타입 필드 가방" 패턴 자체**의 문제일
수 있다. 같은 평행 구조가 같은 혐의를 받는다 — `core_value`(definition/do/
dont/body), `identity`(description/do/dont/body), `service`(10필드, 최악).
나머지 감사는 "필드를 정당화"가 아니라 **"이 분해가 애초에 맞나"** 렌즈로.

## 작업 정의

- [ ] domain/Mission.ts + 서버 Pydantic: what_we_do/why/direction 제거,
      body 만 (+ label). schema_parity 갱신.
- [ ] 인스펙터/렌더러: 3필드 입력 폐기, label=선언 편집 + body 편집만.
- [ ] 마이그레이션: 기존 what_we_do/why/direction 값을 label(한 줄)+body 로 병합.
- [ ] CONCEPTS.md mission 정의 갱신.
- [ ] 다른 kind 재감사 (core_value·identity·service 우선).

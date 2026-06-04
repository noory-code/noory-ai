---
kind: mission
canvas: foundation
field_count: 4
status: reviewing   # draft → reviewing → done
---

# mission — 미션

> 그 프로젝트가 무엇을·왜 하는가의 최상위 선언. 정본:
> `viewer/src/domain/Mission.ts`. 공통 BaseFields 는 ../README 참조.

## 1. 경영학 프레임워크 매핑 (감사 근거)

미션은 전략경영에 확립된 분해틀이 있다 — 추측 대신 이걸로 판정한다.

- **Sinek, Golden Circle** (*Start With Why*, 2009): **Why → How → What**.
- **Drucker** (*The Practice of Management*, 1954): "What is our business?"
  = 목적·고객·고객가치.
- **Collins & Porras** (*Built to Last*, 1994): Core Ideology =
  Core **Purpose** + Core **Values** (+ BHAG = vision, *시간 기반*).
- **Campbell & Yeung, Ashridge Mission Model** (1991): Mission =
  **Purpose + Strategy + Values + Behaviour Standards**.

Plot 분해: Purpose→mission, Strategy→**없음**(시간 기반, 공간 Plot 배제),
Values→`core_value` 노드, Behaviour→`core_value.do/dont`. ⇒ 미션 노드가
정당하게 담을 것은 **Purpose + (사업정의)What** 뿐.

## 2. 고유 필드 — 무엇 + 의도 + 진짜 필요한가 (경영학 판정)

| 필드 | 경영학 매핑 | 무엇인가 | 진짜 필요/유용한가 |
|---|---|---|---|
| `why` | Sinek **Why** / Collins **Core Purpose** / Ashridge **Purpose** | 미션의 인간적 목적/믿음 | ✅ **상향 — 미션의 심장.** (1차 "중복 위험" 판정 철회: 이론상 Purpose 가 가장 본질) |
| `what_we_do` | Sinek **What** / Drucker 사업 정의 | 본체 한 문장(행위+결과) | ✅ **필수** |
| `direction` | Ashridge **Strategy** / 미래=**Vision** | "작동 원리/지향" | ❌ **제거 1순위.** Strategy·Vision 은 *시간 기반* → Plot 공간 기반 배제([[feedback_plot_space_vs_time]]); 실제 값(히어로↔팬 순환)은 Core **Values** → 이미 `core_value` 노드가 책임 → 중복 |
| `body` | — | 산문 서술 | ⚠️ Purpose+What 외 narrative. 유지하되 direction 흡수 금지 |

## 3. 핵심 질문

경영학 정답에 가까운 미션 필드 셋은 **`why`(Purpose) + `what_we_do`(What)**
+ 선택적 `body`. `direction` 은 (a)Vision=시간기반 배제, (b)Values=core_value
중복 — 둘 중 무엇으로 봐도 미션 노드에 남을 자리가 없다.

## 4. §2 분석에 대한 비판 (self red-team)

§1~2 의 경영학 매핑을 비판적으로 검증한다. **끌어온 방식 자체의 허점:**

1. **시간기반 논리 오용 (철회).** §2 는 `direction` 을 "Vision=시간기반 →
   Plot 공간기반 배제"로 컷했다. 그러나 실제 값(히어로↔팬 순환)은 미래
   포부가 아니라 **현재형 작동 원리** — Vision 이 아니다. "시간기반→컷"은
   오분류를 갖다 붙인 것. **이 논거는 철회.** direction 의심의 유일한
   근거는 *core_value 중복* 으로 좁아진다.
2. **프레임워크 비수렴.** Sinek(3) / Ashridge(4) / Drucker(질문형) 는
   서로 다른 분해를 준다. "Purpose+What"만 고른 건 cherry-picking —
   권위로 결론을 포장한 셈. 프레임워크는 *질문* 을 줄 뿐 *필드 스키마* 를
   확정해주지 않는다.
3. **`why` 격상의 근거 약함.** "Sinek 이 Why 가 심장이라 했으니"는
   appeal-to-authority. 이 데이터에선 `what_we_do` 의 "누구나를 *위해*"에
   why 가 이미 섞임(1차 판정이 옳았음). 이론이 아니라 **충전율**(11개
   미션류 노드가 why/what 을 실제로 따로 쓰나)로 판정해야 한다.
4. **노비스 도구에 과한 분해.** Plot 본질 = "본질을 *모르는* 사람"을 돕기
   (VISION). Purpose/Strategy/Values 구분은 전략경영 전공 어휘다. 학문은
   *판단 근거* 로 쓰되, 사용자가 모르는 분류를 필드로 강요하면 본질에
   역행. 이론정합 4필드 < 노비스가 채울 2~3필드일 수 있다.

**비판 후 robust 결론:** 프레임워크를 다 걷어내도 남는 건
**`direction` ⊃ core_value 중복** 하나뿐. `why`/`what` 분리·격상은
데이터(충전율)로 검증 전엔 *약한* 주장.

## 5. 결론 (사용자 확정, 2026-06-04)

**미션을 `what_we_do` / `why` / `direction` 3개 타입 필드로 쪼갠 것 자체가
잘못이다.** 미션은 *쪼개지지 않는 하나의 선언* 이다. 한 미션을 각도만
달리 자른 조각들을 별개 필드로 둔 탓에 → 서로 메아리치고(중복), 어느
하나도 깔끔히 못 자르는 교착이 생겼다. "어느 필드를 컷하나"는 잘못된
질문이었고, 옳은 답은 **필드 분해를 걷어내는 것.**

- **미션의 데이터 형식 = 단일 선언(statement) + 선택적 `body`(부연 산문).**
  what_we_do / why / direction 의 3분할 폐기.
- why·direction 의 내용(목적·작동원리)은 별도 필드가 아니라 그 한 선언과
  body 안에서 자연스럽게 표현된다.

### ⚠️ 횡단 함의 (다른 kind 로 번짐)

이 오류는 미션 고유가 아니라 **"kind = 타입 필드 가방" 설계 패턴 자체**의
문제일 가능성이 크다. 같은 평행 구조를 가진 kind 들이 같은 의심을 받는다:
- `core_value` (definition/do/dont/body), `identity` (description/do/dont/body)
  — 하나의 가치/정체성을 4조각.
- `service` (10필드) — 가장 심한 과분해 후보.
→ 나머지 kind 감사를 "필드를 정당화" 가 아니라 **"이 분해가 애초에
맞나"** 의 렌즈로 진행한다.

## 6. 작업 정의

- [ ] 미션 데이터 모델: 3필드 → 단일 선언 + 선택 body 로 (CONCEPTS.md +
      domain/Mission.ts + 서버 Pydantic + 인스펙터/렌더러)
- [ ] 마이그레이션: 기존 what_we_do/why/direction 값을 단일 선언+body 로 병합
- [ ] **다른 kind 도 "과분해" 렌즈로 재감사** (core_value·identity·service 우선)

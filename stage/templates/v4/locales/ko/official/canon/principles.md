# 원칙

이 문서는 이 프로젝트의 안정적 원칙의 인덱스와 핵심 요약을 소유한다.

각 원칙의 상세 SSOT는 `principles/`에 있다. 원칙은 체크리스트가 아니다 — 모든 결정 지점(`operations/during.md`), 모든 결정 레코드(`decisions/pending/`), 모든 회고에서 결정과 행동을 통제하는 기준이다.

Thinking, Behavior, Completion 섹션은 하니스 코어다 — Stage 플러그인이 고정하고 감사가 검증하며, 이를 제거하면 하니스 자체의 전제가 깨진다. Design과 Methodology 섹션 및 참조되는 규칙 소유자는 프로젝트가 조정할 수 있으며, 프로젝트는 자신의 원칙을 `principles/`에 개별 레코드로 추가한다.

## 사고 원칙

모든 분석, 계획, 구현, 문서, 답변에 적용된다.

| Principle | 통제 대상 |
|---|---|
| SSOT (Single Source of Truth) | 소유권 결정 — 모든 지속적 사실, 상태, 책임, 기준은 정확히 하나의 소유 위치를 가진다. |
| MECE (Mutually Exclusive, Collectively Exhaustive) | 커버리지 결정 — 작업 분해, 케이스 분류, 실패 처리, 테스트 범위, 완료 조건. |
| Fail Fast | 조기 노출 결정 — 잘못된 전제와 불완전한 상태는 절대 조용히 통과하지 않는다. |
| AHA (Avoid Hasty Abstractions) | 추상화 시점 — 반복이 보이기 전에는 새로운 추상화, 규칙, 범주, 절차를 만들지 않는다. |

## 설계 원칙

구조, 책임, 추상화, 경계를 결정할 때 적용된다.

| Principle | 통제 대상 |
|---|---|
| DRY (Don't Repeat Yourself) | 중복 점검 — 반복되는 기준과 흐름은 통합 후보이며, AHA와 견주어 판단한다. |
| KISS (Keep It Simple, Stupid) | 단순성 점검 — 과도한 분리와 절차는 위반으로 취급된다. |
| SoC (Separation of Concerns) | 문서, 코드, 절차 사이의 책임 경계. |
| SRP (Single Responsibility Principle) | 하나의 모듈, 문서, 절차는 하나의 책임을 소유한다. |
| LoD (Law of Demeter) | 결합도 점검 — 알 필요 없는 내부에 의존하지 않는다. |
| OCP (Open-Closed Principle) | 확장 점검 — 기존 동작을 깨지 않고 케이스를 추가한다. |
| LSP (Liskov Substitution Principle) | 계약 점검 — 대체물은 기존 계약을 깨서는 안 된다. |
| ISP (Interface Segregation Principle) | 표면 점검 — 비대한 인터페이스나 사용되지 않는 의존성을 두지 않는다. |
| DIP (Dependency Inversion Principle) | 의존 방향 — 상위 정책은 절대 하위 세부를 따르지 않는다. |
| Postel's Law | 관용 균형 — 입력을 얼마나 관대하게 받고 출력을 얼마나 엄격하게 낼지, Fail Fast의 한계 안에서 정한다. |
| Clean Architecture | 도메인 로직과 외부 세부 사이의 경계. |
| DDD (Domain-Driven Design) | 도메인 용어, 경계, 모델 정합. |

도메인 경계와 SSOT는 처음부터 엄격하다. 잘못된 추상화는 중복보다 비용이 크다. 과도한 분리는 KISS 위반이다.

## 방법론 원칙

코드, 문서, 설계, 계획 등 모든 종류의 작업을 검증할 때 적용된다.

| Principle | 통제 대상 |
|---|---|
| TDD (Red → Green → Refactor) | 실행 가능한 테스트가 존재하는 곳에서는 검증이 구현에 선행한다. |
| BDD (Given / When / Then) | 기대 결과는 사용자의 행동 관점에서 표현된다. |
| Test pyramid | 검증 비용과 배치 결정. |
| F.I.R.S.T | 검증 품질 — 빠르고, 독립적이고, 반복 가능하고, 자체 판정되고, 시의적절하게. |

## Behavior principles

작업 자체를 수행하는 방식에 적용된다.

| Principle | 통제 대상 |
|---|---|
| Honesty | 검증되지 않은 사실을 단언하지 않는다. 모르는 것은 모른다고 밝힌다. 경로, 명령어, 스펙, 버전은 말하기 전에 검증한다. |
| No temporary passes | 통과를 가장하는 우회는 절대 통과가 아니다. |
| No partial completion | 부분적으로 된 것은 된 것이 아니다. |
| No silent substitution | 요청을 절대 다른 것으로 조용히 대체하지 않는다. |
| Plan execution | 확정된 계획은 완수한다. 이탈은 물리적 불가능일 때만 허용되며, 사용자에게 알린다. |
| Question protocol | 질문하기 전에 상위 목적에서 답을 도출한다. 사용자만 결정할 수 있는 것만 질문한다. |

## Completion principle

작업은 외부 관점 완료, 내부 관점 완료, 회고가 모두 충족될 때에만 완료된다.

## 참조 규칙 소유자

- 출력 규칙: `operations/output.md`
- 문서화 규칙: `operations/documentation.md`
- 검증 규칙: `operations/verification.md`
- UX 원칙(사용자 대면 작업): 사용자 중심성, don't make me think, 일관성, 명확한 피드백, 시각적 위계, 접근성 — 프로젝트가 사용자 대면 작업을 할 때 상세 레코드는 `principles/`에 둔다.


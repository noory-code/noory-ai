# Stage 인덱스

이 문서는 프로젝트 컨텍스트를 올바른 Stage 위치로 라우팅한다.

## 수명주기

- `planned`: `work/planned/`, `proposals/`, 그리고 추구 결정이 없는 로드맵 레코드에 있는 계획된 작업.
- `current`: `work/current/`, `decisions/pending/`, `state/`, 그리고 열린 추구 결정이 있는 로드맵 레코드에서 실현 중인 작업.
- `official`: `official/` 아래로 승격되어 확정된 진실.

## 권위

- `official/`: 공식 산출물과 승인된 진실을 위한 유일한 권한 영역.
- `work/`, `decisions/`, `state/`, `proposals/`, `roadmap/`: 변경 가능한 책임 패밀리.
- `operations/`: 프로젝트 소유의 Stage 정책. 공통 행동 규칙은 플러그인 소유이며, 설치된
  Stage 플러그인의 `operations/` 디렉터리에 있다.

## 라우팅 규칙

| 정보 | 위치 |
|---|---|
| 원칙 인덱스와 요약 | `official/canon/principles.md` |
| 개별 원칙 | `official/canon/principles/` |
| 용어 인덱스와 요약 | `official/canon/vocabulary.md` |
| 개별 용어 | `official/canon/vocabulary/` |
| 불변 조건 인덱스와 요약 | `official/canon/invariants.md` |
| 개별 불변 조건 | `official/canon/invariants/` |
| 시스템 구조 | `official/model/` |
| 모델 컴포넌트 | `official/model/components/` |
| 모델 경계 | `official/model/boundaries/` |
| 모델 인터페이스 | `official/model/interfaces/` |
| 공식 결정 | `official/decisions/index.md` |
| 공식 결정 레코드 | `official/decisions/records/` |
| 보관된 결정 | `official/decisions/archive/` |
| 보관된 제안 | `official/proposals/archive/` |
| 보관된 상태 레코드 | `official/state/archive/` |
| 아카이브된 작업 인덱스 | `official/work/archive/index.md` |
| 아카이브된 작업 항목 | `official/work/archive/items/` |
| 아카이브된 회고 | `official/work/archive/retrospectives/` |
| 진행 중 작업 | `work/active.md` |
| 현재 작업 카드 | `work/current/` |
| 리뷰 후보 | `work/review.md` |
| 작업 회고 | `work/retrospectives/` |
| 계획된 작업 인덱스 | `work/planned/index.md` |
| 계획된 작업 카드 | `work/planned/` |
| 작업 뷰 | `work/views/` |
| 대기 중 결정 인덱스 | `decisions/index.md` |
| 대기 중 결정 레코드 | `decisions/pending/` |
| 현재 관측 | `state/current.md` |
| 관측 레코드 | `state/observations/` |
| 미해결 질문 | `state/questions.md` |
| 질문 레코드 | `state/questions/` |
| 가정 | `state/assumptions.md` |
| 가정 레코드 | `state/assumptions/` |
| 리스크 | `state/risks.md` |
| 리스크 레코드 | `state/risks/` |
| 제안 인덱스 | `proposals/index.md` |
| 제안 본문 | `proposals/` |
| 로드맵 인덱스 | `roadmap/index.md` |
| 로드맵 마일스톤 | `roadmap/milestones/` |
| 로드맵 테마 | `roadmap/themes/` |
| 작업 종류별 검증 기준 | `operations/verification.md` |
| 발견 처리 규칙 | `operations/discovery.md` |
| 공통 운영 규칙 | 설치된 Stage 플러그인의 플러그인 소유 `operations/` |

## 핵심 규칙

계획된 산출물은 진실이 아니다. 현재 산출물은 진실이 아니다. 공식 산출물만이 진실이다.


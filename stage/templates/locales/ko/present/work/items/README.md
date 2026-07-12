# 작업 항목

이 디렉터리는 진행 중인 작업 항목의 SSOT를 소유한다.

작업 항목은 기획, 설계, 개발, QA, 운영 등 프로젝트가 수행하는 모든 종류의 작업을 다룬다. 작업 항목은 코드 변경이 아니라 책임 있는 작업의 단위다.

## 규칙

- 작업 항목 하나는 파일 하나를 가진다.
- `active.md`와 `review.md`는 현재 뷰이며 본문을 절대 중복하지 않는다.
- 작업이 완료 후보가 되면 그 검증, 회고, 승격 결정을 링크한다.
- 훅은 각 작업 파일의 frontmatter를 상태 SSOT로 사용한다.
- 작업이 더 이상 현재 흐름에 속하지 않으면 `status: archived`로 설정하고 `past/work/archive/items/`로 이동한다.

## 상태 필드

작업 상태 열거형의 문서 SSOT는 `operations/artifacts.md`이다.

- `kind`: 이 작업이 어떤 종류인지(예: `planning`, `design`, `development`, `qa`, `ops`). 프로젝트는 `past/canon/vocabulary.md`에 자신의 분류 체계를 정의한다.
- `venue`: 선택 사항. 어떤 실행 표면이 이 작업 항목을 수행해야 하는지 — 둘 이상의 에이전트나 세션이 프로젝트를 작업할 때 사람이 올바른 창을 열기 위해 읽는 라우팅 힌트다. 값은 프로젝트가 정의하며, 프로젝트는 venue와 `kind -> venue` 라우팅을 `past/canon/vocabulary.md`에 선언한다. 참고용일 뿐이다. 훅은 절대 `venue`로 게이트하지 않는다. 빈 값은 미지정을 뜻한다.
- `parent`: 선택 사항. 상위 작업 항목의 ID. 계층은 큰 작업을 분류 가능하게 유지한다 — 하위 항목이 열려 있는 동안 상위 항목은 완료가 아니다.
- `scope`: 이 작업이 소유하는 경로. 여러 항목은 쉼표로 구분한다. 빈 값은 어떤 경로도 소유하지 않는다. `*`는 진짜 전역 범위일 때만 선언한다.
- `promotes`: 이 작업이 승격할 수 있는 `.stage/past/` 경로. 여러 항목은 쉼표로 구분한다.
- `retrospective_ref`: `retrospective: completed`일 때 링크되는 회고 파일 ID 또는 경로.
- `decision_refs`: 선택 사항. `present/work/decisions/`의 결정 레코드 ID 또는 경로.
- `source`: 선택 사항. 이 작업이 실현하는 백로그 항목 ID. 그 백로그 항목의 `realized_by`가 이곳을 되돌아 가리킨다.

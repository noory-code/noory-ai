# 작업 항목

이 디렉터리는 진행 중인 작업 계층의 SSOT를 소유한다.

에픽 폴더는 `_epic.md`와 스토리 폴더를 가진다. 스토리 폴더는 `_story.md`와 액션 카드를
가진다. 독립 스토리는 최상위에 설 수 있지만 액션은 그럴 수 없다.

## 규칙

- 폴더 위치가 유일한 계층 사실이며 작업 frontmatter에는 `parent` 필드가 없다.
- 최상위 에픽 또는 독립 스토리 하나가 수명주기 위치 사이를 통째로 이동한다.
- `work/active.md`와 `work/review.md`는 현재 뷰이며 본문을 절대 중복하지 않는다.
- 작업이 완료 후보가 되면 그 검증, 회고, 승격 결정을 링크한다.
- 훅은 각 작업 파일의 frontmatter를 상태 SSOT로 사용한다.
- 작업이 더 이상 현재 흐름에 속하지 않으면 `status: archived`로 설정하고 `official/work/archive/items/`로 이동한다.

## 상태 필드

작업 상태 열거형의 문서 SSOT는 `operations/artifacts.md`이다.

- `kind`: 이 작업이 어떤 종류인지(예: `planning`, `design`, `development`, `qa`, `ops`). 프로젝트는 `official/canon/vocabulary.md`에 자신의 분류 체계를 정의한다.
- `venue`: 선택 사항. 어떤 실행 표면이 이 작업 항목을 수행해야 하는지 — 둘 이상의 에이전트나 세션이 프로젝트를 작업할 때 사람이 올바른 창을 열기 위해 읽는 라우팅 신호다. 값은 프로젝트가 정의한다: 기계가 읽는 `kind -> venue` 라우팅은 `settings.json`의 `venue_routing`에 있고(등록이 거기서 venue를 도출하고 감사가 일관성을 검사하며, 예외는 `authorizes: venue_exception`을 선언한 결정 레코드가 필요하다), `official/canon/vocabulary.md`는 각 venue의 의미만 소유한다. 훅은 `venue`로 게이트하지 않는다. 라우팅이 선언되지 않은 프로젝트에서는 항목별 참고 필드일 뿐이다. 빈 값은 미지정을 뜻한다.
- `scope`: 이 작업이 소유하는 경로. 여러 항목은 쉼표로 구분한다. 빈 값은 어떤 경로도 소유하지 않는다. `*`는 진짜 전역 범위일 때만 선언한다.
- `promotes`: 이 작업이 승격할 수 있는 `.stage/official/` 경로. 여러 항목은 쉼표로 구분한다.
- `retrospective_ref`: `retrospective: completed`일 때 링크되는 회고 파일 ID 또는 경로.
- `decision_refs`: 이 작업 항목이 확정한 결정 레코드 — 그 항목이 `decided`로 만든 것들. 선택 사항이며 확정하기 전까지는 비어 있다. 이 항목이 따르는 결정의 목록이 아니다. 다른 항목이 확정한 결정을 실행하는 항목은 그 레코드를 본문에서 링크한다. 참조된 레코드는 자기 `work_item`에서 이 항목을 되가리켜야 하고, 그 일대일 연결이 venue 예외가 어느 항목 하나를 허가했는지 특정하는 근거다.
- `source`: 선택 사항. 역사적인 원본 참조.

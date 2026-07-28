# 계획된 작업 카드

이 디렉터리는 아직 시작하지 않은 계획 작업 계층의 SSOT를 소유한다.

최상위 항목은 에픽 폴더 또는 독립 스토리 폴더다. 여기에서 캡처되고, 시작할 때 폴더 하나로
`work/current/`에 이동하며, 종결되면 `official/work/archive/items/`에 안착한다. 폴더 위치가
계층의 SSOT다.

## 규칙

- 에픽 폴더는 `_epic.md`와 스토리 폴더를 가진다. 스토리 폴더는 `_story.md`와 액션 카드를
  가진다. 액션은 이 디렉터리에 바로 놓일 수 없다.
- 카드 id는 현재 작업과 같은 `W-*` 카운터에서 할당된다. 하나의 id가 두 수명주기 위치에
  동시에 존재하지 않는다.
- `index.md`는 카드 본문을 복제하지 않는다. 순서, 상태, 링크만 담는다.
- 디렉터리 경로가 유일한 계층 사실이며 작업 frontmatter에는 `parent` 필드가 없다.
- 계획 상태: `captured`, `triaged`, `ready`, `selected`, `deferred`, `rejected`. 작업 시작은
  여기서의 상태 수정이 아니라 최상위 폴더의 이동이다.
- 에픽, 스토리, 액션은 각각 `_epic.md`, `_story.md`, `_template.md`를 복사해 만든다.
- 하지 않기로 한 이유(`rejected`)는 카드에 기록하고, 필요하면 `official/decisions/`에도 기록한다.

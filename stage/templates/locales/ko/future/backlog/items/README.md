# 계획된 작업 카드

이 디렉터리는 계획된 작업 카드 — 아직 시작하지 않은 `W-*` 작업 항목 — 의 SSOT를 소유한다.

작업 카드는 전 생애에 걸쳐 하나의 산출물이다: 여기에서 캡처되고, 작업이 시작되면
`present/work/items/`로 물리적으로 이동하며(`scripts/start_work.py`), 종결되면
`past/work/archive/items/`에 안착한다 — 보드 위를 이동하는 카드처럼. 계획된 카드는 기획,
설계, 개발, QA, 운영 등 프로젝트가 하는 모든 종류의 작업을 다룬다.

## 규칙

- 계획된 카드 하나는 파일 하나를 가지며, 이름은 `W-00000001.md`다(`-short-title` 접미사는
  선택 사항).
- 카드 id는 현재 작업과 같은 `W-*` 카운터에서 할당된다. 하나의 id가 두 수명주기 위치에
  동시에 존재하지 않는다.
- `index.md`는 카드 본문을 복제하지 않는다. 순서, 상태, 링크만 담는다.
- 카드는 frontmatter `parent` 필드로 계층을 이루며, parent는 계획된 카드 또는 이미 시작된
  카드를 가리킬 수 있다.
- 계획 상태: `captured`, `triaged`, `ready`, `selected`, `deferred`, `rejected`. 작업 시작은
  여기서의 상태 수정이 아니라 이동이다: `python3 stage/scripts/start_work.py --project-root .
  W-00000001 --scope "..."`가 카드를 `present/work/items/`로 옮기고 `active`로 설정하며,
  scope 선언을 요구하고, 그 시점에 venue/split 계약을 강제한다.
- 새 카드는 `register_work.py --backlog --title "..." --kind <kind> --scope ""`로 캡처하거나
  `_template.md`를 복사해 만든다.
- 하지 않기로 한 이유(`rejected`)는 카드에 기록하고, 필요하면 `past/decisions/`에도 기록한다.

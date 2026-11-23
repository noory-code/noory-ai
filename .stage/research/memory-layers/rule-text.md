# 덜어낸 규칙 문장과 그 내용이 이미 있는 자리

2026-11-23, W-00000417 의 작업 세션(클라우드)이 커밋 2401aeb 의 저장소에서 쟀습니다.
훅은 클라우드에서 돌지 않으므로 `stage/hooks/stage_context.py` 의 `session_context()` 를 직접 불러 글을 얻었습니다.
글자 수는 파이썬의 `len()` 값입니다. 여기서 "규칙 문장"은 `## Stage context` 조각, 곧 첫 `###` 제목 앞까지의 글입니다.

## 크기

| | 고치기 전 | 고친 뒤 | 차이 |
|---|---|---|---|
| 규칙 문장 전체 | 3,373자 (15줄) | 1,384자 (6줄) | 1,989자 줄어듦 |

| 조건 (이 저장소의 기록, 결정 82건, 규칙 후보 39건) | 고치기 전 | 고친 뒤 |
|---|---|---|
| 진행 중 카드 네 장(지금 상태) | 결정 제목 76건, 후보 0건 | 결정 제목 82건, 후보 14건 |
| 진행 중 카드 다섯 장 | 재지 않음. W-00000413 은 63건으로 적음 | 결정 제목 82건, 후보 13건 |

다섯 장의 수치는 이 저장소의 `.stage/` 를 저장소 밖에 복사하고 W-00000416 의 카드를 다른 번호로 하나 더 넣어 쟀습니다.
고친 뒤에도 전체는 9,983자입니다. 남은 자리는 규칙 후보가 채웁니다. 상한은 그대로 10,000자입니다.

## 줄마다 한 일

"이미 있는 자리"는 이 세션이 파일을 열어 그 문장이 있는 것을 확인한 자리입니다.

| 고치기 전의 줄 | 글자 수 | 한 일 | 그 내용이 이미 있는 자리 |
|---|---|---|---|
| Global lifecycle axis | 102 | 한 줄로 줄여 남김(`Lifecycle: …`) | `.stage/index.md` 의 "Lifecycle", "Core rule" |
| Space axis (폴더 여덟 개가 책임을 나눈다) | 121 | 덜어냄. `.stage/index.md` 를 가리킴 | `.stage/index.md` 의 "Authority", "Routing rules" |
| Core principles 와 원칙 여섯 개의 요약 (다섯 줄) | 389 | 덜어냄. 원칙 목록의 경로만 남김 | `.stage/official/canon/principles.md`. 여섯 원칙이 거기 있는지는 감사가 본다(`audit_stage.py`, "Core principles are missing") |
| Cite the governing principles in every decision record and retrospective | 75 | 덜어냄 | 결정: 결정 템플릿의 `## Principles applied`, `stage-decision` 스킬. 회고: 해당 없음. 아래 "틀린 문장" 참고 |
| Register an active work item … before modifying governed files | 160 | 관문 한 줄로 합쳐 남김 | 훅의 거부 문구 `Stage registration gate violation: …`(`stage/hooks/stage_work.py`). `stage-work` 스킬과 `register_work.py` 를 이름으로 알려 준다 |
| Modifying `.stage/official/` is gated ONLY by a pending intent … | 317 | 관문 한 줄로 합쳐 남김. 새 카드가 필요 없다는 것만 남김 | 훅의 거부 문구 `Stage promotion gate violation: …`(`stage/hooks/stage_runtime.py`). `stage-retrospective` 와 `scripts/promote_intent.py` 를 알려 준다. `.stage/` 가 등록 관문 밖이라는 것은 `stage/operations/hooks.md` 의 "Registration gate scope", 보관은 `stage-archive` 스킬 |
| Artifact map (기록 종류 열한 개의 폴더, `start_work.py`, 손으로 옮기지 말 것) | 608 | 덜어냄. `.stage/index.md` 를 가리킴 | 폴더: `.stage/index.md` 의 "Routing rules", `stage/operations/artifacts.md`. `start_work.py` 와 "Never hand-move": `stage-work` 스킬의 "Start now" |
| 인라인 인터프리터 코드 금지 | 285 | 203자로 줄여 남김 | 훅의 거부 문구(`stage/hooks/stage_guard.py`), `stage/operations/hooks.md` 의 "Blocked actions" |
| Venue routing 과 그 뒤의 규칙 | 947 | 525자로 줄여 남김. 배정 표, "사람에게 묻지 않는다", 실행 방식(팀원, 드라이버, `claude-venue.md`)은 남김 | 예외 결정(`authorizes: venue_exception`)과 `split`: `stage-work` 스킬의 "Draft the item" 과 `register_work.py` 의 거부 문구. 구현 venue 가 못 정한 결정을 계획 venue 카드로 넘기는 것: `stage-handoff` 스킬 |
| Stage document language | 338 | 211자로 줄여 남김 | `stage/README.md`, `stage/docs/SCHEMA_V5.md`, 이 저장소의 `CLAUDE.md` "Language" |

남긴 줄을 고른 기준은 하나입니다. 세션이 첫 도구 호출 전에 알아야 하고, 거부 문구로는 늦는 것만 남겼습니다.

- 인라인 코드 금지와 venue 실행 방식은 각각 0.66.1 과 그 앞 릴리스에서 까닭을 적고 일부러 넣은 줄입니다
  (`stage/CHANGELOG.md`: "A session used to learn this only from the denial"). 그래서 줄이되 빼지 않았습니다.
- 배정 표와 문서 언어는 이 프로젝트의 설정값이라 다른 자리에서 읽으려면 `settings.json` 을 열어야 합니다.

## 틀린 문장 하나

"Cite the governing principles in every decision record and retrospective" 의 회고 쪽은 지금의 계약과 어긋나 있었습니다.
DE-00000093 뒤로 회고는 세 칸만 가지고, `stage/operations/retrospective.md` 는 원칙 인용을 결정 기록의
`## Principles applied` 가 소유한다고 적습니다. 이 문장은 그 결정 뒤에도 세션마다 실렸습니다.

## 재지 못한 것

- 덜어낸 문장을 세션이 실제로 썼는지. M-00000006 의 (가)가 말하는 하중이고, 이번에도 잴 기록이 없습니다.
  덜어낸 근거는 "쓰이지 않는다"가 아니라 "같은 내용이 다른 자리에 있다"입니다.
- 기기에서 도는 세션이 줄어든 글로 일할 때 거부를 더 자주 받는지. 클라우드 세션은 이 글을 받지 않아 볼 수 없습니다.
- 다른 프로젝트에서의 크기. 배정 표의 길이는 프로젝트마다 다릅니다. 이 저장소는 종류가 열 개입니다.

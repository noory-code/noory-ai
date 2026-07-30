---
id: W-00000141
title: 설명 문서 갱신이 프로젝트가 쌓은 내용을 무엇으로 알아보는가
kind: design
venue: claude
milestone:
source:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000141
promotion: promoted
review: not_required
scope: .stage/decisions/pending/, .stage/state/observations/
promotes: .stage/official/decisions/records/DE-00000042.md, .stage/official/decisions/index.md
decision_refs: DE-00000042
---

# W-00000141 설명 문서 갱신이 프로젝트가 쌓은 내용을 무엇으로 알아보는가

## Purpose

설명 문서를 갱신하는 명령이 프로젝트가 쌓은 데이터를 지운다. 그런데 이것은 구현 실수가 아니라
**DE-00000029 가 결정한 동작**이다. 그 결정은 소유 경계를 템플릿의 표 모양으로 정하고 세 갈래를
세웠고, 첫 갈래를 이렇게 적었다: "표가 없는 문서 — 각 폴더의 `README.md`, `_template.md`,
`state/current.md` 등. 통째로 현행 템플릿으로 교체한다."

그 전제가 틀렸다. `state/current.md` 는 관측 인덱스를 **불릿 목록**으로 쌓는다 — 표가 아니라서
보호 갈래에 안 걸리고, 프로젝트 데이터라서 지워지면 안 된다. novel-workspace 에서 인자 없는
기본 실행이 관측 22행을 지웠다(stage 0.54.4, 2026-07-30). 이 저장소는 같은 파일을
`guidance_overrides` 로 선언해 두고 있다 — 같은 위험을 먼저 밟은 흔적이고, **우회를 아는 사람만
안전하다**는 뜻이다.

따라서 물음은 "코드를 어떻게 고치나"가 아니라 **"프로젝트가 쌓은 내용을 무엇으로 알아보는가"**
다. 표 모양은 그 답으로 부족하다는 것이 실측으로 드러났다.

같은 보고가 두 번째 사실도 가져왔다: 빈 표 갈래(둘째 갈래)에서 `official/work/archive/index.md`
의 본문 문단이 한 줄로 뭉개졌다. 이쪽은 결정과 어긋나는 구현 결함이므로 이 카드의 물음이
아니고, 뒤따르는 구현 카드가 함께 받는다.

## Actions

- 결정 기록을 세운다. 물음: 기본 실행이 프로젝트가 쌓은 내용을 무엇으로 식별하는가.
- 후보를 적고 각각의 비용을 센다. 최소 셋:
  - **덮어쓰기를 기본에서 뺀다** — 대상 파일이 템플릿 본문 이상으로 내용을 갖고 있으면 기본
    실행이 건드리지 않고, 사람이 콕 집을 때만 교체한다. 새 선언이 필요 없고 데이터 쪽으로
    실패한다.
  - **프로젝트가 선언한다** — `guidance_overrides` 를 정식 통로로 올린다. 지금 두 프로젝트가
    손으로 하는 것이 규칙이 되지만, 데이터를 한 번 잃은 뒤에 배우게 된다.
  - **템플릿이 선언한다** — 어느 경로가 프로젝트 데이터를 쌓는지 플러그인이 명시한다. SSOT 는
    깔끔하지만 템플릿마다 새 필드를 유지해야 한다.
- 적용 자리를 센다 — 코드, 설정, 문서, 실패 경로, **그리고 같은 주제를 이미 정한 상위 결정**
  (DE-00000028·29). 결정이 DE-00000029 를 대체하는지 좁히는지 명시한다.
- 관측을 남긴다: 다른 프로젝트가 실제로 데이터를 잃었다는 사실.

## Scope

`.stage/decisions/pending/`, `.stage/state/observations/`.

**안 하는 것**: 코드 변경. 이 카드는 결정까지다. 구현은 뒤따르는 fix 카드(codex)가 받는다.

## Success criteria

- 결정 기록이 서고 `status: decided` 다. 물음·후보·선택·이유·적용 자리를 담는다.
- 결정이 **DE-00000029 와의 관계를 명시**한다: 어느 갈래를 무엇으로 바꾸는지, 나머지 두 갈래는
  그대로인지. 안 적으면 다음 사람이 두 결정을 나란히 읽고 어느 것이 참인지 못 고른다.
- 선택한 규칙이 **`state/current.md` 를 실제로 지킨다**. 결정 본문이 그 파일을 예로 들어
  기본 실행에서 어떻게 되는지 한 줄로 답한다.
- 관측 기록이 서고 `state/current.md` 인덱스에 걸린다.
- 뒤따르는 구현 카드가 무엇을 해야 하는지 결정에서 바로 읽힌다 — 구현 카드가 설계를 다시
  하지 않는다.

## Related truth

- DE-00000029 — 갱신이 무엇을 교체하고 무엇을 남기는지 정한 결정. 첫 갈래가 `state/current.md`
  를 이름으로 지목한다.
- DE-00000028 — 낡은 설명 문서를 검사가 찾고 갱신은 명시적 명령으로 한다.
- `stage/scripts/guidance_docs.py:125` `plan_refresh` — 세 갈래가 코드로 서 있는 자리.
  표가 없으면 `RefreshPlan("refresh", template_text)` 로 통째 교체한다.
- `stage/scripts/refresh_guidance.py:37` — 도움말이 "채워진 표를 가진 파일만 명시했을 때
  교체된다"고 말한다. 표가 없는 파일은 그 약속의 대상이 아니다.
- 실측 보고: novel-workspace, stage 0.54.4, 2026-07-30. 잃은 것 —
  `state/current.md`(관측 22행), `official/model/` 의 경계·인터페이스·개요 표,
  `official/work/archive/index.md`(문단 뭉개짐). git 으로 복구하고 `guidance_overrides` 로 재발
  차단.

## Progress


## Verification


### Executed at close — 2026-07-30

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

[R-00000141](../../retrospectives/R-00000141.md) — 결정이 예시로 적은 파일 이름이 그 결정의
전제였다.

## Promotion decision

FINAL: promoted. DE-00000042 는 앞으로의 작업을 구속하는 계약이고 일회성 허가(`authorizes:
venue_exception`)가 아니므로, DE-00000030 의 기계적 판정에 따라
`official/decisions/records/` 로 승격한다.

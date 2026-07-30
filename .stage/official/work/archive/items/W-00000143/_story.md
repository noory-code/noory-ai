---
id: W-00000143
title: 쌓이는 자리가 자동 갱신을 되찾는 길을 정한다
kind: design
venue: claude
milestone:
priority:
autonomous: false
acceptance:
  - "python3 stage/scripts/audit_stage.py"
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000143
promotion: not_applicable
review: not_required
scope: .stage/decisions/pending/, .stage/state/observations/, .stage/work/planned/
promotes:
decision_refs: DE-00000047
---

# W-00000143 쌓이는 자리가 자동 갱신을 되찾는 길을 정한다

## Purpose

설명 문서를 템플릿에서 갱신하는 명령이 지금은 프로젝트가 쌓은 내용을 만나면 건드리지 않고
보고만 한다. 데이터는 안전해졌다. 대신 관측 인덱스나 모델 지도처럼 프로젝트가 계속 쌓는
문서는 사람이 경로를 하나씩 집어야만 갱신된다. 플러그인이 설명글을 고쳐도 그 문서들은 낡은 채로
남는다. DE-00000042 가 이 값을 치르기로 하고, 되찾는 길을 후속으로 넘겼다 — 쌓이는 자리를
템플릿이 빈 그릇으로 배포하면 기존 갈래가 그 문서를 자동으로 지킨다.

읽어 보니 그 길이 DE-00000042 가 적어 둔 모양 그대로는 아니다. 확인한 값 셋:

- **빈 그릇을 알아보는 장치는 이미 있지만 표만 안다.** 그런데 쌓이는 문서 다섯 중 표를 쓰는
  것은 하나도 없다. 관측 인덱스는 불릿이고(템플릿이 빈 불릿 하나를 이미 배포한다), 모델 문서
  셋은 그릇 없는 산문이고, 불변 조건은 플러그인이 직접 쓴 불릿 다섯이다.
- **표가 없는 프로젝트 파일을 만나면 합치기가 거절하고, 거절 하나가 명령 전체를 실패로 만든다.**
  템플릿만 빈 표로 바꿔 내보내면 마이그레이션을 받기 전까지 모든 프로젝트의 기본 갱신이 실패한다.
- **어느 스크립트도 이 다섯을 쓰지 않는다.** 사람과 에이전트가 손으로 쓴다. 그래서 표로 옮기는
  일은 기계 형식 변경이 아니라 사용자가 읽는 면을 바꾸는 일이다.

그래서 이 카드가 정할 것은 "템플릿을 표로 바꾸자"가 아니다. **표가 아닌 그릇을 코드가 알아보게
할지, 문서를 표로 옮길지, 문서마다 나눌지**다.

## Actions

- 갈래를 하나 더 둘지 정한다. 둔다면 빈 목록 그릇의 판정 조건과 합치기 규칙을 결정에 적는다.
- 이미 배포된 프로젝트에서 무엇이 일어나는지 정한다. 지금은 거절 하나가 명령을 실패시키므로,
  마이그레이션 없이 먼저 나갈 길이 있는지 아니면 한 릴리스에 함께 실려야 하는지를 정한다.
- 감사 쪽 쌍도 같은 그릇 개념을 받게 한다. 갱신만 고치면 새 갈래가 붙은 문서는 감사에서 영원히
  낡음으로 보고된다.
- 모델 문서 셋과 불변 조건 문서는 이 결정에서 열린 물음으로 이름을 걸어 남긴다. 불변 조건은
  플러그인이 쓴 목록이라 목록을 아는 갈래가 생기면 "깨끗할 때 자동 갱신"에서 "항상 건너뜀"으로
  조용히 넘어간다 — 그 결과를 결정이 미리 말한다.
- 결정 기록을 쓰고, 코드·템플릿·마이그레이션은 별도 구현 카드로 넘긴다.

## User value

플러그인이 설명글을 고치면 프로젝트가 손 안 대고 받는다. 지금은 낡음 보고를 읽고 사람이 경로를
하나씩 집어 줘야 하고, 안 집으면 프로젝트 문서가 낡은 판으로 남는다.

## Scope

### Included

- 결정 기록 하나 — 쌓이는 자리를 자동 갱신이 어떻게 알아볼지.
- 곁따라 나온 관측 하나 — v3 세대 템플릿 트리가 아직 디스크에 있고 초기화 스킬 문장이 그것을
  가리킨다.

### Excluded

- 코드·템플릿·마이그레이션 구현. 구현 카드 몫이다.
- 모델 문서 셋과 불변 조건 문서의 그릇 모양 확정. 결정 안에서 열린 물음으로만 남는다.
- v3 템플릿 트리 정리. 관측으로만 남긴다.

## Risks

- 빈 표 갈래는 본문이 한 줄로 뭉개진 결함 이력이 있고 재현 조건을 아직 못 찾았다(R-00000142).
  갈래를 넓히면 그 결함에 노출되는 문서가 늘어난다.
- 표로 옮기면 사용자가 읽는 면이 나빠진다. 관측 본문은 여러 줄로 감기는 산문인데 표 행은 한 줄
  이다.
- 이 저장소에서는 관측 인덱스가 `guidance_overrides` 에 들어 있어 기본 실행이 판정에 닿지 않는다.
  검증은 임시 프로젝트나 단위 시험으로 해야 하고, 이 저장소의 실행 결과는 근거가 못 된다.

## Success criteria

- 결정 기록이 갈래 표를 갱신하고 DE-00000029·DE-00000042 와의 관계를 표 하나로 밝힌다.
- 적용 자리 표가 코드·도움말·문서·회귀 시험·한국어 번역본을 다 센다.
- 이미 배포된 프로젝트에서 기본 갱신이 어떻게 되는지 결정 본문이 명시한다 — 실패로 끝나는 경로
  포함.
- 사람이 겪는 결과를 결정이 목표로 적는다: 이 저장소에서 override 를 걷고 기본 갱신을 돌려도
  관측 인덱스가 살아 있고, 플러그인이 고친 설명글은 자동으로 들어온다. 실측은 구현 카드가 한다.
- `python3 stage/scripts/audit_stage.py` 통과.

## Next action

쌓이는 문서 다섯의 그릇 모양을 어떻게 정할지 결정 초안을 쓴다.

## Progress

## Verification

### Executed at close — 2026-07-30

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0

$ python3 stage/scripts/audit_stage.py
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision

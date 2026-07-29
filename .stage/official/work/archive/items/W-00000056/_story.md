---
id: W-00000056
title: 마이그레이션의 안내 산문 갱신 방식 결정 (Q-00000001)
kind: planning
venue: claude
priority: high
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000055
promotion: not_applicable
scope: .stage/decisions/pending/, .stage/work/planned/, .stage/state/questions.md, .stage/state/questions/
promotes:
decision_refs: DE-00000028
---

# W-00000056 마이그레이션의 안내 산문 갱신 방식 결정 (Q-00000001)

## Purpose

스키마 마이그레이션이 .stage 안내 문서의 산문을 갱신하지 않아 v3 잔재가 남는 문제의 처리 방식을 결정한다

## Source

Q-00000001. W-00000053(안내 문서 갱신)과 W-00000055(검증 템플릿 중립화)에서 두 번 부딪힌
근본 원인.

## User value

Stage 사용자가 v3에서 v4로 마이그레이션한 뒤에도 `.stage/` 안내 문서가 현행 스키마와 일치한다고
믿을 수 있다. 지금은 산문이 조용히 낡은 채 남고 감사도 잡지 못한다.

## Scope

### Included

- Q-00000001의 결정 후보 3가지를 검토해 하나를 고른다: (1) 마이그레이션이 손대지 않은 뼈대
  문서를 현행 템플릿으로 자동 교체, (2) 감사가 안내 문서를 템플릿과 대조해 드리프트 경고,
  (3) init 재실행을 문서화(현재의 암묵적 경로).
- 결정을 결정 레코드로 남기고, 구현이 필요하면 구현 항목을 분리 등록한다.

### Excluded

- 구현 자체(결정 후 별도 항목). 이 카드는 결정까지만.

## Dependencies

없음. 이 프로젝트는 이미 수동 갱신됐으므로 급하지 않다.

## Risks

자동 교체(후보 1)는 사용자가 편집한 안내 문서를 덮을 위험이 있다. 뼈대와 편집본을 구분하는
기준이 결정의 핵심.

## Success criteria

- 세 후보 중 하나가 원칙 근거와 함께 결정 레코드로 기록된다.
- 구현이 필요하면 구현 항목이 `parent: W-00000056` 계보로 등록된다.

## Next action

없음. 결정은 DE-00000028에 기록됐고 구현은 W-00000057이 소유한다.

## Progress

- 코드 근거 확인: `audit_stage.py`의 `audit_template_files`는 템플릿 파일의 존재만 확인하고
  내용을 비교하지 않는다. `init_stage.py`는 기존 파일을 건너뛰며 `--force`는 인덱스 표와 상태
  문서까지 덮어 프로젝트 데이터를 파괴한다. `escalate_work.py`는 프로젝트의 `_template.md`를
  런타임에 읽는다.
- 드리프트 분류: W-00000053이 갱신한 문서들의 드리프트는 스키마 세대 변경과 언어 불일치
  두 종류였고, 후자는 스키마 마이그레이션이 개입하는 시점이 아니다. 후보를 4개로 넓혀
  (D: 복사본 폐지) 비교했다.
- 결정: DE-00000028 — 감사가 감지하고 명시적 명령이 갱신한다.
- 구현 항목 등록: W-00000057 (kind development). 계보는 프론트매터 `parent`가 아니라 카드
  본문 `Source`가 소유한다 — `parent`는 집계 관계여서(하위가 열려 있는 동안 상위는 미완)
  결정만 소유하는 이 카드를 구현이 끝날 때까지 열어 두게 되고, 이 카드의 제외 범위와
  모순된다. 성공 기준의 문자적 표현(`parent: W-00000056`)에서 벗어난 지점이다.
- Q-00000001은 이 결정으로 닫고 `state/questions/`에서 제거했다(답은 DE-00000028이 소유하며,
  파일은 git 이력에 남는다).

## Verification

### Executed at close — 2026-07-25

```
$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
WARNING KIND001 [.stage/official/work/archive/items/W-00000040.md]: Work kind `bug` has no `passed` criterion in operations/verification.md.
Summary: errors=0, warnings=1
```

## Retrospective

## Promotion decision

---
id: W-00000276
title: Avatar에서 선택의 이유와 개인 기준의 변화를 살펴보게 한다
kind: development
venue: codex
milestone:
autonomous: false
acceptance:
  - "python3 -m unittest discover -s avatar/tests -q"
  - "python3 -m unittest tests.test_plugin_contracts -q"
  - "git diff --check"
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000276
promotion: not_applicable
review: passed
scope: avatar/
promotes:
decision_refs:
---

# W-00000276 Avatar에서 선택의 이유와 개인 기준의 변화를 살펴보게 한다

## Purpose

사용자가 여러 프로젝트의 선택을 근거와 함께 돌아보고 개인 기준을 직접 확인하거나 고칠 수 있게 합니다

## Actions

W-00000273의 약속을 바탕으로 독립적인 로컬 기록·조회·수정부터 만듭니다.

검토를 마친 `.stage/research/llm-work/implementation-design.md`의 Avatar 계약을 구현합니다.
직접 입력, 확인·변경·철회, 출처 첨부, 반복 요청, 변경 이력에 대한 실패 사례부터 확인합니다.
모듈이 500줄을 넘으면 역할에 따라 나눌지 검토합니다.
플러그인을 두 호스트가 찾을 수 있도록 필요한 marketplace와 계약 검사도 갱신합니다.
이 변경은 `avatar/` 밖의 범위를 넘으므로 보고서에 경로와 이유를 적습니다. 카드의 scope는 바꾸지 않습니다.

## User value

자신이 밝힌 기준과 실제 선택, 생각이 달라진 시점을 근거와 함께 돌아볼 수 있습니다.

## Scope

### Included

- 사용자 입력과 명시적으로 받은 기록을 보관하고 원문 출처를 연결합니다.
- 개인 기준의 확인·수정·철회를 남기고 이전 버전과 변경 이유를 조회합니다.
- 다른 선택을 검토 후보로 보여주고 사용자의 판단을 기록합니다.
- 확인한 개인 기준을 내보내며 Claude와 Codex용 스킬·manifest·문서를 제공합니다.
- 로컬 데이터는 플러그인 설치 캐시 밖에 저장합니다.

### Excluded

- 성격이나 숨은 동기를 확정하지 않습니다.
- 기록을 허가 없이 전역 수집하거나 원격으로 전송하지 않습니다.
- 프로젝트 예외를 자동으로 개인의 일반 기준으로 올리지 않습니다.

## Risks

새 플러그인이 Distill의 전역 저장만 반복하면 독립적인 가치가 없습니다. 선택을 돌아보고 기준을 고치는 흐름을 검사합니다.
중복 입력과 동시 쓰기, 삭제된 원문과 형식이 다른 입력을 명시적으로 처리합니다.

## Success criteria

- 직접 입력하거나 다른 플러그인에서 받은 선택과 기준을 출처에 연결해 기록하고 다시 볼 수 있습니다
- 개인 기준을 확인하고 수정하면 이전 내용과 변경 이유가 남으며 프로젝트의 예외를 개인의 일반 기준으로 자동 확정하지 않습니다
- 달라진 선택을 검토할 후보로 보여주고 확인한 개인 기준을 다른 작업에서 사용할 수 있게 제공합니다
- Stage와 Distill 없이도 기본 기록과 조회·수정 기능을 사용할 수 있고 두 호스트용 플러그인 구성을 제공합니다

## Next action

제품별 테스트와 독립 리뷰를 마쳤습니다. W-00000277의 세 번째 시험은 실제 수신 세션 여섯 개가 모두 정상 종료했고 독립 리뷰도 통과했습니다.
2026-10-07 사용자 승인 뒤 전용 worktree의 제품 소스를 커밋했습니다. 커밋 번호는 구현·검증 기록에서 확인합니다.
작업별 회고와 완료 절차를 진행합니다.

## Related truth

SSOT, AHA, KISS, TDD, Honesty를 적용합니다. 부모의 사용자 합의가 이전 Avatar 구현 보류를 이번 범위에서 갱신합니다.

## Progress

2026-10-05: 구현 작업을 등록했습니다. avatar 디렉터리는 아직 만들지 않았습니다.

2026-10-06: Codex CLI의 사용량 오류 뒤 사용자가 이 세션에서 직접 구현하도록 허용했습니다. 감독이 전용 worktree에서 구현과 검사를 이어갔습니다. Claude CLI로 독립 리뷰를 받았으며, 반려된 항목은 실패 시험으로 재현하고 수정했습니다. 드라이버의 완료 판정으로 보고하지 않습니다. 제품 커밋·푸시는 아직 하지 않았습니다.

2026-10-31: 원래 제품 커밋 `04a3e7e2`(`codex/criteria-integration`)과 같은 변경(`git patch-id --stable` 일치)이 배포용 커밋 `d279c191` 로 `main` 에 들어가 있습니다. 닫기는 `d279c191` 을 HEAD 로 둔 임시 작업 공간에서 했습니다. `.stage/` 는 `c692799e` 상태로, 리뷰 명령은 W-00000286 커밋 `1ab2fdf5` 상태로 커밋하지 않고 덮어 썼습니다.

## Verification

독립 실행·변경 이력·범위 제한·중복 입력을 검사하고 두 호스트에서 명시적인 스킬 호출을 확인합니다.

2026-10-06: 실행 위치, 제품별 검사 수, 리뷰 원본과 한계는 [구현·검증 기록](../../../../research/llm-work/integration/implementation-status.md)에 모았습니다. 실제 두 호스트 인계와 제품 소스 보존이 남아 있어 이 카드를 완료로 바꾸지 않습니다.

### Executed at close — 2026-10-31

```
$ python3 -m unittest discover -s avatar/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 24 tests in 4.124s

OK

$ python3 -m unittest tests.test_plugin_contracts -q
[exit 0]
----------------------------------------------------------------------
Ran 7 tests in 0.002s

OK

$ git diff --check
[exit 0]

```

### Review at close — 2026-10-31

```
Review report: .stage/.runtime/driver/logs/W-00000276.md
```

## Retrospective

[R-00000276](../../../retrospectives/R-00000276.md).

## Promotion decision

이 카드는 결정이나 승격 경로를 소유하지 않으므로 `not_applicable`이다.

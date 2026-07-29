---
id: W-00000067
title: 설정 파일을 읽는 자리를 하나로 모은다
kind: development
venue: codex
priority: high
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000066
promotion: not_applicable
scope: stage/hooks/, stage/scripts/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json
promotes:
decision_refs:
---

# W-00000067 설정 파일을 읽는 자리를 하나로 모은다

## Purpose

프로젝트 설정 파일을 읽는 코드가 열다섯 군데에 흩어져 각자 경로를 만들고 각자 파싱한다.
읽는 자리를 하나로 모은다. 동작은 바뀌지 않는다

## Source

W-00000026의 선행 작업. 그 카드는 "설정을 읽는 곳이 이미 한 군데로 모여 있다"는 전제로
쓰였는데, 확인해 보니 사실이 아니었다.

## User value

이 카드 자체로는 사용자가 보는 변화가 없다. 다음 카드(W-00000026, 설정에 주석 달기)가
한 군데만 고쳐서 끝나게 만드는 것이 값어치다. 지금 형식을 바꾸려면 열다섯 군데를 동시에
건드려야 하고, 그런 커밋은 검토가 불가능하다.

## Scope

### Included

- `stage_paths.py`에 설정 파일을 읽는 함수 하나를 둔다. 경로를 만드는 것도 파싱하는 것도
  그 함수만 한다.
- 지금 각자 읽는 자리를 전부 그 함수로 돌린다.
- 실패했을 때의 동작은 자리마다 지금 그대로 유지한다(아래 위험 참조).
- 기존 테스트가 전부 통과해야 한다. 동작이 바뀌지 않았다는 것이 이 카드의 검증이다.

### Excluded

- 주석 허용, 파일 이름 추가(`settings.jsonc`), 템플릿 변경, 감사 규칙 — 전부 W-00000026.
- 설정 스키마 변경. 키를 더하거나 빼지 않는다.

## Dependencies

없음. 이 카드가 W-00000026의 선행이다.

## 이미 확인된 것

- `stage/hooks/stage_paths.py`에 `settings_path = stage_root / "settings.json"`이 **10번**
  나온다. 각각 바로 뒤에서 `json.loads`를 따로 부른다.
- 그 밖에 따로 읽는 파일: `stage/scripts/migrate_stage.py`(115행, 202행에서 쓰기도 한다),
  `stage/scripts/init_stage.py`(65행), `stage/scripts/guidance_docs.py`(`load_settings`),
  `stage/scripts/audit_stage.py`(자체 `load_settings`).
- 읽기만 하는 것이 아니다. `migrate_stage.py`는 `schema_version`을 다시 써 넣는다. 쓰는 쪽도
  같이 볼 것.

## Risks

**실패 처리가 자리마다 다르고, 그 차이는 의도된 것이다.** 어떤 자리는 설정을 못 읽으면 빈
값으로 넘어가고, 어떤 자리는 오류를 돌려주며, 게이트는 아예 막는다(fail-closed). 하나로
모으면서 이 차이를 없애면 보안 성격의 동작이 조용히 약해진다. 읽는 방법만 합치고, 못 읽었을
때 무엇을 할지는 부르는 쪽이 계속 정하게 할 것.

## Success criteria

- 설정 파일 이름 문자열이 코드에 한 번만 나온다(문서·주석·오류 문구 제외).
- 못 읽었을 때의 동작이 자리마다 지금과 같다. 특히 게이트의 fail-closed가 유지된다.
- `python3 -m unittest discover -s stage/scripts/tests -q`와 `-s stage/hooks/tests -q` 통과.
- `python3 stage/scripts/audit_stage.py --project-root .` 오류 0 경고 0.

## Next action

codex 창에서 아래로 시작한다.

```
python3 stage/scripts/start_work.py --project-root . W-00000067 \
  --scope "stage/hooks/, stage/scripts/, stage/CHANGELOG.md, stage/.claude-plugin/plugin.json, stage/.codex-plugin/plugin.json"
```

동작을 바꾸지 않는 정리이므로 기존 테스트가 검증이다. 다만 실패 처리 차이를 지키는지 확인하는
테스트가 없다면 그것은 새로 쓴다.

커밋하지 않는다 — 검토와 커밋은 맡긴 쪽이 한다(`stage-handoff`의 위임 실행).

venue: codex(development).

## Progress

구현은 codex 창이 위임 실행했고(모델 `gpt-5.6-sol`), 검토와 커밋은 claude 창이 했다.

`stage_paths.read_settings()`가 경로와 파싱만 소유하고, 못 읽었을 때 무엇을 할지는 고르지
않는다. 경로와 파싱 결과와 예외를 그대로 돌려주고 부르는 쪽이 판단한다. 이 카드가 지키라고
한 것이 그것이다 — 언어와 라우팅은 기본값으로 넘어가고, 실행기와 한계는 막고, 게이트는
설정을 못 믿으면 거부한다. 열다섯 자리가 각자의 정책을 그대로 유지했다.

검토에서 자리별로 대조한 것: `governance_broken`의 거부, `load_limits_config`가 읽기 실패와
형식 오류를 다른 문구로 구분하는 것, `schema_migration_banner`가 파일이 없을 때와 깨졌을 때를
가르는 것. 전부 이전과 같다.

새 테스트는 없다. 실패 동작을 지키는 테스트가 이미 소비자별로 있었기 때문이며(막는 쪽 셋,
넘어가는 쪽 둘, 게이트 둘), 이 판단이 맞는지 직접 확인했다.

숫자로는 85줄이 들어가고 164줄이 빠졌다. 설정 파일 이름이 코드에 한 번만 남았다.

## Verification

### Executed at close — 2026-07-25

```
$ python3 -m unittest discover -s stage/scripts/tests -q
[exit 0]
... (7 earlier lines omitted)
Unattended run on isolated branch: stage/driver/W-00000001-1784982066 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784982066
Unattended run finished: 1 item(s) closed on isolated branch stage/driver/W-00000001-1784982066. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784982066 (base: main)
Unattended run finished: 0 item(s) closed on isolated branch stage/driver/W-00000001-1784982066. Human review + merge required; the base branch was not modified.
Unattended run on isolated branch: stage/driver/W-00000001-1784982066 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784982066
Outcome: blocked — parent aggregation-close failed: W-00000001: parent close failed: boom; handoff on stage/driver/W-00000001-1784982066
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Unattended run on isolated branch: stage/driver/W-00000001-1784982066 (base: main)
[W-00000002] completed on stage/driver/W-00000001-1784982066
[W-00000003] completed on stage/driver/W-00000001-1784982066
Unattended run finished: 2 item(s) closed on isolated branch stage/driver/W-00000001-1784982066. Human review + merge required; the base branch was not modified.
Outcome: blocked — unattended mode requires a `limits` config (absent is not unlimited here); refusing to run
Recommended next action: attempt cap reached / no progress / global limit exceeded → escalate_work
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
Stage project already uses schema v4; no migration needed.
Preflight passed. Close every other agent/editor window before continuing; the schema-v4 maintenance marker now denies concurrent Stage writes.
  unchanged operations/verification.md (unchanged)
  delete backlog B-00000001-realized.md (realized by W-00000009; git history keeps the file)
  convert backlog B-00000002-open.md -> W-00000001.md (planned work card)
  convert backlog B-00000003-child.md -> W-00000002.md (planned work card)
  update backlog index (1 closed rows removed)
  stamp  settings.json schema_version = 4
Schema-v4 migration complete with no blocking audit findings. Guidance drift remains a non-blocking audit warning until the explicit refresh command is run.
All migration changes are staged; this command does not commit. Review them, then commit with: git commit -m "chore(stage): migrate project harness to schema v4"
Before committing, `migrate_stage.py --abort` restores the staged/working tree. After committing, rollback means `git revert <migration-commit>`.
----------------------------------------------------------------------
Ran 311 tests in 29.467s

OK

$ python3 -m unittest discover -s stage/hooks/tests -q
[exit 0]
----------------------------------------------------------------------
Ran 324 tests in 0.889s

OK

$ python3 stage/scripts/audit_stage.py --project-root .
[exit 0]
Stage audit: /Users/woogis/Workspace/repo/noory-ai/.stage
OK: no findings
Summary: errors=0, warnings=0
```

## Retrospective

## Promotion decision

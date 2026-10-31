---
id: W-00000299
title: 클라우드에서 닫은 카드를 로컬 codex 로 표본 재검토한다
kind: qa
venue: codex
milestone:
autonomous: false
acceptance: []
status: completed
verification: passed
retrospective: completed
retrospective_ref: R-00000299
promotion: not_applicable
review: not_required
scope: .stage/work/
promotes:
decision_refs:
---

# W-00000299 클라우드에서 닫은 카드를 로컬 codex 로 표본 재검토한다

## Purpose

클라우드 카드의 같은 모델 계열 닫기 리뷰가 실행자의 사각지대를 함께 놓치는지 로컬 codex 재검토로 확인해 DE-00000082 를 유지할지 판단한다.

## Actions

- `origin/claude/w268-cloud`의 `2baf077c`에서 `codex/w299-cloud-review-sample` 브랜치를 만들고 별도 worktree에서 검사했습니다.
- 현재 카드와 보관 카드의 frontmatter에서 `environment: cloud`, `review: passed`를 함께 만족하는 카드를 전부 골랐습니다.
- `git log --all --grep='W-0000029[3-7]'`와 `git show`로 소스 커밋을 찾았습니다. 각 커밋을 임시 폴더에 `git archive`로 풀어 당시 코드와 테스트를 검사했습니다.

## User value

같은 모델 계열의 리뷰가 놓친 사례를 실제 코드와 비교해, 클라우드 실행 정책을 판단할 근거를 남깁니다.

## Scope

### Included

표본 5개의 성공 기준 6개를 다시 판정하고 기록된 리뷰와 비교합니다. 카드·회고·작업 인덱스만 영구 변경합니다.

### Excluded

표본 카드, 제품 코드, DE-00000082, 정책과 설정은 고치지 않습니다. 결함은 이 카드의 후속 작업에만 남깁니다.

## Risks

표본은 한 브랜치의 가까운 시기에 닫힌 Stage 카드 5개입니다. 전체 클라우드 작업의 실패 확률이나 모델 간 우열을 추정할 수 없습니다. 현재 브랜치에 합쳐지지 않은 작업과 `environment`가 없는 과거 카드는 포함하지 않았습니다.

## Success criteria

- 클라우드에서 닫은 카드 가운데 고른 표본을 로컬 codex 가 다시 판정하고, 반려 비율과 그 이유를 DE-00000082 의 판단 근거로 남긴다

## Next action

정책 소유자가 아래 강화 권고와 권한 제한 후속 작업을 검토합니다. 이 작업에서는 정책을 바꾸지 않습니다.
## Related truth

[DE-00000082](../../../decisions/pending/DE-00000082.md)의 정책을 평가했습니다. 이미 결정된 기록이므로 이 카드의 `decision_refs`에 소유권을 중복 기록하지 않습니다.
## Progress

### 표본과 소스 커밋

기준 시점은 `2baf077c`입니다. 검색 범위는 `.stage/work/current/`와 `.stage/official/work/archive/items/`입니다. frontmatter 조건과 각 카드의 같은 모델 계열 리뷰 설명을 함께 확인했습니다.

| 카드 | 위치 | 소스 커밋 | 닫기 커밋 |
|---|---|---|---|
| W-00000293 | official/work/archive/items/W-00000293/_story.md | `6c02735427271eb5b5275e14b0bf8f484074dd75` | `a1ef490e` |
| W-00000294 | official/work/archive/items/W-00000294/_story.md | `c3e702d6778ded14951d691439cdc780d53b62d7` | `ca646b28` |
| W-00000295 | official/work/archive/items/W-00000295/_story.md | `639f2b6b7c4ad086efdd775d28f5489bb4067c26` | `e41edfe7` |
| W-00000296 | official/work/archive/items/W-00000296/_story.md | `af7baa87242775802c76ed56abb96fc6d8682a78` | `7433a454` |
| W-00000297 | work/current/W-00000297/_story.md | `0469ab96e4cfb8e2855d9bb5f80b6333d23f957f` | `2baf077c` |

경로는 `.stage/` 아래를 가리킵니다. W-00000300도 `environment: cloud`이지만 `review: pending`이므로 제외했습니다. 표본을 늘리려고 조건 밖의 카드를 넣지 않았습니다.

### 직접 판정한 성공 기준

기존 PASS를 증거로 사용하지 않고 소스와 실행 결과로 판단했습니다. 아래에서 기록된 리뷰와 비교합니다. 카드 본문을 읽는 과정에서 기존 판정도 보았으므로, 기존 판정을 가린 실험은 아닙니다.

| 카드 | Success criteria 원문 | 판정 | 한 줄 근거와 실패하는 입력 종류 |
|---|---|---|---|
| W-00000293 | 다른 브랜치가 이미 쓴 번호로 계획 카드를 등록하면 그 브랜치 이름과 함께 거절된다는 것을 테스트가 확인한다 | PASS | `register_backlog_card()`가 `branch_record_numbers()`로 브랜치를 찾고, 실제 다른 ref를 만든 테스트가 `--backlog`에서도 종료 코드 1·브랜치 이름·카드 미생성을 확인합니다. |
| W-00000294 | 감사가 WORK027 로 거부할 승격 선택으로 닫으려 하면 닫기 도구가 카드를 바꾸지 않고 같은 이유로 거절한다는 것을 테스트가 확인한다 | PASS | approved의 경로 유무와 promoted의 경로 누락·파일 부재를 넣은 4가지 사례가 같은 오류와 카드 바이트 보존을 확인하며, 파일이 있는 promoted는 닫힙니다. |
| W-00000294 | 닫기 도구와 감사가 승격 기록 검사를 한 곳에서 공유한다 | PASS | `audit_stage.completed_promotion_errors()`를 감사와 `close_work.main()`이 함께 호출하고, 닫기에서는 검사 실행 전에 거절합니다. |
| W-00000295 | 프로젝트의 claude 리뷰 명령과 대역 리뷰어가 판정 파일 하나에만 쓰기를, 변경 경로 파일 폴더에 읽기를, unittest 실행만을 허락하고 프로젝트 파일 편집 권한을 주지 않는다는 것을 테스트가 확인한다 | FAIL | 두 경로가 허용하는 `Bash(python3 -m unittest:*)` 안의 Python 코드는 다른 파일도 쓸 수 있지만 테스트는 argv만 확인합니다. 실패하는 입력 종류는 import·setUp·테스트 본문에서 프로젝트 파일을 쓰는 unittest 모듈입니다. |
| W-00000296 | 프로젝트의 claude 리뷰 명령과 대역 리뷰어가 판정 파일에 Edit 규칙만 주고 Write 규칙을 주지 않는다는 것을 테스트가 확인한다 | PASS | 두 명령의 정확한 argv에 Edit 규칙만 남았고, 테스트도 Write 규칙 부재를 각각 확인합니다. 이 기준은 실행한 테스트의 파일 쓰기까지 막는다고 주장하지 않습니다. |
| W-00000297 | 드라이버가 close_work 를 부를 때 바깥 제한 시간이 검사 시간과 리뷰 제한 시간을 함께 덮는다는 것을 테스트가 확인한다 | PASS | 당시 `close_work`의 acceptance + 추가 검사 개수와 드라이버 계산이 같으며, 테스트가 검사 3개 × 30초 + 리뷰 3600초 + 60초와 리뷰 인자를 확인합니다. |

### 기록된 리뷰와 비교

- W-00000293의 기준 1개, W-00000294의 기준 2개, W-00000296의 기준 1개, W-00000297의 기준 1개는 기존 PASS와 같습니다.
- W-00000295의 기준 1개는 기존 PASS와 다릅니다. 기존 이유는 대역의 정확한 argv와 fake claude가 받은 argv가 같고 `acceptEdits`가 없다는 것이었습니다. 이는 직접 Edit 호출 범위를 확인하지만, 허용한 unittest가 실행하는 코드의 쓰기까지 제한한다는 증거는 아닙니다. 따라서 성공 기준 전체는 통과하지 못합니다.
- W-00000294의 리뷰에 추가된 실행 보고 계약 행은 `## Success criteria` 항목이 아니므로 분모를 늘리지 않았습니다.
- W-00000297의 부모 닫기는 여전히 기본 리뷰 시간을 쓰지만, 이 카드의 성공 기준인 바깥 제한 시간 계산과는 구별했습니다. 실행 보고에 이미 공개된 제한이므로 이를 새로운 FAIL로 세지 않았습니다.

### 반려 비율과 정책 권고

FAIL이 하나 이상인 카드는 W-00000295 한 개입니다. **반려 비율은 1 / 5 = 20%**입니다. 기준별로는 6개 중 1개가 FAIL입니다. W-00000296에서 Write 규칙을 없앴어도 허용한 unittest의 파일 쓰기 문제는 해결되지 않지만, 그 카드의 좁은 성공 기준까지 실패로 바꾸지는 않았습니다.

**DE-00000082를 강화할 것을 권고합니다.** 클라우드 실행 자체는 유지하되, 권한 제한이나 닫기·검증 절차를 바꾸는 카드는 같은 모델 계열의 리뷰에 더해 로컬 Codex의 검토를 거쳐 닫도록 하십시오. 이번 표본에서는 argv 확인을 실제 쓰기 제한의 증거로 받아들인 사례가 1개 나왔습니다. 나머지 4개는 명시된 기준을 만족했으므로 전체 정책을 되돌릴 근거는 부족합니다. 강화한 뒤에도 같은 방식으로 다시 표본을 검사해야 합니다. 이는 권고이며 이번 작업에서 결정이나 정책을 수정하지 않았습니다.

### 후속 작업

- W-00000295의 쓰기 제한을 다시 설계하십시오. 해당 종류가 닿는 곳은 `.stage/settings.json`의 `review.reviewers.claude`, `stage/scripts/claude_review_companion.py`, 템플릿 권한 안내, `stage/operations/cloud-execution.md`의 설명, `test_template_v4.py`와 `test_environment_venues.py`의 검증입니다. 명령 인자 제한과 자식 프로세스의 파일 접근 제한을 구분해야 합니다.
- 파일을 쓰는 테스트를 실제 리뷰 실행 경로에서 돌려 거절 여부를 확인하십시오. 소스를 읽기 전용으로 제공하는 실행 환경을 검토하고, 쓸 수 있어야 하는 캐시·결과 폴더를 별도로 정하십시오. 이 카드에서는 제품 코드나 표본 카드를 고치지 않았습니다.
- 이 발견은 후속 작업으로 수용합니다. 사용자가 발견을 이 카드에만 적으라고 지시했으므로 별도 관측이나 새 작업 카드는 만들지 않았습니다.

### Executor report

What changed: 표본 5개의 기준 6개를 소스 커밋에서 검토하고 판정·비교·반려 비율·권고와 회고를 기록했습니다.
Why: 같은 모델 계열 리뷰가 놓친 사례를 DE-00000082의 판단 근거로 남깁니다.
Decisions made: SSOT에 따라 당시 소스 커밋으로 판단했습니다. MECE에 따라 주어진 조건에 맞는 카드를 전부 골랐습니다. Honesty에 따라 argv 테스트와 실제 파일 접근 제한을 구분했습니다. 범위 밖 임시 작업은 `.w299-snapshots/`의 커밋 복사본과 재현 fixture이며 검사 후 삭제합니다. 도구가 세션 기록 경로도 범위 경고에 표시했지만 직접 수정하지 않았습니다.
Work not done: 실제 Claude 세션의 권한 거절 실험과 정책 변경·결함 수정은 하지 않았습니다. 제품 소스와 표본 카드는 변경하지 않았습니다.
## Verification

### 소스 커밋에서 실행한 검사

각 스냅샷 루트에서 `env -u GIT_INDEX_FILE python3 -m unittest discover -s stage/scripts/tests -p <파일> -q`를 실행했습니다. 기존 소스는 수정하지 않았습니다.

| 카드 | 테스트 파일 | 관측 결과 |
|---|---|---|
| W-00000293 | test_register_work.py | 47개, OK, exit 0 |
| W-00000294 | test_close_work.py | 70개, OK, exit 0 |
| W-00000295 | test_environment_venues.py / test_template_v4.py | 7개 / 24개, 모두 OK, exit 0 |
| W-00000296 | test_environment_venues.py / test_template_v4.py | 7개 / 24개, 모두 OK, exit 0 |
| W-00000297 | test_drive.py / test_drive_unattended.py | 두 명령 모두 exit 0; unattended는 46개, OK |

### W-00000295 반례

커밋 `639f2b6b`의 `claude_command()`와 프로젝트 리뷰 명령 모두 `Bash(python3 -m unittest:*)`를 허용합니다. 대역의 `main()`은 이 argv로 `subprocess.run()`을 호출하며 파일 쓰기를 제한하는 별도 실행 환경을 만들지 않습니다. 재현은 실제 표본 소스 대신 임시 fixture에서 했습니다.

```python
from pathlib import Path
import unittest

class WriteEffect(unittest.TestCase):
    def test_allowed_unittest_can_write_non_verdict_file(self):
        target = Path(__file__).parent / 'project-file.txt'
        target.write_text('changed by unittest\n', encoding='utf-8')
        self.assertEqual(target.read_text(), 'changed by unittest\n')
```

실행: `python3 -m unittest discover -s .w299-snapshots/probe -q` → 테스트 1개, OK, exit 0. 뒤이어 `cat .w299-snapshots/probe/project-file.txt`가 `changed by unittest`를 출력했습니다. 따라서 허용한 명령 종류에는 판정 파일 이외의 파일을 쓰는 실행이 포함됩니다. 실제 Claude 프로세스에서 이 명령을 승인하는지는 이번에 다시 시험하지 않았습니다. 이 한계와 별개로 기존 argv 테스트가 성공 기준의 쓰기 제한을 증명하지 못한다는 점은 소스와 재현으로 확인했습니다.

전체 테스트 스위트나 실제 클라우드 세션을 다시 실행한 것은 아닙니다. W-00000299를 닫는 감사 결과는 아래에 도구가 기록합니다.
### Executed at close — 2026-10-31

```
$ python3 stage/scripts/audit_stage.py
[exit 0]
k — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000034/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000035/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000036/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000037/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000038/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000039/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000048/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000055/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000061/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000074/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000080/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000090/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000123/_epic.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000137/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000154/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000159/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000160/_story.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000191.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
WARNING WORK029 [.stage/official/work/archive/items/W-00000189/W-00000192.md]: Success criteria are empty in archived work — do not invent a historical answer; ask the human before registering future work.
Summary: errors=0, warnings=32
```

## Retrospective

[R-00000299](../../retrospectives/R-00000299.md)에 외부·내부 완료와 후속 조치를 기록했습니다.
## Promotion decision

`not_applicable`입니다. 이번 작업은 판단 근거만 남기며 공식 정책을 승격하거나 변경하지 않습니다.

---
id: W-00000431
title: Stage 0.70.0 을 릴리스하고 기기에서 시험한다
kind: release
venue: claude
milestone:
autonomous: false
acceptance: []
status: archived
terminal_disposition: accepted
verification: passed
retrospective: completed
retrospective_ref: R-00000431
promotion: not_applicable
review: not_required
scope: stage/CHANGELOG.md,stage/.claude-plugin,stage/.codex-plugin
promotes:
decision_refs:
---

# W-00000431 Stage 0.70.0 을 릴리스하고 기기에서 시험한다

## Purpose

Unreleased 에 쌓인 변경(PO·PM·전문가 구조, 후속 후보와 규칙 후보의 문턱, 기록된 확인으로 닫기, 여섯 규칙)이 설치하는 사람에게 닿는다

## Actions


## User value


## Scope

### Included


### Excluded


## Risks


## Success criteria

- stage/CHANGELOG.md 의 맨 위 릴리스와 두 매니페스트가 0.70.0 이고 Unreleased 는 비어 있다
- 맥북의 claude plugin list 가 0.70.0 과 저장소 폴더에서 읽는다는 줄을 보여 준다
- Windows 세션이 0.70.0 에서 훅이 실행되는 것을 확인했다

## Next action

없음. 세 기준이 모두 채워져 닫는다.

## Related truth

## Sessions

## Progress

- 2026-11-26 사용자가 PO 세션에서 릴리스를 요청했다: "Stage 릴리스 합시다", "시험하구요." PO 세션 session_018VXR6NxmjDnZJNGb3TZWco 가 등록하고 시작했다. 성공 기준의 둘째와 셋째는 앞 릴리스 카드 W-00000372 의 것을 버전만 바꿔 옮겼다. 사용자의 "시험"을 기기에서의 확인으로 읽었다.
- 올리는 자리는 minor 다. `--main-session` 이 `--po-session` 이 되고 옛 역할 이름(`work`, `planning`, `discussion`, `consolidation`)을 호환 없이 거절하므로 깨는 변경이 들어 있다. 1.0 전이라 깨는 변경도 minor 로 올린다(0.69.0 이 `method` 를 필수로 하며 그렇게 했다). PO 세션이 사용자의 위임으로 정했다.
- 릴리스 커밋은 PO 세션이 이 브랜치에서 직접 만든다. 저장소의 릴리스 절차(루트 `CLAUDE.md`, "Plugin Changes")가 `release_plugin.py` 한 번과 커밋·푸시 한 번이라 PM 세션을 띄우지 않는다.
- 2026-11-26 PO 세션이 `release_plugin.py stage --bump minor` 로 0.70.0 을 만들고 커밋 3846e93c 로 올렸다. 그 커밋에서 훅 시험, 루트의 플러그인 계약 시험, `audit_stage.py`(오류 0), `release_plugin.py stage --check-released --since 0.67.0`(더해진 줄 없음)을 돌렸다. 첫째 성공 기준은 여기서 볼 수 있다. 둘째와 셋째는 사용자의 기계에서만 볼 수 있어 닫지 않고 병합한다. This change was merged without a close review.

## Verification

- Checked 2026-11-26 on Korean Windows 11 (ARM64, cp949, Python 3.14.10) at 1e585fd9: Windows 세션이 0.70.0 에서 훅이 실행되는 것을 확인했다 — held; `claude plugin marketplace update noory-ai` 와 `claude plugin update stage@noory-ai` 로 0.69.0 에서 0.70.0 으로 올린 뒤 저장소에서 `claude -p` 로 새 세션을 열어 실행 기록을 봤다 — `claude plugin list` 가 `stage@noory-ai` 에 `Version: 0.70.0` 을 보여 줬고, 그 세션은 Stage 를 `plugins\cache\noory-ai\stage\0.70.0` 에서 불러왔다. `SessionStart:startup` 훅이 실행돼 `## Stage context` 를 넣었고, `PreToolUse:Bash` 훅이 `python -c "print('.stage probe')"` 를 "Stage guard cannot verify what opaque inline interpreter code writes" 로 거부했고, `Stop` 훅이 성공으로 끝났다
- 같은 날 같은 기기의 `1e585fd9` 에서 `python -m unittest discover -s stage/hooks/tests -q` 는 491개가 통과했고(44개 건너뜀), `python -m unittest discover -s stage/scripts/tests -q` 는 1039개가 통과했다(6개 건너뜀, 529초). `python -m unittest discover -s plainly/tests -q` 는 22개가 통과했다.
- Checked 2026-11-26 on macOS 27.2.1 (arm64, Claude Code 2.1.321, Stage 설치본 0.70.0) at 1e585fd9: 맥북의 claude plugin list 가 0.70.0 과 저장소 폴더에서 읽는다는 줄을 보여 준다 — held; `claude plugin list` — `stage@noory-ai` 아래에 `Version: 0.70.0` 과 `Read from: /Users/woogis/Workspace/repo/noory-ai/stage` 가 나왔다

- Checks at close 2026-11-26: 3 passed — `python3 -m unittest discover -s stage/hooks/tests -q`; `python3 stage/scripts/release_plugin.py stage --check-released --since 0.67.0`; `python3 stage/scripts/audit_stage.py --project-root .`
- Load at close 2026-11-26: attempts 1, review FAIL rounds 0, repeated findings 0, driver rounds 0, driver failures 0 (timed out 0)

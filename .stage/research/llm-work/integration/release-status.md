# 세 플러그인 배포 기록

기준일: 2026-10-07. 담당 작업: W-00000278, CI 수정: W-00000279.

## 목적

사용자는 "푸시하고 병함하고 배포하고 그러세요"라고 요청했습니다.
검토한 세 플러그인을 원격 main에 반영하고, 배포한 파일을 새 Claude·Codex 세션에서 읽는지 확인합니다.

## 배포 결과

| 플러그인 | 버전 | 저장소 | 현재 확인한 상태 |
|---|---|---|---|
| Distill | [1.10.0](https://github.com/noory-code/novel-ai/releases/tag/distill-v1.10.0) | noory-code/novel-ai | main 병합, 릴리스 게시, 두 호스트에서 불러오기 통과 |
| Stage | [0.63.3](https://github.com/noory-code/noory-ai/releases/tag/stage-v0.63.3) | noory-code/noory-ai | main 병합, 릴리스 게시, 두 호스트에서 불러오기 통과 |
| Avatar | [0.1.2](https://github.com/noory-code/noory-ai/releases/tag/avatar-v0.1.2) | noory-code/noory-ai | main 병합, 릴리스 게시, 두 호스트에서 불러오기 통과 |

- [noory-ai PR #5](https://github.com/noory-code/noory-ai/pull/5): CI 30개 통과 후 `72fddba172c05731b5035e4517c4750a1ad81453`으로 병합했습니다.
- [novel-ai PR #2](https://github.com/noory-code/novel-ai/pull/2): CI 7개 통과 후 `eb42c708f44ee2c7d5f4b25460add297551e8a85`로 병합했습니다.

각 릴리스는 위 병합 커밋을 가리킵니다. 두 저장소의 PR 검사 총 37개가 통과했습니다.
검사에는 Linux·macOS·Windows가 포함됩니다. 병합 후 새로 시작된 main CI의 완료를 주장하는 수치는 아닙니다.

## CI에서 발견하고 고친 문제

첫 CI 실행은 실패했습니다. 실패 로그를 지우지 않고 보존했습니다.

- Stage는 Windows가 대소문자를 무시하며 경로를 정렬해 다른 운영체제와 순서가 달랐습니다. 경로의 각 부분을 문자열로 비교하도록 고쳤습니다. 새 Windows 경로 테스트는 수정 전 실패하고 수정 후 통과했습니다.
- Stage의 audit 테스트는 중복 ID를 가진 파일 중 먼저 읽힌 파일을 골랐습니다. 먼저 정렬하도록 고쳤습니다. 이제 의도한 카드가 선택되므로 잘못 붙었던 INDEX 오류 세 개를 기대 목록에서 뺐습니다.
- Avatar의 동시 읽기 테스트는 준비 과정에서 연 SQLite 연결을 닫지 않았습니다. Windows가 임시 DB를 지우지 못했습니다. 트랜잭션을 끝낸 뒤 연결도 닫도록 고쳤습니다.

수정 후 로컬에서 Stage hooks 377개, scripts 655개, Avatar 24개, plugin 계약 7개가 통과했습니다.
Claude가 diff와 주변 코드를 읽고 결함을 찾지 못했다고 보고했습니다. 리뷰 세션은 명령 권한 때문에 테스트를 직접 실행하지 못했습니다. 감독 세션이 위 검사를 실행했습니다.

두 번째 CI는 Windows hooks를 통과한 뒤 scripts에서 실패 54개와 오류 18개를 냈습니다.
여러 줄 Python 테스트 명령을 Windows 셸이 나누어 실행했습니다. 경로 구분자와 짧은 경로 이름도 문자열 비교를 깨뜨렸습니다.
또한 레코드를 닫고 다시 열 때 CRLF를 LF로 바꿨고, 출력 파이프가 Unicode 안내 문자를 처리하지 못했습니다.
원인을 고친 뒤 회귀 테스트 네 개가 RED→GREEN으로 바뀌었습니다. scripts 전체 659개도 통과했습니다. Claude가 이 수정도 독립적으로 검토했습니다.

세 번째 CI에서는 Windows 경로를 문자열로 비교하던 테스트 두 개가 남았습니다.
두 곳 모두 경로를 정규화해 비교하도록 고쳤습니다. 관련 로컬 테스트 34개가 통과했고 Claude가 수정한 부분을 검토했습니다.
Stage 0.63.3으로 실행한 네 번째 CI는 30개가 모두 통과했습니다.

Distill은 테스트 379개, mypy, Ruff 검사와 형식 검사, 저장소 검사, PR CI 작업 일곱 개를 통과했습니다.

## 배포 범위와 보존한 자료

기존 작업 폴더에는 검토한 소스와 관련 없는 변경이 함께 있었습니다. 원격 main에서 별도 배포 브랜치를 만들어 제품 커밋만 적용했습니다.

- noory-ai: `/Users/woogis/.codex/worktrees/criteria-release/noory-ai`
- novel-ai: `/Users/woogis/Workspace/repo/novel-ai-stage-worktrees/criteria-release`

이 경로는 처음 구현한 작업 폴더와 다릅니다. 원래의 소스 커밋과 시험 경로는 보존했습니다. 작업 카드의 scope를 넓혀 이 차이를 감추지 않았습니다.

원본 소스 커밋 기록은 [source-commits.json](evidence/2026-10-07-source-commits.json)에 있습니다. 그 파일의 미푸시·미병합 표시는 기록 당시의 사실이므로 고치지 않습니다.
이번 배포의 PR, CI, 실행 기록은 [배포 증거 폴더](evidence/2026-10-07-release/)에 추가합니다.

연구에서만 사용한 Avatar 명령 묶음은 제품에 포함하지 않았습니다. 개인 기준 DB와 사용자 대화는 배포 파일에 포함하지 않았습니다.

## 새 세션에서 불러오기

두 저장소에서 병합한 main을 새로 받아 시험했습니다. 원격 파일, 시험용 복사본과 Codex 설치 캐시의 SHA-256을 대조했습니다.
Claude와 Codex에서 스킬 세 개를 불러오고 같은 플러그인 경로의 manifest에서 Stage 0.63.3, Avatar 0.1.2, Distill 1.10.0을 읽었습니다.
Claude의 Skill·Read 호출과 Codex가 설치 캐시의 스킬·manifest를 읽은 명령 및 출력을 확인했습니다.
main을 한 번 더 받아 Stage 파일 378개, Avatar 파일 14개, Distill 파일 122개가 시험한 파일과 모두 같음을 확인했습니다.
최종 실행 기록은 [published/](evidence/2026-10-07-release/published/), 파일 대조 결과는 [merged-source-check.json](evidence/2026-10-07-release/merged-source-check.json)에 있습니다.
빈 임시 프로젝트에서 훅을 끄고 스킬과 manifest를 읽었습니다. MCP 도구는 호출하지 않았습니다. 이 검사는 플러그인과 스킬이 불러와지는지 확인하며, 개인 기록을 만들지 않습니다.

Codex의 별도 시험용 marketplace는 기존 설치 캐시와 이름을 달리합니다. [공식 플러그인 문서](https://developers.openai.com/plugins/build/plugins)의 로컬 marketplace 설정을 따릅니다.
첫 Codex 호출은 CLI 설정 키를 잘못 넘겨 실패했습니다. 키를 바로잡은 다음에는 설치가 필요하다는 오류를 확인했습니다.
공식 CLI로 시험용 플러그인 세 개를 설치한 뒤 정상으로 불러왔습니다. 시험이 끝나면 그 세 항목만 삭제했습니다.
최종 시험에서도 설정 파일의 시험 전후 SHA-256이 같았습니다. 실패한 호출과 정리 결과도 증거 폴더에 남겼습니다.
기존 세션의 플러그인을 업데이트한 것은 아닙니다. 사용 환경에서는 플러그인을 업데이트하고 새 세션을 열어야 새 버전을 사용합니다.

## 원칙과 완료 범위

SSOT: 버전은 배포 커밋의 manifest와 변경 기록으로 확인합니다.
Honesty: CI 실패, 리뷰가 직접 실행하지 못한 검사, 아직 확인하지 않은 단계도 기록합니다.
Completion: 병합만으로 끝내지 않고 새 세션에서 실제로 불러온 경로와 버전을 확인합니다.

요청한 푸시·병합·릴리스 게시와 새 버전 불러오기를 마쳤습니다.
`python3 .stage/research/llm-work/integration/verify_release_evidence.py`로 저장한 배포 증거를 다시 검사할 수 있습니다.
배포 작업 W-00000278과 CI 수정 작업 W-00000279는 close_work.py의 검사를 통과해 닫았습니다.
마지막 Stage 감사에서 오류는 0개였습니다. 경고 32개는 과거 보관 카드의 빈 완료 조건이며 이번 배포 전에도 있었습니다.
제품을 실제 업무에 적용했을 때의 비용 절감 효과는 이 배포 검사로 측정하지 않았습니다.

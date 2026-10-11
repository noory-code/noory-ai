# 개발 중인 플러그인을 두 CLI에서 시험하는 방법

날짜: 2026-10-05. 작업: W-00000277.

이번 기록은 플러그인을 찾고 검사하는 경로만 확인합니다.
Avatar는 아직 구현하지 않았습니다. 세 플러그인의 연결 시험 결과는 아닙니다.

## Codex에서 관찰한 결과

설치된 Codex CLI는 0.160.0입니다.
다음 명령은 이번 실행에서만 marketplace 경로를 바꿉니다.

```text
codex -c 'marketplaces.noory-ai={source_type="local",source="/Users/woogis/Workspace/repo/noory-ai"}' plugin marketplace list --json
```

결과에서 `noory-ai`의 root가 현재 저장소 경로로 나왔습니다.
이어 같은 설정으로 `plugin list --available --json`을 실행했습니다.
Stage의 source는 현재 저장소의 `stage/`였고, version은 `0.62.0`이었습니다.
이는 플러그인을 찾았다는 증거입니다. AI가 스킬을 읽고 실행했다는 증거는 아닙니다.

실제 연결 시험에서는 임시 프로젝트와 시험할 체크아웃 경로를 지정합니다.
새 Avatar가 목록에 나오고 해당 스킬을 실제로 호출하는지 각각 확인해야 합니다.

## Claude에서 관찰한 결과

설치된 Claude CLI는 2.1.289입니다.
현재 Stage에 다음 검사를 실행했습니다.

```text
claude plugin validate ./stage
```

종료 코드는 0이었고 검사를 통과했습니다. 경고는 1개였습니다.
플러그인 루트의 `CLAUDE.md`는 프로젝트 지침으로 자동 주입되지 않는다는 내용입니다.
따라서 Avatar의 사용 절차는 배포할 스킬 안에 넣고, 실제 호출로 확인해야 합니다.

Claude의 `--plugin-dir`은 지정한 폴더를 해당 세션에서 불러옵니다.
첫 연결 시험에서도 이 옵션으로 개발 중인 플러그인을 불러옵니다.

## 공식 문서

- [Codex plugin 구성](https://developers.openai.com/plugins/build/plugins): 기존 `.codex-plugin/plugin.json`을 지원합니다.
- [Claude plugin 개발](https://code.claude.com/docs/en/plugins/create): `--plugin-dir`과 manifest 검사를 설명합니다.

## 아직 확인하지 않은 것

- 새 Avatar의 두 manifest와 marketplace 등록
- 실제 Claude와 Codex의 Avatar 스킬 호출
- 같은 기준을 조회하고 변경한 뒤 다음 세션에서 적용하는 과정
- 기준 조회가 실패했을 때 예전 기록을 최신 기준으로 쓰지 않는지

전역 설정이나 기존 개인 데이터는 이 확인 과정에서 바꾸지 않았습니다.

## 2026-10-06 후속 확인

위 내용은 구현 전 관찰입니다. 이후 Avatar를 구현하고 두 manifest와 marketplace 구성을 검사했습니다.
Claude의 새 세션에서 `avatar:avatar` 스킬을 실제로 호출했고 성공 응답을 받았습니다.
Codex는 개발 중 Avatar 0.1.0을 사용 가능한 목록에 표시했습니다. Codex 스킬 호출과 실제 양방향 인계는 남았습니다.
후속 원본과 한계는 [구현·검증 기록](implementation-status.md)에 모았습니다.

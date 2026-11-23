---
id: W-00000407
title: Python 3.14 만 있는 기기에서 rag 서버가 설치되게 한다
kind: fix
venue: claude
environment: cloud
milestone:
autonomous: false
acceptance: []
status: active
verification: pending
retrospective: pending
retrospective_ref:
promotion: pending
review: pending
scope: rag/server/pyproject.toml,rag/server/uv.lock,rag/CHANGELOG.md
promotes:
decision_refs:
---

# W-00000407 Python 3.14 만 있는 기기에서 rag 서버가 설치되게 한다

## Purpose

rag 서버를 설치하는 사람이 Python 3.14 에서 kuzu 빌드 오류를 만나지 않는다

## Actions


## User value

2026-11-23 에 한국어 Windows 11(cp949) 세션이 `1d462c7f` 에서 본 것이다. 이 기기에 깔린 x86_64 Python 은
3.14.10 하나였다.

- `rag/server` 에서 `uv run pytest` 를 실행하면 uv 가 Python 3.14 를 고르고 `kuzu==0.11.3` 을 소스에서 빌드하려다
  멈춘다. 오류는 `setuptools.build_meta.get_requires_for_build_wheel` 안의 `_get_kuzu_version` 에서 나는
  `UnicodeDecodeError: 'cp949' codec can't decode byte 0xe2` 이다. kuzu 의 빌드 스크립트가 인코딩을 지정하지 않고
  파일을 읽는다.
- `rag/server/pyproject.toml` 은 `requires-python = ">=3.11"` 이라 3.14 를 허용한다. `rag/server/uv.lock` 에 있는
  kuzu 0.11.3 의 Windows wheel 은 `cp311`, `cp312`, `cp313` 의 `win_amd64` 세 개뿐이다.
- x86_64 Python 3.13.18 을 따로 받아 `UV_PYTHON` 으로 지정하면 kuzu wheel 을 받아 설치한다.
  `uv run --extra dev pytest -q -m "not slow"` 는 121개가 통과했다(13개는 `slow` 라서 고르지 않았다).

확인하지 않은 것:

- 영어 Windows 나 macOS, Linux 의 Python 3.14 에서 kuzu 가 소스에서 빌드되는지는 확인하지 않았다.
- kuzu 에 3.14 wheel 이 있는 새 버전이 있는지는 확인하지 않았다.

## Scope

### Included

- 고치는 방법을 정한다. 후보는 `requires-python` 을 3.13 까지로 좁히는 것, `rag/server/.python-version` 을 두는
  것, kuzu 를 3.14 wheel 이 있는 버전으로 올리는 것이다.
- `rag/server/uv.lock` 을 다시 만든다.

### Excluded

- 이 Windows 기기에서 uv 가 관리하는 Python 3.11 과 3.13 의 링크가 깨진 것은 저장소의 문제가 아니라서 다루지
  않는다.

## Risks

- `requires-python` 을 좁히면 Python 3.14 만 있는 기기에서 uv 가 3.13 을 내려받는다. uv 가 Python 을 내려받지
  못하게 설정한 기기에서는 설치가 거절된다.

## Success criteria

- Python 3.14 만 설치된 한국어 Windows 에서 rag/server 의 uv run --extra dev pytest -m "not slow" 가 kuzu 를 소스에서 빌드하지 않고 통과한다
- 맥북에서 rag/server 의 같은 명령이 전과 같이 통과한다

## Next action

작업 세션 session_018VXR6NvDBdQga8T4NuJ3u9 의 보고를 받아 검사를 다시 돌리고 닫기 리뷰로 넘긴다.

Windows 기기가 없어도 고칠 수 있다. 맥북이나 클라우드 세션이 카드를 시작해 고치고, 첫째 성공 기준은 Windows
세션이 확인한다(`.stage/operations/verification.md` 의 "Windows 동작 확인").

## Related truth

## Sessions

- session_018VXR6NvDBdQga8T4NuJ3u9 — work — 2026-11-23 — opened from the index: not reported yet

## Progress

- 2026-11-23 지휘 세션 session_018VXR6RJwybKUJRATYqvEuM 이 카드를 시작했다. 성공 기준은 Python 3.14 만 있는 한국어 Windows 에서만 볼 수 있다. 사용자가 기계 확인을 기다리지 말고 진행하라고 했으므로("맥 윈도우즈 상관하지 말고 하세요") 고침을 만들어 병합하고, 그 확인은 O-00000062 에 올린다. 클라우드에서 볼 수 있는 것(잠금 파일에 3.14 용 wheel 이 있는지, Linux 에서 시험이 도는지)까지 본다.

## Verification

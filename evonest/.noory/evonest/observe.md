```json
{
  "perspective": "Observability Advocate",
  "test_results": {
    "total": 411,
    "passed": 411,
    "failed": 0,
    "slow_tests": []
  },
  "build_status": "clean_with_lint_warnings",
  "improvements": [
    {
      "id": "improve-001",
      "priority": "high",
      "category": "observability",
      "title": "MCP 도구 호출 시 에러 처리에 진단 컨텍스트 추가",
      "description": "tools/improve.py:19-24에서 OSError를 조용히 삼키고 있습니다. 로그 파일 읽기 실패 시 사용자가 문제를 진단할 수 없도록 합니다. 에러 발생 시 파일 경로, 권한 정보, 실패 이유를 로깅하여 프로덕션 문제 추적을 가능하게 해야 합니다.",
      "files": ["src/evonest/tools/improve.py"],
      "estimated_complexity": "low"
    },
    {
      "id": "improve-002",
      "priority": "high",
      "category": "observability",
      "title": "improve 도구의 비동기 subprocess 실패 시 진단 정보 부족",
      "description": "tools/improve.py:42-47에서 subprocess가 stdout/stderr을 DEVNULL로 리디렉션하여 실패 시 아무런 진단 정보가 남지 않습니다. 프로세스가 실패해도 사용자는 왜 실패했는지 알 수 없습니다. stderr을 캡처하고 exit code가 0이 아닐 때 로깅하여 실패 원인 추적을 가능하게 해야 합니다.",
      "files": ["src/evonest/tools/improve.py"],
      "estimated_complexity": "medium"
    },
    {
      "id": "improve-003",
      "priority": "medium",
      "category": "observability",
      "title": "전역 예외 핸들러에 실행 컨텍스트 추가",
      "description": "cli.py:207-209와 _runner.py:135-137에서 Exception을 포괄적으로 잡아 단순히 str(exc)만 출력합니다. 스택 트레이스, 실행 중이던 명령, 프로젝트 경로, 설정 값 등의 컨텍스트가 없어 production 이슈 재현이 어렵습니다. 에러 발생 시 충분한 진단 정보를 로깅해야 합니다.",
      "files": ["src/evonest/cli.py", "src/evonest/_runner.py"],
      "estimated_complexity": "medium"
    },
    {
      "id": "improve-004",
      "priority": "medium",
      "category": "observability",
      "title": "ProcessManager 재시도 로직의 추적성 개선",
      "description": "process_manager.py:169-191의 rate limit 재시도 로직은 exponential backoff를 수행하지만, 재시도 시도 간 상태 변화(예: 네트워크 복구, API quota 회복)를 추적할 방법이 없습니다. 각 재시도 시도에 unique ID를 부여하고, 재시도 체인을 연결하는 로그를 추가하여 긴 재시도 시퀀스 디버깅을 용이하게 해야 합니다.",
      "files": ["src/evonest/core/process_manager.py"],
      "estimated_complexity": "medium"
    },
    {
      "id": "improve-005",
      "priority": "medium",
      "category": "observability",
      "title": "ClaudeRunner의 max turns 도달 시 부분 출력 손실",
      "description": "claude_runner.py:82-94에서 max turns 도달 시 output을 빈 문자열로 설정하여 부분 결과를 버립니다. 디버깅 시 어디까지 진행되었는지 알 수 없습니다. 부분 출력을 보존하고 메타데이터에 'truncated_reason: max_turns'를 추가하여 진단 가능성을 높여야 합니다.",
      "files": ["src/evonest/core/claude_runner.py"],
      "estimated_complexity": "low"
    },
    {
      "id": "improve-006",
      "priority": "low",
      "category": "observability",
      "title": "로깅 레벨 설정 및 구조화된 로그 포맷 부재",
      "description": "프로젝트 전체에서 logger를 사용하지만(51회 호출), 로깅 레벨 설정, 포맷터, 핸들러 구성이 명시적으로 보이지 않습니다. 사용자가 디버그 레벨 로그를 활성화하거나 JSON 형식으로 로그를 출력할 방법이 없습니다. 설정 가능한 로깅 설정(레벨, 포맷, 출력 대상)을 config.json에 추가하여 운영 환경 진단을 용이하게 해야 합니다.",
      "files": ["src/evonest/core/config.py", "src/evonest/__init__.py"],
      "estimated_complexity": "medium"
    },
    {
      "id": "improve-007",
      "priority": "low",
      "category": "test-coverage",
      "title": "에러 메시지 품질에 대한 테스트 커버리지 추가",
      "description": "tests/test_claude_runner.py, tests/test_orchestrator.py, tests/test_phases.py에서 stderr를 테스트하지만, 에러 메시지가 실제로 actionable한지(파일 경로, 명령어, 해결 방법 포함)는 검증하지 않습니다. 에러 메시지가 사용자 친화적이고 디버깅에 충분한 정보를 제공하는지 테스트하는 케이스를 추가해야 합니다.",
      "files": ["tests/test_claude_runner.py", "tests/test_orchestrator.py", "tests/test_phases.py"],
      "estimated_complexity": "medium"
    },
    {
      "id": "improve-008",
      "priority": "low",
      "category": "code-quality",
      "title": "Ruff 린팅 경고 수정 (E501: 100자 제한 초과)",
      "description": "src/evonest/core/phases.py:375, 388, src/evonest/core/process_manager.py:54, tests/test_phases.py:596, 607, tests/test_server.py:247에서 라인 길이가 100자를 초과합니다. 일관된 코드 포맷팅을 위해 ruff format으로 자동 수정하거나 라인을 분할해야 합니다.",
      "files": ["src/evonest/core/phases.py", "src/evonest/core/process_manager.py", "tests/test_phases.py", "tests/test_server.py"],
      "estimated_complexity": "low"
    }
  ],
  "observations": [
    "411개 테스트 모두 통과 (51.91초)",
    "타입 검사 통과 (mypy strict 모드)",
    "Ruff 린팅 경고 6건 발견 (E501: 라인 길이 초과)",
    "프로젝트에 TODO/FIXME/HACK 주석 없음 (코드 품질 양호)",
    "로깅 인프라는 존재하나(51회 호출), 구성 가능한 로깅 설정 부재",
    "여러 곳에서 예외를 조용히 처리하여(OSError pass, Exception을 str만 출력) 진단 정보 손실",
    "subprocess 호출 시 stderr을 DEVNULL로 버리는 패턴 발견 - 실패 시 진단 불가",
    "에러 핸들링은 존재하나 에러 메시지에 충분한 컨텍스트(파일 경로, 상태, 재시도 정보) 부족",
    "ProcessManager의 rate limit 재시도는 잘 구현되었으나 재시도 체인 추적성 부족"
  ]
}
```
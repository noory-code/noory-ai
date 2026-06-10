async def로 되어 있어서 grep 패턴이 매치되지 않았습니다. 정확한 개수는:
- test_process_manager.py: 4개 (새 파일)
- test_claude_runner.py: 2개
- test_orchestrator.py: 1개
- test_phases.py: 4개

**총 11개의 새로운 테스트**를 추가했습니다.

이제 최종 결과를 JSON으로 반환하겠습니다.

```json
{
  "status": "completed",
  "files_modified": [
    "tests/test_claude_runner.py",
    "tests/test_orchestrator.py",
    "tests/test_phases.py"
  ],
  "files_created": [
    "tests/test_process_manager.py"
  ],
  "summary": "에러 메시지 품질 검증을 위한 11개 테스트 추가 완료",
  "build_check": "passed",
  "notes": [
    "test_process_manager.py: 4개 테스트 (명령어 이름, timeout 정보, stderr 보존, rate limit 메시지 검증)",
    "test_claude_runner.py: 2개 테스트 (FileNotFoundError/TimeoutExpired 시 actionable 정보 포함 검증)",
    "test_orchestrator.py: 1개 테스트 (Observe 실패 시 stderr의 actionable 정보 검증)",
    "test_phases.py: 4개 테스트 (observe/plan/verify 단계별 에러 메시지에 파일 경로/명령어/해결 방법 포함 검증)",
    "전체 422개 테스트 통과, 린팅 통과, 타입 체크 통과"
  ]
}
```
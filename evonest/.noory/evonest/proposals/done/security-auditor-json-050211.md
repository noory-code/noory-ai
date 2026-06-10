# 제안: JSON 파싱 오류 처리에서 빈 딕셔너리 반환으로 인한 데이터 손실 은폐

**우선순위**: medium  
**작성 페르소나**: security-auditor  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/core/repositories.py:37-45의 _read_json() 함수는 JSONDecodeError 발생 시 경고 로그만 출력하고 빈 딕셔너리를 반환합니다. 이는 손상된 설정 파일이나 데이터 파일을 조용히 무시하여 보안 설정이나 중요 메타데이터가 유실될 수 있습니다. 특히 config.json, progress.json 같은 중요 파일의 손상을 감지하지 못하면 시스템이 안전하지 않은 기본값으로 동작할 수 있습니다. 중요 파일(config, progress)에 대해서는 예외를 발생시키거나 복구 절차를 수행하도록 개선 필요합니다.

## 관련 파일

- src/evonest/core/repositories.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
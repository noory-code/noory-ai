# 제안: verify.build/test 명령어에서 shell=True 사용으로 인한 쉘 인젝션 위험

**우선순위**: high  
**작성 페르소나**: security-auditor  
**사이클**: 0  
**상태**: 검토 대기

## 설명

src/evonest/core/phases.py:608, 633에서 config.verify.build와 config.verify.test 값을 shell=True 옵션으로 subprocess.run()에 전달합니다. 이 설정 값들은 사용자가 .evonest/config.json에서 제어할 수 있으므로, 악의적인 명령어 주입이 가능합니다. 예를 들어 config.json에 "verify": {"build": "make build && rm -rf /"} 같은 값을 설정하면 위험한 명령이 실행됩니다. subprocess.run()을 배열 형식 인자로 변경하거나 shlex.split()을 사용하여 안전하게 파싱해야 합니다.

## 관련 파일

- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
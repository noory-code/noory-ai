# 제안: 사용자 경험 개선을 위한 제안 워크플로우 단순화

**우선순위**: high  
**작성 페르소나**: product-strategist  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 analyze → proposals → improve 3단계 플로우는 사용자가 제안을 검토하고 실행하는 과정이 단절되어 있습니다. Product Direction에서 '인간 중심'을 강조하지만, 실제로는 제안 리스트 조회와 실행이 별도 명령어로 분리되어 있어 friction이 높습니다. 제안: proposals 조회 시 인터랙티브 선택 UI 제공 (번호 입력으로 즉시 실행 가능), 또는 analyze 완료 후 자동으로 상위 3개 제안을 보여주고 선택 프롬프트 제공. Mission의 '자율적이면서도 인간 주도' 가치를 실현하려면 제안 검토-실행 간 마찰을 줄여야 합니다.

## 관련 파일

- src/evonest/tools/proposals.py
- src/evonest/tools/improve.py
- src/evonest/cli.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
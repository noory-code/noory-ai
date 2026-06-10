# 제안: config.json의 3단계 level 시스템을 폐지하고 단순 플래그로 통합

**우선순위**: low  
**작성 페르소나**: contrarian  
**사이클**: 0  
**상태**: 검토 대기

## 설명

quick/standard/deep 레벨이 각각 model, observe_mode, max_turns를 bundle로 변경하는데, 실제로는 사용자가 개별 설정을 원할 가능성이 높음. 현재 설계는 'Netflix 요금제' 같은 추상화인데, 이는 CLI 도구에는 과도함. 차라리 --model, --max-turns-observe, --observe-mode를 독립 플래그로 제공하고, 프리셋은 문서에만 남기는 것이 더 직관적임. 코드 복잡도도 줄어듦.

## 관련 파일

- src/evonest/core/config.py
- src/evonest/cli.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
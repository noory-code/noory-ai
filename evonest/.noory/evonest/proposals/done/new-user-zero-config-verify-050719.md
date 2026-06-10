# 제안: 디폴트 동작 불명확 — zero-config 약속에도 불구하고 verify 설정 없으면 검증 건너뜀

**우선순위**: medium  
**작성 페르소나**: new-user  
**사이클**: 0  
**상태**: 검토 대기

## 설명

README.md 96-107줄에서 verify 명령어가 null이면 '자동 revert를 할 수 없다'고 설명하지만, Quick Start 섹션에서는 이를 언급하지 않는다. 초보자는 evonest_init() 후 바로 evolve를 실행했을 때 verify가 스킵되는 이유를 모를 것이다. 'Zero-config actually work'를 표방한다면, 프로젝트 타입을 자동 감지해서 디폴트 verify 명령을 제안하거나, 최소한 경고 메시지를 출력해야 한다.

## 관련 파일

- src/evonest/core/initializer.py
- src/evonest/core/phases.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
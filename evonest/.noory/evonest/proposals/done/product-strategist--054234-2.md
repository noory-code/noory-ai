# 제안: 페르소나 커뮤니티 에코시스템을 위한 기반 구축

**우선순위**: high  
**작성 페르소나**: product-strategist  
**사이클**: 0  
**상태**: 검토 대기

## 설명

ROADMAP.md Vision에서 '페르소나 커뮤니티 공유'를 명시했지만, 현재 동적 페르소나(.evonest/dynamic-personas.json)는 로컬 생성만 가능하고 공유 메커니즘이 없습니다. Product Direction의 핵심 비전 중 하나인 커뮤니티 생태계를 실현하려면 선행 작업이 필요합니다. 제안: (1) 페르소나 포맷 표준화 (메타데이터: author, version, tags), (2) 페르소나 export/import CLI 명령 추가 (evonest personas export <id> → JSON), (3) 페르소나 검증 스키마 구현 (안전성 체크). 이는 향후 noory-code/evonest-personas 저장소 런칭을 위한 기술 기반이 됩니다.

## 관련 파일

- src/evonest/core/mutations.py
- src/evonest/tools/personas.py
- src/evonest/cli.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
# 제안: 설정 파일 필드 발견 가능성 향상

**우선순위**: medium  
**작성 페르소나**: ux-critic  
**사이클**: 0  
**상태**: 검토 대기

## 설명

config.json의 필드들이 문서에만 존재하고, 템플릿에는 주석 예제가 부족함. 사용자가 '어떤 필드를 설정할 수 있는지' 찾으려면 docs/configuration.md를 읽어야 함. JSONC 지원을 활용해 templates/config.json에 주석으로 모든 가능한 필드와 기본값, 설명을 포함하면 IDE에서 바로 확인 가능. 점진적 노출(progressive disclosure) 원칙에 부합.

## 관련 파일

- src/evonest/templates/config.json
- docs/configuration.md

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
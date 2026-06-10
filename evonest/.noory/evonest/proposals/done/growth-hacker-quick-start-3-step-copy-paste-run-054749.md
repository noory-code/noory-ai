# 제안: Quick Start 섹션을 3-step 'Copy-Paste & Run' 형식으로 개편

**우선순위**: high  
**작성 페르소나**: growth-hacker  
**사이클**: 0  
**상태**: 검토 대기

## 설명

현재 Quick Start는 5단계로 구성되어 있고 `.evonest/identity.md` 수동 편집이 필수입니다. 이는 첫 사용자에게 friction을 유발합니다. 대신 1) 플러그인 설치 2) `/evonest:analyze .` 실행 3) 제안 확인 — 3단계로 압축하고, identity.md 편집은 선택적 최적화 단계로 분리하면 초기 진입 장벽이 현저히 낮아집니다. 기본 템플릿 identity.md만으로도 동작 가능하도록 observe 프롬프트를 개선해야 합니다.

## 관련 파일

- README.md
- src/evonest/prompts/observe.md

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
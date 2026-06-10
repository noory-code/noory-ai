# 제안: Viral loop 설계 — 프로젝트별 'Evolved with Evonest' 배지 자동 생성

**우선순위**: medium  
**작성 페르소나**: growth-hacker  
**사이클**: 0  
**상태**: 검토 대기

## 설명

evonest가 commit/PR을 생성할 때 자동으로 README.md 하단에 '[![Evolved with Evonest](badge-url)](evonest-repo)' 배지를 추가하는 옵션을 제공하면 word-of-mouth 전파가 가능합니다. 사용자가 활성화할 수 있도록 `.evonest/config.json`에 `badge_enabled: true` 옵션을 추가하고, execute 단계에서 README 패치를 자동으로 제안합니다. 이는 low-friction viral mechanic이며 GitHub ecosystem에서 효과적으로 작동합니다.

## 관련 파일

- src/evonest/core/phases.py
- src/evonest/core/config.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
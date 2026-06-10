# 제안: 파일 경로 인젝션 테스트 — 'proposals/', 'stimuli/' 디렉토리 traversal 공격 차단 검증

**우선순위**: high  
**작성 페르소나**: growth-hacker  
**사이클**: 0  
**상태**: 검토 대기

## 설명

repositories.py의 StimuliRepository.add(), ProposalRepository.add()는 사용자 입력(stimulus content, proposal title)을 파일명으로 변환합니다. _slugify()가 있지만 '..' 또는 '/' 문자를 완전히 제거하는지 테스트가 필요합니다. 악의적 title='../../../etc/passwd' 입력 시 directory traversal이 발생하는지 확인하고, Path.resolve()를 사용해 .evonest/ 외부로 쓰기를 차단하는 로직을 추가해야 합니다. 현재 test_proposal_add_filename_pattern은 정상 케이스만 다루고 있습니다.

## 관련 파일

- tests/test_repositories.py
- src/evonest/core/repositories.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
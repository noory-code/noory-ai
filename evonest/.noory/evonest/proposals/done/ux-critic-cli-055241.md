# 제안: CLI 플래그 명명 일관성 개선

**우선순위**: high  
**작성 페르소나**: ux-critic  
**사이클**: 0  
**상태**: 검토 대기

## 설명

analyze와 run(evolve) 명령어가 동일한 기능을 다른 이름으로 제공: --observe-mode(analyze) vs --observe-mode(run), --all-personas(both). 하지만 run에는 --cycles가 있고 analyze에는 --level이 있음. 사용자가 두 명령어 간 차이를 이해하기 어려움. 'level'과 'observe-mode'의 관계도 불명확 — level은 model+observe_mode+max_turns를 한번에 설정하는데, observe-mode 플래그가 별도로 존재하면 혼란스러움.

## 관련 파일

- src/evonest/cli.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
# 제안: 적응적 학습 효과의 사용자 가시성 개선

**우선순위**: medium  
**작성 페르소나**: product-strategist  
**사이클**: 0  
**상태**: 검토 대기

## 설명

Core Values의 핵심인 '적응적 지능(성공한 페르소나가 더 자주 실행)'은 강력한 차별화 포인트이지만, 사용자가 이 효과를 체감하기 어렵습니다. evonest_progress에서 weight를 보여주지만, '왜 이 페르소나가 성공했는지' 내러티브가 없습니다. 제안: (1) status/progress 명령에 '학습 스토리' 섹션 추가 (예: 'security-auditor가 최근 3회 연속 성공 → weight 1.0 → 2.1로 상승', '이유: CVE 관련 제안 모두 merge됨'), (2) 그래프 시각화 옵션 (페르소나 weight 변화 추이를 ASCII chart로 표시). 이는 사용자가 '학습하는 AI'를 실감하게 하여 제품 가치를 극대화합니다.

## 관련 파일

- src/evonest/tools/status.py
- src/evonest/tools/progress.py
- src/evonest/core/history.py

---

*이것은 설계 수준의 제안입니다. 코드는 변경되지 않았습니다.*  
*팀에서 검토, 거부 또는 실행하세요.*
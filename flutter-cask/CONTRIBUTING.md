# Contributing to Flutter Cask

Flutter Cask에 기여해주셔서 감사합니다! 이 문서는 새로운 스킬을 추가하거나 기존 스킬을 개선하는 방법을 설명합니다.

## 새 스킬 추가하기

### 1. 스킬 생성 스크립트 사용

프로젝트 루트에서 `new-skill.sh` 스크립트를 사용하면 새로운 스킬을 빠르게 생성할 수 있습니다.

```bash
./new-skill.sh <skill-name> <package-name>
```

**예시:**
```bash
./new-skill.sh flutter-dio dio
```

이 명령은 `skills/flutter-dio/` 디렉토리와 기본 `SKILL.md` 파일을 생성합니다.

### 2. 스킬 구조

모든 스킬은 다음 구조를 따라야 합니다:

```
skills/flutter-example/
├── SKILL.md              # 필수: 스킬 메타데이터 및 가이드
└── references/           # 선택: 상세 레퍼런스 문서
    ├── advanced.md
    └── examples.md
```

### 3. SKILL.md 필수 섹션

`SKILL.md` 파일은 다음 섹션을 포함해야 합니다:

#### Frontmatter (필수)
```yaml
---
name: flutter-example
description: Example package for Flutter development
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [example, sample, demo]
---
```

**필드 설명:**
- `name`: 스킬 이름 (kebab-case)
- `description`: 한 줄 설명 (50자 이내)
- `version`: 스킬 버전 (현재 "1.1.0" 사용)
- `category`: 카테고리 (현재 모든 스킬은 "flutter-lib")
- `type`: 타입 (현재 "unit" 사용)
- `style`: 스타일 (현재 "guide" 사용)
- `triggers`: 스킬 활성화 키워드 배열

#### Title (필수)
```markdown
# Flutter Example

간단한 설명 한 줄
```

#### Installation (필수)
```markdown
## Installation

\`\`\`bash
flutter pub add example_package
\`\`\`
```

패키지가 dev dependency인 경우:
```bash
flutter pub add dev:example_package
```

build_runner가 필요한 경우 Code Generation 섹션 추가:
```markdown
## Code Generation

\`\`\`bash
# 일회성 빌드
dart run build_runner build --delete-conflicting-outputs

# 감시 모드
dart run build_runner watch -d
\`\`\`
```

#### Quick Reference (필수)
```markdown
## Quick Reference

\`\`\`dart
import 'package:example_package/example_package.dart';

// 기본 사용 예제
void example() {
  // 코드 예제
}
\`\`\`
```

**가이드라인:**
- 가장 일반적인 사용 사례 3-5개 포함
- 주석은 핵심 개념 설명에만 사용
- 실제 동작하는 코드 제공
- Flutter 및 Dart 컨벤션 준수

#### Common Issues (필수)
```markdown
## Common Issues

| Issue | Fix |
|------|------|
| 문제 설명 | 해결 방법 |
| 또 다른 문제 | 해결 방법 |
```

실제 사용자가 겪는 일반적인 문제와 해결 방법을 포함하세요.

#### References (선택)
```markdown
## References

| File | Description |
|------|------|
| [advanced.md](references/advanced.md) | 고급 사용법 및 패턴 |
| [examples.md](references/examples.md) | 추가 코드 예제 |
```

`references/` 디렉토리가 있는 경우에만 이 섹션을 포함하세요.

### 4. References 디렉토리 (선택)

복잡한 패키지의 경우 `references/` 디렉토리에 추가 문서를 작성할 수 있습니다:

```
skills/flutter-example/references/
├── advanced.md          # 고급 사용법
├── patterns.md          # 일반적인 패턴
└── troubleshooting.md   # 문제 해결
```

#### References 디렉토리 사용 기준

`references/` 디렉토리는 다음 기준 중 **2개 이상 해당**하는 경우에만 생성하세요:

1. **주요 사용 사례가 3개 이상**: 패키지가 서로 다른 여러 사용 시나리오를 지원 (예: riverpod의 Provider, StateNotifier, AsyncNotifier)
2. **고급 패턴 필요**: 기본 사용법 외에 복잡한 패턴이나 아키텍처 가이드 필요 (예: go-router의 중첩 라우팅, 리다이렉션)
3. **코드 생성 도구 사용**: build_runner 기반 코드 생성 + 어노테이션 설명 필요 (예: freezed, json_serializable)
4. **플랫폼별 설정 필요**: iOS/Android 네이티브 설정이 복잡함 (예: firebase-messaging, admob)
5. **Quick Reference 섹션이 100줄 초과**: SKILL.md의 코드 예제가 너무 길어져서 가독성 저하

**예시:**
- **references 필요**: riverpod (사용 사례 5+, 고급 패턴), go-router (고급 패턴, 100줄 초과)
- **references 불필요**: package-info (사용 사례 2개, 단순), share (기본 사용법만 존재)

**참고:** 35개 스킬 중 8개만 references 디렉토리를 가지고 있습니다. 대부분의 스킬은 SKILL.md만으로 충분합니다.

## 스킬 작성 모범 사례

### 1. 코드 예제
- 실제 동작하는 코드 작성
- Flutter/Dart 컨벤션 준수
- 명확하고 간결하게 작성
- 불필요한 주석 제거

### 2. 설명
- 간단명료하게 작성
- 전문 용어는 필요시에만 사용
- 한국어로 작성

### 3. 구조
- 템플릿 구조 준수
- 섹션 순서 유지
- 일관된 포맷 사용

### 4. 메타데이터
- triggers에 관련 키워드 포함
- description은 50자 이내로 작성
- version은 "1.1.0" 유지

## 기존 스킬 개선하기

1. 해당 스킬의 `SKILL.md` 파일 수정
2. 코드 예제가 최신 패키지 버전과 호환되는지 확인
3. Common Issues 섹션 업데이트
4. 필요시 references 문서 추가

## 테스트

스킬 추가 또는 수정 후:
1. SKILL.md 파일 문법 확인
2. 코드 예제 동작 확인
3. 링크 및 경로 확인

## 질문이나 제안사항

- GitHub Issues에 질문 남기기
- Pull Request 전에 토론 시작
- 기존 스킬 참고하기

---

## 참고: 기존 스킬 예시

**간단한 스킬 (references 없음):**
- `skills/flutter-connectivity/SKILL.md`
- `skills/flutter-package-info/SKILL.md`

**복잡한 스킬 (references 있음):**
- `skills/flutter-riverpod/` (6개 레퍼런스 문서)
- `skills/flutter-go-router/` (3개 레퍼런스 문서)

궁금한 점이 있다면 기존 스킬을 참고하세요!

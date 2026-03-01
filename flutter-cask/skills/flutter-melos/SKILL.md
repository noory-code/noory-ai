---
name: flutter-melos
description: Melos를 사용한 Flutter 모노레포 관리
metadata:
  version: "1.1.0"
  category: flutter-tool
  type: unit
  style: guide
  triggers: [melos, 모노레포, 멀티 패키지, workspace]
---

# Flutter Melos

Flutter/Dart 모노레포 관리 도구. 패키지 간 의존성, 공유 설정, 일괄 명령 실행.

---

## 설치

```bash
# 전역 설치
dart pub global activate melos

# 프로젝트에 추가
dart pub add melos --dev
```

---

## Quick Reference

### 루트 pubspec.yaml

```yaml
name: my_project
publish_to: none

environment:
  sdk: ^3.6.0

workspace:
  - {project}_entities
  - {project}_core
  - {project}_app
  - {project}_admin

dev_dependencies:
  melos: ^6.0.0

melos:
  scripts:
    # 코드 생성
    generate:
      run: melos exec -c 1 --depends-on build_runner -- dart run build_runner build --delete-conflicting-outputs
      description: Run build_runner in all packages

    # 테스트
    test:
      run: melos exec -- flutter test
      description: Run tests in all packages

    # 포맷
    format:
      run: melos exec -- dart format .
      description: Format all packages

    # 분석
    analyze:
      run: melos exec -- dart analyze
      description: Analyze all packages
```

### 패키지 pubspec.yaml

```yaml
name: {project}_entities
description: Domain entities

environment:
  sdk: ^3.6.0

resolution: workspace  # 필수!

dependencies:
  freezed_annotation: ^2.4.0

dev_dependencies:
  build_runner: ^2.4.0
  freezed: ^2.5.0
```

---

## 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `melos bootstrap` | 의존성 설치 + 패키지 연결 |
| `melos clean` | 모든 패키지 clean |
| `melos exec -- <cmd>` | 모든 패키지에서 명령 실행 |
| `melos run <script>` | 스크립트 실행 |
| `melos list` | 패키지 목록 |

### exec 옵션

```bash
# 순차 실행 (build_runner 등)
melos exec -c 1 -- dart run build_runner build

# 특정 패키지만
melos exec --scope="{project}_entities" -- flutter test

# 의존성 있는 패키지만
melos exec --depends-on="freezed" -- dart run build_runner build
```

---

## 폴더 구조

```
{project}/
├── pubspec.yaml              # 루트 (workspace 정의)
├── melos.yaml                # (선택) 별도 설정 파일
├── {project}_entities/
│   └── pubspec.yaml          # resolution: workspace
├── {project}_core/
│   └── pubspec.yaml
├── {project}_app/
│   └── pubspec.yaml
└── {project}_admin/
    └── pubspec.yaml
```

---

## 규칙

| 항목 | 규칙 |
|------|------|
| **resolution** | 모든 패키지에 `resolution: workspace` 필수 |
| **workspace** | 루트 pubspec.yaml에 모든 패키지 경로 명시 |
| **버전 동기화** | 공유 의존성은 루트에서 관리 |
| **스크립트** | 반복 작업은 melos scripts로 정의 |

---

## 흔한 실수

| ❌ | ✅ |
|---|---|
| `resolution: workspace` 누락 | 모든 패키지에 추가 |
| 루트에서 `flutter pub get` | `melos bootstrap` 사용 |
| 개별 패키지에서 의존성 추가 | 루트 pubspec.yaml에서 관리 |
| `-c 1` 없이 build_runner | `melos exec -c 1` (순차 실행) |

---

## 참고

- [Melos 공식 문서](https://melos.invertase.dev/)
- [Getting Started](https://melos.invertase.dev/getting-started)

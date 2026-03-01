---
name: flutter-fvm
description: FVM을 사용한 Flutter SDK 버전 관리
metadata:
  version: "1.1.0"
  category: flutter-tool
  type: unit
  style: guide
  triggers: [fvm, Flutter 버전, SDK 버전, 버전 관리]
---

# Flutter FVM

프로젝트별 Flutter SDK 버전 관리 도구. 팀 전체가 동일한 버전 사용 보장.

---

## 설치

```bash
# macOS (Homebrew)
brew tap leoafarias/fvm
brew install fvm

# 또는 pub global
dart pub global activate fvm
```

---

## Quick Reference

### 주요 명령어

| 명령어 | 설명 |
|--------|------|
| `fvm install <version>` | SDK 버전 설치 |
| `fvm use <version>` | 프로젝트 버전 설정 |
| `fvm list` | 설치된 버전 목록 |
| `fvm releases` | 사용 가능한 버전 |
| `fvm global <version>` | 전역 기본 버전 설정 |
| `fvm doctor` | 환경 진단 |

### 버전 설치 및 사용

```bash
# 사용 가능한 버전 확인
fvm releases --channel stable

# 특정 버전 설치
fvm install 3.24.0

# 프로젝트에 버전 설정 (.fvmrc 생성)
fvm use 3.24.0

# Flutter 명령 실행 (FVM 경유)
fvm flutter doctor
fvm dart --version
```

---

## .fvmrc 설정

```json
{
  "flutter": "3.24.0",
  "flavors": {}
}
```

**Git에 포함**:
- `.fvmrc` - 커밋 (버전 공유)
- `.fvm/` - gitignore (로컬 심볼릭 링크)

**.gitignore**:
```
.fvm/flutter_sdk
```

---

## VSCode 설정

`.vscode/settings.json`:
```json
{
  "dart.flutterSdkPath": ".fvm/flutter_sdk"
}
```

---

## 규칙

| 항목 | 규칙 |
|------|------|
| **버전 고정** | `.fvmrc`로 프로젝트 버전 명시 |
| **팀 동기화** | `.fvmrc` Git 커밋 필수 |
| **IDE 설정** | `.fvm/flutter_sdk` 경로 사용 |
| **CI/CD** | `fvm install && fvm flutter build` |

---

## 흔한 실수

| ❌ | ✅ |
|---|---|
| `flutter doctor` 직접 실행 | `fvm flutter doctor` |
| `.fvm/` 전체 커밋 | `.fvmrc`만 커밋 |
| VSCode 기본 SDK 사용 | `dart.flutterSdkPath` 설정 |
| 버전 미명시 | `fvm use <version>` 필수 |

---

## 참고

- [FVM 공식 문서](https://fvm.app/)
- [Getting Started](https://fvm.app/documentation/getting-started/overview)

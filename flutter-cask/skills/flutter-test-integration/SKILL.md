---
name: flutter-test-integration
description: integration_test를 사용한 E2E 테스트
metadata:
  version: "1.1.0"
  category: flutter-test
  type: unit
  style: guide
  triggers: [integration test, 통합 테스트, E2E, end-to-end]
---

# Flutter Integration Test

전체 앱의 E2E 플로우를 실제 디바이스/에뮬레이터에서 테스트.

---

## 설치

```bash
flutter pub add 'dev:integration_test:{"sdk":"flutter"}'
```

---

## 폴더 구조

```
lib/
  main.dart
integration_test/        # test/ 와 별도
  app_test.dart
test_driver/             # 웹 테스트 시 필요
  integration_test.dart
```

---

## Quick Reference

### 기본 구조

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('E2E Test', () {
    testWidgets('complete user flow', (tester) async {
      // 앱 실행
      await tester.pumpWidget(const MyApp());

      // 테스트 로직
      expect(find.text('Home'), findsOneWidget);

      await tester.tap(find.byKey(const Key('login_button')));
      await tester.pumpAndSettle();

      expect(find.text('Welcome'), findsOneWidget);
    });
  });
}
```

### Key 사용 (필수)

```dart
// lib/main.dart
ElevatedButton(
  key: const Key('submit_button'),  // 테스트용 Key
  onPressed: _submit,
  child: const Text('Submit'),
)
```

### 웹 테스트 드라이버

```dart
// test_driver/integration_test.dart
import 'package:integration_test/integration_test_driver.dart';

Future<void> main() => integrationDriver();
```

---

## 실행

```bash
# 모바일/데스크톱
flutter test integration_test/app_test.dart

# 웹 (ChromeDriver 필요)
chromedriver --port=4444  # 별도 터미널

flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/app_test.dart \
  -d chrome
```

---

## 플랫폼별 실행

| 플랫폼 | 명령어 |
|--------|--------|
| Android | `flutter test integration_test/ -d <device_id>` |
| iOS | `flutter test integration_test/ -d <device_id>` |
| macOS | `flutter test integration_test/` |
| Linux | `xvfb-run flutter test integration_test/` (CI) |
| Web | `flutter drive` (ChromeDriver 필요) |

---

## Firebase Test Lab

```bash
# Android APK 빌드
flutter build apk --debug
pushd android
./gradlew app:assembleAndroidTest
./gradlew app:assembleDebug -Ptarget=integration_test/app_test.dart
popd

# Firebase Console에서 업로드
# - App APK: build/app/outputs/apk/debug/*.apk
# - Test APK: build/app/outputs/apk/androidTest/debug/*.apk
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| Binding 에러 | `IntegrationTestWidgetsFlutterBinding.ensureInitialized()` 확인 |
| 위젯 못 찾음 | `Key` 추가 및 `pumpAndSettle()` 사용 |
| 웹 테스트 실패 | ChromeDriver 실행 확인 |
| CI 리눅스 | `xvfb-run` 사용 |

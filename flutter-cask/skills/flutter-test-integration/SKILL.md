---
name: flutter-test-integration
description: E2E testing using integration_test
metadata:
  version: "1.1.0"
  category: flutter-test
  type: unit
  style: guide
  triggers: [integration test, E2E, end-to-end]
---

# Flutter Integration Test

Test complete end-to-end app flows on real devices and emulators.

---

## Installation

```bash
flutter pub add 'dev:integration_test:{"sdk":"flutter"}'
```

---

## Folder Structure

```
lib/
  main.dart
integration_test/        # separate from test/
  app_test.dart
test_driver/             # required for web testing
  integration_test.dart
```

---

## Quick Reference

### Basic Structure

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('E2E Test', () {
    testWidgets('complete user flow', (tester) async {
      // launch app
      await tester.pumpWidget(const MyApp());

      // test logic
      expect(find.text('Home'), findsOneWidget);

      await tester.tap(find.byKey(const Key('login_button')));
      await tester.pumpAndSettle();

      expect(find.text('Welcome'), findsOneWidget);
    });
  });
}
```

### Using Keys (Required)

```dart
// lib/main.dart
ElevatedButton(
  key: const Key('submit_button'),  // Key for finding the widget in tests
  onPressed: _submit,
  child: const Text('Submit'),
)
```

### Web Test Driver

```dart
// test_driver/integration_test.dart
import 'package:integration_test/integration_test_driver.dart';

Future<void> main() => integrationDriver();
```

---

## Running Tests

```bash
# mobile/desktop
flutter test integration_test/app_test.dart

# web (requires ChromeDriver)
chromedriver --port=4444  # separate terminal

flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/app_test.dart \
  -d chrome
```

---

## Platform Commands

| Platform | Command |
|--------|--------|
| Android | `flutter test integration_test/ -d <device_id>` |
| iOS | `flutter test integration_test/ -d <device_id>` |
| macOS | `flutter test integration_test/` |
| Linux | `xvfb-run flutter test integration_test/` (CI) |
| Web | `flutter drive` (requires ChromeDriver) |

---

## Firebase Test Lab

```bash
# build Android APK
flutter build apk --debug
pushd android
./gradlew app:assembleAndroidTest
./gradlew app:assembleDebug -Ptarget=integration_test/app_test.dart
popd

# upload in Firebase Console
# - App APK: build/app/outputs/apk/debug/*.apk
# - Test APK: build/app/outputs/apk/androidTest/debug/*.apk
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Binding error | Check `IntegrationTestWidgetsFlutterBinding.ensureInitialized()` |
| Widget not found | Add a `Key` and use `pumpAndSettle()` |
| Web test failure | Check that ChromeDriver is running |
| CI Linux | Use `xvfb-run` |

---

## Changelog

### [1.1.0] - 2026-03-01
- 초기 릴리스

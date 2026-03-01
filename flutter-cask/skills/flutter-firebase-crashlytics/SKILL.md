---
name: flutter-firebase-crashlytics
description: Firebase Crashlytics 크래시 리포팅
metadata:
  version: "1.1.0"
  category: flutter-firebase
  type: unit
  style: guide
  triggers: [firebase_crashlytics, crashlytics, 크래시 리포트, 에러 추적, 앱 충돌]
---

# Flutter Firebase Crashlytics

앱 크래시 자동 수집 및 리포팅. 에러 원인 분석에 필수.

---

## 설치

```bash
flutter pub add firebase_crashlytics
```

## 사전 요구사항

- Firebase 프로젝트 설정 완료
- `flutterfire configure` 실행됨

---

## Quick Reference

### 초기화

```dart
import 'package:firebase_crashlytics/firebase_crashlytics.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  // Flutter 에러 자동 수집
  FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterError;

  // 비동기 에러 수집
  PlatformDispatcher.instance.onError = (error, stack) {
    FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
    return true;
  };

  runApp(MyApp());
}
```

### 수동 에러 리포트

```dart
try {
  await riskyOperation();
} catch (e, stack) {
  await FirebaseCrashlytics.instance.recordError(
    e,
    stack,
    reason: 'riskyOperation 실패',
    fatal: false,
  );
}
```

### 사용자 정보 추가

```dart
// 사용자 식별
await FirebaseCrashlytics.instance.setUserIdentifier('user_123');

// 커스텀 키
await FirebaseCrashlytics.instance.setCustomKey('role', 'admin');
await FirebaseCrashlytics.instance.setCustomKey('screen', 'checkout');

// 로그 메시지 (크래시 발생 시 함께 전송)
FirebaseCrashlytics.instance.log('결제 프로세스 시작');
```

### 테스트 크래시

```dart
// 테스트용 강제 크래시 (개발 중만 사용)
FirebaseCrashlytics.instance.crash();
```

### 수집 비활성화 (개발/디버그)

```dart
void main() async {
  await Firebase.initializeApp();

  // 디버그 모드에서 비활성화
  if (kDebugMode) {
    await FirebaseCrashlytics.instance.setCrashlyticsCollectionEnabled(false);
  }

  runApp(MyApp());
}
```

### Riverpod ErrorLogger

```dart
class CrashlyticsObserver extends ProviderObserver {
  @override
  void providerDidFail(
    ProviderBase provider,
    Object error,
    StackTrace stackTrace,
    ProviderContainer container,
  ) {
    FirebaseCrashlytics.instance.recordError(
      error,
      stackTrace,
      reason: 'Provider: ${provider.name ?? provider.runtimeType}',
    );
  }
}

// main.dart
runApp(
  ProviderScope(
    observers: [CrashlyticsObserver()],
    child: MyApp(),
  ),
);
```

### 전체 초기화 예시

```dart
Future<void> initCrashlytics() async {
  final crashlytics = FirebaseCrashlytics.instance;

  if (kDebugMode) {
    await crashlytics.setCrashlyticsCollectionEnabled(false);
    return;
  }

  FlutterError.onError = crashlytics.recordFlutterError;

  PlatformDispatcher.instance.onError = (error, stack) {
    crashlytics.recordError(error, stack, fatal: true);
    return true;
  };
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 리포트 안보임 | 앱 재시작 후 전송됨, 몇 분 대기 |
| dSYM 없음 (iOS) | Archive 후 자동 업로드 확인 |
| 난독화 안풀림 | ProGuard mapping 업로드 |
| 너무 많은 리포트 | 중복 제거, fatal만 분류 |

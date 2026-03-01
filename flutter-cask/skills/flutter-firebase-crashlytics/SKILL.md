---
name: flutter-firebase-crashlytics
description: Firebase Crashlytics crash reporting
metadata:
  version: "1.1.0"
  category: flutter-firebase
  type: unit
  style: guide
  triggers: [firebase_crashlytics, crashlytics, crash report, error tracking, app crash]
---

# Flutter Firebase Crashlytics

Automatic crash collection and reporting. Essential for error root cause analysis.

---

## Installation

```bash
flutter pub add firebase_crashlytics
```

## Prerequisites

- Firebase project configured
- `flutterfire configure` has been run

---

## Quick Reference

### Initialization

```dart
import 'package:firebase_crashlytics/firebase_crashlytics.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  // auto-collect Flutter errors
  FlutterError.onError = FirebaseCrashlytics.instance.recordFlutterError;

  // collect async errors
  PlatformDispatcher.instance.onError = (error, stack) {
    FirebaseCrashlytics.instance.recordError(error, stack, fatal: true);
    return true;
  };

  runApp(MyApp());
}
```

### Manual Error Reporting

```dart
try {
  await riskyOperation();
} catch (e, stack) {
  await FirebaseCrashlytics.instance.recordError(
    e,
    stack,
    reason: 'riskyOperation failed',
    fatal: false,
  );
}
```

### Adding User Information

```dart
// user identification
await FirebaseCrashlytics.instance.setUserIdentifier('user_123');

// custom keys
await FirebaseCrashlytics.instance.setCustomKey('role', 'admin');
await FirebaseCrashlytics.instance.setCustomKey('screen', 'checkout');

// log message (sent together when crash occurs)
FirebaseCrashlytics.instance.log('Payment process started');
```

### Test Crash

```dart
// force crash for testing (development only)
FirebaseCrashlytics.instance.crash();
```

### Disable Collection (Development/Debug)

```dart
void main() async {
  await Firebase.initializeApp();

  // disable in debug mode
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

### Full Initialization Example

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

## Common Issues

| Situation | Solution |
|------|------|
| Report not visible | Sent after app restart, wait a few minutes |
| No dSYM (iOS) | Verify automatic upload after Archive |
| Obfuscation not resolved | Upload ProGuard mapping |
| Too many reports | Deduplicate, classify fatal only |

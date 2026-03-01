---
name: flutter-talker
description: Structured logging and debug console
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [talker, talker_flutter, logging, logger, debug, log]
---

# Flutter Talker

Structured logging library. Color console, error tracking, and UI log viewer.

---

## Installation

```bash
flutter pub add talker
flutter pub add talker_flutter  # UI viewer
flutter pub add talker_dio_logger  # Dio interceptor (optional)
flutter pub add talker_riverpod_logger  # Riverpod observer (optional)
```

---

## Quick Reference

### Basic Usage

```dart
import 'package:talker/talker.dart';

final talker = Talker();

// log by level
talker.debug('Debug message');
talker.info('Info message');
talker.warning('Warning message');
talker.error('Error message');

// error with stack trace
try {
  throw Exception('Test error');
} catch (e, st) {
  talker.handle(e, st, 'Operation failed');
}
```

### Global Instance Setup

```dart
// talker_instance.dart
final talker = Talker(
  settings: TalkerSettings(
    enabled: true,
    useHistory: true,
    maxHistoryItems: 1000,
    useConsoleLogs: true,
  ),
);

// usage
import 'talker_instance.dart';
talker.info('App started');
```

### Custom Log

```dart
class ApiLog extends TalkerLog {
  ApiLog(String message) : super(message);

  @override
  String get title => 'API';

  @override
  AnsiPen get pen => AnsiPen()..cyan();
}

// usage
talker.logTyped(ApiLog('GET /users - 200'));
```

### Dio Interceptor

```dart
import 'package:talker_dio_logger/talker_dio_logger.dart';

final dio = Dio();
dio.interceptors.add(
  TalkerDioLogger(
    talker: talker,
    settings: TalkerDioLoggerSettings(
      printRequestHeaders: true,
      printResponseHeaders: true,
      printResponseMessage: true,
    ),
  ),
);
```

### Riverpod Observer

```dart
import 'package:talker_riverpod_logger/talker_riverpod_logger.dart';

runApp(
  ProviderScope(
    observers: [
      TalkerRiverpodObserver(
        talker: talker,
        settings: TalkerRiverpodLoggerSettings(
          printProviderCreated: true,
          printProviderUpdated: true,
          printProviderDisposed: true,
          printProviderFailed: true,
        ),
      ),
    ],
    child: MyApp(),
  ),
);
```

### UI Log Viewer

```dart
import 'package:talker_flutter/talker_flutter.dart';

// as a separate screen
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => TalkerScreen(talker: talker),
  ),
);

// or add to developer menu
ListTile(
  title: Text('View Logs'),
  onTap: () => Navigator.push(
    context,
    MaterialPageRoute(builder: (_) => TalkerScreen(talker: talker)),
  ),
)
```

### Production Settings

```dart
final talker = Talker(
  settings: TalkerSettings(
    enabled: !kReleaseMode,  // disable in release
    useHistory: !kReleaseMode,
    useConsoleLogs: !kReleaseMode,
  ),
);
```

### Crashlytics Integration

```dart
class CrashlyticsTalkerObserver extends TalkerObserver {
  @override
  void onError(TalkerError err) {
    FirebaseCrashlytics.instance.recordError(
      err.exception,
      err.stackTrace,
      reason: err.message,
    );
  }
}

final talker = Talker(
  observers: [CrashlyticsTalkerObserver()],
);
```

---

## Common Issues

| Situation | Solution |
|------|------|
| Logs not showing | Check settings.enabled |
| History memory usage | Limit maxHistoryItems, disable in release |
| Console color broken | Check terminal ANSI support |
| Logs exposed in release | Disable with kReleaseMode check |

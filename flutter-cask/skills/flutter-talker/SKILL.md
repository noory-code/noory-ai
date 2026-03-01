---
name: flutter-talker
description: 구조화된 로깅 및 디버그 콘솔
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [talker, talker_flutter, 로깅, logger, 디버그, 로그]
---

# Flutter Talker

구조화된 로깅 라이브러리. 컬러 콘솔, 에러 추적, UI 로그 뷰어.

---

## 설치

```bash
flutter pub add talker
flutter pub add talker_flutter  # UI 뷰어
flutter pub add talker_dio_logger  # Dio 인터셉터 (선택)
flutter pub add talker_riverpod_logger  # Riverpod 옵저버 (선택)
```

---

## Quick Reference

### 기본 사용

```dart
import 'package:talker/talker.dart';

final talker = Talker();

// 로그 레벨별 출력
talker.debug('디버그 메시지');
talker.info('정보 메시지');
talker.warning('경고 메시지');
talker.error('에러 메시지');

// 에러와 스택트레이스
try {
  throw Exception('테스트 에러');
} catch (e, st) {
  talker.handle(e, st, '작업 실패');
}
```

### 전역 인스턴스 설정

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

// 사용
import 'talker_instance.dart';
talker.info('앱 시작');
```

### 커스텀 로그

```dart
class ApiLog extends TalkerLog {
  ApiLog(String message) : super(message);

  @override
  String get title => 'API';

  @override
  AnsiPen get pen => AnsiPen()..cyan();
}

// 사용
talker.logTyped(ApiLog('GET /users - 200'));
```

### Dio 인터셉터

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

### Riverpod 옵저버

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

### UI 로그 뷰어

```dart
import 'package:talker_flutter/talker_flutter.dart';

// 별도 화면으로
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => TalkerScreen(talker: talker),
  ),
);

// 또는 개발자 메뉴에 추가
ListTile(
  title: Text('로그 보기'),
  onTap: () => Navigator.push(
    context,
    MaterialPageRoute(builder: (_) => TalkerScreen(talker: talker)),
  ),
)
```

### 프로덕션 설정

```dart
final talker = Talker(
  settings: TalkerSettings(
    enabled: !kReleaseMode,  // 릴리스에서 비활성화
    useHistory: !kReleaseMode,
    useConsoleLogs: !kReleaseMode,
  ),
);
```

### Crashlytics 연동

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

## 주의사항

| 상황 | 해결 |
|------|------|
| 로그 안보임 | settings.enabled 확인 |
| 히스토리 메모리 | maxHistoryItems 제한, 릴리스에서 비활성화 |
| 콘솔 색상 깨짐 | 터미널 ANSI 지원 확인 |
| 릴리스 로그 노출 | kReleaseMode 체크로 비활성화 |

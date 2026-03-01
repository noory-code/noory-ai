---
name: flutter-connectivity
description: 네트워크 연결 상태 감지 및 모니터링
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [connectivity_plus, 네트워크 상태, 오프라인, 인터넷 연결, 와이파이]
---

# Flutter Connectivity Plus

네트워크 연결 상태 감지. 오프라인/온라인 모드 전환에 활용.

---

## 설치

```bash
flutter pub add connectivity_plus
```

---

## Quick Reference

### 현재 상태 확인

```dart
import 'package:connectivity_plus/connectivity_plus.dart';

Future<bool> isConnected() async {
  final result = await Connectivity().checkConnectivity();
  return !result.contains(ConnectivityResult.none);
}

Future<void> checkConnection() async {
  final result = await Connectivity().checkConnectivity();

  if (result.contains(ConnectivityResult.wifi)) {
    print('WiFi 연결');
  } else if (result.contains(ConnectivityResult.mobile)) {
    print('모바일 데이터');
  } else if (result.contains(ConnectivityResult.ethernet)) {
    print('이더넷');
  } else if (result.contains(ConnectivityResult.none)) {
    print('연결 없음');
  }
}
```

### 연결 상태 스트림

```dart
class ConnectivityService {
  final _connectivity = Connectivity();
  StreamSubscription<List<ConnectivityResult>>? _subscription;

  void startMonitoring(void Function(bool isOnline) onChanged) {
    _subscription = _connectivity.onConnectivityChanged.listen((result) {
      final isOnline = !result.contains(ConnectivityResult.none);
      onChanged(isOnline);
    });
  }

  void stopMonitoring() {
    _subscription?.cancel();
  }
}
```

### Riverpod Provider

```dart
@riverpod
Stream<bool> connectivity(Ref ref) {
  return Connectivity().onConnectivityChanged.map(
    (result) => !result.contains(ConnectivityResult.none),
  );
}

// 사용
final isOnline = ref.watch(connectivityProvider).valueOrNull ?? true;
```

### 오프라인 배너

```dart
class OfflineBanner extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectivityAsync = ref.watch(connectivityProvider);

    return connectivityAsync.when(
      data: (isOnline) => isOnline
          ? SizedBox.shrink()
          : Container(
              width: double.infinity,
              color: Colors.red,
              padding: EdgeInsets.all(8),
              child: Text(
                '인터넷 연결이 없습니다',
                style: TextStyle(color: Colors.white),
                textAlign: TextAlign.center,
              ),
            ),
      loading: () => SizedBox.shrink(),
      error: (_, __) => SizedBox.shrink(),
    );
  }
}
```

### 실제 인터넷 연결 확인

```dart
// connectivity는 네트워크 인터페이스만 확인
// 실제 인터넷 연결은 별도 확인 필요
Future<bool> hasInternetAccess() async {
  try {
    final result = await InternetAddress.lookup('google.com');
    return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
  } on SocketException catch (_) {
    return false;
  }
}
```

### 연결 복구 시 데이터 동기화

```dart
class SyncManager {
  void init() {
    Connectivity().onConnectivityChanged.listen((result) async {
      if (!result.contains(ConnectivityResult.none)) {
        // 온라인 복귀 시 동기화
        await syncPendingData();
      }
    });
  }

  Future<void> syncPendingData() async {
    // 오프라인 중 쌓인 데이터 서버 전송
  }
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| WiFi 연결인데 인터넷 안됨 | DNS lookup으로 실제 연결 확인 |
| 상태 변경 안됨 | 스트림 구독 확인, 권한 확인 |
| iOS 시뮬레이터 이슈 | 실제 기기에서 테스트 |
| 배터리 소모 | 필요할 때만 모니터링, dispose 필수 |

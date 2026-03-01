---
name: flutter-connectivity
description: Network connectivity detection and monitoring
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [connectivity_plus, network status, offline, internet connection, wifi]
---

# Flutter Connectivity Plus

Network connectivity detection for offline/online mode switching.

---

## Installation

```bash
flutter pub add connectivity_plus
```

---

## Quick Reference

### Check Current Status

```dart
import 'package:connectivity_plus/connectivity_plus.dart';

Future<bool> isConnected() async {
  final result = await Connectivity().checkConnectivity();
  return !result.contains(ConnectivityResult.none);
}

Future<void> checkConnection() async {
  final result = await Connectivity().checkConnectivity();

  if (result.contains(ConnectivityResult.wifi)) {
    print('WiFi connected');
  } else if (result.contains(ConnectivityResult.mobile)) {
    print('Mobile data');
  } else if (result.contains(ConnectivityResult.ethernet)) {
    print('Ethernet');
  } else if (result.contains(ConnectivityResult.none)) {
    print('No connection');
  }
}
```

### Connectivity Stream

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

// usage
final isOnline = ref.watch(connectivityProvider).valueOrNull ?? true;
```

### Offline Banner

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
                'No internet connection',
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

### Verify Actual Internet Access

```dart
// connectivity_plus only checks the network interface;
// verifying actual internet access requires a separate DNS lookup
Future<bool> hasInternetAccess() async {
  try {
    final result = await InternetAddress.lookup('google.com');
    return result.isNotEmpty && result[0].rawAddress.isNotEmpty;
  } on SocketException catch (_) {
    return false;
  }
}
```

### Sync Data on Reconnection

```dart
class SyncManager {
  void init() {
    Connectivity().onConnectivityChanged.listen((result) async {
      if (!result.contains(ConnectivityResult.none)) {
        // sync when back online
        await syncPendingData();
      }
    });
  }

  Future<void> syncPendingData() async {
    // send data accumulated while offline to the server
  }
}
```

---

## Common Issues

| Issue | Fix |
|------|------|
| WiFi connected but no internet | Use a DNS lookup to verify actual connectivity |
| Status not changing | Check the stream subscription and permissions |
| iOS simulator issue | Test on a real device |
| Battery drain | Monitor only when needed and always dispose the subscription |

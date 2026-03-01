---
name: flutter-geolocator
description: GPS 위치 정보 조회 및 추적
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [geolocator, GPS, 위치, location, 좌표]
---

# Flutter Geolocator

현재 위치 조회, 위치 추적, 거리 계산.

---

## 설치

```bash
flutter pub add geolocator
```

## 플랫폼 설정

### iOS (ios/Runner/Info.plist)

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>주변 매장을 찾기 위해 위치 정보가 필요합니다.</string>
<key>NSLocationAlwaysUsageDescription</key>
<string>백그라운드 위치 추적을 위해 위치 정보가 필요합니다.</string>
```

### Android (android/app/src/main/AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<!-- 백그라운드 위치 (선택) -->
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

---

## Quick Reference

### 권한 요청

```dart
import 'package:geolocator/geolocator.dart';

Future<bool> requestPermission() async {
  bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    return false;  // 위치 서비스 비활성화
  }

  LocationPermission permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      return false;  // 권한 거부
    }
  }

  if (permission == LocationPermission.deniedForever) {
    await Geolocator.openAppSettings();  // 설정 화면으로
    return false;
  }

  return true;
}
```

### 현재 위치 조회

```dart
Future<Position?> getCurrentLocation() async {
  final hasPermission = await requestPermission();
  if (!hasPermission) return null;

  return await Geolocator.getCurrentPosition(
    desiredAccuracy: LocationAccuracy.high,
  );
}

// 사용
final position = await getCurrentLocation();
if (position != null) {
  print('위도: ${position.latitude}');
  print('경도: ${position.longitude}');
}
```

### 마지막 알려진 위치 (빠름)

```dart
final lastPosition = await Geolocator.getLastKnownPosition();
```

### 위치 추적 스트림

```dart
StreamSubscription<Position>? _positionStream;

void startTracking() {
  _positionStream = Geolocator.getPositionStream(
    locationSettings: LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10,  // 10m 이동 시마다 업데이트
    ),
  ).listen((position) {
    print('새 위치: ${position.latitude}, ${position.longitude}');
  });
}

void stopTracking() {
  _positionStream?.cancel();
}
```

### 거리 계산

```dart
// 두 좌표 간 거리 (미터)
final distanceInMeters = Geolocator.distanceBetween(
  37.5665, 126.9780,  // 서울시청
  37.5172, 127.0473,  // 강남역
);
print('거리: ${(distanceInMeters / 1000).toStringAsFixed(1)}km');

// 방위각 계산
final bearing = Geolocator.bearingBetween(
  37.5665, 126.9780,
  37.5172, 127.0473,
);
```

### Riverpod Provider

```dart
@riverpod
Future<Position?> currentPosition(Ref ref) async {
  final permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied ||
      permission == LocationPermission.deniedForever) {
    return null;
  }
  return Geolocator.getCurrentPosition();
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 권한 거부 | deniedForever면 openAppSettings() 안내 |
| 위치 부정확 | desiredAccuracy: high 사용 |
| 배터리 소모 | distanceFilter 설정, 추적이 끝나면 즉시 cancel |
| 시뮬레이터 | Features > Location에서 위치 설정 |
| 타임아웃 | timeLimit 파라미터 설정 |

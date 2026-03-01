---
name: flutter-geolocator
description: GPS location retrieval and tracking
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [geolocator, GPS, location, coordinates]
---

# Flutter Geolocator

Get the current location, track location changes, and calculate distances.

---

## Installation

```bash
flutter pub add geolocator
```

## Platform Setup

### iOS (ios/Runner/Info.plist)

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>Location access is required to find nearby stores.</string>
<key>NSLocationAlwaysUsageDescription</key>
<string>Location access is required for background location tracking.</string>
```

### Android (android/app/src/main/AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<!-- background location (optional) -->
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

---

## Quick Reference

### Request Permission

```dart
import 'package:geolocator/geolocator.dart';

Future<bool> requestPermission() async {
  bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    return false;  // location service is disabled
  }

  LocationPermission permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      return false;  // permission denied
    }
  }

  if (permission == LocationPermission.deniedForever) {
    await Geolocator.openAppSettings();  // direct the user to Settings
    return false;
  }

  return true;
}
```

### Get Current Location

```dart
Future<Position?> getCurrentLocation() async {
  final hasPermission = await requestPermission();
  if (!hasPermission) return null;

  return await Geolocator.getCurrentPosition(
    desiredAccuracy: LocationAccuracy.high,
  );
}

// usage
final position = await getCurrentLocation();
if (position != null) {
  print('Latitude: ${position.latitude}');
  print('Longitude: ${position.longitude}');
}
```

### Last Known Position (faster)

```dart
final lastPosition = await Geolocator.getLastKnownPosition();
```

### Location Tracking Stream

```dart
StreamSubscription<Position>? _positionStream;

void startTracking() {
  _positionStream = Geolocator.getPositionStream(
    locationSettings: LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 10,  // update for every 10m of movement
    ),
  ).listen((position) {
    print('New position: ${position.latitude}, ${position.longitude}');
  });
}

void stopTracking() {
  _positionStream?.cancel();
}
```

### Distance Calculation

```dart
// distance between two coordinates (in meters)
final distanceInMeters = Geolocator.distanceBetween(
  37.5665, 126.9780,  // Seoul City Hall
  37.5172, 127.0473,  // Gangnam Station
);
print('Distance: ${(distanceInMeters / 1000).toStringAsFixed(1)}km');

// bearing calculation
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

## Common Issues

| Issue | Fix |
|------|------|
| Permission denied forever | Call openAppSettings() to direct the user to Settings |
| Inaccurate location | Set desiredAccuracy to high |
| Battery drain | Use distanceFilter and cancel the stream immediately when tracking ends |
| Simulator | Set location in Features > Location |
| Timeout | Set the timeLimit parameter |

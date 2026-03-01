---
name: flutter-secure-storage
description: 암호화된 키-값 저장소 (토큰, 비밀키)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [secure storage, 토큰 저장, 암호화 저장소, keychain, keystore]
---

# Flutter Secure Storage

iOS Keychain, Android Keystore를 사용한 암호화 저장소. 민감 데이터 저장용.

---

## 설치

```bash
flutter pub add flutter_secure_storage
```

## 플랫폼 설정

### Android (android/app/build.gradle)

```groovy
android {
    defaultConfig {
        minSdkVersion 18  // 최소 18 이상
    }
}
```

### iOS (ios/Runner/Info.plist) - 선택

```xml
<!-- 앱 삭제 시 데이터 보존하려면 -->
<key>SecAttrAccessible</key>
<string>kSecAttrAccessibleAfterFirstUnlock</string>
```

---

## Quick Reference

### 기본 사용

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const storage = FlutterSecureStorage();

// 저장
await storage.write(key: 'access_token', value: 'abc123');
await storage.write(key: 'refresh_token', value: 'xyz789');

// 읽기
final token = await storage.read(key: 'access_token');

// 삭제
await storage.delete(key: 'access_token');

// 모두 삭제
await storage.deleteAll();

// 모든 키 조회
final allKeys = await storage.readAll();
```

### Android 옵션 (EncryptedSharedPreferences)

```dart
const storage = FlutterSecureStorage(
  aOptions: AndroidOptions(
    encryptedSharedPreferences: true,  // API 23+ 권장
  ),
);
```

### iOS 옵션

```dart
const storage = FlutterSecureStorage(
  iOptions: IOSOptions(
    accessibility: KeychainAccessibility.first_unlock,
    // 앱 삭제 후에도 데이터 유지하려면:
    // accessibility: KeychainAccessibility.first_unlock_this_device,
  ),
);
```

### Supabase Auth 토큰 저장 패턴

```dart
class SecureTokenStorage {
  static const _storage = FlutterSecureStorage();
  static const _accessTokenKey = 'supabase_access_token';
  static const _refreshTokenKey = 'supabase_refresh_token';

  static Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await Future.wait([
      _storage.write(key: _accessTokenKey, value: accessToken),
      _storage.write(key: _refreshTokenKey, value: refreshToken),
    ]);
  }

  static Future<({String? access, String? refresh})> getTokens() async {
    final results = await Future.wait([
      _storage.read(key: _accessTokenKey),
      _storage.read(key: _refreshTokenKey),
    ]);
    return (access: results[0], refresh: results[1]);
  }

  static Future<void> clearTokens() async {
    await Future.wait([
      _storage.delete(key: _accessTokenKey),
      _storage.delete(key: _refreshTokenKey),
    ]);
  }
}
```

### 존재 여부 확인

```dart
final hasToken = await storage.containsKey(key: 'access_token');

if (hasToken) {
  final token = await storage.read(key: 'access_token');
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| Android minSdk 에러 | minSdkVersion 18 이상 설정 |
| null 반환 | 키가 없으면 null 반환 (기본값 처리) |
| 앱 재설치 후 데이터 유실 | iOS: accessibility 옵션 확인 |
| 느린 성능 | 대용량 데이터는 Hive 사용, 토큰만 저장 |
| Web 미지원 | Web은 localStorage fallback 또는 별도 처리 |

---

## 보안 팁

```dart
// 1. 민감 데이터만 저장 (토큰, API 키)
// 2. 대용량 데이터는 Hive + 암호화 사용
// 3. 로그아웃 시 반드시 deleteAll()
// 4. 토큰 만료 시간도 함께 저장

await storage.write(
  key: 'token_expiry',
  value: DateTime.now().add(Duration(hours: 1)).toIso8601String(),
);
```

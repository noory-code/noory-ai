---
name: flutter-secure-storage
description: Encrypted key-value storage (tokens, secret keys)
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [secure storage, token storage, encrypted storage, keychain, keystore]
---

# Flutter Secure Storage

Encrypted storage backed by iOS Keychain and Android Keystore. Use it to store sensitive data.

---

## Installation

```bash
flutter pub add flutter_secure_storage
```

## Platform Setup

### Android (android/app/build.gradle)

```groovy
android {
    defaultConfig {
        minSdkVersion 18  // minimum API 18
    }
}
```

### iOS (ios/Runner/Info.plist) — optional

```xml
<!-- to preserve data after app deletion -->
<key>SecAttrAccessible</key>
<string>kSecAttrAccessibleAfterFirstUnlock</string>
```

---

## Quick Reference

### Basic Usage

```dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const storage = FlutterSecureStorage();

// write
await storage.write(key: 'access_token', value: 'abc123');
await storage.write(key: 'refresh_token', value: 'xyz789');

// read
final token = await storage.read(key: 'access_token');

// delete
await storage.delete(key: 'access_token');

// delete all
await storage.deleteAll();

// read all keys
final allKeys = await storage.readAll();
```

### Android Options (EncryptedSharedPreferences)

```dart
const storage = FlutterSecureStorage(
  aOptions: AndroidOptions(
    encryptedSharedPreferences: true,  // recommended for API 23+
  ),
);
```

### iOS Options

```dart
const storage = FlutterSecureStorage(
  iOptions: IOSOptions(
    accessibility: KeychainAccessibility.first_unlock,
    // to retain data after app reinstall:
    // accessibility: KeychainAccessibility.first_unlock_this_device,
  ),
);
```

### Supabase Auth Token Storage Pattern

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

### Check Key Existence

```dart
final hasToken = await storage.containsKey(key: 'access_token');

if (hasToken) {
  final token = await storage.read(key: 'access_token');
}
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Android minSdk error | Set minSdkVersion to 18 or above |
| Returns null | Returns null when the key does not exist; handle defaults explicitly |
| Data lost after app reinstall | Check the iOS accessibility option |
| Slow performance | Use Hive for large data; store tokens only in secure storage |
| Web not supported | Use a localStorage fallback or separate handling |

---

## Security Tips

```dart
// 1. Store sensitive data only (tokens, API keys)
// 2. Use Hive + encryption for large data
// 3. Always call deleteAll() on logout
// 4. Also store the token expiry time

await storage.write(
  key: 'token_expiry',
  value: DateTime.now().add(Duration(hours: 1)).toIso8601String(),
);
```

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release

---
name: flutter-hive
description: Hive를 사용한 경량 NoSQL 로컬 저장소
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [hive, NoSQL, 로컬 저장소, 박스, 오프라인 캐시]
---

# Flutter Hive

경량 NoSQL 로컬 저장소. SQLite보다 빠르고 간단.

---

## 설치

```bash
flutter pub add hive
flutter pub add hive_flutter
flutter pub add dev:hive_generator
flutter pub add dev:build_runner
```

## 초기화

```dart
// main.dart
import 'package:hive_flutter/hive_flutter.dart';

void main() async {
  await Hive.initFlutter();

  // 어댑터 등록 (코드젠 사용 시)
  Hive.registerAdapter(UserAdapter());

  // 박스 열기
  await Hive.openBox('settings');
  await Hive.openBox<User>('users');

  runApp(MyApp());
}
```

---

## Quick Reference

### 단순 Key-Value 저장

```dart
final box = Hive.box('settings');

// 저장
box.put('theme', 'dark');
box.put('language', 'ko');

// 읽기
final theme = box.get('theme', defaultValue: 'light');

// 삭제
box.delete('theme');

// 모두 삭제
await box.clear();
```

### 타입 어댑터 (코드젠)

```dart
import 'package:hive/hive.dart';

part 'user.g.dart';

@HiveType(typeId: 0)
class User extends HiveObject {
  @HiveField(0)
  late String name;

  @HiveField(1)
  late int age;

  @HiveField(2, defaultValue: false)
  bool isPremium = false;
}
```

```bash
dart run build_runner build
```

### 타입 박스 사용

```dart
final userBox = Hive.box<User>('users');

// 저장
final user = User()
  ..name = 'Kim'
  ..age = 25;
userBox.add(user);  // 자동 키
userBox.put('user1', user);  // 수동 키

// 읽기
final allUsers = userBox.values.toList();
final user1 = userBox.get('user1');

// 업데이트 (HiveObject 상속 시)
user.name = 'Lee';
user.save();

// 삭제
user.delete();
```

### 암호화 박스

```dart
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// 키 생성/로드
Future<List<int>> getEncryptionKey() async {
  const storage = FlutterSecureStorage();
  final key = await storage.read(key: 'hive_key');
  if (key != null) return base64Decode(key);

  final newKey = Hive.generateSecureKey();
  await storage.write(key: 'hive_key', value: base64Encode(newKey));
  return newKey;
}

// 암호화 박스 열기
final key = await getEncryptionKey();
await Hive.openBox('secrets', encryptionCipher: HiveAesCipher(key));
```

### ValueListenableBuilder

```dart
ValueListenableBuilder(
  valueListenable: Hive.box('settings').listenable(keys: ['theme']),
  builder: (context, box, _) {
    final theme = box.get('theme', defaultValue: 'light');
    return Text('Theme: $theme');
  },
)
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| Box not found | `Hive.openBox()` 먼저 호출 |
| typeId 중복 | 각 모델마다 고유 typeId 사용 |
| 필드 추가 후 에러 | `@HiveField(n, defaultValue: ...)` 사용 |
| 웹에서 안됨 | `hive_flutter` 대신 `hive` + IndexedDB 설정 |
| 대용량 데이터 느림 | LazyBox 사용: `Hive.openLazyBox()` |

---

## LazyBox (대용량)

```dart
final lazyBox = await Hive.openLazyBox<User>('largeData');

// 비동기 읽기 (메모리 절약)
final user = await lazyBox.get('user1');
```

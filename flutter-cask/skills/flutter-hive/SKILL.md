---
name: flutter-hive
user-invocable: true
description: Lightweight NoSQL local storage using Hive
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [hive, NoSQL, local storage, box, offline cache]
---

# Flutter Hive

Lightweight NoSQL local storage. Faster and simpler than SQLite.

---

## Installation

```bash
flutter pub add hive
flutter pub add hive_flutter
flutter pub add dev:hive_generator
flutter pub add dev:build_runner
```

## Initialization

```dart
// main.dart
import 'package:hive_flutter/hive_flutter.dart';

void main() async {
  await Hive.initFlutter();

  // register adapters (when using code generation)
  Hive.registerAdapter(UserAdapter());

  // open boxes
  await Hive.openBox('settings');
  await Hive.openBox<User>('users');

  runApp(MyApp());
}
```

---

## Quick Reference

### Simple Key-Value Storage

```dart
final box = Hive.box('settings');

// write
box.put('theme', 'dark');
box.put('language', 'en');

// read
final theme = box.get('theme', defaultValue: 'light');

// delete
box.delete('theme');

// clear all
await box.clear();
```

### Type Adapter (Code Generation)

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

### Using a Typed Box

```dart
final userBox = Hive.box<User>('users');

// write
final user = User()
  ..name = 'Kim'
  ..age = 25;
userBox.add(user);  // auto key
userBox.put('user1', user);  // manual key

// read
final allUsers = userBox.values.toList();
final user1 = userBox.get('user1');

// update (when extending HiveObject)
user.name = 'Lee';
user.save();

// delete
user.delete();
```

### Encrypted Box

```dart
import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// generate or load the encryption key
Future<List<int>> getEncryptionKey() async {
  const storage = FlutterSecureStorage();
  final key = await storage.read(key: 'hive_key');
  if (key != null) return base64Decode(key);

  final newKey = Hive.generateSecureKey();
  await storage.write(key: 'hive_key', value: base64Encode(newKey));
  return newKey;
}

// open an encrypted box
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

## Common Issues

| Issue | Fix |
|------|------|
| Box not found | Call `Hive.openBox()` before accessing the box |
| Duplicate typeId | Use a unique typeId for each model |
| Error after adding a field | Use `@HiveField(n, defaultValue: ...)` for new fields |
| Not working on web | Use `hive` with IndexedDB config instead of `hive_flutter` |
| Slow with large data | Use LazyBox: `Hive.openLazyBox()` |

---

## LazyBox (Large Data)

```dart
final lazyBox = await Hive.openLazyBox<User>('largeData');

// async read (reduces memory usage)
final user = await lazyBox.get('user1');
```

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release

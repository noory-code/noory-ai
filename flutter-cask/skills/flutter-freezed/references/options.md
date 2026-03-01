# Configuration Options

## @Freezed Annotation

```dart
@Freezed(
  copyWith: true,              // generate copyWith (default: true)
  equal: true,                 // generate == operator (default: true)
  toStringOverride: true,      // generate toString (default: true)
  makeCollectionsUnmodifiable: true,  // make List/Map immutable (default: true)
)
abstract class User with _$User { ... }
```

---

## @unfreezed (Mutable Class)

```dart
@unfreezed
abstract class MutableUser with _$MutableUser {
  factory MutableUser({
    required String name,
    required final int id,  // final makes it immutable
  }) = _MutableUser;
}

final user = MutableUser(name: 'Kim', id: 1);
user.name = 'Lee';  // OK (mutable)
// user.id = 2;     // error (immutable)
```

---

## @Default (Default Values)

```dart
@freezed
abstract class Settings with _$Settings {
  const factory Settings({
    @Default(false) bool darkMode,
    @Default(16) int fontSize,
  }) = _Settings;
}

final settings = Settings();  // darkMode: false, fontSize: 16
```

---

## @Assert (Validation)

```dart
@freezed
abstract class User with _$User {
  @Assert('age >= 0', 'age must be non-negative')
  const factory User({
    required String name,
    required int age,
  }) = _User;
}
```

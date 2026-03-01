# 설정 옵션

## @Freezed 어노테이션

```dart
@Freezed(
  copyWith: true,              // copyWith 생성 (기본: true)
  equal: true,                 // == 연산자 생성 (기본: true)
  toStringOverride: true,      // toString 생성 (기본: true)
  makeCollectionsUnmodifiable: true,  // List/Map 불변화 (기본: true)
)
abstract class User with _$User { ... }
```

---

## @unfreezed (가변 클래스)

```dart
@unfreezed
abstract class MutableUser with _$MutableUser {
  factory MutableUser({
    required String name,
    required final int id,  // final 붙이면 불변
  }) = _MutableUser;
}

final user = MutableUser(name: 'Kim', id: 1);
user.name = 'Lee';  // OK (가변)
// user.id = 2;     // 에러 (불변)
```

---

## @Default (기본값)

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

## @Assert (검증)

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

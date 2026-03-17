---
name: flutter-freezed
description: Immutable data class generation using the Freezed package
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [freezed, immutable class, data class, union type, sealed class]
---

# Flutter Freezed

Generate immutable data classes and union types using the Freezed package.

---

## Installation

```bash
# required
flutter pub add freezed_annotation
flutter pub add dev:freezed
flutter pub add dev:build_runner

# for JSON serialization
flutter pub add json_annotation
flutter pub add dev:json_serializable
```

## Code Generation

```bash
# one-time build
dart run build_runner build --delete-conflicting-outputs

# watch mode
dart run build_runner watch --delete-conflicting-outputs
```

---

## Quick Reference

```dart
// basic immutable class
@freezed
abstract class User with _$User {
  const factory User({required String name}) = _User;
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// Union Type (sealed)
@freezed
sealed class State with _$State {
  const factory State.loading() = StateLoading;
  const factory State.data(String value) = StateData;
  const factory State.error(Exception e) = StateError;
}

// usage
final user = User(name: 'Kim');
final copy = user.copyWith(name: 'Lee');
final json = user.toJson();

// pattern matching
switch (state) {
  StateLoading() => print('loading'),
  StateData(:final value) => print(value),
  StateError(:final e) => print(e),
}
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Missing `part` file error | Run `dart run build_runner build` |
| Changes not reflected | Add the `--delete-conflicting-outputs` flag |
| Cannot add methods | Add a `const ClassName._();` private constructor |
| Nested copyWith not working | Apply @freezed to nested classes as well |

---

## References

| File | Description |
|------|------|
| [basic-usage.md](references/basic-usage.md) | Basic usage, copyWith, adding methods |
| [union-types.md](references/union-types.md) | Union types, pattern matching, shared properties |
| [json.md](references/json.md) | JSON serialization, type key customization |
| [options.md](references/options.md) | @Freezed, @unfreezed, @Default, @Assert |

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release

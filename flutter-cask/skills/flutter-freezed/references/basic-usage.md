# Freezed Basic Usage

## File Structure

```dart
// user.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';      // required
part 'user.g.dart';            // for JSON serialization

@freezed
abstract class User with _$User {
  const factory User({
    required String id,
    required String name,
    String? email,
  }) = _User;

  // JSON serialization (optional)
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

## Auto-generated Features

| Feature | Description |
|------|------|
| `toString()` | String representation including all fields |
| `==` / `hashCode` | Value-based equality comparison |
| `copyWith()` | Copy the object with partial field changes |
| Immutability | All fields are `final` |

---

## copyWith

### Basic Usage

```dart
final user = User(id: '1', name: 'Kim');

// change only some fields
final updated = user.copyWith(name: 'Lee');
// User(id: 1, name: Lee, email: null)
```

### Deep Copy (nested objects)

```dart
@freezed
abstract class Company with _$Company {
  const factory Company({
    required String name,
    required Director director,
  }) = _Company;
}

@freezed
abstract class Director with _$Director {
  const factory Director({
    required String name,
  }) = _Director;
}

// modify a nested object
final newCompany = company.copyWith.director(name: 'New Director');
```

---

## Adding Methods and Getters

Adding custom methods requires a private constructor:

```dart
@freezed
abstract class User with _$User {
  const User._();  // private constructor (required!)

  const factory User({
    required String firstName,
    required String lastName,
  }) = _User;

  // custom getter
  String get fullName => '$firstName $lastName';

  // custom method
  bool isAdmin() => lastName == 'Admin';
}
```

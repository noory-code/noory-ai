# Freezed 기본 사용법

## 파일 구조

```dart
// user.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';      // 필수
part 'user.g.dart';            // JSON 직렬화 시

@freezed
abstract class User with _$User {
  const factory User({
    required String id,
    required String name,
    String? email,
  }) = _User;

  // JSON 직렬화 (선택)
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}
```

## 자동 생성되는 것들

| 기능 | 설명 |
|------|------|
| `toString()` | 모든 필드 포함한 문자열 |
| `==` / `hashCode` | 값 기반 동등성 비교 |
| `copyWith()` | 일부 필드만 변경한 복사본 |
| 불변성 | 모든 필드 `final` |

---

## copyWith

### 기본 사용

```dart
final user = User(id: '1', name: 'Kim');

// 일부 필드만 변경
final updated = user.copyWith(name: 'Lee');
// User(id: 1, name: Lee, email: null)
```

### Deep Copy (중첩 객체)

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

// 중첩 객체 수정
final newCompany = company.copyWith.director(name: 'New Director');
```

---

## 메서드/게터 추가

private 생성자 필요:

```dart
@freezed
abstract class User with _$User {
  const User._();  // private 생성자 (필수!)

  const factory User({
    required String firstName,
    required String lastName,
  }) = _User;

  // 커스텀 게터
  String get fullName => '$firstName $lastName';

  // 커스텀 메서드
  bool isAdmin() => lastName == 'Admin';
}
```

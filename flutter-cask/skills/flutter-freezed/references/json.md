# JSON 직렬화

## 단일 클래스

```dart
@freezed
abstract class User with _$User {
  const factory User({
    required String id,
    @JsonKey(name: 'user_name') required String name,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// 사용
final user = User.fromJson({'id': '1', 'user_name': 'Kim'});
final json = user.toJson();
```

---

## Union Type JSON

기본적으로 `runtimeType` 필드로 타입 구분:

```dart
@freezed
sealed class Response with _$Response {
  const factory Response.data(String value) = ResponseData;
  const factory Response.error(String message) = ResponseError;

  factory Response.fromJson(Map<String, dynamic> json) => _$ResponseFromJson(json);
}

// JSON 예시
// {"runtimeType": "data", "value": "hello"}
// {"runtimeType": "error", "message": "failed"}
```

---

## 타입 키 커스터마이징

```dart
@Freezed(unionKey: 'type', unionValueCase: FreezedUnionCase.pascal)
sealed class Response with _$Response {
  const factory Response.data(String value) = ResponseData;
  const factory Response.error(String message) = ResponseError;

  factory Response.fromJson(Map<String, dynamic> json) => _$ResponseFromJson(json);
}

// JSON 예시
// {"type": "Data", "value": "hello"}
```

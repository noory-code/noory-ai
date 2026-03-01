# JSON Serialization

## Single Class

```dart
@freezed
abstract class User with _$User {
  const factory User({
    required String id,
    @JsonKey(name: 'user_name') required String name,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// usage
final user = User.fromJson({'id': '1', 'user_name': 'Kim'});
final json = user.toJson();
```

---

## Union Type JSON

By default, the type is identified by the `runtimeType` field:

```dart
@freezed
sealed class Response with _$Response {
  const factory Response.data(String value) = ResponseData;
  const factory Response.error(String message) = ResponseError;

  factory Response.fromJson(Map<String, dynamic> json) => _$ResponseFromJson(json);
}

// JSON example
// {"runtimeType": "data", "value": "hello"}
// {"runtimeType": "error", "message": "failed"}
```

---

## Customizing the Type Key

```dart
@Freezed(unionKey: 'type', unionValueCase: FreezedUnionCase.pascal)
sealed class Response with _$Response {
  const factory Response.data(String value) = ResponseData;
  const factory Response.error(String message) = ResponseError;

  factory Response.fromJson(Map<String, dynamic> json) => _$ResponseFromJson(json);
}

// JSON example
// {"type": "Data", "value": "hello"}
```

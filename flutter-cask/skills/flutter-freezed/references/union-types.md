# Union Types (Sealed Class)

Type-safe representation of multiple states.

## Definition

```dart
@freezed
sealed class Result<T> with _$Result<T> {
  const factory Result.success(T data) = ResultSuccess<T>;
  const factory Result.loading() = ResultLoading<T>;
  const factory Result.error(String message) = ResultError<T>;
}
```

---

## Pattern Matching (Dart 3+)

```dart
// switch expression
final message = switch (result) {
  ResultSuccess(:final data) => 'Success: $data',
  ResultLoading() => 'Loading...',
  ResultError(:final message) => 'Error: $message',
};

// if-case
if (result case ResultSuccess(:final data)) {
  print('Got data: $data');
}
```

---

## Shared Properties

Fields with the same name in all constructors can be accessed directly:

```dart
@freezed
sealed class Media with _$Media {
  const factory Media.image(String url, int width) = MediaImage;
  const factory Media.video(String url, Duration length) = MediaVideo;
}

// url exists in all constructors -> can be accessed directly
final media = Media.image('http://...', 800);
print(media.url);  // OK

// width only exists in MediaImage -> cannot be accessed directly
// print(media.width);  // compile error
```

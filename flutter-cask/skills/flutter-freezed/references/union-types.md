# Union Types (Sealed Class)

여러 상태를 타입 안전하게 표현.

## 정의

```dart
@freezed
sealed class Result<T> with _$Result<T> {
  const factory Result.success(T data) = ResultSuccess<T>;
  const factory Result.loading() = ResultLoading<T>;
  const factory Result.error(String message) = ResultError<T>;
}
```

---

## 패턴 매칭 (Dart 3+)

```dart
// switch 표현식
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

## 공유 속성

모든 생성자에 동일한 이름의 필드가 있으면 직접 접근 가능:

```dart
@freezed
sealed class Media with _$Media {
  const factory Media.image(String url, int width) = MediaImage;
  const factory Media.video(String url, Duration length) = MediaVideo;
}

// url은 모든 생성자에 있음 -> 직접 접근 가능
final media = Media.image('http://...', 800);
print(media.url);  // OK

// width는 MediaImage에만 있음 -> 직접 접근 불가
// print(media.width);  // 컴파일 에러
```

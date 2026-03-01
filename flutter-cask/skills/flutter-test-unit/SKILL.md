---
name: flutter-test-unit
description: test + mockito를 사용한 Unit 테스트
metadata:
  version: "1.1.0"
  category: flutter-test
  type: unit
  style: guide
  triggers: [unit test, 유닛 테스트, 단위 테스트, mockito, mock]
---

# Flutter Unit Test

함수, 메서드, 클래스의 로직을 격리하여 테스트.

---

## 설치

```bash
flutter pub add dev:test dev:mockito dev:build_runner
```

---

## 폴더 구조

```
lib/
  counter.dart
test/
  counter_test.dart      # _test.dart 접미사 필수
```

---

## Quick Reference

### 기본 테스트

```dart
import 'package:test/test.dart';
import 'package:my_app/counter.dart';

void main() {
  test('Counter increments', () {
    final counter = Counter();
    counter.increment();
    expect(counter.value, 1);
  });
}
```

### 그룹화

```dart
void main() {
  group('Counter', () {
    test('starts at 0', () {
      expect(Counter().value, 0);
    });

    test('increments', () {
      final counter = Counter()..increment();
      expect(counter.value, 1);
    });

    test('decrements', () {
      final counter = Counter()..decrement();
      expect(counter.value, -1);
    });
  });
}
```

### Mockito

```dart
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:http/http.dart' as http;

import 'fetch_test.mocks.dart';

@GenerateMocks([http.Client])
void main() {
  test('fetches data', () async {
    final client = MockClient();

    // Mock 설정
    when(client.get(Uri.parse('https://api.example.com/data')))
        .thenAnswer((_) async => http.Response('{"id": 1}', 200));

    final result = await fetchData(client);
    expect(result.id, 1);

    // 호출 검증
    verify(client.get(Uri.parse('https://api.example.com/data'))).called(1);
  });
}
```

Mock 생성:
```bash
dart run build_runner build
```

---

## 실행

```bash
# 특정 파일
flutter test test/counter_test.dart

# 특정 그룹
flutter test --plain-name "Counter"

# 전체
flutter test
```

---

## Matchers

| Matcher | 설명 |
|---------|------|
| `equals(value)` | 값 비교 |
| `isNull` / `isNotNull` | null 체크 |
| `isA<Type>()` | 타입 체크 |
| `throwsException` | 예외 발생 |
| `throwsA(isA<MyError>())` | 특정 예외 |
| `contains(value)` | 컬렉션 포함 |

---

## 주의사항

| 상황 | 해결 |
|------|------|
| Mock 클래스 없음 | `dart run build_runner build` 실행 |
| 테스트 파일 인식 안됨 | `_test.dart` 접미사 확인 |
| async 테스트 실패 | `await` 및 `async` 키워드 확인 |

---
name: flutter-test-unit
description: Unit testing using test + mockito
metadata:
  version: "1.1.0"
  category: flutter-test
  type: unit
  style: guide
  triggers: [unit test, mockito, mock]
---

# Flutter Unit Test

Test functions, methods, and class logic in isolation.

---

## Installation

```bash
flutter pub add dev:test dev:mockito dev:build_runner
```

---

## Folder Structure

```
lib/
  counter.dart
test/
  counter_test.dart      # _test.dart suffix required
```

---

## Quick Reference

### Basic Test

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

### Grouping

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

    // configure mock
    when(client.get(Uri.parse('https://api.example.com/data')))
        .thenAnswer((_) async => http.Response('{"id": 1}', 200));

    final result = await fetchData(client);
    expect(result.id, 1);

    // verify call
    verify(client.get(Uri.parse('https://api.example.com/data'))).called(1);
  });
}
```

Generate mocks:
```bash
dart run build_runner build
```

---

## Running Tests

```bash
# specific file
flutter test test/counter_test.dart

# specific group
flutter test --plain-name "Counter"

# all
flutter test
```

---

## Matchers

| Matcher | Description |
|---------|------|
| `equals(value)` | Value comparison |
| `isNull` / `isNotNull` | Null check |
| `isA<Type>()` | Type check |
| `throwsException` | Exception thrown |
| `throwsA(isA<MyError>())` | Specific exception |
| `contains(value)` | Collection contains value |

---

## Common Issues

| Situation | Solution |
|------|------|
| No mock class | Run `dart run build_runner build` |
| Test file not recognized | Check `_test.dart` suffix |
| Async test failure | Check `await` and `async` keywords |

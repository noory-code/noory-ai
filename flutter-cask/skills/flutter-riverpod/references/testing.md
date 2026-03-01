# Riverpod Testing

Testing patterns using Provider overrides.

## Basic Setup

```dart
// test/widget_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('Counter increments', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        child: MyApp(),
      ),
    );

    expect(find.text('0'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pump();

    expect(find.text('1'), findsOneWidget);
  });
}
```

---

## Provider Override

```dart
testWidgets('Shows user name', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        // value override
        userProvider.overrideWithValue(
          User(id: '1', name: 'Test User'),
        ),
      ],
      child: MyApp(),
    ),
  );

  expect(find.text('Test User'), findsOneWidget);
});
```

---

## AsyncNotifier Override

```dart
testWidgets('Shows todo list', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        // override with AsyncValue
        todoListProvider.overrideWith(() => MockTodoList()),
      ],
      child: MyApp(),
    ),
  );
});

class MockTodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    return [
      Todo(id: '1', title: 'Test Todo'),
    ];
  }
}
```

---

## Unit Test (Container)

```dart
void main() {
  test('Counter increments', () {
    final container = ProviderContainer();
    addTearDown(container.dispose);

    expect(container.read(counterProvider), 0);

    container.read(counterProvider.notifier).increment();

    expect(container.read(counterProvider), 1);
  });
}
```

---

## Mocking Dependencies

```dart
// original
@riverpod
class TodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    final repo = ref.watch(todoRepositoryProvider);
    return repo.fetchAll();
  }
}

// test
testWidgets('Shows todos', (tester) async {
  final mockRepo = MockTodoRepository();
  when(mockRepo.fetchAll()).thenAnswer((_) async => [
    Todo(id: '1', title: 'Test'),
  ]);

  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        todoRepositoryProvider.overrideWithValue(mockRepo),
      ],
      child: MyApp(),
    ),
  );

  await tester.pumpAndSettle();

  expect(find.text('Test'), findsOneWidget);
});
```

---

## Testing Loading/Error States

```dart
testWidgets('Shows loading', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        todoListProvider.overrideWith(
          () => _LoadingTodoList(),
        ),
      ],
      child: MyApp(),
    ),
  );

  expect(find.byType(CircularProgressIndicator), findsOneWidget);
});

class _LoadingTodoList extends _$TodoList {
  @override
  Future<List<Todo>> build() async {
    await Future.delayed(const Duration(days: 1));  // loading forever
    return [];
  }
}
```

---
name: flutter-test-widget
description: Widget testing using flutter_test
metadata:
  version: "1.1.0"
  category: flutter-test
  type: unit
  style: guide
  triggers: [widget test, testWidgets, WidgetTester]
---

# Flutter Widget Test

Test a single widget's UI and interactions.

---

## Installation

```yaml
# pubspec.yaml (included in the Flutter SDK)
dev_dependencies:
  flutter_test:
    sdk: flutter
```

---

## Quick Reference

### Basic Structure

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('MyWidget has title', (tester) async {
    // 1. build widget
    await tester.pumpWidget(const MyWidget(title: 'Hello'));

    // 2. find widget
    final titleFinder = find.text('Hello');

    // 3. verify
    expect(titleFinder, findsOneWidget);
  });
}
```

### Finders

```dart
// find by text
find.text('Hello')

// find by type
find.byType(ElevatedButton)

// find by key
find.byKey(const Key('submit_button'))

// find by icon
find.byIcon(Icons.add)

// ancestor/descendant relationship
find.descendant(
  of: find.byType(ListTile),
  matching: find.text('Item'),
)
```

### Matchers

```dart
expect(finder, findsOneWidget);      // exactly 1
expect(finder, findsNothing);        // 0
expect(finder, findsWidgets);        // 1 or more
expect(finder, findsNWidgets(3));    // exactly N
expect(finder, findsAtLeast(2));     // at least N
```

### Interactions

```dart
// tap
await tester.tap(find.byType(ElevatedButton));
await tester.pump();  // apply setState

// enter text
await tester.enterText(find.byType(TextField), 'hello');
await tester.pump();

// drag
await tester.drag(find.byType(ListView), const Offset(0, -300));
await tester.pumpAndSettle();  // wait for animations to complete

// scroll
await tester.scrollUntilVisible(
  find.text('Item 50'),
  500.0,
  scrollable: find.byType(Scrollable),
);
```

### Pump Methods

| Method | Purpose |
|--------|------|
| `pump()` | Render one frame |
| `pump(Duration)` | Advance time by the specified duration |
| `pumpAndSettle()` | Wait until all animations complete |
| `pumpWidget(widget)` | Build a widget |

---

## Example: Counter Test

```dart
testWidgets('Counter increments', (tester) async {
  await tester.pumpWidget(const MaterialApp(home: CounterPage()));

  // verify initial value
  expect(find.text('0'), findsOneWidget);

  // tap button
  await tester.tap(find.byIcon(Icons.add));
  await tester.pump();

  // verify increment
  expect(find.text('1'), findsOneWidget);
});
```

---

## Running Tests

```bash
# specific file
flutter test test/widget_test.dart

# all tests
flutter test
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Widget not found | Make sure `pump()` is called after `pumpWidget` |
| Animation incomplete | Use `pumpAndSettle()` |
| Overflow error | Wrap in a smaller test widget |
| Missing MediaQuery | Wrap with `MaterialApp` |

---

## Changelog

### [1.1.0] - 2026-03-01
- 초기 릴리스

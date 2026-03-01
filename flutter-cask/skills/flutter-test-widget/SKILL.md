---
name: flutter-test-widget
description: flutter_test를 사용한 Widget 테스트
metadata:
  version: "1.1.0"
  category: flutter-test
  type: unit
  style: guide
  triggers: [widget test, 위젯 테스트, testWidgets, WidgetTester]
---

# Flutter Widget Test

단일 위젯의 UI와 상호작용을 테스트.

---

## 설치

```yaml
# pubspec.yaml (SDK 내장)
dev_dependencies:
  flutter_test:
    sdk: flutter
```

---

## Quick Reference

### 기본 구조

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('MyWidget has title', (tester) async {
    // 1. 위젯 빌드
    await tester.pumpWidget(const MyWidget(title: 'Hello'));

    // 2. 위젯 찾기
    final titleFinder = find.text('Hello');

    // 3. 검증
    expect(titleFinder, findsOneWidget);
  });
}
```

### Finders

```dart
// 텍스트로 찾기
find.text('Hello')

// 타입으로 찾기
find.byType(ElevatedButton)

// Key로 찾기
find.byKey(const Key('submit_button'))

// 아이콘으로 찾기
find.byIcon(Icons.add)

// 조상/자손 관계
find.descendant(
  of: find.byType(ListTile),
  matching: find.text('Item'),
)
```

### Matchers

```dart
expect(finder, findsOneWidget);      // 정확히 1개
expect(finder, findsNothing);        // 0개
expect(finder, findsWidgets);        // 1개 이상
expect(finder, findsNWidgets(3));    // 정확히 N개
expect(finder, findsAtLeast(2));     // 최소 N개
```

### 상호작용

```dart
// 탭
await tester.tap(find.byType(ElevatedButton));
await tester.pump();  // setState 반영

// 텍스트 입력
await tester.enterText(find.byType(TextField), 'hello');
await tester.pump();

// 드래그
await tester.drag(find.byType(ListView), const Offset(0, -300));
await tester.pumpAndSettle();  // 애니메이션 완료 대기

// 스크롤
await tester.scrollUntilVisible(
  find.text('Item 50'),
  500.0,
  scrollable: find.byType(Scrollable),
);
```

### Pump 메서드

| 메서드 | 용도 |
|--------|------|
| `pump()` | 한 프레임 렌더링 |
| `pump(Duration)` | 지정 시간만큼 진행 |
| `pumpAndSettle()` | 애니메이션 완료까지 대기 |
| `pumpWidget(widget)` | 위젯 빌드 |

---

## 예시: 카운터 테스트

```dart
testWidgets('Counter increments', (tester) async {
  await tester.pumpWidget(const MaterialApp(home: CounterPage()));

  // 초기값 확인
  expect(find.text('0'), findsOneWidget);

  // 버튼 탭
  await tester.tap(find.byIcon(Icons.add));
  await tester.pump();

  // 증가 확인
  expect(find.text('1'), findsOneWidget);
});
```

---

## 실행

```bash
# 특정 파일
flutter test test/widget_test.dart

# 전체
flutter test
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 위젯 못 찾음 | `pumpWidget` 후 `pump()` 호출 확인 |
| 애니메이션 미완료 | `pumpAndSettle()` 사용 |
| Overflow 에러 | 테스트용 작은 위젯으로 감싸기 |
| MediaQuery 없음 | `MaterialApp`으로 감싸기 |

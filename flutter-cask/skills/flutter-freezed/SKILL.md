---
name: flutter-freezed
description: Freezed 패키지를 사용한 불변 데이터 클래스 생성
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [freezed, 불변 클래스, data class, union type, sealed class]
---

# Flutter Freezed

Freezed 패키지를 사용한 불변 데이터 클래스 및 Union Type 생성.

---

## 설치

```bash
# 필수
flutter pub add freezed_annotation
flutter pub add dev:freezed
flutter pub add dev:build_runner

# JSON 직렬화 시
flutter pub add json_annotation
flutter pub add dev:json_serializable
```

## 코드 생성

```bash
# 일회성 빌드
dart run build_runner build --delete-conflicting-outputs

# 감시 모드
dart run build_runner watch --delete-conflicting-outputs
```

---

## Quick Reference

```dart
// 기본 불변 클래스
@freezed
abstract class User with _$User {
  const factory User({required String name}) = _User;
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// Union Type (sealed)
@freezed
sealed class State with _$State {
  const factory State.loading() = StateLoading;
  const factory State.data(String value) = StateData;
  const factory State.error(Exception e) = StateError;
}

// 사용
final user = User(name: 'Kim');
final copy = user.copyWith(name: 'Lee');
final json = user.toJson();

// 패턴 매칭
switch (state) {
  StateLoading() => print('loading'),
  StateData(:final value) => print(value),
  StateError(:final e) => print(e),
}
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| `part` 파일 없음 에러 | `dart run build_runner build` 실행 |
| 변경 사항 미반영 | `--delete-conflicting-outputs` 옵션 추가 |
| 메서드 추가 불가 | `const ClassName._();` private 생성자 추가 |
| 중첩 copyWith 안됨 | 중첩 클래스도 @freezed 적용 필요 |

---

## References

| 파일 | 내용 |
|------|------|
| [basic-usage.md](references/basic-usage.md) | 기본 사용법, copyWith, 메서드 추가 |
| [union-types.md](references/union-types.md) | Union Types, 패턴 매칭, 공유 속성 |
| [json.md](references/json.md) | JSON 직렬화, 타입 키 커스터마이징 |
| [options.md](references/options.md) | @Freezed, @unfreezed, @Default, @Assert |

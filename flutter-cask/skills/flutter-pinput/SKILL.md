---
name: flutter-pinput
description: PIN/OTP 코드 입력 위젯
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [pinput, PIN 입력, OTP, 인증 코드, 6자리 코드]
---

# Flutter Pinput

PIN/OTP 코드 입력 위젯. MFA 인증, SMS 인증에 사용.

---

## 설치

```bash
flutter pub add pinput
```

---

## Quick Reference

### 기본 사용

```dart
import 'package:pinput/pinput.dart';

final pinController = TextEditingController();
final focusNode = FocusNode();

Pinput(
  length: 6,
  controller: pinController,
  focusNode: focusNode,
  onCompleted: (pin) {
    print('Completed: $pin');
    verifyOtp(pin);
  },
  onChanged: (value) {
    print('Changed: $value');
  },
)
```

### 커스텀 스타일

```dart
final defaultPinTheme = PinTheme(
  width: 56,
  height: 56,
  textStyle: TextStyle(
    fontSize: 22,
    fontWeight: FontWeight.w600,
  ),
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(8),
    border: Border.all(color: Colors.grey[300]!),
  ),
);

final focusedPinTheme = defaultPinTheme.copyWith(
  decoration: defaultPinTheme.decoration!.copyWith(
    border: Border.all(color: Colors.blue, width: 2),
  ),
);

final submittedPinTheme = defaultPinTheme.copyWith(
  decoration: defaultPinTheme.decoration!.copyWith(
    color: Colors.grey[100],
  ),
);

final errorPinTheme = defaultPinTheme.copyWith(
  decoration: defaultPinTheme.decoration!.copyWith(
    border: Border.all(color: Colors.red),
  ),
);

Pinput(
  length: 6,
  controller: pinController,
  defaultPinTheme: defaultPinTheme,
  focusedPinTheme: focusedPinTheme,
  submittedPinTheme: submittedPinTheme,
  errorPinTheme: errorPinTheme,
  pinputAutovalidateMode: PinputAutovalidateMode.onSubmit,
  validator: (value) {
    return value == '123456' ? null : '잘못된 코드입니다';
  },
)
```

### 밑줄 스타일

```dart
final defaultPinTheme = PinTheme(
  width: 56,
  height: 56,
  textStyle: TextStyle(fontSize: 22, fontWeight: FontWeight.w600),
  decoration: BoxDecoration(
    border: Border(
      bottom: BorderSide(color: Colors.grey[300]!, width: 2),
    ),
  ),
);
```

### 원형 스타일

```dart
final defaultPinTheme = PinTheme(
  width: 56,
  height: 56,
  textStyle: TextStyle(fontSize: 22),
  decoration: BoxDecoration(
    shape: BoxShape.circle,
    border: Border.all(color: Colors.grey[300]!),
  ),
);
```

### 에러 상태 처리

```dart
bool hasError = false;

Pinput(
  length: 6,
  controller: pinController,
  forceErrorState: hasError,
  errorPinTheme: errorPinTheme,
  onCompleted: (pin) async {
    final success = await verifyOtp(pin);
    if (!success) {
      setState(() => hasError = true);
      pinController.clear();
      // 진동 피드백
      HapticFeedback.heavyImpact();
    }
  },
)
```

### SMS 자동 완성 (Android)

```dart
Pinput(
  length: 6,
  controller: pinController,
  androidSmsAutofillMethod: AndroidSmsAutofillMethod.smsUserConsentApi,
  listenForMultipleSmsOnAndroid: true,
  onCompleted: (pin) => verifyOtp(pin),
)
```

### 입력 제한

```dart
Pinput(
  length: 6,
  controller: pinController,
  inputFormatters: [
    FilteringTextInputFormatter.digitsOnly,  // 숫자만
  ],
  keyboardType: TextInputType.number,
  obscureText: true,  // 비밀번호처럼 숨김
  obscuringCharacter: '●',
)
```

---

## 주의사항

| 상황 | 해결 |
|------|------|
| 키보드 안열림 | focusNode.requestFocus() 호출 |
| 자동완성 안됨 | SMS 형식 확인 (마지막에 코드) |
| 붙여넣기 안됨 | 기본 지원됨, length 확인 |
| 스타일 깨짐 | copyWith로 일관된 테마 유지 |
| dispose 누락 | controller, focusNode dispose 필수 |

---

## MFA 페이지 예시

→ [references/mfa-example.md](references/mfa-example.md) 참조

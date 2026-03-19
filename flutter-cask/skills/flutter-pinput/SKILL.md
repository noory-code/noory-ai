---
name: flutter-pinput
user-invocable: true
description: PIN/OTP code input widget
metadata:
  version: "1.1.0"
  category: flutter-lib
  type: unit
  style: guide
  triggers: [pinput, PIN input, OTP, verification code, 6-digit code]
---

# Flutter Pinput

A PIN/OTP code input widget for MFA authentication and SMS verification flows.

---

## Installation

```bash
flutter pub add pinput
```

---

## Quick Reference

### Basic Usage

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

### Custom Style

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
    return value == '123456' ? null : 'Invalid code';
  },
)
```

### Underline Style

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

### Circle Style

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

### Error State Handling

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
      // haptic feedback
      HapticFeedback.heavyImpact();
    }
  },
)
```

### SMS Auto-fill (Android)

```dart
Pinput(
  length: 6,
  controller: pinController,
  androidSmsAutofillMethod: AndroidSmsAutofillMethod.smsUserConsentApi,
  listenForMultipleSmsOnAndroid: true,
  onCompleted: (pin) => verifyOtp(pin),
)
```

### Input Restrictions

```dart
Pinput(
  length: 6,
  controller: pinController,
  inputFormatters: [
    FilteringTextInputFormatter.digitsOnly,  // digits only
  ],
  keyboardType: TextInputType.number,
  obscureText: true,  // hide input like a password
  obscuringCharacter: '●',
)
```

---

## Common Issues

| Issue | Fix |
|------|------|
| Keyboard not opening | Call focusNode.requestFocus() |
| Auto-fill not working | Check that the SMS format has the code at the end |
| Paste not working | Supported by default; check that the length is correct |
| Style inconsistency | Use copyWith to maintain a consistent theme |
| Missing dispose | Always dispose the controller and focusNode |

---

## MFA Page Example

See [references/mfa-example.md](references/mfa-example.md)

---

## Changelog

### [1.1.0] - 2026-03-01
- Initial release

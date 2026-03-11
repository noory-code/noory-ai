import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'theme_colors.dart';

// Layer 3 — AppTheme
// ColorScheme + TextTheme을 합쳐 ThemeData를 구성한다.
// 펜슬 Material Color Scheme 6개 variant와 1:1 대응.
//
// 사용법 (MaterialApp):
//   MaterialApp(
//     theme: AppTheme.light,
//     darkTheme: AppTheme.dark,
//     themeMode: ThemeMode.system,
//   )
//
//   // Medium/High Contrast 지원 시
//   MaterialApp(
//     theme: AppTheme.light,
//     darkTheme: AppTheme.dark,
//     highContrastTheme: AppTheme.lightHc,
//     highContrastDarkTheme: AppTheme.darkHc,
//   )
//
// 위젯에서 컬러 접근:
//   Theme.of(context).colorScheme.primary
//   Theme.of(context).colorScheme.surface
//
// 위젯에서 텍스트 스타일 접근:
//   Theme.of(context).textTheme.displayLarge
//   Theme.of(context).textTheme.bodyMedium
abstract final class AppTheme {
  /// light (기본) — 펜슬 Material Color Scheme: light
  static ThemeData get light => ThemeData(
        useMaterial3: true,
        colorScheme: ThemeColors.lightScheme,
        textTheme: _textTheme,
      );

  /// dark — 펜슬 Material Color Scheme: dark
  static ThemeData get dark => ThemeData(
        useMaterial3: true,
        colorScheme: ThemeColors.darkScheme,
        textTheme: _textTheme,
      );

  /// light Medium Contrast — 펜슬 Material Color Scheme: light-mc
  static ThemeData get lightMc => ThemeData(
        useMaterial3: true,
        colorScheme: ThemeColors.lightMcScheme,
        textTheme: _textTheme,
      );

  /// dark Medium Contrast — 펜슬 Material Color Scheme: dark-mc
  static ThemeData get darkMc => ThemeData(
        useMaterial3: true,
        colorScheme: ThemeColors.darkMcScheme,
        textTheme: _textTheme,
      );

  /// light High Contrast — 펜슬 Material Color Scheme: light-hc
  static ThemeData get lightHc => ThemeData(
        useMaterial3: true,
        colorScheme: ThemeColors.lightHcScheme,
        textTheme: _textTheme,
      );

  /// dark High Contrast — 펜슬 Material Color Scheme: dark-hc
  static ThemeData get darkHc => ThemeData(
        useMaterial3: true,
        colorScheme: ThemeColors.darkHcScheme,
        textTheme: _textTheme,
      );

  // M3 Type Scale — 펜슬 typography/ 토큰과 1:1 대응
  // Google Fonts Roboto 기준. 폰트만 교체하려면 여기서 변경.
  static TextTheme get _textTheme => GoogleFonts.robotoTextTheme(
        const TextTheme(
          // display
          displayLarge: TextStyle(fontSize: 57, height: 1.12, fontWeight: FontWeight.w300),   // typography/display/large
          displayMedium: TextStyle(fontSize: 45, height: 1.16, fontWeight: FontWeight.w300),  // typography/display/medium
          displaySmall: TextStyle(fontSize: 36, height: 1.22, fontWeight: FontWeight.w400),   // typography/display/small

          // headline
          headlineLarge: TextStyle(fontSize: 32, height: 1.25, fontWeight: FontWeight.w400),  // typography/headline/large
          headlineMedium: TextStyle(fontSize: 28, height: 1.29, fontWeight: FontWeight.w400), // typography/headline/medium
          headlineSmall: TextStyle(fontSize: 24, height: 1.33, fontWeight: FontWeight.w400),  // typography/headline/small

          // title
          titleLarge: TextStyle(fontSize: 22, height: 1.27, fontWeight: FontWeight.w400),     // typography/title/large
          titleMedium: TextStyle(fontSize: 16, height: 1.50, fontWeight: FontWeight.w500),    // typography/title/medium
          titleSmall: TextStyle(fontSize: 14, height: 1.43, fontWeight: FontWeight.w500),     // typography/title/small

          // body
          bodyLarge: TextStyle(fontSize: 16, height: 1.50, fontWeight: FontWeight.w400),      // typography/body/large
          bodyMedium: TextStyle(fontSize: 14, height: 1.43, fontWeight: FontWeight.w400),     // typography/body/medium
          bodySmall: TextStyle(fontSize: 12, height: 1.33, fontWeight: FontWeight.w400),      // typography/body/small

          // label
          labelLarge: TextStyle(fontSize: 14, height: 1.43, fontWeight: FontWeight.w500),     // typography/label/large
          labelMedium: TextStyle(fontSize: 12, height: 1.33, fontWeight: FontWeight.w500),    // typography/label/medium
          labelSmall: TextStyle(fontSize: 11, height: 1.45, fontWeight: FontWeight.w500),     // typography/label/small
        ),
      );
}

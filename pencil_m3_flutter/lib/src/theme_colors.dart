import 'package:flutter/material.dart';
import 'semantic_color_palette.dart';

// Layer 2 — Theme Colors
// SemanticColorPalette(팔레트 원시값)에서 6개 variant별 역할 색상을 정의한다.
// ColorScheme은 이 상수들을 참조한다.
//
// 사용법:
//   ThemeColors.light.primary     // 직접 참조 (드물게)
//   → 대부분은 Theme.of(context).colorScheme.primary 로 접근한다.
abstract final class ThemeColors {
  static const light   = _ThemeColorSet.light;
  static const dark    = _ThemeColorSet.dark;
  static const lightMc = _ThemeColorSet.lightMc;
  static const darkMc  = _ThemeColorSet.darkMc;
  static const lightHc = _ThemeColorSet.lightHc;
  static const darkHc  = _ThemeColorSet.darkHc;

  // ColorScheme 헬퍼 — AppTheme에서 사용
  static ColorScheme get lightScheme   => light.toColorScheme();
  static ColorScheme get darkScheme    => dark.toColorScheme();
  static ColorScheme get lightMcScheme => lightMc.toColorScheme();
  static ColorScheme get darkMcScheme  => darkMc.toColorScheme();
  static ColorScheme get lightHcScheme => lightHc.toColorScheme();
  static ColorScheme get darkHcScheme  => darkHc.toColorScheme();
}

// 각 variant의 색상 집합
final class _ThemeColorSet {
  final Brightness brightness;
  final Color primary;
  final Color onPrimary;
  final Color primaryContainer;
  final Color onPrimaryContainer;
  final Color secondary;
  final Color onSecondary;
  final Color secondaryContainer;
  final Color onSecondaryContainer;
  final Color tertiary;
  final Color onTertiary;
  final Color tertiaryContainer;
  final Color onTertiaryContainer;
  final Color error;
  final Color onError;
  final Color errorContainer;
  final Color onErrorContainer;
  final Color surface;
  final Color onSurface;
  final Color surfaceVariant;
  final Color onSurfaceVariant;
  final Color outline;
  final Color outlineVariant;
  final Color shadow;
  final Color scrim;
  final Color inverseSurface;
  final Color onInverseSurface;
  final Color inversePrimary;

  const _ThemeColorSet({
    required this.brightness,
    required this.primary,
    required this.onPrimary,
    required this.primaryContainer,
    required this.onPrimaryContainer,
    required this.secondary,
    required this.onSecondary,
    required this.secondaryContainer,
    required this.onSecondaryContainer,
    required this.tertiary,
    required this.onTertiary,
    required this.tertiaryContainer,
    required this.onTertiaryContainer,
    required this.error,
    required this.onError,
    required this.errorContainer,
    required this.onErrorContainer,
    required this.surface,
    required this.onSurface,
    required this.surfaceVariant,
    required this.onSurfaceVariant,
    required this.outline,
    required this.outlineVariant,
    required this.shadow,
    required this.scrim,
    required this.inverseSurface,
    required this.onInverseSurface,
    required this.inversePrimary,
  });

  ColorScheme toColorScheme() => ColorScheme(
        brightness: brightness,
        primary: primary,
        onPrimary: onPrimary,
        primaryContainer: primaryContainer,
        onPrimaryContainer: onPrimaryContainer,
        secondary: secondary,
        onSecondary: onSecondary,
        secondaryContainer: secondaryContainer,
        onSecondaryContainer: onSecondaryContainer,
        tertiary: tertiary,
        onTertiary: onTertiary,
        tertiaryContainer: tertiaryContainer,
        onTertiaryContainer: onTertiaryContainer,
        error: error,
        onError: onError,
        errorContainer: errorContainer,
        onErrorContainer: onErrorContainer,
        surface: surface,
        onSurface: onSurface,
        surfaceContainerHighest: surfaceVariant,
        onSurfaceVariant: onSurfaceVariant,
        outline: outline,
        outlineVariant: outlineVariant,
        shadow: shadow,
        scrim: scrim,
        inverseSurface: inverseSurface,
        onInverseSurface: onInverseSurface,
        inversePrimary: inversePrimary,
      );

  // --- light ---
  static const light = _ThemeColorSet(
    brightness: Brightness.light,
    primary: SemanticColorPalette.primary40,
    onPrimary: SemanticColorPalette.primary100,
    primaryContainer: SemanticColorPalette.primary90,
    onPrimaryContainer: SemanticColorPalette.primary10,
    secondary: SemanticColorPalette.secondary40,
    onSecondary: SemanticColorPalette.secondary100,
    secondaryContainer: SemanticColorPalette.secondary90,
    onSecondaryContainer: SemanticColorPalette.secondary10,
    tertiary: SemanticColorPalette.tertiary40,
    onTertiary: SemanticColorPalette.tertiary100,
    tertiaryContainer: SemanticColorPalette.tertiary90,
    onTertiaryContainer: SemanticColorPalette.tertiary10,
    error: SemanticColorPalette.error40,
    onError: SemanticColorPalette.error100,
    errorContainer: SemanticColorPalette.error90,
    onErrorContainer: SemanticColorPalette.error10,
    surface: SemanticColorPalette.neutral99,
    onSurface: SemanticColorPalette.neutral10,
    surfaceVariant: SemanticColorPalette.neutralVariant90,
    onSurfaceVariant: SemanticColorPalette.neutralVariant30,
    outline: SemanticColorPalette.neutralVariant50,
    outlineVariant: SemanticColorPalette.neutralVariant80,
    shadow: SemanticColorPalette.neutral0,
    scrim: SemanticColorPalette.neutral0,
    inverseSurface: SemanticColorPalette.neutral20,
    onInverseSurface: SemanticColorPalette.neutral95,
    inversePrimary: SemanticColorPalette.primary80,
  );

  // --- dark ---
  static const dark = _ThemeColorSet(
    brightness: Brightness.dark,
    primary: SemanticColorPalette.primary80,
    onPrimary: SemanticColorPalette.primary20,
    primaryContainer: SemanticColorPalette.primary30,
    onPrimaryContainer: SemanticColorPalette.primary90,
    secondary: SemanticColorPalette.secondary80,
    onSecondary: SemanticColorPalette.secondary20,
    secondaryContainer: SemanticColorPalette.secondary30,
    onSecondaryContainer: SemanticColorPalette.secondary90,
    tertiary: SemanticColorPalette.tertiary80,
    onTertiary: SemanticColorPalette.tertiary20,
    tertiaryContainer: SemanticColorPalette.tertiary30,
    onTertiaryContainer: SemanticColorPalette.tertiary90,
    error: SemanticColorPalette.error80,
    onError: SemanticColorPalette.error20,
    errorContainer: SemanticColorPalette.error30,
    onErrorContainer: SemanticColorPalette.error90,
    surface: SemanticColorPalette.neutral10,
    onSurface: SemanticColorPalette.neutral90,
    surfaceVariant: SemanticColorPalette.neutralVariant30,
    onSurfaceVariant: SemanticColorPalette.neutralVariant80,
    outline: SemanticColorPalette.neutralVariant60,
    outlineVariant: SemanticColorPalette.neutralVariant30,
    shadow: SemanticColorPalette.neutral0,
    scrim: SemanticColorPalette.neutral0,
    inverseSurface: SemanticColorPalette.neutral90,
    onInverseSurface: SemanticColorPalette.neutral20,
    inversePrimary: SemanticColorPalette.primary40,
  );

  // --- light-mc (Medium Contrast) ---
  static const lightMc = _ThemeColorSet(
    brightness: Brightness.light,
    primary: SemanticColorPalette.primary30,
    onPrimary: SemanticColorPalette.primary100,
    primaryContainer: SemanticColorPalette.primary80,
    onPrimaryContainer: SemanticColorPalette.primary10,
    secondary: SemanticColorPalette.secondary30,
    onSecondary: SemanticColorPalette.secondary100,
    secondaryContainer: SemanticColorPalette.secondary80,
    onSecondaryContainer: SemanticColorPalette.secondary10,
    tertiary: SemanticColorPalette.tertiary30,
    onTertiary: SemanticColorPalette.tertiary100,
    tertiaryContainer: SemanticColorPalette.tertiary80,
    onTertiaryContainer: SemanticColorPalette.tertiary10,
    error: SemanticColorPalette.error30,
    onError: SemanticColorPalette.error100,
    errorContainer: SemanticColorPalette.error80,
    onErrorContainer: SemanticColorPalette.error10,
    surface: SemanticColorPalette.neutral99,
    onSurface: SemanticColorPalette.neutral10,
    surfaceVariant: SemanticColorPalette.neutralVariant90,
    onSurfaceVariant: SemanticColorPalette.neutralVariant20,
    outline: SemanticColorPalette.neutralVariant40,
    outlineVariant: SemanticColorPalette.neutralVariant70,
    shadow: SemanticColorPalette.neutral0,
    scrim: SemanticColorPalette.neutral0,
    inverseSurface: SemanticColorPalette.neutral20,
    onInverseSurface: SemanticColorPalette.neutral95,
    inversePrimary: SemanticColorPalette.primary80,
  );

  // --- dark-mc (Medium Contrast) ---
  static const darkMc = _ThemeColorSet(
    brightness: Brightness.dark,
    primary: SemanticColorPalette.primary90,
    onPrimary: SemanticColorPalette.primary10,
    primaryContainer: SemanticColorPalette.primary20,
    onPrimaryContainer: SemanticColorPalette.primary90,
    secondary: SemanticColorPalette.secondary90,
    onSecondary: SemanticColorPalette.secondary10,
    secondaryContainer: SemanticColorPalette.secondary20,
    onSecondaryContainer: SemanticColorPalette.secondary90,
    tertiary: SemanticColorPalette.tertiary90,
    onTertiary: SemanticColorPalette.tertiary10,
    tertiaryContainer: SemanticColorPalette.tertiary20,
    onTertiaryContainer: SemanticColorPalette.tertiary90,
    error: SemanticColorPalette.error90,
    onError: SemanticColorPalette.error10,
    errorContainer: SemanticColorPalette.error20,
    onErrorContainer: SemanticColorPalette.error90,
    surface: SemanticColorPalette.neutral10,
    onSurface: SemanticColorPalette.neutral90,
    surfaceVariant: SemanticColorPalette.neutralVariant30,
    onSurfaceVariant: SemanticColorPalette.neutralVariant90,
    outline: SemanticColorPalette.neutralVariant70,
    outlineVariant: SemanticColorPalette.neutralVariant40,
    shadow: SemanticColorPalette.neutral0,
    scrim: SemanticColorPalette.neutral0,
    inverseSurface: SemanticColorPalette.neutral90,
    onInverseSurface: SemanticColorPalette.neutral20,
    inversePrimary: SemanticColorPalette.primary40,
  );

  // --- light-hc (High Contrast) ---
  static const lightHc = _ThemeColorSet(
    brightness: Brightness.light,
    primary: SemanticColorPalette.primary10,
    onPrimary: SemanticColorPalette.primary100,
    primaryContainer: SemanticColorPalette.primary95,
    onPrimaryContainer: SemanticColorPalette.primary0,
    secondary: SemanticColorPalette.secondary10,
    onSecondary: SemanticColorPalette.secondary100,
    secondaryContainer: SemanticColorPalette.secondary95,
    onSecondaryContainer: SemanticColorPalette.secondary0,
    tertiary: SemanticColorPalette.tertiary10,
    onTertiary: SemanticColorPalette.tertiary100,
    tertiaryContainer: SemanticColorPalette.tertiary95,
    onTertiaryContainer: SemanticColorPalette.tertiary0,
    error: SemanticColorPalette.error10,
    onError: SemanticColorPalette.error100,
    errorContainer: SemanticColorPalette.error95,
    onErrorContainer: SemanticColorPalette.error0,
    surface: SemanticColorPalette.neutral100,
    onSurface: SemanticColorPalette.neutral0,
    surfaceVariant: SemanticColorPalette.neutralVariant95,
    onSurfaceVariant: SemanticColorPalette.neutralVariant10,
    outline: SemanticColorPalette.neutralVariant10,
    outlineVariant: SemanticColorPalette.neutralVariant50,
    shadow: SemanticColorPalette.neutral0,
    scrim: SemanticColorPalette.neutral0,
    inverseSurface: SemanticColorPalette.neutral10,
    onInverseSurface: SemanticColorPalette.neutral100,
    inversePrimary: SemanticColorPalette.primary90,
  );

  // --- dark-hc (High Contrast) ---
  static const darkHc = _ThemeColorSet(
    brightness: Brightness.dark,
    primary: SemanticColorPalette.primary95,
    onPrimary: SemanticColorPalette.primary10,
    primaryContainer: SemanticColorPalette.primary10,
    onPrimaryContainer: SemanticColorPalette.primary100,
    secondary: SemanticColorPalette.secondary95,
    onSecondary: SemanticColorPalette.secondary10,
    secondaryContainer: SemanticColorPalette.secondary10,
    onSecondaryContainer: SemanticColorPalette.secondary100,
    tertiary: SemanticColorPalette.tertiary95,
    onTertiary: SemanticColorPalette.tertiary10,
    tertiaryContainer: SemanticColorPalette.tertiary10,
    onTertiaryContainer: SemanticColorPalette.tertiary100,
    error: SemanticColorPalette.error95,
    onError: SemanticColorPalette.error10,
    errorContainer: SemanticColorPalette.error10,
    onErrorContainer: SemanticColorPalette.error100,
    surface: SemanticColorPalette.neutral0,
    onSurface: SemanticColorPalette.neutral100,
    surfaceVariant: SemanticColorPalette.neutralVariant20,
    onSurfaceVariant: SemanticColorPalette.neutralVariant95,
    outline: SemanticColorPalette.neutralVariant95,
    outlineVariant: SemanticColorPalette.neutralVariant50,
    shadow: SemanticColorPalette.neutral0,
    scrim: SemanticColorPalette.neutral0,
    inverseSurface: SemanticColorPalette.neutral95,
    onInverseSurface: SemanticColorPalette.neutral0,
    inversePrimary: SemanticColorPalette.primary30,
  );
}

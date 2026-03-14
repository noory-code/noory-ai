import 'package:flutter/material.dart';

// Layer 1 — Semantic Color Palette
// 펜슬 material-design-guide.lib.pen 의 팔레트 토큰을 그대로 옮긴 원시 값.
// 이 값을 직접 UI에 쓰지 말 것. AppSemanticColors 또는 colorScheme을 사용한다.
abstract final class SemanticColorPalette {
  /// Seed color — HCT 알고리즘으로 팔레트 전체를 생성한 기준 색상
  static const Color seed = Color(0xFFE91E63);
  // --- Primary ---
  static const Color primary0 = Color(0xFF000000);
  static const Color primary10 = Color(0xFF3E0021);
  static const Color primary20 = Color(0xFF650038);
  static const Color primary30 = Color(0xFF8E0050);
  static const Color primary40 = Color(0xFFB3006A);
  static const Color primary50 = Color(0xFFD81B7B);
  static const Color primary60 = Color(0xFFF04D96);
  static const Color primary70 = Color(0xFFFF80B1);
  static const Color primary80 = Color(0xFFFFB0CB);
  static const Color primary90 = Color(0xFFFFD9E4);
  static const Color primary95 = Color(0xFFFFECF0);
  static const Color primary99 = Color(0xFFFFFBFF);
  static const Color primary100 = Color(0xFFFFFFFF);

  // --- Secondary ---
  static const Color secondary0 = Color(0xFF000000);
  static const Color secondary10 = Color(0xFF2C1519);
  static const Color secondary20 = Color(0xFF432930);
  static const Color secondary30 = Color(0xFF5B3E46);
  static const Color secondary40 = Color(0xFF75545D);
  static const Color secondary50 = Color(0xFF906C76);
  static const Color secondary60 = Color(0xFFAB868F);
  static const Color secondary70 = Color(0xFFC7A0AA);
  static const Color secondary80 = Color(0xFFE3BBC5);
  static const Color secondary90 = Color(0xFFFFD8E1);
  static const Color secondary95 = Color(0xFFFFECF0);
  static const Color secondary99 = Color(0xFFFFFBFF);
  static const Color secondary100 = Color(0xFFFFFFFF);

  // --- Tertiary ---
  static const Color tertiary0 = Color(0xFF000000);
  static const Color tertiary10 = Color(0xFF2B1700);
  static const Color tertiary20 = Color(0xFF452B00);
  static const Color tertiary30 = Color(0xFF614000);
  static const Color tertiary40 = Color(0xFF7E5700);
  static const Color tertiary50 = Color(0xFF9D6F00);
  static const Color tertiary60 = Color(0xFFBC8700);
  static const Color tertiary70 = Color(0xFFDCA000);
  static const Color tertiary80 = Color(0xFFF9BA2E);
  static const Color tertiary90 = Color(0xFFFFDEA0);
  static const Color tertiary95 = Color(0xFFFEFFD4);
  static const Color tertiary99 = Color(0xFFFFFBFF);
  static const Color tertiary100 = Color(0xFFFFFFFF);

  // --- Neutral ---
  static const Color neutral0 = Color(0xFF000000);
  static const Color neutral10 = Color(0xFF201A1B);
  static const Color neutral20 = Color(0xFF362F30);
  static const Color neutral30 = Color(0xFF4D4546);
  static const Color neutral40 = Color(0xFF655C5D);
  static const Color neutral50 = Color(0xFF7F7475);
  static const Color neutral60 = Color(0xFF998E8F);
  static const Color neutral70 = Color(0xFFB4A8A9);
  static const Color neutral80 = Color(0xFFD0C4C4);
  static const Color neutral90 = Color(0xFFEDE0E1);
  static const Color neutral95 = Color(0xFFFBF0F0);
  static const Color neutral99 = Color(0xFFFFFBFF);
  static const Color neutral100 = Color(0xFFFFFFFF);

  // --- Neutral Variant ---
  static const Color neutralVariant0 = Color(0xFF000000);
  static const Color neutralVariant10 = Color(0xFF24191C);
  static const Color neutralVariant20 = Color(0xFF3A2D31);
  static const Color neutralVariant30 = Color(0xFF524347);
  static const Color neutralVariant40 = Color(0xFF6B5A5E);
  static const Color neutralVariant50 = Color(0xFF857277);
  static const Color neutralVariant60 = Color(0xFF9F8C90);
  static const Color neutralVariant70 = Color(0xFFBBA6AB);
  static const Color neutralVariant80 = Color(0xFFD7C1C6);
  static const Color neutralVariant90 = Color(0xFFF4DDE2);
  static const Color neutralVariant95 = Color(0xFFFFEDF0);
  static const Color neutralVariant99 = Color(0xFFFFFBFF);
  static const Color neutralVariant100 = Color(0xFFFFFFFF);

  // --- Error ---
  static const Color error0 = Color(0xFF000000);
  static const Color error10 = Color(0xFF410002);
  static const Color error20 = Color(0xFF690005);
  static const Color error30 = Color(0xFF93000A);
  static const Color error40 = Color(0xFFBA1A1A);
  static const Color error50 = Color(0xFFDE3730);
  static const Color error60 = Color(0xFFFF5449);
  static const Color error70 = Color(0xFFFF897D);
  static const Color error80 = Color(0xFFFFB4AB);
  static const Color error90 = Color(0xFFFFDAD6);
  static const Color error95 = Color(0xFFFFEDEA);
  static const Color error99 = Color(0xFFFFFBFF);
  static const Color error100 = Color(0xFFFFFFFF);
}

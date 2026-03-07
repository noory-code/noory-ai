#!/bin/bash

# Flutter 스킬의 패키지 버전 체크 스크립트
# pub.dev API를 사용하여 최신 버전과 비교

set -e

SKILLS_DIR="skills"
OUTPUT_FILE="version-report.md"
EXIT_CODE=0

echo "# Flutter 스킬 버전 체크 보고서" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "생성 시각: $(date -u +"%Y-%m-%d %H:%M:%S UTC")" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| 스킬 | 패키지 | 문서화된 버전 | 최신 버전 | 상태 |" >> "$OUTPUT_FILE"
echo "|------|--------|--------------|----------|------|" >> "$OUTPUT_FILE"

# 스킬별 패키지 이름 매핑
declare -A PACKAGE_MAP
PACKAGE_MAP["flutter-riverpod"]="flutter_riverpod"
PACKAGE_MAP["flutter-freezed"]="freezed"
PACKAGE_MAP["flutter-go-router"]="go_router"
PACKAGE_MAP["flutter-hive"]="hive"
PACKAGE_MAP["flutter-secure-storage"]="flutter_secure_storage"
PACKAGE_MAP["flutter-firebase-analytics"]="firebase_analytics"
PACKAGE_MAP["flutter-firebase-crashlytics"]="firebase_crashlytics"
PACKAGE_MAP["flutter-firebase-messaging"]="firebase_messaging"
PACKAGE_MAP["flutter-firebase-performance"]="firebase_performance"
PACKAGE_MAP["flutter-screenutil"]="flutter_screenutil"
PACKAGE_MAP["flutter-shimmer"]="shimmer"
PACKAGE_MAP["flutter-svg"]="flutter_svg"
PACKAGE_MAP["flutter-google-fonts"]="google_fonts"
PACKAGE_MAP["flutter-pinput"]="pinput"
PACKAGE_MAP["flutter-quill"]="flutter_quill"
PACKAGE_MAP["flutter-image-picker"]="image_picker"
PACKAGE_MAP["flutter-cached-image"]="cached_network_image"
PACKAGE_MAP["flutter-webview"]="webview_flutter"
PACKAGE_MAP["flutter-local-notifications"]="flutter_local_notifications"
PACKAGE_MAP["flutter-geolocator"]="geolocator"
PACKAGE_MAP["flutter-package-info"]="package_info_plus"
PACKAGE_MAP["flutter-connectivity"]="connectivity_plus"
PACKAGE_MAP["flutter-quick-actions"]="quick_actions"
PACKAGE_MAP["flutter-share"]="share_plus"
PACKAGE_MAP["flutter-admob"]="google_mobile_ads"
PACKAGE_MAP["flutter-in-app-purchase"]="in_app_purchase"
PACKAGE_MAP["flutter-talker"]="talker"
PACKAGE_MAP["flutter-fvm"]="fvm"
PACKAGE_MAP["flutter-melos"]="melos"

check_package_version() {
  local skill_name=$1
  local package_name=$2

  # pub.dev API에서 최신 버전 조회
  local latest_version=$(curl -s "https://pub.dev/api/packages/${package_name}" | \
    grep -o '"latest":{"version":"[^"]*"' | \
    head -1 | \
    sed 's/.*"version":"\([^"]*\)".*/\1/')

  if [ -z "$latest_version" ]; then
    echo "| $skill_name | $package_name | - | ❌ API 오류 | ⚠️ 확인 불가 |" >> "$OUTPUT_FILE"
    return
  fi

  # SKILL.md에서 문서화된 버전 추출 (metadata.version)
  local skill_file="${SKILLS_DIR}/${skill_name}/SKILL.md"
  local doc_version=$(grep -A 5 "^metadata:" "$skill_file" | grep "version:" | sed 's/.*version: "\([^"]*\)".*/\1/')

  # 버전 비교
  if [ "$doc_version" != "$latest_version" ]; then
    echo "| $skill_name | $package_name | $doc_version | $latest_version | ⚠️ 업데이트 필요 |" >> "$OUTPUT_FILE"
    EXIT_CODE=1
  else
    echo "| $skill_name | $package_name | $doc_version | $latest_version | ✅ 최신 |" >> "$OUTPUT_FILE"
  fi
}

# 각 스킬 체크
for skill_name in "${!PACKAGE_MAP[@]}"; do
  if [ -d "${SKILLS_DIR}/${skill_name}" ]; then
    echo "체크 중: $skill_name"
    check_package_version "$skill_name" "${PACKAGE_MAP[$skill_name]}"
    sleep 0.5  # API rate limiting 방지
  fi
done

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [ $EXIT_CODE -eq 0 ]; then
  echo "## ✅ 결과: 모든 스킬이 최신 상태입니다" >> "$OUTPUT_FILE"
else
  echo "## ⚠️ 결과: 일부 스킬에 업데이트가 필요합니다" >> "$OUTPUT_FILE"
  echo "" >> "$OUTPUT_FILE"
  echo "업데이트가 필요한 스킬을 확인하고 \`update-flutter-skills\` 스킬을 사용하여 업데이트하세요." >> "$OUTPUT_FILE"
fi

cat "$OUTPUT_FILE"

exit $EXIT_CODE

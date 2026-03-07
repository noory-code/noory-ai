#!/bin/bash

# Flutter Cask - 새 스킬 생성 스크립트
# Usage: ./new-skill.sh <skill-name> <package-name>
# Example: ./new-skill.sh flutter-dio dio

set -e

# 인자 확인
if [ "$#" -lt 2 ]; then
  echo "Usage: ./new-skill.sh <skill-name> <package-name>"
  echo "Example: ./new-skill.sh flutter-dio dio"
  exit 1
fi

SKILL_NAME=$1
PACKAGE_NAME=$2
SKILL_DIR="skills/${SKILL_NAME}"
TEMPLATE_DIR="skills/template"

# 스킬 디렉토리가 이미 존재하는지 확인
if [ -d "$SKILL_DIR" ]; then
  echo "❌ Error: Skill directory already exists: $SKILL_DIR"
  exit 1
fi

# 템플릿 디렉토리 확인
if [ ! -d "$TEMPLATE_DIR" ]; then
  echo "❌ Error: Template directory not found: $TEMPLATE_DIR"
  exit 1
fi

# 스킬 디렉토리 생성
echo "📁 Creating skill directory: $SKILL_DIR"
mkdir -p "$SKILL_DIR"

# 템플릿 복사 및 치환
echo "📝 Generating SKILL.md from template"

# 패키지명 첫 글자 대문자로 변환 (bash 3.x 호환)
TITLE_CASE=$(echo "${PACKAGE_NAME}" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}')

sed -e "s/{{SKILL_NAME}}/${SKILL_NAME}/g" \
    -e "s/{{PACKAGE_NAME}}/${PACKAGE_NAME}/g" \
    -e "s/{{DESCRIPTION}}/Flutter ${PACKAGE_NAME} 패키지 사용 가이드/g" \
    -e "s/{{TITLE}}/Flutter ${TITLE_CASE}/g" \
    -e "s/{{SHORT_DESCRIPTION}}/${PACKAGE_NAME} 패키지를 사용한 Flutter 개발 가이드/g" \
    -e "s/{{TRIGGER_KEYWORDS}}/${PACKAGE_NAME}/g" \
    -e "s/{{COMMON_ISSUE}}/패키지 설치 오류/g" \
    -e "s/{{FIX_DESCRIPTION}}/flutter pub get을 실행하고 재시작/g" \
    "${TEMPLATE_DIR}/SKILL.md" > "${SKILL_DIR}/SKILL.md"

echo ""
echo "✅ Skill created successfully!"
echo ""
echo "📂 Location: ${SKILL_DIR}/"
echo "📄 Next steps:"
echo "   1. Edit ${SKILL_DIR}/SKILL.md with package-specific details"
echo "   2. Add code examples to Quick Reference section"
echo "   3. Update Common Issues table with real issues"
echo "   4. (Optional) Create references/ directory for additional docs"
echo ""
echo "📚 See CONTRIBUTING.md for skill structure guidelines"

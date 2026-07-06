#!/bin/bash
# 颜色验证脚本 - 检查是否还有旧配色残留

echo "=================================="
echo "🎨 护眼配色验证脚本"
echo "=================================="
echo ""

# 定义要检查的旧颜色
OLD_COLORS=(
  "#667eea"
  "#764ba2"
  "#f093fb"
  "#f5576c"
  "#409eff"
  "#4facfe"
  "#00f2fe"
  "#fa709a"
  "#fee140"
  "#1e1e2e"
  "#2d2d44"
  "#f5f7fa"
  "#606266"
  "#909399"
  "#e4e7ed"
)

# 定义检查的文件类型
FILE_TYPES=("*.vue" "*.scss" "*.css" "*.ts")

# 统计变量
TOTAL_ISSUES=0
FILES_CHECKED=0

echo "📂 检查文件..."
echo ""

# 遍历所有前端文件
for pattern in "${FILE_TYPES[@]}"; do
  while IFS= read -r file; do
    if [ -f "$file" ]; then
      FILES_CHECKED=$((FILES_CHECKED + 1))
      FILE_HAS_ISSUE=0

      for color in "${OLD_COLORS[@]}"; do
        if grep -q "$color" "$file" 2>/dev/null; then
          if [ $FILE_HAS_ISSUE -eq 0 ]; then
            echo "⚠️  发现旧配色: $file"
            FILE_HAS_ISSUE=1
          fi
          echo "   - 颜色: $color"
          grep -n "$color" "$file" | head -2 | while read -r line; do
            echo "     $line"
          done
          TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
        fi
      done

      if [ $FILE_HAS_ISSUE -eq 1 ]; then
        echo ""
      fi
    fi
  done < <(find frontend-vue/src -type f -name "$pattern" 2>/dev/null)
done

echo "=================================="
echo "📊 检查结果"
echo "=================================="
echo "检查文件数: $FILES_CHECKED"
echo "发现问题数: $TOTAL_ISSUES"
echo ""

if [ $TOTAL_ISSUES -eq 0 ]; then
  echo "✅ 所有文件配色已更新为护眼配色！"
  exit 0
else
  echo "⚠️  发现 $TOTAL_ISSUES 处旧配色，建议检查并更新"
  exit 1
fi

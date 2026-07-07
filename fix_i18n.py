#!/usr/bin/env python3
"""
Fix i18n file structure by moving orphaned content to correct locations
"""

with open('/home/user/nlp_project/frontend-vue/src/i18n/index.ts', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Find the line numbers (0-indexed)
# zh-CN success ends around line 219 (0-indexed: 218)
# en-US success ends around line 436 (0-indexed: 435)
# Orphaned en-US content starts around line 447 (0-indexed: 446)
# Orphaned zh-CN content starts around line 795 (0-indexed: 794)

# Find exact positions
zh_cn_success_end_idx = None
en_us_success_end_idx = None
orphaned_en_start_idx = None
orphaned_zh_start_idx = None

for i, line in enumerate(lines):
    # Find zh-CN closing after success section
    if i > 215 and i < 225 and line.strip() == '},' and i > 0 and 'copySuccess' in lines[i-1]:
        zh_cn_success_end_idx = i
    # Find en-US success closing
    elif i > 432 and i < 442 and line.strip() == '},' and i > 0 and 'copySuccess' in lines[i-1]:
        en_us_success_end_idx = i
    # Find orphaned en-US content (after createI18n, looking for 'upload:')
    elif 'upload:' in line and i > 440 and i < 460 and line.strip().startswith('upload:'):
        orphaned_en_start_idx = i
    # Find orphaned zh-CN content
    elif '// 文本增强分析' in line and i > 790:
        orphaned_zh_start_idx = i

print(f"zh-CN success ends at index: {zh_cn_success_end_idx} (line {zh_cn_success_end_idx + 1 if zh_cn_success_end_idx else 'N/A'})")
print(f"en-US success ends at index: {en_us_success_end_idx} (line {en_us_success_end_idx + 1 if en_us_success_end_idx else 'N/A'})")
print(f"Orphaned en-US starts at index: {orphaned_en_start_idx} (line {orphaned_en_start_idx + 1 if orphaned_en_start_idx else 'N/A'})")
print(f"Orphaned zh-CN starts at index: {orphaned_zh_start_idx} (line {orphaned_zh_start_idx + 1 if orphaned_zh_start_idx else 'N/A'})")

# Show context
if orphaned_en_start_idx:
    print(f"\nOrphaned en-US content (lines {orphaned_en_start_idx + 1} to {orphaned_en_start_idx + 10}):")
    for i in range(orphaned_en_start_idx, min(len(lines), orphaned_en_start_idx + 10)):
        print(f"{i+1}: {lines[i]}")

if orphaned_zh_start_idx:
    print(f"\nOrphaned zh-CN content (lines {orphaned_zh_start_idx + 1} to {orphaned_zh_start_idx + 10}):")
    for i in range(orphaned_zh_start_idx, min(len(lines), orphaned_zh_start_idx + 10)):
        print(f"{i+1}: {lines[i]}")

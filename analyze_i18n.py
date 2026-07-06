#!/usr/bin/env python3
import re

# Read the file
with open('/home/user/nlp_project/frontend-vue/src/i18n/index.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find key positions
zh_cn_end = None
en_us_success_end = None
orphaned_zh_start = None
orphaned_en_start = None

for i, line in enumerate(lines):
    # Find where zh-CN ends (after 'success' section)
    if i > 200 and i < 230 and line.strip() == '},' and 'copySuccess' in lines[i-1]:
        zh_cn_end = i

    # Find where en-US success section ends
    if i > 430 and i < 450 and line.strip() == '},' and 'copySuccess' in lines[i-1]:
        en_us_success_end = i

    # Find start of orphaned zh-CN content (textAnalysis in Chinese)
    if '// 文本增强分析' in line and i > 790:
        orphaned_zh_start = i

    # Find start of orphaned en-US content (after createI18n)
    if 'upload:' in line and i > 440 and i < 460:
        orphaned_en_start = i

print(f"zh-CN ends at line: {zh_cn_end}")
print(f"en-US success ends at line: {en_us_success_end}")
print(f"Orphaned zh-CN content starts at: {orphaned_zh_start}")
print(f"Orphaned en-US content starts at: {orphaned_en_start}")

# Show context around key lines
if zh_cn_end:
    print(f"\nContext around zh-CN end (lines {zh_cn_end-2} to {zh_cn_end+3}):")
    for i in range(max(0, zh_cn_end-2), min(len(lines), zh_cn_end+3)):
        print(f"{i+1}: {lines[i]}", end='')

if en_us_success_end:
    print(f"\n\nContext around en-US success end (lines {en_us_success_end-2} to {en_us_success_end+5}):")
    for i in range(max(0, en_us_success_end-2), min(len(lines), en_us_success_end+5)):
        print(f"{i+1}: {lines[i]}", end='')

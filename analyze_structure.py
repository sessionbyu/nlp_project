#!/usr/bin/env python3
"""
Complete fix for i18n file structure
"""

with open('/home/user/nlp_project/frontend-vue/src/i18n/index.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# The file should have this structure:
# Line 1-4: imports
# Line 5: const messages: LocaleMessages = {
# Line 6-221: zh-CN (with missing upload, tasks, monitoring, textAnalysis, profile at the end)
# Line 223-...: en-US (with missing upload, tasks, monitoring at line 437+)
# ...: close messages
# ...: createI18n

# Current problem:
# 1. en-US ends at line 439 but should continue with upload, tasks, monitoring
# 2. zh-CN ends at line 221 but should continue with textAnalysis, profile
# 3. There's orphaned content after createI18n

# The orphaned content is:
# - Lines 447-523: en-US upload, tasks (up to tasks validation section)
# - Lines 523-795: continues with more en-US content (tasks end, monitoring, etc)
# - Lines 796-970: zh-CN content (textAnalysis, profile)

# Let's find exact line breaks
lines = content.split('\n')

# Find where to insert zh-CN missing content (after zh-CN success section)
zh_cn_insert_point = None
en_us_insert_point = None

for i, line in enumerate(lines):
    # Find the end of zh-CN success section
    if i > 215 and i < 225 and 'copySuccess' in lines[i-1] and line.strip() == '},':
        zh_cn_insert_point = i
    # Find the end of en-US success section
    elif i > 432 and i < 442 and 'copySuccess' in lines[i-1] and line.strip() == '},':
        en_us_insert_point = i

print(f"Will insert zh-CN content after line {zh_cn_insert_point + 1}")
print(f"Will insert en-US content after line {en_us_insert_point + 1}")

# Find orphaned content sections
# en-US orphaned content starts at line 447 (0-indexed: 446)
# zh-CN orphaned content starts at line 796 (0-indexed: 795)
orphaned_en_start = None
orphaned_zh_start = None

for i, line in enumerate(lines):
    if '// File Upload' in line and i > 440 and i < 460:
        orphaned_en_start = i
    elif '// 文本增强分析' in line and i > 790:
        orphaned_zh_start = i

print(f"Orphaned en-US content starts at line {orphaned_en_start + 1}")
print(f"Orphaned zh-CN content starts at line {orphaned_zh_start + 1}")

# Find where orphaned en-US ends (before orphaned zh-CN starts)
orphaned_en_end = orphaned_zh_start - 1 if orphaned_zh_start else None
print(f"Orphaned en-US content ends at line {orphaned_en_end + 1 if orphaned_en_end else 'N/A'}")

# Find where orphaned zh-CN ends (at end of file or before createI18n)
# Actually, orphaned zh-CN is at the end, so we need to find where it ends
# Let's find the last '},' before EOF
orphaned_zh_end = len(lines) - 1
for i in range(len(lines) - 1, orphaned_zh_start, -1):
    if lines[i].strip() == '},':
        orphaned_zh_end = i
        break

print(f"Orphaned zh-CN content ends at line {orphaned_zh_end + 1}")

# Extract the orphaned content
orphaned_en_lines = lines[orphaned_en_start:orphaned_en_end]
orphaned_zh_lines = lines[orphaned_zh_start:orphaned_zh_end + 1]

print(f"\nOrphaned en-US has {len(orphaned_en_lines)} lines")
print(f"Orphaned zh-CN has {len(orphaned_zh_lines)} lines")

# Build new content
# 1. Lines before en-US insert point (0 to en_us_insert_point)
# 2. Insert orphaned en-US content (with proper indentation)
# 3. Lines from en-US insert point to createI18n
# 4. Close en-US and messages properly
# 5. createI18n and rest of file

# Let's find where the messages object should close
# It should be after the last content of en-US
# Currently at line 439 (index 438)
create_i18n_start = None
for i, line in enumerate(lines):
    if 'const i18n = createI18n(' in line and i > 440:
        create_i18n_start = i
        break

print(f"\ncreateI18n starts at line {create_i18n_start + 1}")

# Show what's between en-US insert point and createI18n
if en_us_insert_point and create_i18n_start:
    print(f"\nContent between en-US insert and createI18n (lines {en_us_insert_point + 1} to {create_i18n_start + 1}):")
    for i in range(en_us_insert_point, min(en_us_insert_point + 5, create_i18n_start)):
        print(f"{i+1}: {lines[i]}")
    print("...")
    for i in range(create_i18n_start - 3, create_i18n_start + 3):
        print(f"{i+1}: {lines[i]}")

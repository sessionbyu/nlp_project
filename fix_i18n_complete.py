#!/usr/bin/env python3
"""
Fix i18n file by reorganizing content into proper structure
"""

with open('/home/user/nlp_project/frontend-vue/src/i18n/index.ts', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Section boundaries (1-indexed line numbers):
# zh-CN part 1: lines 1-221
# zh-CN part 2: lines 796-970 (textAnalysis, profile)
# en-US part 1: lines 223-437
# en-US part 2: lines 524-795 (upload, tasks, monitoring, textAnalysis, profile in English)
# createI18n: lines 441-447

# Convert to 0-indexed
zh_cn1_end = 220  # exclusive
zh_cn2_start = 795  # line 796
zh_cn2_end = 969  # line 970 (exclusive)

en_us1_start = 222  # line 223 (0-indexed: 222)
en_us1_end = 437  # exclusive
en_us2_start = 523  # line 524
en_us2_end = 795  # exclusive (line 795)

create_i18n_start = 440  # line 441

# Extract sections
import_section = lines[:5]  # Lines 1-5 (imports and messages start)
zh_cn1 = lines[5:zh_cn1_end]  # Lines 6-220 (zh-CN part 1)
en_us1 = lines[en_us1_start:en_us1_end]  # Lines 223-437 (en-US part 1)
orphaned_zh = lines[zh_cn2_start:zh_cn2_end]  # Lines 796-969 (zh-CN part 2)
orphaned_en = lines[en_us2_start:en_us2_end]  # Lines 524-795 (en-US part 2)
create_i18n_section = lines[create_i18n_start:]  # Lines 441-end (createI18n and exports)

# Combine sections
new_lines = []

# Add import section and messages start
new_lines.extend(import_section)

# Add zh-CN part 1
new_lines.extend(zh_cn1)

# Add orphaned zh-CN content (with proper indentation adjustment if needed)
new_lines.extend(orphaned_zh)

# Close zh-CN
new_lines.append('  },\n')
new_lines.append('\n')

# Add en-US
new_lines.append("  'en-US': {\n")
new_lines.extend(en_us1)

# Add orphaned en-US content
new_lines.extend(orphaned_en)

# Close en-US
new_lines.append('  },\n')
new_lines.append('\n')

# Close messages object
new_lines.append('}\n')
new_lines.append('\n')

# Add createI18n section
new_lines.extend(create_i18n_section)

# Write the fixed file
with open('/home/user/nlp_project/frontend-vue/src/i18n/index.ts', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed i18n file!")
print(f"Total lines: {len(new_lines)}")
print(f"Original lines: {len(lines)}")

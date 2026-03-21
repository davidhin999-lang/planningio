import sys
sys.path.insert(0, '.')
from words import GROUP_CONFIG

cfg = GROUP_CONFIG.get('tournament', {})
words = cfg.get('words', {})
easy = words.get('easy', [])

# Deduplicate preserving order
seen = set()
deduped = []
for w in easy:
    key = w.lower().strip()
    if key not in seen:
        seen.add(key)
        deduped.append(w)

print(f"Before: {len(easy)} words")
print(f"After: {len(deduped)} words")
print(f"Removed: {len(easy) - len(deduped)} duplicates")

# Update the file
with open('words.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Rebuild the tournament easy list
quoted = [f'"{w}"' for w in deduped]
lines = []
for i in range(0, len(quoted), 6):
    chunk = quoted[i:i+6]
    lines.append('                ' + ', '.join(chunk) + ',')

words_block = '\n'.join(lines)

# Find and replace the tournament easy list
import re
pattern = r'"tournament":\s*\{[^}]*"easy":\s*\[(.*?)\],'
replacement = f'''"tournament": {{
        "label": "Tournament",
        "ranked_week": 1,
        "words": {{
            "easy": [
{words_block}
            ],'''

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('words.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Deduplicated tournament list saved")

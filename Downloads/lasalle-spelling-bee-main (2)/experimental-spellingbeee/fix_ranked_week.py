import re

with open('words.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace group1's ranked_week from 3 to 2
# Look for "group1": { ... "ranked_week": 3
pattern = r'("group1":\s*\{[^}]*"ranked_week":\s*)3'
replacement = r'\g<1>2'

content = re.sub(pattern, replacement, content)

with open('words.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed group1 ranked_week from 3 to 2')

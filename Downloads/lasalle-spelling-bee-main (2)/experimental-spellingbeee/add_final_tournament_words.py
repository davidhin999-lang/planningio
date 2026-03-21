import re

# Final 32 words to add (169-200)
final_words = [
    "loudly", "classical", "garage", "saturday", "library", "celebrity",
    "fence", "material", "afternoon", "excuse me", "fruits", "american",
    "boring", "dishes", "white", "happiness", "sea lion", "laundromat",
    "octopus", "skirt", "jelly fish", "sneakers", "brown", "colors",
    "paintings", "eraser", "enthusiastic", "rainforest", "sandcastle", "flood",
    "often", "volcano"
]

print(f"Adding {len(final_words)} final words")

with open('words.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the tournament easy words list and append to it
# Pattern: "easy": [ ... ], (find the closing bracket and comma)
pattern = r'("tournament":\s*\{[^}]*"easy":\s*\[[^\]]*)"geography",'

# Build the addition
quoted_words = [f'"{w}"' for w in final_words]
addition = ', '.join(quoted_words)

# Replace the closing of the easy list
old_closing = '"geography",'
new_closing = '"geography", ' + addition + ','

if old_closing in content:
    content = content.replace(old_closing, new_closing)
    with open('words.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Final 32 words added")
else:
    print("ERROR: Could not find closing bracket")

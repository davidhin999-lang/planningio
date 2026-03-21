import re

with open('static/style.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Replace position:fixed with position:absolute in body.theme-competition::before
content = content.replace(
    'body.theme-competition::before {\n  content: "";\n  position: fixed;',
    'body.theme-competition::before {\n  content: "";\n  position: absolute;'
)

# Fix 2: Increase emoji size
content = content.replace(
    '.ref-image { font-size: clamp(80px, 8vw, 120px); }',
    '.ref-image { font-size: clamp(100px, 10vw, 150px); }'
)

# Fix 3: Increase photo size
content = content.replace(
    '.ref-image-photo { width: clamp(160px, 16vw, 240px); height: clamp(160px, 16vw, 240px); }',
    '.ref-image-photo { width: clamp(200px, 20vw, 300px); height: clamp(200px, 20vw, 300px); }'
)

with open('static/style.css', 'w', encoding='utf-8') as f:
    f.write(content)

print('CSS fixed successfully')

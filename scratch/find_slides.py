import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.finditer(r'<div class=["\']slide\b[^"\']*["\']\s+id=["\']([^"\']+)["\']', text)
for i, m in enumerate(matches):
    print(f"Slide {i+1} (index {i}): id='{m.group(1)}' at char {m.start()}")

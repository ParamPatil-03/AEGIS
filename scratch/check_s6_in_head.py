import re

with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    head = f.read()

# find what's in slide-6
m = re.search(r'<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-6["\'][\s\S]*?(?=<div class=["\']slide|\Z)', head)
if m:
    s = m.group(0)
    print("Slide 6 title / headers:")
    for line in s.splitlines()[:40]:
        if any(h in line for h in ['<h', 'class="s', 'class="col', '<canvas']):
            print(line)

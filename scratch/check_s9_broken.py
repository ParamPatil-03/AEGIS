with open('scratch/broken_theme_index.html', 'r', encoding='utf-8') as f:
    broken = f.read()

import re
m = re.search(r'(<div class=["\']slide\b[^"\']*["\']\s+id=["\']slide-6["\'][\s\S]*?)(?=<div class=["\']slide|\Z)', broken)
if m:
    s9 = m.group(1)
    print("Slide 9 in broken:", len(s9))
    for line in s9.splitlines()[:50]:
        if any(k in line.lower() for k in ['cme', 'sun', 'canvas', 'earth', 'globe', 'simulation']):
            print(line)

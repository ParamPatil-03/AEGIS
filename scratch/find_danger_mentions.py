with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'(?:danger|warning)', text)]
print('danger/warning mentions in head:', len(matches))
for pos in matches[:10]:
    line = text[max(0, text.rfind('\n', 0, pos)):text.find('\n', pos)]
    print(line.strip()[:120])

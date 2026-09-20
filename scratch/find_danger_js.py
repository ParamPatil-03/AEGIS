with open('scratch/head_index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'classList\.add\([\'"](?:danger|warning)[\'"]\)', text)]
print('classList.add danger/warning in head:', len(matches))
for pos in matches:
    print('--- SNIPPET ---')
    print(text[pos-150:pos+250].encode('ascii', errors='replace').decode('ascii'))

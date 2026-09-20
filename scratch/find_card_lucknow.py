with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'card-lucknow', text)]
print('card-lucknow occurrences:', len(matches))
for pos in matches:
    print('--- SNIPPET ---')
    print(text[pos-100:pos+300].encode('ascii', errors='replace').decode('ascii'))

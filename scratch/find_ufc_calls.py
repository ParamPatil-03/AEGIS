with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'updateFeedCards', text)]
print('updateFeedCards mentions:', len(matches))
for pos in matches:
    print('--- CALL ---')
    print(text[pos-50:pos+100].encode('ascii', errors='replace').decode('ascii'))

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('val-lucknow-1h')
print('Found val-lucknow-1h at:', pos)
if pos != -1:
    print(text[pos-200:pos+300].encode('ascii', errors='replace').decode('ascii'))

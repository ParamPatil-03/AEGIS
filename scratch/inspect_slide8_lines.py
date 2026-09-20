with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="slide-5"')
end_pos = text.find('id="slide-6"')
slide_html = text[pos:end_pos]

import re
lines = slide_html.splitlines()
for i, line in enumerate(lines):
    if any(k in line for k in ['s6-', 'data-sources', 'meth-panel', '<h2', '</div']):
        if len(line.strip()) < 120:
            print(f"{i}: {line.strip()}")

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="slide-5"')
end_pos = text.find('id="slide-6"')
slide_html = text[pos:end_pos]

import re
tags = re.findall(r'<div[^>]*class=["\']([^"\']+)["\'][^>]*>', slide_html)
print("Classes in Slide 8 (#slide-5):")
for t in set(tags):
    print(" -", t)

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('id="slide-5"')
end_pos = text.find('id="slide-6"')
slide_html = text[pos:end_pos]

import re
# Find all divs with class in slide_html
matches = re.findall(r'<div class="([^"]+)"', slide_html)
print("Classes found in slide 5:", matches)

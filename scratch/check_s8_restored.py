with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos_start = text.find('/* --- SLIDE 8: METHODOLOGY & ARCHITECTURE')
pos_end = text.find('/* --- SLIDE 7: STATION MAP')

print("Slide 8 CSS in restored index.html:")
print(text[pos_start:pos_end][:1200])

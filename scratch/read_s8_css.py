import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos_start = text.find('/* --- SLIDE 8: METHODOLOGY & ARCHITECTURE --- */')
pos_end = text.find('/* --- SLIDE 7: STATION MAP --- */')

print("Slide 8 CSS in index.html:")
print(text[pos_start:pos_end])
